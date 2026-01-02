# Scripts

Utility scripts for the Hayamimi project.

## deps.py

Dependency matrix query and manipulation tool.

### Usage

```bash
# Show what a feature depends on
python scripts/deps.py query LOG-001

# Show what depends on a feature
python scripts/deps.py reverse CLI-001

# Show full dependency tree (⬇ dependencies, ⬆ dependents)
python scripts/deps.py tree CORE-005

# Show which phase a feature is in
python scripts/deps.py phase CORE-001

# Validate the entire matrix for circular dependencies
python scripts/deps.py validate

# List all features with their phases and dependency counts
python scripts/deps.py list

# Add a dependency (FROM depends on TO)
python scripts/deps.py add-dep FEATURE-A FEATURE-B

# Remove a dependency
python scripts/deps.py remove-dep FEATURE-A FEATURE-B

# Add a new feature to the matrix
python scripts/deps.py add-feature FEATURE-ID

# Delete a feature from the matrix (only if no other features depend on it)
python scripts/deps.py delete-feature FEATURE-ID
```

### Examples

**Before implementing a feature**:
```bash
$ python scripts/deps.py query LOG-001
LOG-001 (Phase 2):
  Depends on:
    - CLI-001 (Phase 1)
```

**Check impact of changes**:
```bash
$ python scripts/deps.py reverse CLI-001
CLI-001 (Phase 1):
  Required by:
    - LOG-001 (Phase 2)
```

**View full dependency tree**:
```bash
$ python scripts/deps.py tree CLI-001
CLI-001 (Phase 1)
└── ⬆ LOG-001 (Phase 2)
```
- ⬇ indicates dependencies (what this feature needs)
- ⬆ indicates dependents (what needs this feature)

**Validate after edits**:
```bash
$ python scripts/deps.py validate
✓ No circular dependencies found
```

**Modify dependencies**:
```bash
# Add dependency: DICT-001 depends on CORE-003
$ python scripts/deps.py add-dep DICT-001 CORE-003
✓ Added dependency: DICT-001 → CORE-003

# Remove dependency
$ python scripts/deps.py remove-dep DICT-001 CORE-003
✓ Removed dependency: DICT-001 ⤫ CORE-003
```

**Manage features**:
```bash
# Add a new feature to the matrix
$ python scripts/deps.py add-feature DEPLOY-003
✓ Added feature: DEPLOY-003
  Note: Update FEATURES.md manually and add the feature to a phase in DEPENDENCIES.md

# Delete a feature (only if nothing depends on it)
$ python scripts/deps.py delete-feature DEPLOY-003
✓ Deleted feature: DEPLOY-003
  Note: Update FEATURES.md manually and remove the feature from phases in DEPENDENCIES.md
```

### Integration with Commands

Commands can use this tool to:
- Verify dependencies before implementation
- Check if prerequisite features are complete
- Validate dependency integrity after updates
- Query phase information for planning

### Implementation

The tool parses `planning/DEPENDENCIES.md` directly, extracting:
- Dependency relationships from the matrix
- Phase assignments from the Implementation Phases section
- Feature IDs and abbreviations from the legend

It validates the matrix for circular dependencies using depth-first search.
