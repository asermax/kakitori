---
description: Extract and record learnings from current session
---

# Record Learnings Workflow

Extract learnings from the conversation and update framework/learnings files.

## Context

**Framework reference:**
@docs/framework.md - The development framework structure and workflow

**Previous learnings:**
`docs/learnings.md` contains all previous learnings organized by date. Use Grep to search for related concepts already documented, but don't load the entire file to avoid token overhead.

## Process

1. **Analyze conversation**
   - Review the current session's conversation
   - Identify key learnings:
     - What worked well?
     - What didn't work or needed adjustment?
     - What insights emerged about the process?
     - What patterns or best practices were discovered?
     - What questions remain open?

2. **Search existing documentation**
   - Read `docs/framework.md` thoroughly
   - Use Grep to search `docs/learnings.md` for related concepts already documented
   - Read specific sections of `docs/learnings.md` only if Grep finds relevant matches
   - Identify what's already captured vs what's new

3. **Check for duplicates**
   - For each learning identified:
     - Is this already documented in framework.md?
     - Is this already documented in learnings.md?
     - If similar, how does this add to what exists?
   - Only extract truly new insights or refinements

4. **Categorize learnings**
   - **Framework updates**: Structural changes, new document types, workflow adjustments
   - **Process learnings**: What worked/didn't work, insights, patterns
   - **Command improvements**: Feedback on commands (flow, questions, UX)
   - **Framework enhancements**: Ideas for new commands or capabilities
   - **Open questions**: Things to explore or decide later

5. **Present findings**
   - Show user what learnings were extracted
   - Show where duplicates were found
   - Ask: Should we record these? Any corrections?

6. **Update documentation**

   a. **Update docs/learnings.md**:
      - Add new date section if needed
      - Add "What Worked" items
      - Add "What Didn't Work" with Why and Adjustment
      - Add "Key Insights"
      - Add "Patterns That Emerged"
      - Add "Command Improvements" (if applicable)
      - Add "Framework Enhancements" (if applicable)
      - Add "Questions to Explore"

   b. **Update docs/framework.md** (only if structural changes):
      - Update workflow diagram if process changed
      - Update document types if new types added
      - Update project structure if folders changed
      - Add to key habits if new practices emerged

   c. **Update commands** (if command improvements identified):
      - Apply feedback to command files in `.claude/commands/`
      - Update command flow, questions, or guidance
      - Test that changes align with framework philosophy

## Guidelines

**What to Record**:
- Process insights (what worked, what didn't)
- Framework adjustments (structure, workflow changes)
- Pattern discoveries (emergent best practices)
- Decision rationale (why we chose certain approaches)
- Mistakes to avoid (what to watch out for)
- Command improvements (UX, flow, questions)
- Framework enhancements (new capabilities, new commands)
- Open questions (things to explore)

**What NOT to Record**:
- Implementation details (those go in code or feature docs)
- Feature-specific decisions (those go in docs/feature-designs/)
- Temporary notes or TODO items
- Duplicate information already captured

**Duplication Check**:
- Use Grep to search for keywords from learning
- Read relevant sections of existing docs
- Only add if genuinely new or refines existing
- Reference existing docs when expanding on them

## Workflow

**This is a reflective process:**
- Review conversation thoughtfully
- Search thoroughly before adding
- Avoid duplicate information
- Focus on process and framework learnings
- Keep framework.md stable (only update for structural changes)
- Use learnings.md for ongoing insights
- User validates learnings before recording
