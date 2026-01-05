# Distilled AI-Assisted Development Framework

**Source**: "The Cure for the Vibe Coding Hangover" by Corey J. Gallon

## Problem Being Solved

"Vibe coding" produces brittle, unmaintainable code because:
- No architectural thinking upfront
- No clear completion criteria
- Context gets lost between sessions
- Features are too big/intertwined
- No validation strategy

## Core Philosophy

1. **You are the architect, AI is the implementer** - Don't delegate thinking, only doing
2. **Specification > Prompt Engineering** - Write blueprints, not magic prompts
3. **Define done before implementing** - Acceptance criteria upfront
4. **Feature atomicity** - Keep work units small and irreducible
5. **Make it work first** - Ship working software, then optimize

## The Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. VISION.md                                               │
│     └─ Problem, workflows, scope, tech context              │
├─────────────────────────────────────────────────────────────┤
│  2. FEATURES.md                                             │
│     └─ Extract atomic features with IDs                     │
├─────────────────────────────────────────────────────────────┤
│  3. DEPENDENCIES.md                                         │
│     └─ Build matrix, derive implementation phases           │
├─────────────────────────────────────────────────────────────┤
│  4. For each feature (in phase order):                      │
│     ├─ Write spec (specs/FEATURE-ID.md) - WHAT             │
│     ├─ Write design (designs/FEATURE-ID.md) - WHY/HOW      │
│     ├─ Write plan (plans/FEATURE-ID.md) - STEPS            │
│     ├─ Implement with Claude                                │
│     ├─ Test against acceptance criteria                     │
│     ├─ Review and correct                                   │
│     ├─ Update design if better approach found               │
│     └─ Commit atomically                                    │
└─────────────────────────────────────────────────────────────┘
```

## Key Habits

1. **Never start coding without a spec** - Even a quick one
2. **Keep features small** - If it takes more than one session, it's too big
3. **Define done first** - Write acceptance criteria before implementing
4. **Commit atomically** - One feature per commit
5. **Read the code** - Don't just accept it, understand it

## Project Structure

```
project/
├── CLAUDE.md                     # AI context loader
├── docs/
│   ├── framework.md              # This file
│   ├── learnings.md              # Process insights
│   ├── architecture/             # Hard decisions (ADRs)
│   │   ├── README.md             # Index
│   │   └── ADR-*.md              # Individual decisions
│   └── design/                   # Patterns (DES)
│       ├── README.md             # Index
│       └── DES-*.md              # Cross-cutting patterns
├── planning/
│   ├── VISION.md
│   ├── FEATURES.md
│   ├── DEPENDENCIES.md
│   └── BACKLOG.md
├── specs/
│   └── FEATURE-ID.md             # What to build
├── designs/
│   └── FEATURE-ID.md             # Why/how (design rationale)
├── plans/
│   └── FEATURE-ID.md             # Implementation steps
└── src/
```

## Document Types

| Document | Purpose | Scope |
|----------|---------|-------|
| **Feature Spec** (`specs/`) | WHAT to build | Per feature |
| **Feature Design** (`designs/`) | WHY/HOW - design rationale, modeling, data flow | Per feature |
| **Implementation Plan** (`plans/`) | STEPS to implement | Per feature |
| **Architecture Decision** (`docs/architecture/`) | Hard-to-change decisions (platform, language) | Project-wide |
| **Design Pattern** (`docs/design/`) | Cross-cutting patterns & conventions | Project-wide |
| **Dependencies** (`planning/DEPENDENCIES.md`) | WHEN to build (phases) | Project-wide |
| **Backlog** (`planning/BACKLOG.md`) | Bugs, ideas, improvements, tech-debt, questions | Project-wide |

### Feature-Specific vs Project-Wide

**Per Feature** (specs/, designs/, plans/):
- Specific to one feature's requirements
- Can be promoted to pattern if proves reusable
- Document the unique choices for this feature

**Project-Wide** (docs/architecture/, docs/design/):
- Apply across multiple features
- Establish consistency and standards
- Evolved from successful feature-specific approaches

### Backlog vs Features

**Features** (`planning/FEATURES.md`):
- Well-defined units of functionality
- Have specs, designs, plans
- Follow the full implementation workflow

**Backlog** (`planning/BACKLOG.md`):
- Items not ready for full feature treatment
- Bugs, ideas, improvements, tech-debt, questions
- May be promoted to features or resolved directly
- Use `/backlog` command or `scripts/backlog.py` to manage

| Type | Prefix | Typical Resolution |
|------|--------|-------------------|
| Bug | `BUG-` | `/review-code BUG-ID` |
| Idea | `IDEA-` | `/add-feature IDEA-ID` |
| Improvement | `IMP-` | `/review-code IMP-ID` |
| Tech Debt | `DEBT-` | `/review-code DEBT-ID` |
| Question | `Q-` | `/decision Q-ID` |

## Progressive Disclosure

- **Quick reference**: Read `README.md` index files
- **Deep dive**: Follow links to individual decision files

This keeps context manageable while preserving detail.

## Context Loading

`CLAUDE.md` at the project root ensures Claude always has the right context:
- Points to key files to read
- Lists current focus area
- Provides quick reference for patterns

## Implementation Steps

1. Write `VISION.md` first
2. Extract features into `FEATURES.md`
3. Build dependency matrix in `DEPENDENCIES.md`
4. For each feature (in dependency order):
   - Write spec (WHAT to build)
   - Write design (WHY/HOW - design rationale)
   - Write implementation plan (STEPS)
   - Implement
   - Test
   - Review and correct
   - Update design if better approach found
   - Commit

## Templates

All templates are located in `docs/templates/`:

**Planning Phase**:
- `docs/templates/VISION.md` - Project vision document
- `docs/templates/FEATURES.md` - Feature inventory
- `docs/templates/DEPENDENCIES.md` - Dependency matrix

**Per Feature**:
- `docs/templates/feature-spec.md` - Feature specification (copy to `specs/FEATURE-ID.md`)
- `designs/TEMPLATE.md` - Feature design rationale (copy to `designs/FEATURE-ID.md`)
- `docs/templates/implementation-plan.md` - Implementation plan (copy to `plans/FEATURE-ID.md`)

**Project-Wide Decisions**:
- `docs/templates/ADR.md` - Architecture Decision Record (copy to `docs/architecture/ADR-NNN-topic.md`)
- `docs/templates/DES.md` - Design Pattern (copy to `docs/design/DES-NNN-topic.md`)
