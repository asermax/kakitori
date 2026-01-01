# Design Patterns

This directory contains Design Pattern documents (DES) for repeatable patterns and conventions used throughout the kakitori project.

## Index

| ID | Title | Scope | Date |
|----|-------|-------|------|
| [DES-001](DES-001-lazy-command-imports.md) | Lazy Command Imports | Project-wide | 2026-01-01 |
| [DES-002](DES-002-atomic-file-operations.md) | Atomic File Operations with Temp Files | Project-wide | 2026-01-01 |
| [DES-003](DES-003-ffmpeg-graceful-stop.md) | Graceful ffmpeg Termination via stdin | Project-wide | 2026-01-01 |
| [DES-004](DES-004-layered-cleanup.md) | Layered Cleanup with atexit + try/finally | Project-wide | 2026-01-01 |
| [DES-005](DES-005-adaptive-snippet-duration.md) | Adaptive Snippet Duration | Project-wide | 2026-01-01 |
| [DES-006](DES-006-paginated-menu-ui.md) | Two-Level Paginated Menu UI | Project-wide | 2026-01-01 |

## When to Create a DES

Create a DES when establishing patterns that:
- Should be followed consistently across the codebase
- Solve a recurring problem
- Need examples of correct vs incorrect usage
- New code should follow

## Template

See the katachi framework for the DES template.
