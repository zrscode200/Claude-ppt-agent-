# Sub-Agent Prompt Templates

Templates for spawning sub-agents during style extraction, build, and QA phases.

## Style Extractor Prompt

Use when the user provides a reference `.pptx` and the main agent needs a structured style analysis.

```
Analyze the visual style of this reference presentation. Reverse-engineer its design system.

## Slide Images
{SLIDE_IMAGE_LIST}

## Theme Summary (from XML)
{THEME_SUMMARY}

## Instructions

Study every slide image and extract the visual design system across these 8 dimensions:

1. **Background strategy** — dark/light/mixed, solid/gradient/image fills, structural pattern
2. **Layout vocabulary** — what layout types appear, how they're sequenced, content density
3. **Shape language** — shapes used (rects, circles, lines), corners, shadows, decorative vs. functional
4. **Color application** — how each theme color maps to visual elements (headers, backgrounds, accents, etc.)
5. **Typography patterns** — size hierarchy, weight, alignment, case, character spacing
6. **Motif / signature element** — the one distinctive element carried throughout, how it adapts per layout
7. **Spacing conventions** — margins, gaps, density, alignment tendency
8. **Image treatment** — usage patterns, placement, crops, overlays, icon style

Map observed colors to theme slots: primary, secondary, accent, bg_dark, bg_light, text_on_dark, text_on_light, muted.

Read the agent definition at .claude/agents/style-extractor.md for the full checklist and output format.

Read and analyze these images:
{IMAGE_PATHS_WITH_DESCRIPTIONS}

Return the full Style Extraction Report.
```

## Slide Builder Prompt

Use when spawning `slide-builder` agents during the build phase.

```
You are a slide builder. Build slides {START} through {END} for the "{DECK_NAME}" presentation.

## Content Plan (what to build)
{CONTENT_PLAN_EXCERPT}

## Style Plan (how it looks)
{STYLE_PLAN_EXCERPT}

## Theme JSON
{THEME_JSON}

## Instructions

1. Write a JavaScript function `buildSlides_{START}_{END}(pres, theme)` that adds your slides to the `pres` object
2. Use the **content plan** for what goes on each slide (messages, data, structure)
3. Use the **style plan** for how each slide looks (layouts, visual elements, motif)
4. Use the theme object for ALL colors and fonts — never hardcode hex values
5. Follow the PptxGenJS API — no "#" prefix on colors, use `breakLine: true`, use `bullet: true`
6. Never reuse option objects (PptxGenJS mutates them) — use factory functions
7. Every slide MUST have a visual element (shape, chart, icon)
8. Vary layouts — don't repeat the same layout on consecutive slides

Read the agent definition at .claude/agents/slide-builder.md for full rules.

Return ONLY the JavaScript function. Do not create the pres object or call writeFile.
```

If a plan was skipped, replace its section with the defaults being used (e.g., default theme, agent-chosen layouts).

## Slide Editor Prompt

Use when spawning `slide-editor` agents during the improve phase.

```
You are a slide editor. Edit the following slides in the unpacked presentation.

## Your Assigned Slides
{SLIDE_FILE_PATHS}

## Content Changes (from edit content plan)
{CONTENT_CHANGES}

## Style Changes (from edit style plan)
{STYLE_CHANGES}

## Theme JSON (for color/font reference)
{THEME_JSON}

## Rules
- Use the Edit tool for ALL changes — do not use sed or Python scripts
- Bold all headers with b="1" on <a:rPr>
- Create separate <a:p> for each list item — never concatenate
- Copy <a:pPr> from original paragraphs to preserve spacing
- When removing elements, remove the entire group (not just text)
- Use XML entities for smart quotes

Read the agent definition at .claude/agents/slide-editor.md for full rules.
```

Include only the relevant section(s) — if the edit is content-only, omit the style changes section and vice versa.

## QA Section Reviewer Prompt

