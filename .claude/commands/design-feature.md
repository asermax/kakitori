---
argument-hint: [FEATURE-ID]
description: Write design rationale for a feature
---

# Feature Design Workflow

Document the design rationale: modeling, data flow, system behavior.

## Input
Feature ID: $ARGUMENTS

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows

**Feature spec:**
@docs/feature-specs/$ARGUMENTS.md - The specification we're designing for

**Backlog:**
@docs/planning/BACKLOG.md - Related bugs, ideas, improvements, questions

**Project decisions:**
@docs/architecture/README.md - Architecture decisions (ADRs)
@docs/design/README.md - Design patterns (DES)

**Design template:**
@docs/feature-designs/TEMPLATE.md - Template for design documents

**Existing design (if present):**
@docs/feature-designs/$ARGUMENTS.md - Current design to update or create

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Design-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/design-$ARGUMENTS-state.md`:
- Problem context captured
- Design approach decisions
- Modeling choices made
- Data flow documented
- Key decisions with rationale
- Patterns identified (existing DES used, new patterns emerging)

**Detect gaps proactively** - Challenge design completeness:
- "What alternatives were considered and why rejected?"
- "What constraints shaped this design choice?"
- "How does data flow through the system for this feature?"
- "What could go wrong with this approach?"
- Never make design decisions yourself - always propose and get user agreement

## Process

0. **Check existing state**
   - If `docs/feature-designs/$ARGUMENTS.md` exists:
     - Read current design
     - Check for drift: Has spec changed? Are there new acceptance criteria or error scenarios?
     - Summarize to user: design approach, key decisions, modeling choices
     - If drift detected: Highlight discrepancies between design and current spec
     - Ask: "What aspects need refinement? Or should we review the whole design?"
     - Enter iteration mode as appropriate
   - If no design exists: proceed with initial creation

1. **Identify Related Backlog Items**

   1. Read BACKLOG.md and identify items related to this feature:
      - Items with `--related $ARGUMENTS`
      - Q- items that might be answered by design decisions
      - DEBT- items that might be addressed by the design approach
      - IMP- items that could be incorporated

   2. If related items found, present them:
      ```
      "Found N backlog items related to this feature's design:

      [ ] Q-002: What caching strategy should we use?
      [ ] DEBT-001: Refactor data access layer
      [ ] IMP-004: Support batch operations

      Which items should be addressed in this design? (select numbers, 'all', or 'none')"
      ```

   3. Track selected items for automatic resolution at the end

2. **Research phase** (silent, thorough)
   - Read feature spec (`docs/feature-specs/$ARGUMENTS.md`)
   - **Read ADR/DES pattern documents (not just indexes):**
     - Start with `docs/architecture/README.md` and `docs/design/README.md` to identify relevant patterns
     - Use the quick reference tables to find patterns for your task
     - **Explicitly read the full ADR/DES documents** referenced in spec or related to feature domain
     - Example: If spec mentions logging → read full `docs/design/DES-001-logging.md`
     - Example: If spec involves testing → read full `docs/design/DES-003-testing-patterns.md`
   - Explore related codebase areas if needed
   - **For designs involving libraries, frameworks, APIs:**
     - Use Task tool or WebFetch to research official documentation
     - Look up best practices and standard patterns
     - Understand recommended approaches before proposing
   - Build complete understanding without asking questions
   - Proposals must be grounded in actual knowledge, not assumptions

3. **Draft complete design proposal**
   - Create full design document following `docs/feature-designs/TEMPLATE.md`
   - Cover all sections:
     - Problem context (problem being solved, constraints, interactions)
     - Design approach (high-level solution, components/concepts, alternatives)
     - Modeling (entities, relationships, domain model)
     - Data flow (how data moves, interaction paths, trigger-to-result flow)
     - Key decisions (choices made, alternatives considered, rationale, consequences)
     - System behavior (edge cases, error scenarios)
     - Pattern alignment (existing DES used, new patterns emerging)
   - Base all choices on research findings
   - Clearly note any uncertainties or assumptions

4. **Present proposal for review**
   - Show complete design document to user
   - Highlight any uncertainties and ask about them
   - Invite user feedback: "What needs adjustment in this design?"

5. **Iterate based on feedback**
   - Apply user corrections, additions, or changes
   - Re-present updated sections if significant changes
   - Repeat until user approves the design

6. **External validation**
   - Dispatch a general-purpose subagent using the Task tool to review the completed design
   - Provide minimal context: feature spec, ADR index, DES index, completed design
   - Request structured critique covering:
     - **Problem context**: Is the problem clearly articulated? Are constraints explicit?
     - **Design coherence**: Does the approach solve the problem? Are components well-defined?
     - **Modeling**: Are entities and relationships clear? Is the domain model complete?
     - **Data flow**: Is data movement through the system documented?
     - **Key decisions**: Are alternatives documented? Is rationale provided? Are consequences noted?
     - **Pattern alignment**: Does design follow relevant ADRs? Does it use/establish DES patterns correctly?
     - **Gaps**: What scenarios aren't addressed? What edge cases are missing?
   - Review subagent findings with user
   - Discuss which recommendations to accept

7. **Finalize with iteration check**
   - Ask: "Should we iterate based on validation feedback, or is the design complete?"
   - If gaps to address → refine relevant sections (go back to step 5)
   - If complete → finalize document to `docs/feature-designs/$ARGUMENTS.md`

8. **Finalize and Resolve Backlog**

   Finalize document to `docs/feature-designs/$ARGUMENTS.md`

   **Automatically resolve selected backlog items:**

   For each item the user selected to include (from step 1):
   - Q- items: `python scripts/backlog.py fix <ID>` (answered by design)
   - DEBT- items: `python scripts/backlog.py fix <ID>` (addressed in design)
   - IMP- items: Note in item that it's incorporated in feature design

   Report: "Resolved N backlog items: Q-002, DEBT-001"

## Workflow

**This is a collaborative process:**
- Help user articulate the design
- Ask about trade-offs and alternatives
- Document thoroughly with rationale
- Ensure design answers WHY and HOW
- User makes all design decisions
- Reference relevant ADRs and existing DES patterns
