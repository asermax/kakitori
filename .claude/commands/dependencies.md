---
description: Build the dependency matrix for features
---

# Dependency Matrix Workflow

Build the dependency matrix in docs/planning/DEPENDENCIES.md.

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Command guidance principles:**
@docs/command-guidance.md - Core principles for collaborative command workflows (one question at a time, propose don't decide, use AskUserQuestion for structured options, detect gaps proactively, scratchpad usage, research triggers)

**Features document:**
@docs/planning/FEATURES.md - Feature inventory to analyze for dependencies

**Dependencies document:**
@docs/planning/DEPENDENCIES.md - Current dependency matrix (if exists)

## General Guidance

Follow the collaborative workflow principles in @docs/command-guidance.md.

**Dependencies-specific guidance:**

**Use a scratchpad** - Track state in `/tmp/dependencies-state.md`:
- Current analysis phase
- Proposed dependencies with reasoning
- Validation findings (both matrix and phase validations)
- Phase derivation intermediate state
- User feedback and refinements

**Propose complete matrix first** - Analyze all features and propose the complete dependency matrix in one pass. Do NOT ask about each feature pair individually.

**Detect gaps proactively** - Challenge completeness with specific questions:
- "Does X need data from Y to function?"
- "What must work before X can be tested?"
- "Does X share configuration or state with Y?"
- "Could X fail if Y isn't available?"
- Never add dependencies yourself - always propose and get user agreement

**Think in categories** - Present dependencies organized by category (within-category first, then cross-category). This makes review more manageable.

## Process

0. **Check existing state**
   - If `docs/planning/DEPENDENCIES.md` exists:
     - Read current dependency matrix
     - Read current features (check for new features)
     - Compare: Are there new features? Changed feature definitions?
     - Ask: "Should we update for new features, refine existing dependencies, or rebuild from scratch?"
     - Enter iteration mode as appropriate
   - If no dependencies exist: proceed with initial analysis

1. **Analyze features and propose complete matrix**
   - Review all features from FEATURES.md
   - For each feature, analyze:
     - What data/capabilities does it consume?
     - What other features must exist for this to work?
     - What does it share with other features (config, state, resources)?
     - What must be initialized before this can start?
     - What must work for this to be testable?
   - **Apply dependency priority principles:**
     - Core capabilities before workflows (e.g., audio, transcription before dictation)
     - Core workflows before enhancements (e.g., basic dictation before context awareness)
     - Features before configuration (e.g., auto-stop with hardcoded timeout before configurable timeout)
     - Functionality before polish (e.g., error detection before error UI refinements)
     - Core features before deployment modes
     - **Configuration features make things customizable, they're not prerequisites**
   - Build complete proposed dependency matrix
   - Track reasoning for each dependency in scratchpad
   - Track analysis in `/tmp/dependencies-state.md`

2. **Present dependencies by category**
   - Group features by their category (CORE, UI, SETUP, etc.)
   - For each category:
     - Show **intra-category dependencies** first (within the category)
     - Then show **cross-category dependencies** (to other categories)
     - Explain the reasoning for each proposed dependency
   - This category-based approach makes review manageable

3. **User iteration on dependencies**
   - User reviews proposed dependencies category by category
   - Discuss and adjust based on user knowledge
   - Surface hidden dependencies with gap detection questions (see below)
   - Refine matrix based on discussion
   - Update scratchpad with refinements

4. **Validate for cycles**
   - Check for circular dependencies in the refined matrix
   - If found, work with user to resolve:
     - Re-examine dependency (is it really needed?)
     - Revise feature scope
     - Split features
   - Continue until no cycles remain

5. **Agent validation #1: Dependency matrix**
   - Dispatch a general-purpose subagent using the Task tool to review the dependency matrix
   - Provide context: feature inventory, proposed dependency matrix, **user's explicit decisions made during analysis**
   - **User's explicit decisions** include:
     - Specific dependency clarifications user made (e.g., "UI-003 is a mechanism, not dependent on ERROR features")
     - Features confirmed as independent (e.g., "DICT-001 and DICT-002 can be implemented independently")
     - Out-of-scope decisions (e.g., "system requirements validation will not happen")
     - Constraints user stated (e.g., "CORE-005 should be in Phase 1")
   - **Do NOT include**: Agent reasoning, rejected proposals, full conversation history
   - **Include dependency priority principles** in the subagent prompt:
     - Core capabilities → Core workflows → Enhancements → Configuration → Polish → Deployment
     - Features work with hardcoded defaults; configuration makes them customizable later
     - Configuration features are enhancements, not prerequisites
   - Request structured critique covering:
     - **Missing implicit dependencies**: Are there unstated dependencies that should be explicit? What features have hidden requirements on other features?
     - **Hidden coupling**: Do any features share configuration, state, or resources that implies a dependency?
     - **Dependency rationale**: Are the stated reasons for dependencies sound? Are there alternative interpretations?
     - **Over-specification**: Are any dependencies unnecessary or too strict? Could any be removed without affecting correctness?
     - **Initialization order**: Are there initialization-order dependencies that aren't explicit?
     - **Priority violations**: Are any dependencies backwards (e.g., configuration before core feature)?
   - Review subagent findings with user
   - Discuss which recommendations to accept
   - Iterate on matrix if needed

6. **Derive implementation phases**
   - Use topological sort to derive phases from dependencies:
     - Phase 1: Features with no dependencies
     - Phase 2: Features depending only on Phase 1
     - Continue until all features are phased
   - Present proposed phases to user

7. **Agent validation #2: Phase ordering**
   - Dispatch a general-purpose subagent using the Task tool to review the phase ordering
   - Provide context: feature inventory, dependency matrix, proposed phases, **user's explicit decisions made during analysis**
   - **User's explicit decisions** include:
     - Phase placement preferences (e.g., "CORE-005 should be in Phase 1", "DICT-002 is okay in Phase 2")
     - Constraints (e.g., "DEPLOY and DOCS should be last")
     - Out-of-scope items (e.g., "threading is an architectural decision, not a feature")
   - **Do NOT include**: Agent reasoning, rejected proposals, full conversation history
   - **Include dependency priority principles** in the subagent prompt:
     - Expected phase structure: Core capabilities → Core workflows → Enhancements → Configuration → Polish → Deployment
     - Features should work with hardcoded defaults before configuration
   - Request structured critique covering:
     - **Implementation feasibility**: Do the proposed phases create any implementation problems? Can features in each phase realistically be built?
     - **Testing order**: Can features in phase N be tested with only phases 1..N-1 available? Are there testing dependencies that aren't captured?
     - **Developer experience**: Does phase ordering make sense for iterative development? Would a different ordering be more practical?
     - **Parallel opportunities**: Can any features within a phase be built in parallel? Are there dependencies within a phase that should move features to later phases?
     - **Phase balance**: Are phases reasonably sized? Are there phases with too many or too few features?
     - **Priority alignment**: Do phases follow the expected priority structure?
   - Review subagent findings with user
   - Discuss which recommendations to accept

8. **Phase iteration and finalization**
   - Ask user: "Should we adjust these phases based on the validation, or are they ready?"
   - If adjustments needed:
     - Discuss phase ordering concerns
     - Consider parallel implementation opportunities
     - Move features between phases if needed
     - Adjust as needed
   - If complete:
     - Finalize matrix and phases
     - Write document to `docs/planning/DEPENDENCIES.md`

## Gap Detection Questions

Use these questions to surface hidden dependencies during user iteration (step 3):

**Data flow:**
- "Does [X] need data that [Y] produces?"
- "Does [X] transform or process output from [Y]?"

**Initialization order:**
- "What must be initialized before [X] can start?"
- "Does [X] assume [Y] is already running?"

**Shared resources:**
- "Do [X] and [Y] access the same configuration?"
- "Do [X] and [Y] share state or resources?"

**Testing:**
- "What must work for [X] to be testable?"
- "Can [X] be tested in isolation, or does it need [Y]?"

**Error handling:**
- "If [Y] fails, does [X] need to know?"
- "Does [X] have error handling that depends on [Y]?"

## Workflow

**This is a collaborative process:**
- Propose complete matrix first, then iterate - do NOT ask about each pair
- Present dependencies by category for manageable review
- Agent proposes, user confirms - never decide without agreement
- Challenge gaps and hidden coupling throughout
- Work together to resolve cycles
- Dual validation: matrix validation catches dependency issues, phase validation catches ordering issues
- User confirms phases before finalizing
- Iterate until complete
