# Dependency Matrix

Features listed in rows depend on features in columns.
Mark with `X` where row depends on column.

|           | CAT1-001 | CAT1-002 | CAT2-001 | CAT2-002 | CAT3-001 |
|-----------|----------|----------|----------|----------|----------|
| CAT1-001  | -        |          |          |          |          |
| CAT1-002  | X        | -        |          |          |          |
| CAT2-001  | X        |          | -        |          |          |
| CAT2-002  |          |          | X        | -        |          |
| CAT3-001  |          | X        | X        |          | -        |

## Implementation Phases (derived from matrix)

### Phase 1 (No dependencies)

Features that can be implemented first:
- CAT1-001: [name]

### Phase 2 (Depends only on Phase 1)

Features that require Phase 1:
- CAT1-002: [name]
- CAT2-001: [name]

### Phase 3 (Depends on Phase 2)

Features that require Phase 2:
- CAT2-002: [name]
- CAT3-001: [name]

---

## How to Use

1. List all features in both rows and columns
2. For each feature (row), mark which features it depends on (columns)
3. Features with no dependencies can be implemented first
4. Organize remaining features into phases based on dependency depth
