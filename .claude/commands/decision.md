---
description: Document an architecture or design decision
argument-hint: [topic, existing ID, or backlog ID]
---

# Decision Documentation Workflow

Document an architecture or design decision.

## Input

$ARGUMENTS - Optional: topic to document, existing decision ID to update, or **backlog item ID** (Q-XXX)

## Backlog Integration

If a backlog item ID is provided (e.g., `/decision Q-001`):

1. **Load item context**
   - Run `python scripts/backlog.py show <ID>` to get item details
   - Use title and notes as initial context for the decision
   - If item has related features, consider how they're affected

2. **After decision documented**
   - Prompt: "Mark <ID> as resolved?"
   - If yes: Run `python scripts/backlog.py fix <ID>` (questions are resolved by documenting a decision)

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows (one question at a time, propose don't decide, use AskUserQuestion for structured options, detect gaps proactively, scratchpad usage, research triggers)

**Decision indexes:**
@docs/architecture/README.md - Architecture Decision Records (ADRs)
@docs/design/README.md - Design Patterns (DES)

**Backlog:**
@docs/planning/BACKLOG.md - Questions and related items

**Features document (if exists):**
@docs/planning/FEATURES.md - Feature inventory to check for affected features

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Decision-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/decision-<animal-adjective>-state.md` (generate unique ID):
- Current decision being worked on (ADR/DES ID and title)
- Questions asked and answered
- Alternatives discussed
- Agent validation findings
- Gaps identified
- Refinements to apply
- Affected features/specs/designs

**Research when uncertain** - If user shows uncertainty about alternatives, best practices, or technical choices:
- Use Task tool (general-purpose agent) to research options
- Synthesize findings to inform questions
- Present research-backed trade-offs

**Detect gaps proactively** - Challenge completeness throughout:
- "What could go wrong with this decision in 6 months?"
- "What alternatives haven't we considered?"
- "What's the migration path if this decision proves wrong?"
- "Are there hidden costs or consequences we're missing?"
- "What features/components will be affected by this decision?"
- Never fill gaps yourself - always propose and get user agreement

**Impact awareness** - When updating/superseding decisions:
- Check which features reference this decision
- Check which specs/designs reference this decision
- Present impact before making changes

## Process

0. **Check existing state**
   - If user mentioned a specific decision ID → read that decision, enter update mode
   - Otherwise, use AskUserQuestion: Create new decision or update existing?
   - If updating:
     - List existing decisions from both indexes
     - Use AskUserQuestion: Which decision to update?
     - Read current decision document
     - Read docs/planning/FEATURES.md to identify affected features
     - Summarize current state
     - Present complete updated proposal (follow steps 2-4 for updates)
   - If creating new: proceed with creation workflow

1. **Identify Related Backlog Items**

   1. Search BACKLOG.md for related items:
      - Q- items that might be answered by this decision
      - Other items whose resolution depends on this decision

   2. If related items found (beyond the Q-XXX being documented if any), present them:
      ```
      "Found N backlog items that might be resolved by this decision:

      [ ] Q-003: Should we use library X or Y?
      [ ] Q-007: What's our caching strategy?

      Which items will this decision resolve? (select numbers, 'all', or 'none')"
      ```

   3. Track selected items for automatic resolution at the end

2. **Determine decision type** (if creating new)
   - Use AskUserQuestion to present choice:
     - **Question**: "What type of decision are you documenting?"
     - **Header**: "Decision Type"
     - **Options**:
       - **ADR (Architecture)**: Hard-to-change, foundational decisions (platform, language, storage, core libraries, architecture patterns)
       - **DES (Design)**: Evolving patterns and conventions (testing approach, error handling, code style, module organization)
     - **multiSelect**: false

3. **Research phase** (silent, thorough)
   - Read existing decisions from both indexes
   - Read relevant ADRs and DES patterns
   - **For technical decisions involving libraries, frameworks, APIs:**
     - Use Task tool (general-purpose agent) to research:
       - Alternative solutions and their trade-offs
       - Current best practices and community adoption
       - Known issues and gotchas
       - Performance/complexity comparisons
   - Build complete understanding without asking questions
   - Proposals must be grounded in actual knowledge, not assumptions

4. **Draft complete decision document**

   a. **For ADR (Architecture)**
      - Create full ADR document following template
      - Cover all sections:
        - Context/Problem (what problem, what constraints)
        - Decision (clear, unambiguous statement)
        - Consequences - Positive (benefits, what this enables)
        - Consequences - Negative (costs, complexity added)
        - Alternatives (other options considered)
        - Why alternatives rejected (rationale for each)
        - Migration path (how to change this decision later)
        - Monitoring (how to know if decision is still right)
      - Base choices on research findings
      - Clearly note any uncertainties or assumptions
      - Assign next ID (ADR-NNN)

   b. **For DES (Design)**
      - Create full DES document following template
      - Cover all sections:
        - Scope (project-wide or module-specific)
        - Pattern (pattern/convention to follow)
        - Rationale (why this pattern, problem it solves)
        - Good example (code following the pattern)
        - Bad example (anti-pattern to avoid)
        - Exceptions (when OK to deviate)
        - Related patterns (connections to other DES)
      - Base choices on research findings
      - Clearly note any uncertainties or assumptions
      - Assign next ID (DES-NNN)

5. **Present proposal for review**
   - Show complete decision document to user
   - Highlight any uncertainties and ask about them
   - Invite user feedback: "What needs adjustment in this decision?"

6. **Iterate based on feedback**
   - Apply user corrections, additions, or changes
   - Re-present updated sections if significant changes
   - Repeat until user approves the decision

7. **Agent validation**
   - Dispatch a general-purpose subagent using the Task tool to review the drafted decision
   - Provide minimal context: the drafted decision document, relevant indexes

   - **For ADR**, request structured critique covering:
     - **Completeness**: Are all alternatives considered? Are consequences thorough (both positive and negative)?
     - **Clarity**: Is the context/problem clearly stated? Is the decision unambiguous?
     - **Alternatives analysis**: Are rejected alternatives well-reasoned? Are there obvious alternatives missing?
     - **Consequences**: Are trade-offs realistic? Are hidden costs surfaced?
     - **Future-proofing**: Does the decision lock us in unnecessarily? Are escape hatches documented?
     - **Migration path**: Is the path to change this decision clear?

   - **For DES**, request structured critique covering:
     - **Pattern clarity**: Is the pattern well-defined and unambiguous?
     - **Examples quality**: Do examples clearly illustrate the pattern? Are anti-patterns helpful?
     - **Exception cases**: Are valid exceptions clearly defined? Are they too broad/narrow?
     - **Applicability**: Is scope (project-wide vs module-specific) correct?
     - **Completeness**: Does the pattern address common edge cases?
     - **Related patterns**: Are connections to other patterns identified?

   - Review subagent findings with user
   - Discuss which recommendations to accept

8. **Finalize with iteration check**
   - Ask: "Should we iterate based on validation feedback, or is the decision ready?"
   - If gaps/issues to address → refine relevant sections (go back to step 6)
   - If complete → proceed to impact analysis

9. **Impact analysis** (if updating existing decision)
   - Understand the change type:
     - Ask: Should we supersede (major change) or evolve (refinement)?

   - Analyze impact:
     - Check docs/planning/FEATURES.md for features that reference this decision
     - Check docs/feature-specs/ and docs/feature-designs/ directories for references
     - Present impact to user: "This decision is referenced by [features/specs/designs]. Updates may be needed."

   - **For superseding (major change)**:
     - Create new decision with next ID
     - Link to old decision: "Supersedes [OLD-ID]"
     - Update old decision status to "Superseded by [NEW-ID]"
     - Update both indexes
     - Note affected documentation that may need updates

   - **For evolution (refinement)**:
     - Add to "Evolution" section with version number and date
     - Update "Last Updated" date
     - Keep old approach in evolution history
     - Update current approach section
     - Add migration notes if behavior changes

10. **Finalization and Resolve Backlog**

   - Create/update decision document in appropriate directory:
     - ADR: `docs/architecture/ADR-NNN-topic.md`
     - DES: `docs/design/DES-NNN-topic.md`
   - Update appropriate index (README.md)
   - **DES/ADR modification checklist** (follow for each decision):
     1. ✓ Decision document created/updated
     2. ✓ Index (README.md) updated with quick reference entry
     3. Note affected features/specs/designs that may need updates
     4. Document decision in commit message
   - Present checklist completion to user for confirmation

   **Automatically resolve selected backlog items:**

   For each Q- item the user selected to include (from step 1):
   - `python scripts/backlog.py fix <ID>` (answered by decision)

   Report: "Resolved N backlog items: Q-003, Q-007"

## Gap Detection Questions

Use these questions throughout the collaborative process:

**Alternatives and trade-offs:**
- "What other approaches did you consider?"
- "Why didn't those work?"
- "Are there alternatives we haven't thought of?"

**Consequences:**
- "What could go wrong with this decision?"
- "What hidden costs might this have?"
- "What complexity does this add?"
- "What does this enable that we couldn't do before?"

**Future-proofing:**
- "What happens if this decision proves wrong in 6 months?"
- "How would we migrate away from this choice?"
- "Are we locking ourselves in unnecessarily?"

**Context:**
- "What constraints led to this decision?"
- "What problem are we really solving?"
- "Are there unstated assumptions?"

**Impact:**
- "Which features depend on this decision?"
- "What else needs to change if we update this?"

## Workflow

**This is a collaborative process:**
- Research thoroughly before drafting (especially for technical decisions)
- Draft complete proposal first, then gather feedback
- Agent proposes, user confirms - never decide without agreement
- Use AskUserQuestion for structured options (decision type, supersede vs evolve, which decision to update)
- Highlight uncertainties in proposal and ask about them
- Challenge completeness and gaps throughout
- Agent validation provides external perspective
- Impact analysis prevents breaking changes
- Iterate until the decision is complete and validated
- User confirms before finalizing

## Templates

### ADR Template

```markdown
# ADR-NNN: [Title]

**Status**: Accepted | Superseded
**Date**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
**Supersedes**: [ADR-XXX] (if applicable)
**Superseded by**: [ADR-YYY] (if applicable)

## Context

[What problem does this solve? What constraints exist?]

## Decision

[Clear, unambiguous statement of the decision]

## Consequences

### Positive

- [Benefits and capabilities this enables]

### Negative

- [Costs, complexity, trade-offs]

## Alternatives Considered

### [Alternative 1 Name]

- **Description**: [What is this alternative?]
- **Why not chosen**: [Specific reasons for rejection]

### [Alternative 2 Name]

- **Description**: [What is this alternative?]
- **Why not chosen**: [Specific reasons for rejection]

## Migration Path

[If this decision needs to change in the future, what's the path?]

## Monitoring

[How do we know if this decision is still serving us well?]

## Affected Features

- [FEATURE-ID]: [How this feature uses/depends on this decision]

---

## Notes

[Additional context, references, links]

## Evolution

### Version 1.1 (YYYY-MM-DD)

[If refined, document the evolution here]
```

### DES Template

```markdown
# DES-NNN: [Pattern Name]

**Scope**: Project-wide | Module-specific
**Date**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Pattern

[Clear description of the pattern/convention to follow]

## Rationale

[Why this pattern? What problem does it solve?]

## Examples

### Do This

\`\`\`[language]
[Good example following the pattern]
\`\`\`

[Explanation of why this is good]

### Don't Do This

\`\`\`[language]
[Anti-pattern example]
\`\`\`

[Explanation of why this is problematic]

## Exceptions

[When is it OK to deviate from this pattern? What circumstances justify exceptions?]

## Related Patterns

- [DES-XXX]: [How this relates]
- [DES-YYY]: [How this relates]

## Affected Features

- [FEATURE-ID]: [How this feature follows this pattern]

---

## Evolution

### Version 1.1 (YYYY-MM-DD)

[Document pattern refinements here]
```