Use when spawning `qa-reviewer` agents in **section mode**. For ≤6 slides: spawn one agent covering all slides (its within-group consistency checks naturally cover the full deck). For >6 slides: spawn one per section/topic group, running in parallel.

```
You are reviewing slides {START} through {END} ("{SECTION_NAME}"). Assume there are issues — find them.

**Mode: Section** — deep per-slide inspection + within-group consistency checks.

## Slide Images (your section only)
{SECTION_SLIDE_IMAGE_LIST}

## Diagram Assets (your section only)
{SECTION_DIAGRAM_ASSET_LIST}
<!-- Main agent: list each generated diagram image for this section with its target slide.
     May be PNG, SVG, JPG, or other formats. Omit if no diagrams in this section. -->

## Slide XML + Theme
{SECTION_SLIDE_XML_PATHS}
<!-- Main agent: provide the raw XML for this section's slides + theme XML (ppt/theme/theme1.xml).
     For create: unpack the freshly built .pptx. For edit: use the already-unpacked XML.
     The reviewer uses these as ground truth — thumbnails may not render everything. -->

## Expected Content (from content plan — your section only)
{SECTION_CONTENT_PLAN}

## Expected Visual Style (from style plan — your section only)
{SECTION_STYLE_PLAN}

Read the agent definition at .claude/agents/qa-reviewer.md for the full section mode checklist and output format.

For each slide in your section, list ALL issues found, including minor ones. Report severity: CRITICAL, IMPORTANT, or MINOR.

Read and analyze these images:
{SECTION_IMAGE_PATHS_WITH_DESCRIPTIONS}

Report ALL issues found.
```

### When to split vs. use a single agent

- **≤6 slides under review**: spawn a single `qa-reviewer` in section mode covering all slides. No holistic agent needed.
- **>6 slides under review**: spawn per-section agents + one holistic agent (all in parallel).

### How to group sections (when splitting)

- **Plan mode**: use sections defined in the content plan (e.g., "Section I: slides 3-7", "Section II: slides 8-11"). Bookend slides (title, agenda, conclusion) form their own group.
- **Direct mode / no plan**: use section divider slides as natural boundaries. If none exist, group by ~4-5 slides.
- **Edit**: group changed slides by the section they belong to (from the content plan if available). Only review changed slides unless the edit was broad enough to warrant full-deck QA.
- Each section agent gets only its section's slice of the content plan, style plan, slide images, XML files, and diagram assets.

## QA Holistic Reviewer Prompt

Use when spawning a `qa-reviewer` agent in **holistic mode** (>6 slides only). Spawn exactly one, in parallel with the section agents.

```
Assess whether this deck reads as one cohesive presentation. The section agents are handling per-slide inspection and within-section consistency — your job is to catch what only a full-deck view reveals.

**Mode: Holistic** — overall cohesion and cross-slide consistency. Do NOT do per-slide deep inspection.

## All Slide Thumbnails
{ALL_SLIDE_IMAGE_LIST}

## Expected Visual Style (from style plan — full)
{FULL_STYLE_PLAN}

Read the agent definition at .claude/agents/qa-reviewer.md for the full holistic mode checklist and output format.

Read and analyze these images:
{ALL_IMAGE_PATHS_WITH_DESCRIPTIONS}

Report ALL cross-slide issues found.
```

### Notes for both prompts

If a plan was skipped, replace its section with markitdown extraction or defaults.

## Assembly Script Template

Template for the main PptxGenJS wrapper that assembles sub-agent output.

```javascript
const pptxgen = require("pptxgenjs");

// Theme
const theme = {THEME_JSON};

// Create presentation
let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "{AUTHOR}";
pres.title = "{TITLE}";

// === Slide builder functions (from sub-agents) ===

{BUILDER_FUNCTIONS}

// === Build all slides in order ===

{BUILDER_CALLS}

// === Write output ===
pres.writeFile({ fileName: "{OUTPUT_PATH}" })
  .then(() => console.log("Created: {OUTPUT_PATH}"))
  .catch(err => console.error("Error:", err));
```
