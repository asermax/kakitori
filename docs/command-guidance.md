# Command Workflow Guidance

Common principles for all collaborative command workflows in this framework.

## Core Principles

### 1. One Question at a Time

Never batch multiple questions. Wait for answer before proceeding.

**Why:** Prevents cognitive overload, maintains clear conversation flow, ensures each decision gets proper attention.

### 2. Propose, Don't Decide

Agent proposes options, user confirms. Never add or change anything without user agreement.

**Why:** User is the architect, Claude is the implementer. Maintain this relationship throughout.

### 3. Use AskUserQuestion for Structured Options

When presenting 2-4 distinct choices, use the AskUserQuestion tool:

- Provide clear header (max 12 chars, e.g., "Logging", "Format", "Approach")
- Write complete question text
- Add description explaining each option and its implications
- Use `multiSelect: true` if choices aren't mutually exclusive
- Examples: installation modes, logging approaches, technical choices, format options

**When to use plain text instead:**
- Open-ended questions (no predefined options)
- Single simple clarification needed
- Asking for creative input
- Yes/no questions

**Examples:**

```typescript
// ✓ Use AskUserQuestion
"Which logging approach fits your needs?"
- Option 1: File-based (description)
- Option 2: systemd journal (description)
- Option 3: Both modes (description)

// ✓ Use plain text
"What problem are you trying to solve?" (open-ended)
"Should we add X feature?" (simple yes/no)
```

### 4. Detect Gaps Proactively

Throughout the entire process:
- Surface unstated assumptions by asking about them
- Identify potential edge cases and ask user if they're relevant
- Challenge vague or incomplete answers
- Ask "what could go wrong?" and "what's missing?"
- Never fill gaps yourself - always ask the user

### 5. Use a Scratchpad

Track state in `/tmp/<command>-state.md`:
- For `-feature` commands, include the feature ID: `/tmp/<command>-<FEATURE-ID>-state.md`
  - Example: `/tmp/spec-CORE-001-state.md`, `/tmp/design-CORE-001-state.md`
- Current section/phase being worked on
- Questions asked and answered
- Gaps identified
- Topics to revisit
- Decisions made

**Why:** Prevents information loss across question rounds, maintains context during iteration.

### 6. Bridge the Context Gap

The agent reads multiple files (specs, designs, ADRs, DES patterns) and builds comprehensive context. The user reads documents when needed but doesn't have the full picture simultaneously.

**When asking questions or explaining decisions:**
- Include diagrams (ASCII art, sequence diagrams, thread/data flows)
- Provide rich context - don't assume shared understanding
- Explain the "why" behind technical questions
- Show concrete examples, not abstract references
- Name the specific files, components, or patterns being referenced

**Example - asking about thread safety:**

```
# ❌ Bad: Assumes user has full context
"Should we add locking for thread safety?"

# ✅ Good: Provides full context with diagram
"Two different threads access DictationManager:

┌──────────────────────┐     ┌──────────────────────┐
│ CORE-004 Monitor     │     │ CORE-002 Delivery    │
│ Thread               │     │ Thread               │
│                      │     │                      │
│ → calls toggle()     │     │ → calls _on_chunk()  │
│ → reads/writes state │     │ → writes to buffer   │
└──────────────────────┘     └──────────────────────┘

These can run concurrently. For example:
- User presses hotkey (monitor thread reads state)
- Audio chunk arrives at same moment (delivery thread writes buffer)

Should we add a lock to prevent this race condition?"
```

**Why:** The agent has read 5-10 files to reach a question. The user is seeing just the question. Bridge this gap with visual context.

### 7. Research When Needed

When user shows uncertainty, research to provide informed options.

**Research triggers:**
- User says "I'm not sure" or "I don't know"
- Topic involves technical choices (models, libraries, protocols, frameworks)
- User asks "what options do I have?"
- User mentions alternatives they've tried but weren't satisfied with

Use Task tool (general-purpose agent) to research, then synthesize findings to inform questions.

## Workflow Modes

