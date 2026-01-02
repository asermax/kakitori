# Features

Atomic features extracted from the vision.

## Status Symbols

Features track their progress through the development workflow:

- **✓ Defined** - Feature extracted and documented (initial state)
- **⧗ Spec** - Specification in progress
- **✓ Spec** - Specification complete
- **⧗ Design** - Design rationale in progress
- **✓ Design** - Design complete
- **⧗ Plan** - Implementation plan in progress
- **✓ Plan** - Implementation plan complete
- **⧗ Implementation** - Feature implementation in progress
- **✓ Implementation** - Feature complete and tested

Use `python scripts/features.py status set FEATURE-ID "STATUS"` to update status.

---

## [Category 1]

### CAT1-001: [Feature name]
**Status**: ✓ Defined
**Complexity**: [Easy/Medium/Hard]
**Description**: [One line description]

### CAT1-002: [Feature name]
**Status**: ✓ Defined
**Complexity**: [Easy/Medium/Hard]
**Description**: [One line description]

### CAT1-003: [Feature name]
**Status**: ✓ Defined
**Complexity**: [Easy/Medium/Hard]
**Description**: [One line description]

---

## [Category 2]

### CAT2-001: [Feature name]
**Status**: ✓ Defined
**Complexity**: [Easy/Medium/Hard]
**Description**: [One line description]

### CAT2-002: [Feature name]
**Status**: ✓ Defined
**Complexity**: [Easy/Medium/Hard]
**Description**: [One line description]

---

## [Category 3]

### CAT3-001: [Feature name]
**Status**: ✓ Defined
**Complexity**: [Easy/Medium/Hard]
**Description**: [One line description]

---

## Atomicity Check

For each feature:
- ✓ Can be implemented in a single focused session
- ✓ Does ONE thing
- ✓ Has clear acceptance criteria
- ✓ Can be tested independently

If any feature fails these checks, split it into smaller features.
