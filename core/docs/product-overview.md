# PPT Studio — Product Overview

PPT Studio turns a working directory into a presentation-building agent. You describe what you want; the agent plans the deck, builds it, inspects the output with fresh eyes, and fixes what's wrong before handing it back. This doc explains what the agent can do and — at a conceptual level — how it gets there.

## What you can do with it

Four things, all driven by natural conversation:

- **Build a deck from scratch.** Describe the topic, audience, and vibe. The agent collaborates on an outline and a visual direction, then assembles the deck.
- **Turn a document into a deck.** Hand it a markdown file, a PDF, or a `.docx`. It reads the source, proposes a slide structure that fits the material, and builds from there.
- **Review a deck.** Point it at an existing `.pptx` (or just slide images). You get a report covering content clarity, visual quality, consistency, and specific fixes — not vague advice.
- **Improve a deck.** Review-then-edit in one workflow. Findings become concrete edits; each round produces a new version with a changelog so you can compare.

You can invoke any of these explicitly with a slash command, or just say what you want and let the agent route.

## The mental model

Three layers, each doing one job:

**Fundamental actions** are the atoms: `review`, `create`, `edit`. Each one is self-contained — you can use them directly for surgical work ("fix spacing on slide 3," "review just the visuals").

**Composed commands** are pre-wired sequences of atoms for common patterns: `create-deck` (conversation → create), `improve-deck` (review → edit), `deck-from-doc` (review source → create). They exist because these three sequences come up constantly and there's no reason to re-plumb them each time.

## Plan first, build second

For anything non-trivial, the agent works plan-first. Two plan types:

- **Content plan** — what goes on each slide: title, key message, talking points, what visuals/data are needed (what, not how).
- **Style plan** — how the deck looks: theme, color application, motif, per-slide layout direction.

Plans are drafts until approved. You iterate on them in markdown — revise, push back, ask for alternatives — before a single slide gets built. This is where most of the creative decisions land, and it's much cheaper to rework a plan than a rendered deck.

Every draft is preserved (`content-plan-draft-1.md`, `-2.md`, ...), never overwritten. When you approve, the draft gets copied to `content-plan-approved.md`. The trail is intentional: you can see how the thinking evolved, and the agent can reference decisions later.

For quick one-off requests ("just throw together three slides on X"), the agent skips the planning ceremony and goes direct. **Plan mode** vs. **direct mode** is a judgment the agent makes from context — and composed commands can force one or the other.

## Sub-agents, and why they exist

For larger decks, the main agent delegates to sub-agents. This isn't just a parallelism trick — it's there for two specific reasons:

**Context preservation.** Building a 20-slide deck means holding a lot of code, content, and visual state in working memory. If the main agent does it all itself, its context fills up with implementation detail and it loses the thread. Delegating means each sub-agent owns a bounded chunk, writes its output to a file, and returns a one-line confirmation. The main agent stays focused on orchestration and the fix-and-verify loop.

**Fresh eyes.** The agent that built a slide is the worst critic of it — it already knows what the slide is "supposed" to show, so it glosses over problems. A separate QA sub-agent, given only the rendered images and no build context, catches what the builder missed.

Four sub-agents, each for a specific reason:

- **style-extractor** — called when you provide a reference deck, so the agent can learn a visual language from an example rather than inventing one from scratch.
- **slide-builder** — called for decks over ~12 slides, splitting the build across coherent sections (not arbitrary chunks) so each builder owns one topic.
- **slide-editor** — called for edits that touch more than ~8 slides, so XML changes can happen in parallel.
- **qa-reviewer** — called on every deck. Per-section reviewers do deep inspection; a holistic reviewer checks cross-slide consistency. This one is not optional.

## Visual QA is mandatory

Every deck goes through a visual QA pass before it's delivered. Slides get rendered to images, sub-agent reviewers examine them, and specific issues (overlapping text, bad contrast, inconsistent margins, broken hierarchy) are fixed and re-verified.

One rule the agent takes seriously: **zero-issue first pass means you weren't looking hard enough.** At least one fix-and-verify cycle runs before anything is declared done, even on short decks. Reviews work from primary sources (the rendered slides, extracted text, underlying XML) — never from previous review reports, to avoid anchoring bias.

## Versions and artifacts

Every build lands in its own version folder (`v1/`, `v2/`, ...). Edits don't overwrite the previous deck — they produce a new version with a changelog describing what changed. If you ask for a third round of changes, you get `v3/` with a changelog referencing `v2/`. The old decks stick around; nothing is lost.

Alongside versions, each deck accumulates a small set of markdown artifacts: approved plans, review reports, and changelogs. These are the record of how the deck was made — useful for audit, for resuming later, and for the agent itself when it needs to make consistent choices across a long session.

## Autonomy modes

You control how often the agent pauses for your input, configured in `.ppt/config.md`:

| Mode | When it pauses |
|------|----------------|
| **supervised** | Before every significant action — plan drafts, builds, edits |
| **gated** (default) | At plan approval and final delivery |
| **autonomous** | Only when genuinely ambiguous |

Pick the mode that matches how much you want to be in the loop. Supervised is good when you're learning the tool; autonomous is good when you know what you want and just want it built.

## What PPT Studio is not

A few things the agent explicitly doesn't try to be:

- **Not a template library.** It builds decks programmatically from themes (colors, fonts, layout direction) — not by filling in pre-made slide templates. You can point it at a reference deck as a style source, but the output is always generated.
- **Not a design system generator.** Themes are lightweight — a palette, two fonts, a background strategy. The design decisions happen per-deck, in the style plan.
- **Not a one-shot slide-bot.** The plan-then-build loop, the QA cycle, and the version trail are all intentional. If you want zero-ceremony generation, direct mode exists, but the defaults favor getting it right over getting it fast.
- **Not a replacement for a designer.** It gets you to a defensible, non-boring deck quickly. A real designer will still make a better one.

## Where to go next

- `CLAUDE.md` at the workspace root is the agent's full operating manual — detailed rules, file conventions, sub-agent invocation criteria.
- `.claude/skills/ppt-studio/references/` holds the design guide, the PptxGenJS reference, the editing reference, and the sub-agent prompt library. These are what the agent reads when it needs to know how to do something specific.
- `.ppt/config.md` is where you set autonomy mode and default theme.
