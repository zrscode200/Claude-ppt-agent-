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

## QA Reviewer Prompt

Use when spawning `qa-reviewer` agents.

```
Visually inspect these slides. Assume there are issues — find them.

## Slide Images
{SLIDE_IMAGE_LIST}

## Diagram Assets
{DIAGRAM_ASSET_LIST}
<!-- Main agent: list each generated diagram image with its target slide, e.g.
     "slide09_network_diagram.png → used in slide 9"
     May be PNG, SVG, JPG, or other formats. Omit this section entirely if no diagrams were generated as images. -->

## Slide XML + Theme
{SLIDE_XML_PATHS}
<!-- Main agent: always provide the raw slide XML files for the assigned slides,
     plus the theme XML (ppt/theme/theme1.xml). For create: unpack the freshly
     built .pptx. For edit: use the already-unpacked XML from the edit phase.
     The qa-reviewer uses these as ground truth to verify colors, fonts,
     positions, and element structure against what it sees in the images. -->

## Expected Content Per Slide (from content plan)
{CONTENT_PLAN_SUMMARY}

## Expected Visual Style (from style plan)
{STYLE_PLAN_SUMMARY}

## Inspection Checklist

### Content (check against content plan)
- Missing content that should be there per the content plan
- Wrong data or numbers
- Leftover placeholder content
- Typos or truncated text

### Visual Style (check against style plan)
- Theme colors applied correctly
- Correct layouts per the style plan
- Visual motif consistent across slides
- Same layout repeated on consecutive slides
- Text-only slides with no visual elements

### Diagrams & Embedded Images (when diagram assets are provided)
- Labels readable at slide scale (not just when zoomed into the raw PNG)
- Arrows and connectors point to their correct targets
- Visual hierarchy clear (primary elements larger/bolder than secondary)
- Color palette matches the deck theme (no off-brand colors from library defaults)
- Sufficient contrast between adjacent elements within the diagram
- Diagram communicates its message without requiring study — not cluttered
- Proper fit within slide (not stretched, cropped, or leaving dead space)

### Layout & Spacing
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently

### Typography & Contrast
- Low-contrast text (light gray on cream, etc.)
- Low-contrast icons (dark icons on dark backgrounds without contrasting circle)
- Text boxes too narrow causing excessive wrapping

Read the agent definition at .claude/agents/qa-reviewer.md for the full checklist and output format.

For each slide, list ALL issues found, including minor ones. Report severity: CRITICAL, IMPORTANT, or MINOR.

Read and analyze these images:
{IMAGE_PATHS_WITH_DESCRIPTIONS}

Report ALL issues found.
```

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
