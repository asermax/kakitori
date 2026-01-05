---
description: Add a new feature on-the-go without full upfront planning
argument-hint: "[description]"
---

# Add Feature Workflow

Add a new feature to the project without requiring full upfront planning.

## Input

Feature description: $ARGUMENTS (optional - will prompt if not provided)

Can also be a **backlog item ID** (typically IDEA-XXX) to promote to a feature.

## Backlog Integration

If a backlog item ID is provided (e.g., `/add-feature IDEA-001`):

1. **Load item context**
   - Run `python scripts/backlog.py show <ID>` to get item details
   - Use title and notes as initial feature description
   - If item has related features, consider as potential dependencies

2. **After feature added**
   - Prompt: "Mark <ID> as promoted?"
   - If yes: Run `python scripts/backlog.py promote <ID> --feature <FEATURE-ID>`

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows (one question at a time, propose don't decide, use AskUserQuestion for structured options, detect gaps proactively, scratchpad usage, research triggers)

**Feature inventory:**
@planning/FEATURES.md - Existing feature definitions and complexity ratings

**Dependency matrix:**
@planning/DEPENDENCIES.md - Feature dependencies and implementation phases

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Add-feature specific guidance:**

**Use a scratchpad** - Track state in `/tmp/add-feature-<animal-adjective>-state.md` (generate unique ID):
- Feature description being captured
- Category proposed
- ID assigned
- Dependencies identified
- Complexity rating proposed

**Detect gaps proactively** - Challenge completeness throughout:
- "What existing features might this depend on?"
- "Is this truly a new feature or an enhancement to an existing one?"
- "Are there implicit dependencies we haven't considered?"
- Never add requirements yourself - always propose and get user agreement

## Pre-Check

Verify framework is initialized:
- If `planning/` doesn't exist, explain that the framework needs to be set up first
- If FEATURES.md or DEPENDENCIES.md missing, explain what's needed

## Process

### 1. Capture Feature Description

If not provided in arguments, ask:
```
"Describe the feature you want to add:
- What does it do?
- Who uses it?
- Why is it needed?"
```

### 2. Research Existing Features

Read FEATURES.md to understand:
- Existing categories and their purposes
- Feature naming conventions
- Complexity patterns for similar features

### 3. Propose Feature Details

Based on the description and existing patterns, draft a complete proposal:

```
"Based on your description, I propose:

**Category**: [CATEGORY] - [reason based on existing patterns]
**ID**: CATEGORY-NNN (next available)
**Name**: [concise feature name]
**Complexity**: [Easy/Medium/Hard] - [reason based on scope]
**Dependencies**: [proposed deps or 'None'] - [reason based on analysis]

Does this look right? What needs adjustment?"
```

### 4. Iterate Based on Feedback

- Apply user corrections to category, complexity, or dependencies
- Re-present if significant changes
- Repeat until user approves

### 5. Update FEATURES.md

Add new feature entry following the existing format:

```markdown
### CATEGORY-NNN: Feature name
**Status**: ✗ Defined
**Complexity**: [complexity]
**Description**: [description]
```

### 6. Update DEPENDENCIES.md

Add to dependency matrix:

```bash
python scripts/features.py deps add-feature CATEGORY-NNN
```

If dependencies identified:
```bash
python scripts/features.py deps add-dep CATEGORY-NNN DEP-ID
```

### 7. Recalculate Phases

Update phase assignments based on new dependencies:

```bash
python scripts/features.py deps recalculate-phases
```

Show user the phase assignment:
```
"CATEGORY-NNN has been assigned to Phase N.

Reason: [Depends on X which is in Phase M, so this goes in Phase M+1]
         OR [No dependencies, added to Phase 1]"
```

### 8. Summary and Next Steps

Present summary:
```
"Feature added:

ID: CATEGORY-NNN
Description: [description]
Complexity: [complexity]
Dependencies: [list or 'None']
Phase: N

Next steps:
- Create spec: /spec-feature CATEGORY-NNN
- Or continue adding more features

Create spec now? [Y/N]"
```

If user says yes, transition to `/spec-feature CATEGORY-NNN`.

## Error Handling

**Framework not initialized:**
- Explain the framework needs to be set up first
- Don't attempt to create files manually

**Invalid dependency:**
- Feature ID doesn't exist
- Show available features
- Ask user to correct

**Category conflict:**
- ID already exists
- Show what exists
- Assign next available number

## Workflow

**This is a collaborative process:**
- Capture description
- Research existing patterns
- Propose complete feature details (category, complexity, dependencies)
- Iterate based on user feedback
- Update framework files
- Offer next steps
