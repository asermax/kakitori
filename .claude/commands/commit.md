---
description: Analyze uncommitted changes and create grouped conventional commits
---

# Commit Workflow

Analyze changes and create appropriate conventional commits.

## Process

### 1. Analyze Changes

Run in parallel:
```bash
git status
git diff --staged
git diff
git log -5 --oneline
```

### 2. Understand the Changes

Analyze what's changed:
- New files added
- Files modified
- Files deleted
- Which features are affected

### 3. Group Changes Logically

Group changes that should be committed together:
- Related to same feature
- Part of same logical change
- Following conventional commit types

**Commit types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change without feature/fix
- `test`: Adding/updating tests
- `chore`: Build, tooling, maintenance

### 4. Draft Commit Messages

For each group, draft commit message:

```
type(scope): brief description

Longer explanation if needed.
- Detail 1
- Detail 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### 5. Present Plan and Get Confirmation

**CRITICAL**: ALWAYS use `AskUserQuestion` to present proposed groups and get user confirmation, even if:
- There is only one commit group
- The grouping seems obvious or trivial
- All changes are clearly related

Include the full group breakdown with file lists in the question text.

- **IMPORTANT**: Do NOT use markdown formatting (code blocks, bold, italics, etc.) in the actual question text passed to AskUserQuestion - it doesn't support markdown rendering
- Use plain text with clear visual structure (indentation, line breaks, simple characters like dashes and numbers)

Present options:
- **Option 1**: "Proceed with these N commit group(s)" - Accept the proposed distribution
- **Option 2** (conditional): If there are 4+ groups, offer "Merge into fewer commits"
- **Note**: Do NOT include "Other" as an option - the system adds it automatically

Example format:
```
Question: "I've analyzed the changes and propose the following commit groups:

feat(CORE-002): add audio capture functionality
   - src/audio/capture.py (new)
   - src/audio/__init__.py (modified)
   - tests/test_audio.py (new)

docs: update CLAUDE.md with current focus
   - CLAUDE.md (modified)

How would you like to proceed?"

Options:
- "Proceed with these 2 commit groups"
- [Only if 4+ groups] "Merge into fewer commits"
```

### 6. Execute Commits

For each approved commit:
```bash
git add [files]
git commit -m "type(scope): description"
```

For commits with body text:
```bash
git add [files]
git commit -m "$(cat <<'EOF'
type(scope): description

Optional body with additional details.
EOF
)"
```

## Guidelines

**Commit message quality:**
- Use imperative mood in the description (present tense, not past or continuous)
  - **WRONG**: "adding new feature" (present continuous)
  - **WRONG**: "added new feature" (past tense)
  - **RIGHT**: "add new feature" (imperative)
- No period at end of subject line
- Subject line under 50-72 characters
- Body wrapped at 72 chars when needed
- **CRITICAL**: Do NOT use the exclamation mark after the type/scope to indicate breaking changes. Use the `BREAKING CHANGE:` footer instead

**Grouping rules:**
- **IMPORTANT**: Do NOT mix unrelated changes in a single commit
- Each commit should represent a single logical change
- Don't mix features in one commit
- Separate formatting from logic changes
- Separate tests from implementation (unless closely related)
- Keep commits atomic but meaningful

**Examples:**

**WRONG** - Mixing unrelated changes:
```bash
git add app/services/auth.py app/services/exception_handler.py
git commit -m "fix: update auth and exception handler"
```

**RIGHT** - Separate commits for unrelated changes:
```bash
# First commit
git add app/services/auth.py
git commit -m "fix(auth): resolve token expiration issue"

# Second commit
git add app/services/exception_handler.py
git commit -m "refactor(errors): simplify exception handler logic"
```

**Safety:**
- Never force push
- Never modify git config
- Never skip hooks unless explicitly requested
- Warn before committing to main/master

## Workflow

**This is a collaborative process:**
1. Analyze changes (git status, git diff)
2. Understand what's changed
3. Group logically (related changes together)
4. Draft commit messages (conventional commits format)
5. Present plan and get user confirmation (AskUserQuestion)
6. Execute commits (git add + git commit)
