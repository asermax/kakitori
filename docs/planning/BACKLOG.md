# Backlog

Items not ready for full feature treatment. Managed via `/backlog` command or `scripts/backlog.py`.

## Priority Scale

| Priority | Meaning | When to use |
|----------|---------|-------------|
| 1 | Critical | Blocking work, fix ASAP |
| 2 | High | Should address soon |
| 3 | Medium | Address when convenient |
| 4 | Low | Nice to have |
| 5 | Someday | Might never do |

## Item Types

| Type | Prefix | Typical Resolution |
|------|--------|-------------------|
| Bug | `BUG-` | Fix with `/review-code`, update design |
| Idea | `IDEA-` | Promote to FEATURES.md or dismiss |
| Improvement | `IMP-` | Fix with `/review-code` or promote |
| Tech Debt | `DEBT-` | Fix with `/review-code` |
| Question | `Q-` | Resolve with `/decision` or dismiss |

## Index

<!-- Machine-readable index for quick queries. Keep sorted by status (open first), then priority. -->

| ID | Pri | Title | Related | Status |
|----|-----|-------|---------|--------|
| BUG-001 | 2 | Ctrl+C during interactive prompts continues workfl... | - | open |

## Open Items

<!-- Detailed item descriptions. -->

### BUG-001: Ctrl+C during interactive prompts continues workflow instead of exiting
- **Priority**: 2
- **Related**: -
- **Added**: 2026-01-05
- **Notes**: When pressing Ctrl+C during interactive prompts (questionary), the command continues to the next step instead of exiting. Locations: ui.py:108 (confirm_sources), ui.py:144 (prompt_save_location), command.py:115-129 (post-recording prompts), speaker.py:387-391 (speaker identification). Expected: Ctrl+C should exit with code 130, except during recording itself where it should stop recording and continue workflow.

## Resolved Items

<!-- Resolved items for reference. -->