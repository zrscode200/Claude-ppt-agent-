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

## Output File
Write your function to: `{OUTPUT_FILE_PATH}`

## Instructions

1. Write an async JavaScript function `buildSlides_{START}_{END}(pres, theme)` that adds your slides to the `pres` object
2. Export it: `module.exports = { buildSlides_{START}_{END} };`
3. Use the **content plan** for what goes on each slide (messages, data, structure)
4. Use the **style plan** for how each slide looks (layouts, visual elements, motif)
5. Use the theme object for ALL colors and fonts — never hardcode hex values
6. Follow the PptxGenJS API — no "#" prefix on colors, use `breakLine: true`, use `bullet: true`
7. Never reuse option objects (PptxGenJS mutates them) — use factory functions
8. Every slide MUST have a visual element (shape, chart, icon)
9. Vary layouts — don't repeat the same layout on consecutive slides

Read the agent definition at .claude/agents/slide-builder.md for full rules.

Write the function to the output file. Reply with ONLY: "Wrote buildSlides_{START}_{END} to {OUTPUT_FILE_PATH} (N slides)"
Do NOT include code in your response.
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

## Output File
Write your full report to: `{OUTPUT_FILE_PATH}`

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

Write your full report to the output file. Reply with ONLY your summary: "Found N issues: X critical, Y important, Z minor. [PASS | PASS WITH FIXES | FAIL]"
Do NOT include the full report in your response.
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

## Output File
Write your full report to: `{OUTPUT_FILE_PATH}`

## All Slide Thumbnails
{ALL_SLIDE_IMAGE_LIST}

## Expected Visual Style (from style plan — full)
{FULL_STYLE_PLAN}

Read the agent definition at .claude/agents/qa-reviewer.md for the full holistic mode checklist and output format.

Read and analyze these images:
{ALL_IMAGE_PATHS_WITH_DESCRIPTIONS}

Write your full report to the output file. Reply with ONLY your summary: "Found N issues: X critical, Y important, Z minor. [PASS | PASS WITH FIXES | FAIL]"
Do NOT include the full report in your response.
```

### Notes for both prompts

If a plan was skipped, replace its section with markitdown extraction or defaults.

## Assembly Script Template

Template for the main `build.js` wrapper that assembles sub-agent section files via `require()`. Each section file is written by a `slide-builder` sub-agent. The main agent writes this wrapper after all builders confirm, then runs `node build.js`.

```javascript
const pptxgen = require("pptxgenjs");

// Import section files (written by slide-builder sub-agents)
const { buildSlides_{RANGE_1} } = require("./{SECTION_FILE_1}");
const { buildSlides_{RANGE_2} } = require("./{SECTION_FILE_2}");
// ... one require() per section file

// Theme
const theme = {THEME_JSON};

// Create presentation
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "{AUTHOR}";
pres.title = "{TITLE}";

// Sections — ordered list with expected slide counts
const sections = [
  { fn: buildSlides_{RANGE_1}, file: "{SECTION_FILE_1}", expected: {COUNT_1} },
  { fn: buildSlides_{RANGE_2}, file: "{SECTION_FILE_2}", expected: {COUNT_2} },
  // ... one entry per section
];

async function main() {
  for (const { fn, file, expected } of sections) {
    const before = pres.slides.length;
    try {
      await fn(pres, theme);
      const added = pres.slides.length - before;
      if (added !== expected) {
        console.warn(`WARNING: ${file} expected ${expected} slides, got ${added}`);
      }
      console.log(`${file}: OK (${added} slides)`);
    } catch (e) {
      console.error(`FAILED in ${file} (after slide ${before}):`);
      console.error(e.message);
      process.exit(1);
    }
  }

  console.log(`Total: ${pres.slides.length} slides`);
  await pres.writeFile({ fileName: "{OUTPUT_PATH}" });
  console.log("Created: {OUTPUT_PATH}");
}

main();
```

**Notes:**
- Each `require()` loads a section file that exports one `buildSlides_N_M(pres, theme)` function
- Sections run sequentially in slide order — each adds slides to the shared `pres` object
- Per-section try/catch isolates errors to the exact file and slide position
- Slide count validation catches mismatches early (builder added fewer/more slides than expected)
- `process.exit(1)` on first failure — fix one section at a time
- Always run as a fresh `node build.js` process (Node's `require()` cache is per-process)
