---
description: Create a new presentation with brainstorm and planning
argument-hint: <topic or title>
---

# Create Deck

Composed workflow: **Conversation → Create (plan mode)**

The full-service deck creation experience. Adds a brainstorm conversation layer on top of the `/create` fundamental.

## Phase 1: Conversation

**Start freeform.** Ask the user about their presentation:

> "Tell me about this presentation — what's it for, who's the audience, and what are the key messages you want to land?"

Follow the user's thread naturally. Probe for:
- Purpose and context (why does this deck exist?)
- Audience (who will see it, what do they care about?)
- Key messages (what should the audience remember?)
- Tone (formal, casual, technical, creative?)
- Visual direction (dark, minimal, bold, branded?)
- Any existing content, data, or documents to incorporate

**Before moving to planning**, verify you have enough to work with:

- [ ] Purpose
- [ ] Audience
- [ ] Tone
- [ ] Key messages / content outline
- [ ] Approximate slide count
- [ ] Any images, data, or branding to include

If anything is missing, ask. Don't assume.

**User provides `$ARGUMENTS`?** Use it as the starting topic, but still explore. The argument is a seed, not a complete brief.

## Phase 2: Create (Plan Mode)

Follow the `/create` fundamental in plan mode:

1. **Planning** — build content plan and/or style plan collaboratively (see `/create` for the full planning flow)
2. **Build** — theme loading, sub-agent orchestration, output to version folder
3. **QA** — run Review on the built deck, fix issues
4. **Deliver** — show slide images, report file path, offer to refine

## What this adds over `/create`

- The brainstorm conversation phase — exploring the user's needs before jumping into planning
- Always uses plan mode (never direct)
- The checklist ensures no key information is missed
