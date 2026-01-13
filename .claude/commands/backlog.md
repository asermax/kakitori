---
description: Manage bugs, ideas, improvements, tech-debt, and questions
argument-hint: [action, ID, or description]
---

# Backlog Management

Manage backlog items interactively with duplicate detection, refinement, and guided workflows.

## Input

$ARGUMENTS - Optional, can be:
- **Action**: `add bug clipboard issue`, `show BUG-001`, `list --priority 1-2`
- **ID only**: `BUG-001` (auto-detects as "work on this item")
- **Natural language**: `there's a bug with the clipboard` (auto-detects type and action)

## Context

**Backlog file:**
@docs/planning/BACKLOG.md

**Feature documentation:**
`@docs/planning/FEATURES.md` - Feature inventory for related features
`@docs/architecture/README.md` - ADR index (for Q- items about decisions)
`@docs/design/README.md` - DES index (for questions about patterns)

**Script reference:**
`scripts/backlog.py` - CLI tool for backlog management

## Actions

### No arguments - Interactive triage
Show open items by priority and help process them.

### add [type] [description]
Add new item with duplicate detection and refinement.

### show [ID]
Show item details with context from related features.

### list [filters]
List items with optional filters.

### work [ID]
Start working on an item - shows details and suggests next action.

### resolve [ID]
Interactive resolution - ask for resolution type and details.

## Process

### 1. Parse input

If no arguments provided, go to **Triage Mode** (step 2a).
If arguments provided, parse action and execute appropriate flow.

### 2a. Triage Mode (no arguments)

1. Run `python scripts/backlog.py list` to get open items
2. Show summary: "You have N open items. X high priority (1-2)."
3. For each high-priority item, show and ask:
   - "Work on this now?" → Go to **Work Flow**
   - "Skip" → Move to next item
   - "Change priority" → Ask for new priority, update via script
4. After high-priority items, ask if user wants to see medium/low priority

### 2b. Add Flow

1. **Parse type and initial description**
   - If type missing, ask: "What type? (bug, idea, improvement, tech-debt, question)"
   - If description missing, ask: "Brief description?"

2. **Search existing documentation**
   - Search FEATURES.md for features that might relate to the item
   - For Q- items: check ADR and DES indexes to see if question relates to existing decisions
   - Note related features/decisions for later use

3. **Check for duplicates**
   - Run `python scripts/backlog.py check "<description>"`
   - If matches found, show them and ask:
     - "Is this a duplicate of [ID]?" → Run `backlog.py duplicate <new> <existing>`
     - "Add as new" → Continue
     - "Link as related" → Continue, add related ID

4. **Refine the item**

   Review the initial description and help make it unambiguous:

   a. **Clarify the problem/idea**
      - Ask clarifying questions if description is vague
      - For bugs: "What behavior is observed? What's expected?"
      - For ideas: "What problem does this solve? What would success look like?"

   b. **Propose refined title**
      - Clear, specific, action-oriented
      - Should be understandable without context
      - Example: "Context capture returns clipboard content" not "clipboard bug"

   c. **Propose refined description for notes**
      - Brief but complete context
      - Include reproduction steps if bug
      - Include motivation if idea
      - Enough detail to pick up later

   d. **Suggest related features/decisions**
      - Based on documentation search (step 2), suggest `--related FEATURE-ID`
      - For Q- items: note if an existing ADR/DES might already answer the question

   e. **Show proposed item and confirm**
      ```
      Title: [refined title]
      Type: [type]
      Priority: [ask user, 1-5]
      Related: [suggest based on context]
      Notes: [refined description]

      Does this capture it correctly? (yes/adjust)
      ```

5. **Create item**
   - Run `python scripts/backlog.py add <type> "<title>" --priority N --related X --notes "..."`
   - Confirm: "Created [ID]: [title]"

### 2c. Show Flow

1. Run `python scripts/backlog.py show <ID>`
2. If item has related features, read their specs/designs for context
3. Present item with related feature summaries

### 2d. List Flow

1. Parse filters from arguments (--type, --priority, --related, --all)
2. Run `python scripts/backlog.py list [filters]`
3. Present results

### 2e. Work Flow

1. Run `python scripts/backlog.py show <ID>` to get details
2. Read related feature specs/designs if any
3. Show full context
4. Based on item type, suggest action:
   - **BUG/IMP/DEBT**: "Suggest: `/review-code <ID>` to fix this"
   - **IDEA**: "Suggest: `/add-feature <ID>` to promote this to a feature"
   - **Q**: "Suggest: `/decision <ID>` to document a decision"
5. Ask: "Proceed with suggested action?" / "Choose different action" / "Cancel"

### 2f. Resolve Flow

1. Run `python scripts/backlog.py show <ID>` to show current state
2. Ask resolution type:
   - "Fixed" → Ask for commit hash (optional), run `backlog.py fix <ID> [--commit X]`
   - "Promoted" → Ask for feature ID (optional), run `backlog.py promote <ID> [--feature X]`
   - "Dismissed" → Ask for reason, run `backlog.py dismiss <ID> "reason"`
   - "Duplicate" → Ask for duplicate-of ID, run `backlog.py duplicate <ID> <other-ID>`
3. Confirm resolution

## Item Types

| Type | Prefix | Suggested Resolution |
|------|--------|---------------------|
| bug | BUG- | `/review-code` to fix |
| idea | IDEA- | `/add-feature` to promote |
| improvement | IMP- | `/review-code` to implement |
| tech-debt | DEBT- | `/review-code` to clean up |
| question | Q- | `/decision` to document |

## Priority Scale

| Priority | Meaning |
|----------|---------|
| 1 | Critical - blocking work |
| 2 | High - address soon |
| 3 | Medium - when convenient |
| 4 | Low - nice to have |
| 5 | Someday - might never do |

## Examples

### Adding a bug

```
User: /backlog add bug clipboard picking up wrong value

Agent: Let me help capture this properly.

[Checks for duplicates - none found]

To make this actionable later:
- What specific behavior are you seeing?
- When does this happen?

User: when no text is selected, it picks up clipboard instead of returning empty

Agent: Here's the refined item:

Title: Context capture returns clipboard content when no text selected
Type: bug
Priority: ? (1=critical, 2=high, 3=medium, 4=low, 5=someday)
Related: CTX-001 (based on context)
Notes: When cursor is at start of input (nothing to select), capture() returns
       clipboard content instead of None. Expected: return None when no selection.

What priority?

User: 2

Agent: Created BUG-001: "Context capture returns clipboard content when no text selected"

To fix this: /review-code BUG-001
```

### Triaging backlog

```
User: /backlog

Agent: You have 3 open items. 1 high priority.

[1] BUG-001: Context capture returns clipboard content when no text selected
    Priority: 2 (high) | Related: CTX-001
    Added: 2026-01-05

Work on this now? [Work / Skip / Reprioritize]

User: work

Agent: [Shows full details and related feature context]

Suggested action: /review-code BUG-001

Proceed? [Yes / Different action / Cancel]
```

## Workflow

**This is an interactive process:**
- Help users capture items properly (refinement)
- Prevent duplicates
- Suggest appropriate resolution paths
- Connect items to existing features when relevant
