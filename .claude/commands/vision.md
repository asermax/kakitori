---
description: Create or update the project vision document
---

# Vision Document Workflow

Guide the user through creating docs/planning/VISION.md.

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows (one question at a time, propose don't decide, use AskUserQuestion for structured options, detect gaps proactively, scratchpad usage, research triggers)

**Vision document:**
@docs/planning/VISION.md - Current project vision (if exists)

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Vision-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/vision-state.md`:
- Current section being worked on
- Questions asked and answered
- Gaps identified
- Topics to revisit

## Process

0. **Check existing state**
   - If `docs/planning/VISION.md` exists:
     - Read current vision document
     - Read project state (features, specs, implementation progress if any)
     - Summarize current state to user
     - Ask: "What aspects need refinement? Or should we review the whole vision?"
     - Enter iteration mode: analyze each section for gaps given current project state
   - If no vision exists: proceed with initial creation

1. **Understand the problem**
   - What problem are you trying to solve?
   - Who experiences this problem?
   - How do they currently deal with it?

2. **Research existing solutions and technical approaches**
   - Use Task tool (general-purpose agent) to research:
     - Existing solutions (commercial and open source)
     - Technical approaches (models, frameworks, libraries)
     - Known issues with alternatives
     - Best practices and patterns
   - Synthesize findings to inform questions

3. **Define core workflows**
   - What are the main things a user will do with this software?
   - For each workflow:
     - What triggers this workflow?
     - What's the end result?
     - What are the key steps?

4. **Set scope boundaries**
   - What MUST be in v1? (included)
   - What is explicitly NOT in v1? (excluded)
   - Challenge scope creep: "Is this really necessary for v1?"

5. **Technical context**
   - Where does this run? (platform)
   - How do users interact with it?
   - What external systems does it connect to?
   - DETECT: Platform/language/storage choices → prompt for ADR

6. **Write the document**
   - Show draft to user
   - Ask for feedback
   - Iterate until approved

7. **External validation and completeness check**
   - Dispatch a general-purpose subagent using the Task tool to review the completed vision
   - Provide minimal context: just the completed vision document
   - Request structured critique covering:
     - **Clarity**: Is the problem, solution, and scope clearly articulated?
     - **Completeness**: Are workflows fully specified? Is technical context sufficient? Are all workflows covered?
     - **Internal consistency**: Do all sections align? Do workflows solve the problem? Does scope support workflows? Does tech support scope?
     - **Unstated assumptions**: What's implied but not explicit?
     - **Scope boundaries**: Is v1 scope realistic? Are exclusions clear?
     - **Gaps**: Between problem/workflows, workflows/scope, scope/technical context
     - **Edge cases**: What scenarios aren't addressed?
   - Review subagent findings with user
   - Discuss which recommendations to accept
   - Ask user: "Should we iterate on any section based on this feedback, or is the vision complete?"
   - If gaps/issues to address → refine relevant sections
   - If complete → finalize document

## Decision Detection

When user mentions hard-to-change choices, offer to create ADRs:
- Platform choice → "Should we create ADR-001-platform?"
- Language choice → "Should we create ADR-002-language?"
- Storage approach → "Should we create ADR-003-storage?"
- Model/library choice → "Should we create ADR-XXX-topic?"

## Workflow

**This is a collaborative process:**
- Ask one question at a time
- Agent proposes, user confirms - never decide without agreement
- User makes all decisions
- Provide alternatives and trade-offs (research-backed)
- Never fill gaps yourself - always ask the user
- Iterate until the user approves the final document
