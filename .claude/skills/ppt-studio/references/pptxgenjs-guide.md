# PptxGenJS Guide

## Setup & Basic Structure

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';  // 10" x 5.625"
pres.author = 'Your Name';
pres.title = 'Presentation Title';

let slide = pres.addSlide();
slide.addText("Hello World!", { x: 0.5, y: 0.5, fontSize: 36, color: "363636" });

pres.writeFile({ fileName: "output.pptx" });
```

## Layout Dimensions (inches)

- `LAYOUT_16x9`: 10" x 5.625" (default)
- `LAYOUT_16x10`: 10" x 6.25"
- `LAYOUT_4x3`: 10" x 7.5"
- `LAYOUT_WIDE`: 13.3" x 7.5"

---

## Text & Formatting

```javascript
// Basic text
slide.addText("Title", {
  x: 1, y: 1, w: 8, h: 2, fontSize: 24, fontFace: "Arial",
  color: "363636", bold: true, align: "center", valign: "middle"
});

// Character spacing (use charSpacing, NOT letterSpacing)
slide.addText("SPACED TEXT", { x: 1, y: 1, w: 8, h: 1, charSpacing: 6 });

// Rich text arrays
slide.addText([
  { text: "Bold ", options: { bold: true } },
  { text: "Italic ", options: { italic: true } }
], { x: 1, y: 3, w: 8, h: 1 });

// Multi-line (requires breakLine: true)
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2", options: { breakLine: true } },
  { text: "Line 3" }
], { x: 0.5, y: 0.5, w: 8, h: 2 });

// margin: 0 when aligning text with shapes/icons
slide.addText("Title", { x: 0.5, y: 0.3, w: 9, h: 0.6, margin: 0 });
```

---

## Lists & Bullets

```javascript
// Bullets
slide.addText([
  { text: "First item", options: { bullet: true, breakLine: true } },
  { text: "Second item", options: { bullet: true, breakLine: true } },
  { text: "Third item", options: { bullet: true } }
], { x: 0.5, y: 0.5, w: 8, h: 3 });

// Sub-items
{ text: "Sub-item", options: { bullet: true, indentLevel: 1 } }

// Numbered
{ text: "First", options: { bullet: { type: "number" }, breakLine: true } }
```

**NEVER use unicode bullets like "."** — they create double bullets.

---

## Shapes

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.8, w: 1.5, h: 3.0,
  fill: { color: "FF0000" }, line: { color: "000000", width: 2 }
});

slide.addShape(pres.shapes.OVAL, { x: 4, y: 1, w: 2, h: 2, fill: { color: "0000FF" } });

slide.addShape(pres.shapes.LINE, {
  x: 1, y: 3, w: 5, h: 0, line: { color: "FF0000", width: 3, dashType: "dash" }
});

// With transparency
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2, fill: { color: "0088CC", transparency: 50 }
});

// Rounded rectangle
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2, fill: { color: "FFFFFF" }, rectRadius: 0.1
});

// With shadow
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2, fill: { color: "FFFFFF" },
  shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.15 }
});
```

**Shadow options:**

| Property | Type | Notes |
|----------|------|-------|
| `type` | `"outer"` / `"inner"` | |
| `color` | 6-char hex | No `#`, no 8-char hex |
| `blur` | 0-100 pt | |
| `offset` | 0-200 pt | Must be non-negative |
| `angle` | 0-359 degrees | 135 = bottom-right, 270 = upward |
| `opacity` | 0.0-1.0 | Use this, never encode in color |

---

## Images

```javascript
// From file
slide.addImage({ path: "images/chart.png", x: 1, y: 1, w: 5, h: 3 });

// From base64
slide.addImage({ data: "image/png;base64,iVBORw0KGgo...", x: 1, y: 1, w: 5, h: 3 });

// Options
slide.addImage({
  path: "image.png", x: 1, y: 1, w: 5, h: 3,
  rounding: true,     // circular crop
  transparency: 50,
  sizing: { type: 'cover', w: 4, h: 3 }  // or 'contain', 'crop'
});
```

---

## Icons (via react-icons)

```javascript
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaCheckCircle } = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

const iconData = await iconToBase64Png(FaCheckCircle, "#4472C4", 256);
slide.addImage({ data: iconData, x: 1, y: 1, w: 0.5, h: 0.5 });
```

Icon libraries: `react-icons/fa`, `react-icons/md`, `react-icons/hi`, `react-icons/bi`

---

## Backgrounds

```javascript
slide.background = { color: "F1F1F1" };
slide.background = { path: "https://example.com/bg.jpg" };
slide.background = { data: "image/png;base64,..." };
```

---

## Tables

```javascript
slide.addTable([
  [{ text: "Header", options: { fill: { color: "6699CC" }, color: "FFFFFF", bold: true } }, "Cell"],
  [{ text: "Merged", options: { colspan: 2 } }]
], { x: 1, y: 1, w: 8, colW: [4, 4], border: { pt: 1, color: "999999" } });
```

---

## Charts

```javascript
// Bar chart
slide.addChart(pres.charts.BAR, [{
  name: "Sales", labels: ["Q1", "Q2", "Q3"], values: [4500, 5500, 6200]
}], {
  x: 0.5, y: 1, w: 9, h: 4, barDir: "col",
  chartColors: ["0D9488", "14B8A6", "5EEAD4"],
  valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" },
  showValue: true, dataLabelPosition: "outEnd",
  showLegend: false
});

// Line chart
slide.addChart(pres.charts.LINE, [{ name: "Temp", labels: ["Jan", "Feb"], values: [32, 42] }],
  { x: 0.5, y: 4, w: 6, h: 3, lineSize: 3, lineSmooth: true });

// Pie chart
slide.addChart(pres.charts.PIE, [{ name: "Share", labels: ["A", "B"], values: [35, 65] }],
  { x: 7, y: 1, w: 5, h: 4, showPercent: true });
```

**Chart types:** BAR, LINE, PIE, DOUGHNUT, SCATTER, BUBBLE, RADAR

---

## Slide Masters

```javascript
pres.defineSlideMaster({
  title: 'TITLE_SLIDE', background: { color: '283A5E' },
  objects: [{
    placeholder: { options: { name: 'title', type: 'title', x: 1, y: 2, w: 8, h: 2 } }
  }]
});
let titleSlide = pres.addSlide({ masterName: "TITLE_SLIDE" });
```

---

## Common Pitfalls

1. **NEVER use "#" with hex colors** — causes file corruption
2. **NEVER encode opacity in hex** (8-char like `"00000020"`) — use `opacity` property
3. **Use `bullet: true`** — never unicode "."
4. **Use `breakLine: true`** between text array items
5. **Avoid `lineSpacing` with bullets** — use `paraSpaceAfter`
6. **Fresh instance per presentation** — don't reuse `pptxgen()` objects
7. **NEVER reuse option objects** — PptxGenJS mutates them. Use factory functions:
   ```javascript
   const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 });
   ```
8. **Don't use `ROUNDED_RECTANGLE` with accent borders** — use `RECTANGLE` instead

## Available Shapes

RECTANGLE, OVAL, LINE, ROUNDED_RECTANGLE
