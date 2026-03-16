---
description: Quickly create a presentation without a formal spec
argument-hint: <description of what you want>
---

# Quick Deck

Fast-track deck creation. No spec file, no brainstorm phase. Just build.

## When to Use

User wants something fast: "make me a quick 5-slider on X", "just throw together slides about Y".

## Workflow

1. **Parse the request.** Extract from `$ARGUMENTS` or conversation:
   - Topic / title
   - Approximate slide count (default: 5-7 if not specified)
   - Any specific content mentioned

2. **Pick defaults:**
   - Theme: read `.ppt/config.md` for `default_theme`, or pick one that fits the topic
   - Tone: infer from context (default: professional)
   - Layouts: varied — never repeat the same layout

3. **Create deck folder:** `.ppt/decks/<deck-name>/`
   - No spec file — just go straight to building

4. **Build:**
   - Create version folder `v1/`
   - If >5 slides: spawn sub-agents
   - If ≤5 slides: build directly
   - Use PptxGenJS (default) or template if user provided one

5. **QA:**
   - Convert to images, save to `v1/slides/`
   - Spawn `qa-reviewer` sub-agent
   - Fix issues, re-verify
   - Save findings to `v1/qa-review.md`

6. **Deliver:**
   - Show slide images
   - Report file path
   - Offer: "Want me to refine anything?"

## Key Difference from /create-deck

- No brainstorm conversation
- No spec file created
- Agent makes design decisions autonomously
- Faster, but less user control over the design
