---
description: Extract atomic features from the project vision
---

# Feature Extraction Workflow

Extract atomic features from VISION.md into FEATURES.md.

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows (one question at a time, propose don't decide, use AskUserQuestion for structured options, detect gaps proactively, scratchpad usage, research triggers)

**Vision document:**
@docs/planning/VISION.md - Project vision to extract features from

**Features document:**
@docs/planning/FEATURES.md - Current feature inventory (if exists)

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Features-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/features-state.md`:
- Raw features identified (unorganized) with source traceability
- Agent validation findings
- Refinements to apply
- Category decisions

**Extract all at once** - Review entire vision and extract all features in one pass, maintaining source traceability.

**Detect gaps proactively** - Challenge completeness throughout:
- "What handles errors here?" "What validates this input?"
- "Do we need something that provides feedback to the user?"
- "Should we consider security/logging/configuration/testing?"
- Never add features yourself - always propose and get user agreement

## Process

0. **Check existing state**
   - If `docs/planning/FEATURES.md` exists:
     - Read current feature inventory
     - Read current vision (check for changes)
     - Compare: Are there new workflows? Changed scope? New technical context?
     - Ask: "Should we review for new features, or refine existing ones?"
     - Enter iteration mode as appropriate
   - If no features exist: proceed with initial extraction

1. **Extract all features at once**
   - Review the vision document thoroughly
   - Extract all features in a single pass, building a raw unorganized list
   - For each feature, document source traceability (which vision section it comes from)
   - Consider all aspects:
     - Core workflows and their discrete capabilities
     - Foundational capabilities the system needs
     - Infrastructure features supporting requirements
     - Platform integration and external system interactions
     - Cross-cutting concerns (security, logging, configuration, error handling)
     - User feedback and notification mechanisms
   - Build complete raw list with source references

2. **Agent validation #1: Raw feature list**
   - Dispatch a general-purpose subagent using the Task tool to review the raw feature list
   - Provide minimal context: vision document, architecture decisions, raw feature list
   - Request structured critique focused on:
     - **Completeness**: Are all workflows covered? Are all scope items addressed? What's missing from the vision?
     - **Redundancies**: Duplicate or overlapping features? Features describing the same capability?
     - **Atomicity**: Are features truly atomic (single-session, one thing each)? Should any be split or merged?
     - **Gaps**: What workflows lack supporting features? What cross-cutting concerns are missing?
   - Review subagent findings with user
   - Discuss which recommendations to accept

3. **User iteration on raw features**
   - Based on agent validation, refine the raw feature list
   - Split features that are too large
   - Merge or remove redundant features
   - Add missing features identified in validation
   - Ensure each feature is atomic and traceable to vision

4. **Analyze and categorize**
   - Review refined raw feature list
   - Propose 3-7 natural groupings based on the features - get user agreement
   - **For each category (not individual features):**
     - Present all features in that category together
     - Show: proposed ID, description, complexity for each
     - User reviews the full category
     - Validate/adjust each feature individually within the category
     - Move to next category
   - This category-based approach balances speed with thoroughness

5. **Agent validation #2: Categorized features (comprehensive)**
   - Dispatch a general-purpose subagent using the Task tool to review the completed feature inventory
   - Provide minimal context: vision document, architecture decisions, categorized feature inventory
   - Request structured critique covering:
     - **Completeness**: Are all workflows and v1 requirements covered? Does every workflow have supporting features? Are all scope items covered? Are cross-cutting concerns addressed?
     - **Atomicity**: Are features truly atomic (single-session, one thing each)? Should any be split or merged?
     - **Category alignment**: Do features belong in the right categories? Are groupings logical?
     - **Complexity assessment**: Are ratings reasonable given implementation reality?
     - **Gaps**: What's missing? What workflows lack features?
     - **Redundancies**: Any duplicates or overlapping features remaining?
     - **Dependencies**: Any implicit dependency concerns?
   - Review subagent findings with user
   - Discuss which recommendations to accept

6. **User iteration and finalization**
   - Ask user: "Should we iterate based on this feedback, or is the inventory complete?"
   - If gaps/issues to address → refine features (split, merge, add, adjust complexity, recategorize)
   - If complete → finalize and write document to `docs/planning/FEATURES.md`

## Atomicity Check

Apply to each feature during extraction AND during final review:
- Can this be implemented in a single focused session?
- Does it do ONE thing?
- If no → split into smaller features and re-extract

## Workflow

**This is a collaborative process:**
- Ask one question at a time
- Agent proposes, user confirms - never decide without agreement
- Extract features systematically, section by section
- Challenge gaps and completeness throughout
- User confirms categories, complexity, and IDs for each feature
- Challenge non-atomic features
- Never add features without user agreement
- Iterate until complete