Commands follow different workflows depending on their purpose:

### Information Gathering

**Use for:** Understanding requirements, clarifying scope, exploring options

**Workflow:**
- Ask one question at a time
- Wait for answer before proceeding
- Use AskUserQuestion for structured choices
- Build understanding incrementally

**Example commands:** Initial vision clarification, feature scope questions

### Document Creation

**Use for:** Specs, designs, plans, decisions

**Workflow:**
1. **Research phase (silent, thorough)**
   - Read spec/requirements
   - Read relevant ADRs and DES patterns
   - Explore related codebase areas if needed
   - **For libraries/frameworks/APIs:** Research official documentation and best practices before drafting
   - Build understanding without asking upfront questions
   - Proposals must be grounded in actual knowledge, not assumptions

2. **Draft proposal**
   - Create complete document following template
   - Base all choices on research findings
   - Note any uncertainties/assumptions clearly

3. **Present for review**
   - Show complete proposal to user
   - Highlight uncertainties and ask about them
   - Invite user feedback: "What needs adjustment?"

4. **Iterate**
   - Apply user corrections/additions
   - Re-present updated sections if significant changes
   - Repeat until user approves

5. **Finalize**
   - Apply any validation step (if command includes it)
   - Write document to file

**Key principle:** Always draft first, no upfront questions. Questions happen during review phase.

**Example commands:** `/design-feature`, `/spec-feature`, `/plan-feature`, `/decision`

## Validation Best Practices

### Use Opus for Validation

**Always use Opus model for validation subagents** to get higher quality feedback:

```python
Task(
    subagent_type="general-purpose",
    model="opus",  # Use Opus for validation quality
    prompt="Review this design for..."
)
```

**Why Opus for validation:**
- Provides more thorough critique and catches subtle issues
- Better at offering nuanced suggestions and comprehensive analysis
- Worth the cost: one-time review prevents multiple fix iterations

### Validation Context

Balance fresh perspective with respecting user decisions:

**Include in validation context:**
- ✅ The artifact being validated (spec, design, code, etc.)
- ✅ Relevant templates and examples
- ✅ User's explicit decisions and constraints
- ✅ Project-wide patterns (ADRs, DES documents)

**Exclude from validation context:**
- ❌ Agent's internal reasoning and discussion history
- ❌ Intermediate drafts and iterations
- ❌ Unrelated project context

**Why:** Subagent should validate implementation of decisions, not re-debate the decisions themselves.

## Status Update Guidelines

**Feature commands automatically update status** as they progress through the development workflow.

### Status Progression

- **✓ Defined** - Initial state (feature in FEATURES.md)
- **⧗ Spec** - `/spec-feature` starts
- **✓ Spec** - `/spec-feature` completes
- **⧗ Design** - `/design-feature` starts
- **✓ Design** - `/design-feature` completes
- **⧗ Plan** - `/plan-feature` starts
- **✓ Plan** - `/plan-feature` completes
- **⧗ Implementation** - `/implement-feature` starts
- **✓ Implementation** - `/implement-feature` completes

### When to Update Status

**At command start:**
- Set status to in-progress state (⧗) for the current phase
- Example: `/spec-feature CORE-001` → set status to "⧗ Spec"

**At command completion:**
- Set status to complete state (✓) for the current phase
- Example: `/spec-feature CORE-001` finishes → set status to "✓ Spec"

**How to update:**
```bash
# Find project root from current working directory
python scripts/features.py status set FEATURE-ID "STATUS"
```

**Note:** The `features.py` script automatically locates the project root by searching for `planning/DEPENDENCIES.md`, so it can be called from any subdirectory.

## Collaborative Process

**This is always a collaborative process:**
- Ask one question at a time
- Agent proposes, user confirms - never decide without agreement
- User makes all decisions
- Provide alternatives and trade-offs (research-backed when needed)
- Never fill gaps yourself - always ask the user
- Use AskUserQuestion for structured options (2-4 choices)
- Iterate until the user approves the final result
