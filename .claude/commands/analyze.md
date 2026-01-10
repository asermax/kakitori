---
description: Review project state, find gaps, assess change impact
---

# Analysis Workflow

Review project state, find gaps, assess change impact.

## Context

**Framework reference:**
@docs/framework.md
@docs/planning/VISION.md
@docs/planning/FEATURES.md
@docs/planning/DEPENDENCIES.md
@docs/architecture/README.md
@docs/design/README.md

Read all specs and plans in docs/feature-specs/ and docs/feature-plans/ directories.

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Analyze-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/analyze-<animal-adjective>-state.md` (generate unique ID):
- Analysis type (gap analysis or change impact)
- Areas being examined
- Gaps/issues identified
- Impact findings
- Recommendations proposed

## Process

1. **Determine analysis type**
   - Ask: Are you looking for gaps or assessing a change?
   - Ask: Should I check all documents or focus on a specific area?

2. **For gap analysis - Check completeness**
   - Vision defined?
   - All features extracted from vision?
   - Dependency matrix complete?
   - All features have specs?
   - All specs have plans?

3. **For gap analysis - Find inconsistencies**
   - Features mentioned in vision but not in FEATURES.md
   - Dependencies not reflected in matrix
   - Acceptance criteria without clear verification
   - Undocumented decisions (referenced but no ADR/DES)
   - Spec references not matching plan references
   - Dependency chain issues (cycles, missing features)

4. **For change impact assessment**
   - Ask: What specifically do you want to change?
   - Trace dependencies
   - Identify affected features
   - Report ripple effects

5. **Report findings**
   - List all gaps/issues found
   - Suggest next actions
   - Prioritize by importance
   - Ask: Which should we address first?

## Workflow

**This is a thorough review:**
- Check every document systematically
- Cross-reference all IDs and links
- Identify missing pieces
- Assess change impact carefully
- Provide actionable recommendations
