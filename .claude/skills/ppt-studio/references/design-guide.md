# Design Guide

Comprehensive design reference for building presentations. This supplements the design ideas in the `document-skills:pptx` plugin.

## Color Palettes

Choose colors that match the topic — never default to generic blue.

| Theme | Primary | Secondary | Accent | Use For |
|-------|---------|-----------|--------|---------|
| Midnight Executive | `1E2761` | `CADCFC` | `FFFFFF` | Corporate, finance, leadership |
| Forest & Moss | `2C5F2D` | `97BC62` | `F5F5F5` | Sustainability, growth, health |
| Coral Energy | `F96167` | `F9E795` | `2F3C7E` | Marketing, creative, launches |
| Warm Terracotta | `B85042` | `E7E8D1` | `A7BEAE` | Culture, HR, community |
| Ocean Gradient | `065A82` | `1C7293` | `21295C` | Technology, data, engineering |
| Charcoal Minimal | `36454F` | `F2F2F2` | `212121` | Minimal, editorial, design |

## Layout Patterns

### Slide Types and When to Use

| Layout | Best For | Description |
|--------|----------|-------------|
| Full-bleed dark | Title, section dividers, conclusion | Dark background, centered text, strong visual impact |
| Two-column | Content + visual, comparison | Text left + image/chart right (or vice versa) |
| Three stat callouts | Key metrics, highlights | Large numbers (60-72pt) with small labels below |
| Icon + text rows | Features, benefits, process steps | Icon in colored circle + bold header + description |
| 2x2 or 2x3 grid | Team, features, categories | Cards with consistent styling |
| Half-bleed image | Visual storytelling | Full image on one side, content on the other |
| Timeline / process | Workflows, history, steps | Numbered steps with connecting elements |
| Quote / callout | Testimonials, key statements | Large italic text with attribution |

### Layout Sequencing

**Never repeat the same layout on consecutive slides.** A good sequence:

1. Title (full-bleed dark)
2. Agenda (icon + text rows)
3. Key metrics (stat callouts)
4. Detail (two-column)
5. Data (chart + takeaways)
6. Team/features (grid)
7. Conclusion (full-bleed dark)

## Typography

### Font Pairings

| Header | Body | Character |
|--------|------|-----------|
| Georgia | Calibri | Classic, trustworthy |
| Arial Black | Arial | Bold, modern |
| Trebuchet MS | Calibri | Friendly, approachable |
| Cambria | Calibri | Academic, polished |
| Impact | Arial | High-energy, attention |
| Palatino | Garamond | Elegant, literary |

### Size Scale

| Element | Size | Weight |
|---------|------|--------|
| Slide title | 36-44pt | Bold |
| Section header | 20-24pt | Bold |
| Body text | 14-16pt | Regular |
| Captions / labels | 10-12pt | Regular, muted color |
| Large stat numbers | 60-72pt | Bold |
| Stat labels | 12-14pt | Regular |

### Rules
- Left-align paragraphs and lists — center only titles and stat callouts
- Use `charSpacing: 4-6` on all-caps subtitles for breathing room
- Never go below 10pt — if it doesn't fit, restructure the content

## Spacing

| Element | Minimum |
|---------|---------|
| Slide edge margins | 0.5" |
| Between content blocks | 0.3-0.5" |
| Between cards/sections | 0.3" |
| Text box internal padding | 0.1-0.15" (or `margin: 0` when aligning with shapes) |

**Consistency is key.** Pick either 0.3" or 0.5" for gaps and use it throughout.

## Visual Elements

### Shapes as Design Elements
- **Accent bars**: Thin rectangles (0.08" wide) on the left side of content cards
- **Background panels**: Subtle colored rectangles behind content groups
- **Divider lines**: Thin lines to separate sections within a slide
- **Icon circles**: Colored circles (0.5-0.6" diameter) as icon backgrounds

### Charts
- Always apply palette colors via `chartColors`
- Subtle grid lines (`color: "E2E8F0"`, `size: 0.5`)
- Hide category grid lines (`style: "none"`)
- Use `dataLabelPosition: "outEnd"` for bar charts
- Hide legend for single-series charts

### Icons
- Use react-icons (Font Awesome, Material Design, Heroicons)
- Render at 256px for crisp quality
- Display at 0.4-0.6" on slides
- Always on a contrasting background (colored circle or light panel)

## Anti-Patterns (Never Do These)

1. **Accent lines under titles** — hallmark of AI-generated slides
2. **Text-only slides** — always add a visual element
3. **Generic blue palette** — choose topic-specific colors
4. **Same layout repeated** — vary across slides
5. **Centered body text** — left-align paragraphs
6. **Low contrast** — test text AND icons against backgrounds
7. **Cramped spacing** — leave breathing room
8. **Random spacing** — be consistent throughout
9. **Unicode bullets (.)** — use `bullet: true`
10. **Default chart styling** — always customize colors and clean up grid lines
