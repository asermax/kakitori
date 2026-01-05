---
argument-hint: [description or file path]
description: Review code, propose changes, and ensure decision compliance
---

# Code Review Workflow

Review code, propose changes, fix issues - all while ensuring alignment with design decisions (ADRs/DES). If decisions need updating, this command ensures all documents stay in sync.

## Input

$ARGUMENTS - Description of issue/change, file path, or **backlog item ID** (BUG-XXX, IMP-XXX, DEBT-XXX)

## Backlog Integration

If a backlog item ID is provided (e.g., `/review-code BUG-001`):

1. **Load item context**
   - Run `python scripts/backlog.py show <ID>` to get item details
   - Use title and notes as initial context for the review
   - If item has related features, read those feature specs/designs

2. **After successful commit**
   - Prompt: "Mark <ID> as fixed?"
   - If yes: Run `python scripts/backlog.py fix <ID> --commit <hash>`

## Context

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows

**Project decisions:**
@docs/architecture/README.md - Architecture decisions (ADRs)
@docs/design/README.md - Design patterns (DES)

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Review-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/review-code-<animal-adjective>-state.md` (generate unique ID):
- Request type (bug, improvement, compliance check, question)
- Affected files identified
- Relevant decisions (ADRs/DES) that apply
- Compliance issues found
- Proposed changes and rationale
- Decision updates needed (if any)

## Process

1. **Understand the request** (silent)
   - Parse: bug report, improvement proposal, question, or compliance check
   - Identify affected code areas
   - Determine scope: single file, module, or cross-cutting

2. **Research relevant decisions** (silent)
   - Read `docs/architecture/README.md` and `docs/design/README.md`
   - Use quick reference tables to identify which ADRs/DES patterns apply to the affected code
   - **Read FULL decision documents** (not just the README summaries)
   - Note constraints and patterns that must be followed

3. **Analyze current code** (silent)
   - Read affected files
   - Check compliance with identified decisions
   - Identify gaps, violations, or improvement opportunities
   - Note any code that doesn't follow established patterns

4. **Present findings with decision context**
   - Show current code state (relevant snippets)
   - Explain which decisions apply and how
   - Identify any decision violations or gaps
   - Propose solution with rationale
   - If deviation from decision needed: explain why
   - Include diagrams if helpful (see command-guidance.md: Bridge Context Gap)
   - Ask: "What needs adjustment in this analysis?"

5. **Iterate on proposal**
   - Apply user feedback
   - Re-analyze if scope changes
   - Repeat until user approves approach

6. **Handle decision updates** (if needed)
   When implementation reveals decision should change:

   a. **Impact analysis first**
      - Check FEATURES.md for features referencing this decision
      - Check specs/ and designs/ directories for references
      - Present impact to user before proceeding

   b. **Update decision document**
      - For DES: Add to "Evolution" section, preserve history
      - For ADR (major architectural change): Create new ADR, supersede old

   c. **Sync all references**
      - Update index (README.md in architecture/ or design/) with quick reference entry
      - Note affected features/specs/designs that need updates

7. **Implement approved changes**
   - Apply code changes
   - Add decision reference comments where appropriate
     Format: `// See ADR-NNN: reason` or `// See DES-NNN: reason`
   - Only reference when choice would be unclear without context
   - Run tests and linting
   - Fix any issues found

8. **Automated validation** (subagent)
   - Dispatch general-purpose subagent (model: opus) to review changes
   - Provide minimal context: affected code, relevant ADRs/DES, changes made
   - Request structured critique covering:
     - **Decision compliance**: Do changes follow applicable ADRs and DES?
     - **Pattern application**: Are patterns applied correctly with full details?
     - **Production code purity** (DES-003): No test-specific logic in production code?
     - **README sync**: If decisions were updated, is the README index updated?
     - **Code quality**: Bugs, edge cases, potential issues?
     - **Decision references**: Are code comments appropriate and accurate?
     - **Documentation sync**: Are all affected documents updated?

9. **Fix all validation issues**
   - Automatically address ALL issues identified by subagent
   - Re-run tests after fixes
   - Do NOT ask user - fix everything autonomously

10. **Present final changes for user review**
    - Show complete changes made
    - Summarize decision alignment
    - Highlight any deviations with rationale
    - List any decisions that were updated
    - Ask: "What needs adjustment?"

11. **Iterate based on feedback**
    - Apply user corrections
    - Re-test and re-validate if significant changes
    - Repeat until user approves

12. **Commit**
    - Create commit with decision references in message
    - If decisions were updated, note in commit message
    - Update CLAUDE.md current focus if applicable

## Decision Update Checklist

When updating any ADR or DES, follow this checklist:
- [ ] Decision document updated (full content with rationale)
- [ ] Index (README.md) updated in appropriate folder (quick reference table and summaries)
- [ ] Affected features/specs/designs noted for user awareness
- [ ] Commit message references decision change

## Decision Update Strategy

**Update DES (evolve)**:
- Better approach found, keeps original ID
- Add to "Evolution" section with date and rationale
- Preserve original content for history

**Update ADR (supersede)**:
- Architectural choice was wrong or significantly changed
- Create new ADR with next ID
- Mark old ADR as "Superseded by ADR-NNN"
- Link between old and new

## When to Use This Command

- **Fixing bugs**: Get decision-aware fixes that follow project patterns
- **Proposing improvements**: Ensure changes align with established decisions
- **Compliance checks**: Verify code follows ADRs and DES patterns
- **Updating code for decision changes**: When decisions evolve, update code to match
- **Reporting issues**: Get analysis of what's wrong and how to fix it properly

## Workflow

**This is a collaborative process with autonomous validation:**
- Research decisions and analyze code silently
- Present findings with full decision context
- User approves approach before implementation
- Implement changes following decisions
- Subagent validates compliance autonomously
- Fix ALL validation issues without asking
- Present final changes for user review
- User approves final result
- Commit with decision references
