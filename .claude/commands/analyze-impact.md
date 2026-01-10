---
description: Analyze the impact of a proposed change on features and dependencies
argument-hint: "[change description]"
---

# Analyze Impact Workflow

Analyze the impact of a proposed change on existing features, dependencies, and documentation.

## Input

Change description: $ARGUMENTS (optional - will prompt if not provided)

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows

**Feature inventory:**
@docs/planning/FEATURES.md - Feature definitions and status

**Dependency matrix:**
@docs/planning/DEPENDENCIES.md - Feature dependencies and implementation phases

**Project decisions:**
@docs/architecture/README.md - Architecture decisions (ADRs)
@docs/design/README.md - Design patterns (DES)

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Impact analysis specific guidance:**

**Use a scratchpad** - Track state in `/tmp/analyze-impact-<animal-adjective>-state.md` (generate unique ID):
- Change description being analyzed
- Affected features identified
- Documents requiring updates
- Risk level assessment

**Research thoroughly** - Before presenting findings:
- Use dependency tools to trace feature graph
- Read affected specs and designs
- Understand the scope of change

## Pre-Check

Verify framework is initialized:
- If `docs/planning/` doesn't exist, explain this command requires initialized framework
- If minimal features exist, note the analysis may be limited

## Process

### 1. Capture Change Description

If not provided in arguments, ask:
```
"Describe the change you're considering:
- What are you planning to change?
- Why is this change needed?
- What areas do you think might be affected?"
```

### 2. Analyze Dependencies

Use the features.py script to understand the dependency graph:

```bash
python scripts/features.py deps tree AFFECTED-FEATURE
python scripts/features.py deps reverse AFFECTED-FEATURE
```

Read the relevant specs and designs to understand what would be impacted.

### 3. Present Findings

Draft a complete impact analysis:

```
## Impact Analysis

### Change Summary
[What's being changed]

### Risk Level: [Isolated | Moderate | Significant | Structural]

[Reason for risk assessment]

### Directly Affected Features
| Feature | Impact | Reason |
|---------|--------|--------|
| CORE-001 | High | [reason] |
| API-002 | Medium | [reason] |

### Transitively Affected Features
| Feature | Path | Impact |
|---------|------|--------|
| UI-003 | CORE-001 → UI-003 | Medium |

### Documents Requiring Updates
- docs/feature-specs/CORE-001.md - Update acceptance criteria for X
- docs/feature-designs/API-002.md - Revise data flow for Y
- docs/architecture/ADR-005.md - Consider superseding

### Recommendations
1. [Action item]
2. [Action item]

Does this analysis look complete? What did I miss?
```

### 4. Discuss Next Steps

Based on risk level, propose appropriate next steps:

**Isolated (1-2 features, no transitive):**
```
"This is a contained change. You can proceed with implementation.

Proposed approach:
- Update affected specs first
- Then implement changes

Would you like to start with the spec updates, or proceed differently?"
```

**Moderate (3-5 features or limited transitive):**
```
"This change has moderate impact. I recommend reviewing affected specs before proceeding.

Proposed approach:
1. Review affected specs
2. Consider documenting the decision
3. Implement changes

Which would you like to do first?"
```

**Significant (5+ features or broad transitive):**
```
"This is a significant change with broad impact.

I recommend:
1. Creating an ADR to document the decision and rationale
2. Reviewing all affected specs and designs
3. Considering a phased implementation approach

Would you like to start with the ADR, or take a different approach?"
```

**Structural (architecture or cross-cutting):**
```
"This change affects core architecture and has structural implications.

Before proceeding, I recommend:
1. Creating an ADR with thorough alternatives analysis
2. Reviewing all affected areas in detail
3. Considering if this should be a new phase

This is a significant decision. Would you like to start with an architecture discussion?"
```

### 5. Execute Chosen Action

**Review affected specs:**
- Read and summarize each affected spec
- Highlight which acceptance criteria are impacted
- Propose updates

**Create ADR:**
- Transition to `/decision`
- Pre-fill context with impact analysis

**Plan phased approach:**
- Propose breaking change into phases
- Show which features could be in each phase
- Offer to create implementation plan

## Integration with Other Commands

This command integrates with:
- `/decision` - For documenting significant changes
- `/spec-feature` - For updating affected specs
- `/add-feature` - When change requires new features

## Workflow

**This is an informational command:**
- Gather change description
- Analyze dependencies and trace impact
- Present complete findings with risk assessment
- Propose appropriate next steps based on risk
- Execute user's chosen action
