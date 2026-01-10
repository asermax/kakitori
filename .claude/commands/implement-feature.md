---
argument-hint: [FEATURE-ID]
description: Implement a feature following its plan
---

# Implementation Workflow

Implement a feature following its plan.

## Input
Feature ID: $ARGUMENTS

## Context

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows

**Feature documents:**
@docs/feature-specs/$ARGUMENTS.md - What to build (requirements)
@docs/feature-designs/$ARGUMENTS.md - Why/how (design rationale)
@docs/feature-plans/$ARGUMENTS.md - Implementation steps to follow

**Project decisions:**
@docs/architecture/README.md - Architecture decisions (ADRs)
@docs/design/README.md - Design patterns (DES)

Read dependency code as specified in plan's pre-implementation checklist.

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Implementation-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/implement-$ARGUMENTS-state.md`:
- Current step in the plan
- Steps completed
- Issues encountered during implementation
- Patterns detected that might warrant DES
- Deviations from plan (with rationale)

**Focus on verification** - After each step:
- Verify the step works as expected before proceeding
- Document any issues or adjustments made
- Don't batch steps without verification

## Process

1. **Review plan and decisions** (silent)
   - Read implementation plan (`docs/feature-plans/$ARGUMENTS.md`)
   - Read spec and design
   - **Read full ADR/DES documents (not just indexes):**
     - Identify ADRs/DES listed in plan's pre-implementation checklist
     - Use README quick reference tables to find relevant patterns for your task
     - **Explicitly read the full documents** for each listed pattern
     - Example: Plan says "See DES-003" → read full `docs/design/DES-003-testing-patterns.md`
     - Example: Plan says "See ADR-007" → read full `docs/architecture/ADR-007-logging.md`
   - Read dependency code from pre-implementation checklist
   - Understand constraints and patterns to follow

2. **Implement all steps autonomously**
   - Work through all steps in the plan without asking questions
   - Documentation is the source of truth - implementation should follow it
   - For each step:
     - Implement the code following relevant decisions
     - **Add code comments** referencing decisions when:
       - Implementation choice might seem arbitrary without context
       - Decision significantly impacts the approach
       - Future maintainers would benefit from knowing WHY
       - Format: `// See ADR-003 for why we use X instead of Y`
     - **If a different approach is needed for valid reasons** (e.g., API limitation, deprecated feature, better approach discovered): Update the relevant document (spec/design/plan) immediately, then proceed
     - If no valid justification for deviation: Conform to the documentation
     - Verify the step works before proceeding
     - Document issues in scratchpad
   - Continue until all steps completed

3. **Verify acceptance criteria**
   - Run all tests
   - Run linting and type checking (fix any issues before proceeding)
   - Perform manual checks against spec
   - Ensure all acceptance criteria are met

4. **External validation**
   - Dispatch a general-purpose subagent using the Task tool to review the implementation
   - Provide minimal context: feature spec (acceptance criteria), feature design, implementation plan, implemented code, relevant ADR/DES documents
   - Request structured critique covering:
     - **Acceptance criteria**: Does code satisfy all criteria from spec?
     - **Design alignment**: Does implementation follow the design approach?
     - **Pattern compliance**:
       - Does code follow relevant ADRs and DES patterns listed in plan?
       - **Production code purity** (DES-003): No test-specific logic in production code (no env vars, test_mode params, conditional test paths)?
       - Are patterns applied correctly with full details, not just superficially?
     - **README sync**: If DES or ADR was created/modified during implementation, is the README index updated?
     - **Code quality**: Any obvious bugs, edge cases missed, or potential issues?
     - **Decision references**: Are code comments referencing decisions appropriate?
     - **Documentation sync**: Were spec/design/plan documents updated when implementation required a different approach?

5. **Fix all issues found by subagent**
   - Automatically address ALL issues identified in validation
   - Apply fixes for:
     - Missing acceptance criteria coverage
     - Design misalignment
     - Pattern violations
     - Code quality issues
     - Missing or incorrect decision references
     - Missing documentation updates for justified deviations
   - Re-run tests after fixes
   - Do NOT ask user - fix everything autonomously

6. **Present for user review**
   - Show complete implementation to user
   - Summarize what was implemented
   - Highlight any deviations from plan (with rationale)
   - Note any emergent patterns detected
   - Invite user feedback: "What needs adjustment in this implementation?"

7. **Iterate based on user feedback**
   - Apply user corrections or changes
   - Re-test after changes
   - **When user rejects code changes**: Update documents (spec/design/plan) consistently to reflect the accepted approach
   - Repeat until user approves

8. **Surface patterns for DES consideration**
   - Present discovered patterns to user for selection
   - **Suggest new DES if**:
     - Same approach used 2+ times in this feature
     - Solves common problem that will recur
     - Pattern should be consistent across codebase (even if library-specific)
   - **Suggest updating existing DES if**:
     - Found better approach than documented
     - Discovered exception case or limitation
     - Need to add clarification
   - User selects which patterns to document
   - **DES/ADR modification checklist** (follow for each pattern):
     1. Create/update the DES or ADR document itself
     2. Update README index (quick reference table and summaries)
     3. Update any affected feature designs if pattern changed
     4. Document the pattern change in commit message
   - **Impact awareness** - Before updating any decision:
     - Check what other specs/designs reference this decision
     - Consider ripple effects across the codebase
     - Present impact to user before making changes
   - **Decision Update Strategy**:
     - **Update ADR (supersede)**: Architectural choice was wrong, creates new ADR
     - **Update DES (evolve)**: Better approach found, keeps original ID with version history
     - **Create new DES**: Correction introduces repeatable pattern

9. **Commit**
    - Create atomic commit with feature ID and brief description
    - Follow commit message conventions
    - Update CLAUDE.md current focus

## Working with Decisions

**Using ADRs and DES**:
- Read all decisions listed in the plan's pre-implementation checklist
- Follow constraints and patterns unless there's good reason to deviate
- If deviation is needed:
  - Discuss with user first
  - Consider if decision should be updated
  - Document rationale

**Referencing Decisions in Code**:
- Add comments linking to decisions ONLY when:
  - The choice would be unclear without context
  - The decision constrains the implementation significantly
  - Future changes might question the approach
- Format: `// See [DECISION-ID]: [brief reason]`
- Examples:
  - `// See ADR-002: Using Rust for memory safety requirements`
  - `// See DES-005: Explicit error types instead of exceptions`
- Don't reference low-level patterns obvious from context

**Pattern Detection**:
- Watch for repeated code structures
- Notice when solving cross-cutting concerns
- Identify conventions emerging naturally
- Suggest documentation when patterns should be consistent

## Workflow

**This is an autonomous implementation process:**
- Read plan, spec, design, and decisions silently
- Implement all steps without asking questions during implementation
- Apply relevant ADR and DES decisions
- Add decision references in code when contextually important
- Verify each step works before proceeding (testing, not user confirmation)
- Run linting and type checking in addition to tests
- Run subagent validation after implementation
- **Automatically fix ALL issues found by subagent** (no user approval needed)
- Present complete implementation to user for final review
- Iterate based on user feedback
- **After user accepts**: Sync documentation (update spec/design/plan with deviations)
- Surface patterns for DES consideration; user selects which to document
- Commit when user approves
