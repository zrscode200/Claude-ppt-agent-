# Sub-Agent Prompt Templates

Templates for spawning sub-agents during build and QA phases.

## Slide Builder Prompt

Use when spawning `slide-builder` agents during the build phase.

```
You are a slide builder. Build slides {START} through {END} for the "{DECK_NAME}" presentation.

## Theme
{THEME_JSON}

## Your Assigned Slides

{SLIDE_SPECS}

## Instructions

1. Write a JavaScript function `buildSlides_{START}_{END}(pres, theme)` that adds your slides to the `pres` object
2. Use the theme object for ALL colors and fonts — never hardcode hex values
3. Follow the PptxGenJS API — no "#" prefix on colors, use `breakLine: true`, use `bullet: true`
4. Never reuse option objects (PptxGenJS mutates them) — use factory functions
5. Every slide MUST have a visual element (shape, chart, icon)
6. Vary layouts — don't repeat the same layout on consecutive slides

Read the agent definition at .claude/agents/slide-builder.md for full rules.

Return ONLY the JavaScript function. Do not create the pres object or call writeFile.
```

## Slide Editor Prompt

Use when spawning `slide-editor` agents during the improve phase.

```
You are a slide editor. Edit the following slides in the unpacked presentation.

## Your Assigned Slides
{SLIDE_FILE_PATHS}

## Edit Instructions
{EDIT_INSTRUCTIONS}

## Theme (for color/font reference)
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

## QA Reviewer Prompt

Use when spawning `qa-reviewer` agents.

```
Visually inspect these slides. Assume there are issues — find them.

## Slide Images
{SLIDE_IMAGE_LIST}

## Expected Content Per Slide
{EXPECTED_CONTENT}

## Inspection Checklist
Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (light gray on cream, etc.)
- Low-contrast icons (dark icons on dark backgrounds without contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content
- Same layout repeated on consecutive slides
- Text-only slides with no visual elements

Read the agent definition at .claude/agents/qa-reviewer.md for the full checklist and output format.

For each slide, list ALL issues found, including minor ones. Report severity: CRITICAL, IMPORTANT, or MINOR.

Read and analyze these images:
{IMAGE_PATHS_WITH_DESCRIPTIONS}

Report ALL issues found.
```

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
