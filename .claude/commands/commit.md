---
description: Analyze uncommitted changes and create grouped conventional commits
---

# Commit Workflow

Analyze uncommitted git changes and propose grouped commits using conventional commit format.

## Process

1. **Analyze changes**
   - Run `git status` to see all uncommitted files
   - Run `git diff` to understand the nature of changes
   - Run `git log --oneline -5` to see recent commit message style

2. **Group changes by related work**

   **Principle**: Group by cohesive work done together, even across different scopes.

   Examples of good groupings:
   - Command implementation + learnings about that command
   - Vision document + ADRs created during vision work
   - New command + CLAUDE.md reference update
   - Feature spec + design + plan (all created together)
   - Bug fix + tests for that fix

   Common groupings by category:
   - Framework changes (docs/framework.md, command definitions)
   - Feature-specific changes (docs/feature-specs/, docs/feature-designs/, docs/feature-plans/, implementation)
   - Documentation (README, CLAUDE.md, architecture docs)
   - Vision/planning (docs/planning/VISION.md, FEATURES.md, DEPENDENCIES.md)
   - New commands (.claude/commands/)
   - Build/tooling (package.json, tsconfig, etc.)

   **Note**: Prefer grouping work that was done together in the same session/context over strict scope boundaries.

3. **Determine commit type and scope**

   **Types:**
   - `feat`: New feature or capability
   - `fix`: Bug fix
   - `docs`: Documentation only
   - `refactor`: Code restructuring without behavior change
   - `chore`: Tooling, dependencies, build config
   - `test`: Adding or updating tests

   **Scopes (examples):**
   - `framework`: Changes to the development framework
   - `<feature-id>`: Changes specific to a feature (e.g., FT-001)
   - `design`: Design pattern documentation
   - `vision`: Project vision and planning
   - `commands`: Command definitions
   - `docs`: General documentation

   **When work crosses scopes:**
   - Use comma-separated scopes: `feat(commands,docs): enhance vision workflow and record learnings`
   - Order scopes by significance: most important first

4. **Propose commits**

   For each proposed commit, show:
   - **Message**: `type(scope): description`
   - **Files**: List of files to include
   - **Rationale**: Brief explanation of why these files are grouped together

   Example:
   ```
   Commit 1: feat(commands): add commit workflow command
   Files:
     - .claude/commands/commit.md
   Rationale: New command for analyzing and grouping git commits

   Commit 2: docs(framework): update command reference
   Files:
     - CLAUDE.md
   Rationale: Add /commit to available commands list
   ```

5. **Get user confirmation**
   - Ask: Do you want to proceed with these commits?
   - Ask: Do you want to adjust any groupings?
   - If adjustments requested, iterate on the proposal

6. **Execute commits**
   - For each approved commit:
     - Stage the specific files: `git add <files>`
     - Create commit with message: `git commit -m "type(scope): description"`
     - Show success confirmation

## Workflow

**This is a semi-automated process:**
- Analyze git state thoroughly
- Propose logical groupings based on related work
- Use conventional commit format consistently
- Always get user approval before executing
- Execute commits in sequence after confirmation

## Notes

- If changes are too large or complex, suggest breaking into smaller logical commits
- If a change doesn't fit any grouping, ask user for guidance
- Maintain consistency with project's commit history style
- Consider creating separate commits for different types of work even in same files
