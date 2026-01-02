---
argument-hint: [FEATURE-ID]
description: Write a specification for a feature
---

# Feature Specification Workflow

Write a spec for a specific feature.

## Input
Feature ID: $ARGUMENTS (e.g., "CORE-001")

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows

**Feature inventory:**
@planning/FEATURES.md - Feature definitions and complexity ratings
@planning/DEPENDENCIES.md - Feature dependencies and implementation phases

**Project decisions:**
@docs/architecture/README.md - Architecture decisions (ADRs)
@docs/design/README.md - Design patterns (DES)

**Existing spec (if present):**
@specs/$ARGUMENTS.md - Current spec to update or create

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Spec-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/spec-$ARGUMENTS-state.md`:
- Current section being worked on
- User story components captured
- Acceptance criteria identified
- Edge cases and error scenarios to address
- Gaps identified

**Detect gaps proactively** - Challenge completeness throughout:
- "What inputs could be invalid?"
- "What errors could occur during this operation?"
- "What happens if a dependency fails?"
- "Is this acceptance criterion testable?"
- Never add requirements yourself - always propose and get user agreement

## Process

0. **Check existing state**
   - If `specs/$ARGUMENTS.md` exists:
     - Read current spec
     - Check for drift: Has FEATURES.md description changed? Are there new dependencies?
     - Summarize to user: user story, key acceptance criteria, known edge cases
     - If drift detected: Highlight discrepancies
     - Ask: "What aspects need refinement? Or should we review the whole spec?"
     - Enter iteration mode as appropriate
   - If no spec exists: proceed with initial creation

1. **Research phase** (silent, thorough)
   - Read feature description from `planning/FEATURES.md`
   - Read dependencies from `planning/DEPENDENCIES.md`
   - Read relevant ADRs from `docs/architecture/README.md`
   - Read relevant DES patterns from `docs/design/README.md`
   - Explore related codebase areas if needed
   - **For features involving libraries, frameworks, APIs:**
     - Use Task tool or WebFetch to research typical usage patterns
     - Understand standard behaviors and edge cases
   - Build complete understanding without asking questions
   - Proposals must be grounded in actual knowledge, not assumptions

2. **Draft complete spec proposal**
   - Create full spec document following template
   - Cover all sections:
     - User story (who/what/why - specific and clear)
     - Behavior description (inputs, outputs, what can go wrong)
     - Acceptance criteria (Given/When/Then format, include error cases)
     - Dependencies (features that must exist first)
   - Make reasonable assumptions about typical usage
   - Base choices on research findings
   - Clearly note any uncertainties or assumptions

3. **Present proposal for review**
   - Show complete spec document to user
   - Highlight any uncertainties and ask about them
   - Invite user feedback: "What needs adjustment in this spec?"

4. **Iterate based on feedback**
   - Apply user corrections, additions, or changes
   - Re-present updated sections if significant changes
   - Repeat until user approves the spec

5. **External validation**
   - Dispatch a general-purpose subagent using the Task tool to review the completed spec
   - Provide minimal context: feature description from FEATURES.md, completed spec
   - Request structured critique covering:
     - **User story completeness**: Is who/what/why clear and specific?
     - **Acceptance criteria**: Are all criteria testable (Given/When/Then)? Are they complete?
     - **Edge cases**: Are invalid inputs covered? Are boundary conditions addressed?
     - **Error scenarios**: Are failure modes identified? Is error behavior specified?
     - **Dependencies**: Are required features correctly identified?
     - **Gaps**: What scenarios aren't addressed? What could go wrong?
   - Review subagent findings with user
   - Discuss which recommendations to accept

6. **Finalize with iteration check**
   - Ask: "Should we iterate based on validation feedback, or is the spec complete?"
   - If gaps to address → refine relevant sections (go back to step 4)
   - If complete → finalize document to `specs/$ARGUMENTS.md`

## Workflow

**This is a collaborative process:**
- Ask detailed questions about behavior
- User describes the feature thoroughly
- Capture edge cases and errors
- NEVER assume what the user wants
- Iterate until the spec is clear and complete
