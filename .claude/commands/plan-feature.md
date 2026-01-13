---
argument-hint: [FEATURE-ID]
description: Create step-by-step implementation plan for a feature
---

# Implementation Plan Workflow

Create step-by-step implementation plan for a feature.

## Input
Feature ID: $ARGUMENTS

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows

**Feature documents:**
@docs/feature-specs/$ARGUMENTS.md - What to build (requirements)
@docs/feature-designs/$ARGUMENTS.md - Why/how (design rationale)

**Backlog:**
@docs/planning/BACKLOG.md - Related bugs, improvements, tech-debt

**Project decisions:**
@docs/architecture/README.md - Architecture decisions (ADRs)
@docs/design/README.md - Design patterns (DES)

**Existing plan (if present):**
@docs/feature-plans/$ARGUMENTS.md - Current plan to update or create

Read dependency specs, designs, and code based on "Requires:" field in spec.

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Plan-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/plan-$ARGUMENTS-state.md`:
- Spec and design understanding confirmed
- Relevant ADRs/DES identified
- Implementation steps drafted
- Verification approach for each step
- Pre-implementation checklist items

**Implementation priority** - Order steps following this priority:
1. Core functionality (minimal working feature)
2. Error handling (failure modes from spec)
3. Edge cases (boundary conditions)
4. Configuration/customization (if applicable)
5. Polish/optimization

**Iterative steps** - Each step should be a vertical slice:
- Build each step on the previous, including functionality + error handling + logging + testing for that piece
- Avoid horizontal layers: "implement all X, then add logging to all X, then add tests for all X"
- Prefer vertical slices: "implement A with error handling, logging, and tests → implement B with error handling, logging, and tests"

**Detect gaps proactively** - Challenge plan completeness:
- "Are steps in correct dependency order?"
- "Is each step atomic enough to verify independently?"
- "How will each step be verified before proceeding?"
- "What files/code need to be read first?"
- Never add steps yourself - always propose and get user agreement

## Process

0. **Check existing state**
   - If `docs/feature-plans/$ARGUMENTS.md` exists:
     - Read current plan
     - Check for drift: Has spec changed? Has design changed? Are steps still aligned?
     - Summarize to user: implementation steps, verification approach
     - If drift detected: Highlight discrepancies between plan and current spec/design
     - Ask: "What aspects need refinement? Or should we review the whole plan?"
     - Enter iteration mode as appropriate
   - If no plan exists: proceed with initial creation

1. **Identify Related Backlog Items**

   1. Read BACKLOG.md and identify items related to this feature:
      - Items with `--related $ARGUMENTS`
      - BUG- items that might need fixing during implementation
      - DEBT- items that should be addressed while in this area
      - IMP- items that could be incorporated

   2. If related items found, present them:
      ```
      "Found N backlog items that could be addressed during this feature's implementation:

      [ ] BUG-002: Null pointer when input is empty
      [ ] DEBT-003: Extract common validation logic
      [ ] IMP-001: Add progress indicator

      Which items should be included in the implementation plan? (select numbers, 'all', or 'none')"
      ```

   3. Track selected items - they will be:
      - Incorporated into the implementation plan steps
      - Automatically resolved after implementation completes

2. **Research phase** (silent, thorough)
   - Read feature spec (`docs/feature-specs/$ARGUMENTS.md`)
   - Read feature design (`docs/feature-designs/$ARGUMENTS.md`)
   - Read dependency specs and designs from "Requires:" field in spec
   - Read relevant ADRs from `docs/architecture/README.md`
   - Read relevant DES patterns from `docs/design/README.md`
   - Explore related codebase areas to understand existing structure
   - **For features involving libraries, frameworks, APIs:**
     - Use Task tool or WebFetch to research implementation patterns
     - Understand typical setup/usage sequences
   - Build complete understanding without asking questions
   - Proposals must be grounded in actual knowledge, not assumptions

3. **Draft complete implementation plan**
   - Create full plan document following template
   - Cover all sections:
     - Pre-implementation checklist (dependencies, relevant ADRs/DES, code to read)
     - Implementation steps (ordered by dependency):
       1. Core functionality (minimal working feature)
       2. Error handling (failure modes from spec)
       3. Edge cases (boundary conditions)
       4. Configuration/customization (if applicable)
       5. Polish/optimization
     - For each step: files to modify, what to do, how to verify
     - Verification approach (how to test each acceptance criterion)
   - Base choices on research findings
   - Ensure steps follow design rationale
   - Clearly note any uncertainties or assumptions
   - Include section for related backlog items (if selected in step 1)

4. **Present proposal for review**
   - Show complete plan document to user
   - Highlight any uncertainties and ask about them
   - Invite user feedback: "What needs adjustment in this plan?"

5. **Iterate based on feedback**
   - Apply user corrections, additions, or changes
   - Re-present updated sections if significant changes
   - Repeat until user approves the plan

6. **External validation**
   - Dispatch a general-purpose subagent using the Task tool to review the completed plan
   - Provide minimal context: feature spec, feature design, ADR index, DES index, completed plan
   - Request structured critique covering:
     - **Spec coverage**: Do steps address all acceptance criteria?
     - **Design alignment**: Do steps follow the design approach?
     - **Step ordering**: Are steps in correct dependency order? Any circular dependencies?
     - **Atomicity**: Is each step verifiable independently?
     - **Verification**: Is verification defined for each step? Are tests specified?
     - **Pre-implementation checklist**: Are all dependencies and decisions identified?
     - **Gaps**: What scenarios aren't covered? What could block implementation?
   - Review subagent findings with user
   - Discuss which recommendations to accept

7. **Finalize with iteration check**
   - Ask: "Should we iterate based on validation feedback, or is the plan complete?"
   - If gaps to address → refine steps (go back to step 5)
   - If complete → finalize document to `docs/feature-plans/$ARGUMENTS.md`

## Workflow

**This is a collaborative process:**
- Discuss implementation approach
- User guides the strategy
- Propose steps, ask for validation
- Reference relevant ADRs and patterns
- Iterate until the plan is solid
