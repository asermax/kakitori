#!/usr/bin/env python3
"""
Feature Management Tool

Manage features: dependencies, status tracking, and queries.

Usage:
    # Dependency commands
    python scripts/features.py deps query FEATURE-ID              # Show what FEATURE-ID depends on
    python scripts/features.py deps reverse FEATURE-ID            # Show what depends on FEATURE-ID
    python scripts/features.py deps phase FEATURE-ID              # Show which phase FEATURE-ID is in
    python scripts/features.py deps tree FEATURE-ID               # Show full dependency tree
    python scripts/features.py deps validate                      # Check for circular dependencies
    python scripts/features.py deps list                          # List all features with phases
    python scripts/features.py deps add-dep FROM-ID TO-ID         # Add dependency
    python scripts/features.py deps remove-dep FROM-ID TO-ID      # Remove dependency
    python scripts/features.py deps add-feature FEATURE-ID        # Add new feature to matrix
    python scripts/features.py deps delete-feature FEATURE-ID     # Delete feature from matrix
    python scripts/features.py deps recalculate-phases            # Recalculate phases from dependencies

    # Status commands
    python scripts/features.py status list                        # List all features with status
    python scripts/features.py status list --phase N              # Filter by phase
    python scripts/features.py status list --category CAT         # Filter by category
    python scripts/features.py status list --status "STATUS"      # Filter by status text
    python scripts/features.py status show FEATURE-ID             # Show detailed feature status
    python scripts/features.py status set FEATURE-ID STATUS       # Update feature status

    # Query commands
    python scripts/features.py ready                              # List features ready to implement
    python scripts/features.py next                               # Suggest next feature to implement
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


class DependencyMatrix:
    def __init__(self, filepath: str = "planning/DEPENDENCIES.md"):
        self.filepath = Path(filepath)
        self.features: List[str] = []
        self.matrix: Dict[str, Set[str]] = {}
        self.phases: Dict[str, int] = {}
        self._load()

    def _load(self):
        """Load the dependency matrix from DEPENDENCIES.md"""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Dependency matrix not found: {self.filepath}")

        content = self.filepath.read_text()

        # Extract feature list from matrix header
        header_match = re.search(r'\| *\| ([^\n]+)\n', content)
        if header_match:
            header = header_match.group(1)
            # Parse column headers (abbreviated feature IDs)
            self.column_abbrevs = [col.strip() for col in header.split('|') if col.strip()]

        # Extract legend to map abbreviations to full IDs
        legend_section = re.search(r'\*\*Legend:\*\*(.+?)---', content, re.DOTALL)
        if legend_section:
            self.abbrev_map = self._parse_legend(legend_section.group(1))

        # Parse matrix rows
        matrix_lines = re.findall(r'\| ([A-Z]+-\d+) +\|([^\n]+)', content)
        for feature_id, row in matrix_lines:
            self.features.append(feature_id)
            deps = set()
            # Keep ALL cells including empty ones to maintain column alignment
            cells = [c.strip() for c in row.split('|')]

            # Match cells with column abbreviations
            for idx, cell in enumerate(cells):
                if idx < len(self.column_abbrevs) and cell == 'X':
                    abbrev = self.column_abbrevs[idx]
                    dep_id = self.abbrev_map.get(abbrev, abbrev)
                    if dep_id != feature_id:  # Don't include self-dependencies
                        deps.add(dep_id)

            self.matrix[feature_id] = deps

        # Extract phases
        self._parse_phases(content)

    def _parse_legend(self, legend_text: str) -> Dict[str, str]:
        """Parse legend to map abbreviations to full feature IDs"""
        mapping = {}
        for line in legend_text.strip().split('\n'):
            if ':' in line:
                abbrev_part, full_part = line.split(':', 1)
                abbrev = abbrev_part.strip().replace('-', '').strip()

                # Handle ranges like "C001-C005: CORE-001 through CORE-005"
                if 'through' in full_part:
                    match = re.search(r'([A-Z]+-\d+) through ([A-Z]+-\d+)', full_part)
                    if match:
                        start, end = match.groups()
                        # This is a range - we'll handle individual items separately
                        continue
                else:
                    # Single item like "CLI1: CLI-001"
                    full_id = full_part.strip()
                    mapping[abbrev] = full_id

        # Add common abbreviations
        for i in range(1, 6):
            mapping[f'C00{i}'] = f'CORE-00{i}'
        mapping['CLI1'] = 'CLI-001'
        for i in range(1, 4):
            mapping[f'D00{i}'] = f'DICT-00{i}'
        mapping['CTX1'] = 'CTX-001'
        for i in range(1, 6):
            mapping[f'E00{i}'] = f'EDIT-00{i}'
        for i in range(1, 9):
            mapping[f'S00{i}'] = f'SETUP-00{i}'
        for i in range(1, 5):
            mapping[f'U00{i}'] = f'UI-00{i}'
        for i in range(1, 4):
            mapping[f'ER0{i}'] = f'ERROR-00{i}'
        mapping['L001'] = 'LOG-001'
        for i in range(1, 3):
            mapping[f'DP0{i}'] = f'DEPLOY-00{i}'
        mapping['DOC1'] = 'DOCS-001'

        return mapping

    def _parse_phases(self, content: str):
        """Extract phase assignments from the Implementation Phases section"""
        phase_sections = re.findall(
            r'### Phase (\d+):[^\n]+\n\n[^\n]+\n(.+?)(?=\n\*\*Test Milestone|\n###|$)',
            content,
            re.DOTALL
        )

        for phase_num, phase_content in phase_sections:
            # Extract feature IDs from bullet points
            feature_matches = re.findall(r'- \*\*([A-Z]+-\d+)\*\*:', phase_content)
            for feature_id in feature_matches:
                self.phases[feature_id] = int(phase_num)

    def get_dependencies(self, feature_id: str) -> Set[str]:
        """Get what FEATURE-ID depends on"""
        return self.matrix.get(feature_id, set())

    def get_dependents(self, feature_id: str) -> Set[str]:
        """Get what depends on FEATURE-ID"""
        dependents = set()
        for fid, deps in self.matrix.items():
            if feature_id in deps:
                dependents.add(fid)
        return dependents

    def get_phase(self, feature_id: str) -> int | None:
        """Get which phase FEATURE-ID is in"""
        return self.phases.get(feature_id)

    def validate(self) -> Tuple[bool, List[str]]:
        """Check for circular dependencies"""
        errors = []

        def has_cycle(feature: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(feature)
            rec_stack.add(feature)

            for dep in self.matrix.get(feature, set()):
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    errors.append(f"Circular dependency detected: {feature} -> {dep}")
                    return True

            rec_stack.remove(feature)
            return False

        visited = set()
        for feature in self.features:
            if feature not in visited:
                has_cycle(feature, visited, set())

        return len(errors) == 0, errors

    def print_dependencies(self, feature_id: str):
        """Print what FEATURE-ID depends on"""
        deps = self.get_dependencies(feature_id)
        phase = self.get_phase(feature_id)

        print(f"\n{feature_id} (Phase {phase if phase else 'Unknown'}):")
        if deps:
            print("  Depends on:")
            for dep in sorted(deps):
                dep_phase = self.get_phase(dep)
                print(f"    - {dep} (Phase {dep_phase if dep_phase else 'Unknown'})")
        else:
            print("  No dependencies")

    def print_dependents(self, feature_id: str):
        """Print what depends on FEATURE-ID"""
        dependents = self.get_dependents(feature_id)
        phase = self.get_phase(feature_id)

        print(f"\n{feature_id} (Phase {phase if phase else 'Unknown'}):")
        if dependents:
            print("  Required by:")
            for dep in sorted(dependents):
                dep_phase = self.get_phase(dep)
                print(f"    - {dep} (Phase {dep_phase if dep_phase else 'Unknown'})")
        else:
            print("  No dependents")

    def print_tree(self, feature_id: str, _visited: Set[str] = None, _prefix: str = ""):
        """Print full dependency tree for FEATURE-ID"""
        if _visited is None:
            _visited = set()
            phase = self.get_phase(feature_id)
            print(f"\n{feature_id} (Phase {phase if phase else 'Unknown'})")
            _prefix = ""

        if feature_id in _visited:
            return
        _visited.add(feature_id)

        # Show dependencies (what this feature needs)
        deps = sorted(self.get_dependencies(feature_id))

        # Show dependents (what needs this feature)
        dependents = sorted(self.get_dependents(feature_id))

        all_children = [(dep, True) for dep in deps] + [(dep, False) for dep in dependents]

        for i, (child, is_dependency) in enumerate(all_children):
            child_phase = self.get_phase(child)

            # Check if this is the last item to be printed at this level
            # (last overall item, or last dependency if we have dependents that won't recurse)
            is_last_item = i == len(all_children) - 1

            # Connector for this item
            connector = "└──" if is_last_item else "├──"
            arrow = "⬇" if is_dependency else "⬆"

            print(f"{_prefix}{connector} {arrow} {child} (Phase {child_phase if child_phase else '?'})")

            # Prepare prefix for children - use spaces for last item, vertical line otherwise
            extension = "    " if is_last_item else "│   "
            child_prefix = _prefix + extension

            # Recursively show this child's tree (only dependencies)
            if is_dependency and child not in _visited:
                self.print_tree(child, _visited, child_prefix)

    def add_dependency(self, from_feature: str, to_feature: str):
        """Add dependency: from_feature depends on to_feature"""
        if from_feature not in self.features:
            raise ValueError(f"Feature not found: {from_feature}")
        if to_feature not in self.features:
            raise ValueError(f"Feature not found: {to_feature}")
        if from_feature == to_feature:
            raise ValueError("Cannot add self-dependency")

        self.matrix[from_feature].add(to_feature)
        self._write_matrix()
        print(f"✓ Added dependency: {from_feature} → {to_feature}")

    def remove_dependency(self, from_feature: str, to_feature: str):
        """Remove dependency: from_feature no longer depends on to_feature"""
        if from_feature not in self.features:
            raise ValueError(f"Feature not found: {from_feature}")
        if to_feature not in self.matrix.get(from_feature, set()):
            raise ValueError(f"Dependency does not exist: {from_feature} → {to_feature}")

        self.matrix[from_feature].remove(to_feature)
        self._write_matrix()
        print(f"✓ Removed dependency: {from_feature} ⤫ {to_feature}")

    def add_feature(self, feature_id: str):
        """Add a new feature to the matrix"""
        # Validate feature ID format
        if not re.match(r'^[A-Z]+-\d+$', feature_id):
            raise ValueError(f"Invalid feature ID format: {feature_id} (expected: CATEGORY-NNN)")

        if feature_id in self.features:
            raise ValueError(f"Feature already exists: {feature_id}")

        # Add feature to list (will be sorted when matrix is built)
        self.features.append(feature_id)
        self.features.sort()  # Keep features sorted

        # Initialize empty dependency set
        self.matrix[feature_id] = set()

        # Write updated matrix
        self._write_matrix()
        print(f"✓ Added feature: {feature_id}")
        print(f"  Note: Update FEATURES.md manually and add the feature to a phase in DEPENDENCIES.md")

    def delete_feature(self, feature_id: str):
        """Delete a feature from the matrix"""
        if feature_id not in self.features:
            raise ValueError(f"Feature not found: {feature_id}")

        # Check if other features depend on this one
        dependents = self.get_dependents(feature_id)
        if dependents:
            raise ValueError(
                f"Cannot delete {feature_id}: other features depend on it:\n" +
                "\n".join(f"  - {dep}" for dep in sorted(dependents))
            )

        # Remove feature from list
        self.features.remove(feature_id)

        # Remove from matrix
        del self.matrix[feature_id]

        # Remove as dependency from other features
        for deps in self.matrix.values():
            deps.discard(feature_id)

        # Write updated matrix
        self._write_matrix()
        print(f"✓ Deleted feature: {feature_id}")
        print(f"  Note: Update FEATURES.md manually and remove the feature from phases in DEPENDENCIES.md")

    def _write_matrix(self):
        """Write the matrix back to the file"""
        content = self.filepath.read_text()

        # Find matrix section
        matrix_start = content.find('## Full Dependency Matrix')
        matrix_end = content.find('\n**Legend:**')

        if matrix_start == -1 or matrix_end == -1:
            raise ValueError("Could not find matrix section in file")

        # Build new matrix content
        new_matrix = self._build_matrix_table()

        # Replace matrix section
        new_content = (
            content[:matrix_start] +
            '## Full Dependency Matrix\n\n' +
            new_matrix +
            '\n' +
            content[matrix_end:]
        )

        self.filepath.write_text(new_content)

    def recalculate_phases(self) -> Dict[str, int]:
        """Recalculate phases using topological sort based on dependencies"""
        # Kahn's algorithm for topological sort with level tracking
        in_degree: Dict[str, int] = {f: 0 for f in self.features}
        for feature in self.features:
            for dep in self.matrix.get(feature, set()):
                if dep in in_degree:
                    in_degree[feature] += 1

        # Start with features that have no dependencies
        current_phase = 1
        new_phases: Dict[str, int] = {}
        remaining = set(self.features)

        while remaining:
            # Find all features with in_degree == 0 among remaining
            ready = [f for f in remaining if in_degree[f] == 0]

            if not ready:
                # Circular dependency detected
                raise ValueError(f"Circular dependency detected involving: {remaining}")

            # Assign current phase to all ready features
            for feature in ready:
                new_phases[feature] = current_phase
                remaining.remove(feature)

                # Decrease in_degree for dependents
                for other in remaining:
                    if feature in self.matrix.get(other, set()):
                        in_degree[other] -= 1

            current_phase += 1

        return new_phases

    def _build_matrix_table(self) -> str:
        """Build the matrix table as markdown"""
        # Build header row with abbreviations
        abbrevs = []
        for feature in self.features:
            # Create abbreviation from feature ID
            parts = feature.split('-')
            if parts[0] == 'CORE':
                abbrevs.append(f'C{parts[1]}')
            elif parts[0] == 'CLI':
                abbrevs.append('CLI1')
            elif parts[0] == 'DICT':
                abbrevs.append(f'D{parts[1]}')
            elif parts[0] == 'CTX':
                abbrevs.append('CTX1')
            elif parts[0] == 'EDIT':
                abbrevs.append(f'E{parts[1]}')
            elif parts[0] == 'SETUP':
                abbrevs.append(f'S{parts[1]}')
            elif parts[0] == 'UI':
                abbrevs.append(f'U{parts[1]}')
            elif parts[0] == 'ERROR':
                abbrevs.append(f'ER{parts[1]}')
            elif parts[0] == 'LOG':
                abbrevs.append('L001')
            elif parts[0] == 'DEPLOY':
                abbrevs.append(f'DP{parts[1]}')
            elif parts[0] == 'DOCS':
                abbrevs.append('DOC1')
            else:
                abbrevs.append(feature[:4])

        # Build header
        header = '|            | ' + ' | '.join(abbrevs) + ' |'
        separator = '|------------|' + '------|' * len(abbrevs)

        lines = [header, separator]

        # Build rows
        for row_feature in self.features:
            cells = [f'| {row_feature:10} |']
            for col_feature in self.features:
                if row_feature == col_feature:
                    cells.append(' -    |')
                elif col_feature in self.matrix.get(row_feature, set()):
                    cells.append(' X    |')
                else:
                    cells.append('      |')
            lines.append(''.join(cells))

        return '\n'.join(lines)


class StatusManager:
    def __init__(self, filepath: str = "planning/FEATURES.md"):
        self.filepath = Path(filepath)
        self.features: Dict[str, Dict[str, str]] = {}
        self._load()

    def _load(self):
        """Load feature statuses from FEATURES.md"""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Features file not found: {self.filepath}")

        content = self.filepath.read_text()

        # Parse features from markdown
        # Format: ### FEATURE-ID: Feature name
        # followed by: **Status**: symbol Phase
        feature_pattern = re.compile(
            r'^### ([A-Z]+-\d+): (.+?)$\n'
            r'(?:\*\*Status\*\*: (.+?)$\n)?'
            r'(?:\*\*Complexity\*\*: (.+?)$\n)?'
            r'(?:\*\*Description\*\*: (.+?)$)?',
            re.MULTILINE
        )

        for match in feature_pattern.finditer(content):
            feature_id = match.group(1)
            name = match.group(2).strip()
            status = match.group(3).strip() if match.group(3) else "✗ Not Started"
            complexity = match.group(4).strip() if match.group(4) else "Unknown"
            description = match.group(5).strip() if match.group(5) else ""

            self.features[feature_id] = {
                'name': name,
                'status': status,
                'complexity': complexity,
                'description': description
            }

    def get_status(self, feature_id: str) -> Optional[str]:
        """Get status of a feature"""
        feature = self.features.get(feature_id)
        return feature['status'] if feature else None

    def set_status(self, feature_id: str, status: str):
        """Update status of a feature in FEATURES.md"""
        if feature_id not in self.features:
            raise ValueError(f"Feature not found: {feature_id}")

        content = self.filepath.read_text()

        # Find the feature section and update status
        # Look for the feature header and the status line
        pattern = re.compile(
            rf'^(### {re.escape(feature_id)}: .+?$)\n'
            rf'(\*\*Status\*\*: .+?$)?',
            re.MULTILINE
        )

        def replacer(match):
            header = match.group(1)
            if match.group(2):
                # Status line exists, replace it
                return f"{header}\n**Status**: {status}"
            else:
                # No status line, add it
                return f"{header}\n**Status**: {status}"

        new_content = pattern.sub(replacer, content)

        self.filepath.write_text(new_content)
        self.features[feature_id]['status'] = status
        print(f"✓ Updated {feature_id} status to: {status}")

    def list_features(
        self,
        phase: Optional[int] = None,
        category: Optional[str] = None,
        status_filter: Optional[str] = None,
        dm: Optional[DependencyMatrix] = None
    ):
        """List features with optional filtering"""
        print("\nFeatures:")
        for feature_id in sorted(self.features.keys()):
            feature = self.features[feature_id]

            # Apply filters
            if category and not feature_id.startswith(f"{category}-"):
                continue
            if status_filter and status_filter.lower() not in feature['status'].lower():
                continue
            if phase is not None and dm:
                feature_phase = dm.get_phase(feature_id)
                if feature_phase != phase:
                    continue

            # Get phase info if dm is provided
            phase_info = ""
            if dm:
                feature_phase = dm.get_phase(feature_id)
                phase_info = f" | Phase {feature_phase if feature_phase else '?'}"

            print(f"  {feature_id:12} {feature['status']:20}{phase_info}")

    def show_feature(self, feature_id: str, dm: Optional[DependencyMatrix] = None):
        """Show detailed status for a feature"""
        if feature_id not in self.features:
            raise ValueError(f"Feature not found: {feature_id}")

        feature = self.features[feature_id]

        print(f"\n{feature_id}: {feature['name']}")
        print(f"  Status: {feature['status']}")
        print(f"  Complexity: {feature['complexity']}")

        if dm:
            phase = dm.get_phase(feature_id)
            print(f"  Phase: {phase if phase else 'Unknown'}")

            deps = dm.get_dependencies(feature_id)
            if deps:
                print(f"  Dependencies ({len(deps)}):")
                for dep in sorted(deps):
                    print(f"    - {dep}")

            dependents = dm.get_dependents(feature_id)
            if dependents:
                print(f"  Required by ({len(dependents)}):")
                for dep in sorted(dependents):
                    print(f"    - {dep}")

    def is_complete(self, feature_id: str) -> bool:
        """Check if a feature is complete (implementation done)"""
        feature = self.features.get(feature_id)
        if not feature:
            return False
        status = feature['status'].lower()
        return '✓ implementation' in status or 'complete' in status

    def get_ready_features(self, dm: DependencyMatrix) -> List[str]:
        """Get features that are ready to implement (all deps complete, not started yet)"""
        ready = []

        for feature_id in self.features:
            feature = self.features[feature_id]
            status = feature['status'].lower()

            # Skip if already in progress or complete
            if '⧗' in feature['status'] or self.is_complete(feature_id):
                continue

            # Check if all dependencies are complete
            deps = dm.get_dependencies(feature_id)
            all_deps_complete = all(self.is_complete(dep) for dep in deps)

            if all_deps_complete:
                ready.append(feature_id)

        return ready

    def suggest_next(self, dm: DependencyMatrix) -> Optional[str]:
        """Suggest the next feature to implement based on dependencies and impact"""
        ready = self.get_ready_features(dm)

        if not ready:
            return None

        # Score features by how many other features depend on them (higher = more impactful)
        def impact_score(fid: str) -> int:
            return len(dm.get_dependents(fid))

        # Sort by impact (descending), then by phase (ascending), then by ID
        ready.sort(key=lambda f: (-impact_score(f), dm.get_phase(f) or 999, f))

        return ready[0] if ready else None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    subcommand = sys.argv[1]

    # Find project root (where planning/ directory exists)
    cwd = Path.cwd()
    project_root = cwd
    while project_root != project_root.parent:
        if (project_root / "planning" / "DEPENDENCIES.md").exists():
            break
        project_root = project_root.parent
    else:
        print("Error: Could not find planning/DEPENDENCIES.md")
        sys.exit(1)

    if subcommand == "deps":
        # Dependency management commands
        if len(sys.argv) < 3:
            print("Usage: features.py deps <command> [args]")
            print("\nAvailable commands: query, reverse, phase, tree, validate, list, add-dep, remove-dep, add-feature, delete-feature")
            sys.exit(1)

        command = sys.argv[2]
        matrix_path = project_root / "planning" / "DEPENDENCIES.md"
        dm = DependencyMatrix(str(matrix_path))

        if command == "query":
            if len(sys.argv) < 4:
                print("Usage: features.py deps query FEATURE-ID")
                sys.exit(1)
            feature_id = sys.argv[3]
            dm.print_dependencies(feature_id)

        elif command == "reverse":
            if len(sys.argv) < 4:
                print("Usage: features.py deps reverse FEATURE-ID")
                sys.exit(1)
            feature_id = sys.argv[3]
            dm.print_dependents(feature_id)

        elif command == "phase":
            if len(sys.argv) < 4:
                print("Usage: features.py deps phase FEATURE-ID")
                sys.exit(1)
            feature_id = sys.argv[3]
            phase = dm.get_phase(feature_id)
            print(f"\n{feature_id}: Phase {phase if phase else 'Unknown'}")

        elif command == "validate":
            valid, errors = dm.validate()
            if valid:
                print("\n✓ No circular dependencies found")
            else:
                print("\n✗ Validation errors:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)

        elif command == "list":
            print("\nAll features:")
            for feature_id in sorted(dm.features):
                phase = dm.get_phase(feature_id)
                deps_count = len(dm.get_dependencies(feature_id))
                print(f"  {feature_id:12} Phase {phase if phase else '?'} ({deps_count} dependencies)")

        elif command == "tree":
            if len(sys.argv) < 4:
                print("Usage: features.py deps tree FEATURE-ID")
                sys.exit(1)
            feature_id = sys.argv[3]
            if feature_id not in dm.features:
                print(f"Error: Feature not found: {feature_id}")
                sys.exit(1)
            dm.print_tree(feature_id)

        elif command == "add-dep":
            if len(sys.argv) < 5:
                print("Usage: features.py deps add-dep FROM-ID TO-ID")
                sys.exit(1)
            from_id = sys.argv[3]
            to_id = sys.argv[4]
            try:
                dm.add_dependency(from_id, to_id)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)

        elif command == "remove-dep":
            if len(sys.argv) < 5:
                print("Usage: features.py deps remove-dep FROM-ID TO-ID")
                sys.exit(1)
            from_id = sys.argv[3]
            to_id = sys.argv[4]
            try:
                dm.remove_dependency(from_id, to_id)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)

        elif command == "add-feature":
            if len(sys.argv) < 4:
                print("Usage: features.py deps add-feature FEATURE-ID")
                sys.exit(1)
            feature_id = sys.argv[3]
            try:
                dm.add_feature(feature_id)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)

        elif command == "delete-feature":
            if len(sys.argv) < 4:
                print("Usage: features.py deps delete-feature FEATURE-ID")
                sys.exit(1)
            feature_id = sys.argv[3]
            try:
                dm.delete_feature(feature_id)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)

        elif command == "recalculate-phases":
            try:
                new_phases = dm.recalculate_phases()
                print("\nRecalculated phases:")
                for phase_num in sorted(set(new_phases.values())):
                    features_in_phase = [f for f, p in new_phases.items() if p == phase_num]
                    print(f"\n  Phase {phase_num}:")
                    for fid in sorted(features_in_phase):
                        current_phase = dm.get_phase(fid)
                        changed = " (was {})".format(current_phase) if current_phase != phase_num else ""
                        print(f"    - {fid}{changed}")
                print("\nNote: Update DEPENDENCIES.md Implementation Phases section manually")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)

        else:
            print(f"Unknown deps command: {command}")
            sys.exit(1)

    elif subcommand == "status":
        # Status tracking commands
        if len(sys.argv) < 3:
            print("Usage: features.py status <command> [args]")
            print("\nAvailable commands: list, show, set")
            sys.exit(1)

        command = sys.argv[2]
        features_path = project_root / "planning" / "FEATURES.md"
        sm = StatusManager(str(features_path))

        # Also load dependency matrix for richer status display
        matrix_path = project_root / "planning" / "DEPENDENCIES.md"
        dm = DependencyMatrix(str(matrix_path))

        if command == "list":
            # Parse optional filters
            phase = None
            category = None
            status_filter = None

            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--phase" and i + 1 < len(sys.argv):
                    phase = int(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] == "--category" and i + 1 < len(sys.argv):
                    category = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--status" and i + 1 < len(sys.argv):
                    status_filter = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1

            sm.list_features(phase=phase, category=category, status_filter=status_filter, dm=dm)

        elif command == "show":
            if len(sys.argv) < 4:
                print("Usage: features.py status show FEATURE-ID")
                sys.exit(1)
            feature_id = sys.argv[3]
            try:
                sm.show_feature(feature_id, dm=dm)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)

        elif command == "set":
            if len(sys.argv) < 5:
                print("Usage: features.py status set FEATURE-ID STATUS")
                print("\nExample statuses:")
                print("  ✓ Defined")
                print("  ⧗ Spec")
                print("  ✓ Spec")
                print("  ⧗ Design")
                print("  ✓ Design")
                print("  ⧗ Plan")
                print("  ✓ Plan")
                print("  ⧗ Implementation")
                print("  ✓ Implementation")
                sys.exit(1)
            feature_id = sys.argv[3]
            status = ' '.join(sys.argv[4:])  # Allow multi-word status
            try:
                sm.set_status(feature_id, status)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)

        else:
            print(f"Unknown status command: {command}")
            sys.exit(1)

    elif subcommand == "ready":
        # List features ready to implement
        features_path = project_root / "planning" / "FEATURES.md"
        matrix_path = project_root / "planning" / "DEPENDENCIES.md"

        sm = StatusManager(str(features_path))
        dm = DependencyMatrix(str(matrix_path))

        ready = sm.get_ready_features(dm)

        if ready:
            print("\nFeatures ready to implement (all dependencies complete):\n")
            for fid in sorted(ready, key=lambda f: (dm.get_phase(f) or 999, f)):
                feature = sm.features[fid]
                phase = dm.get_phase(fid)
                dependents = len(dm.get_dependents(fid))
                impact = f"({dependents} dependent{'s' if dependents != 1 else ''})" if dependents > 0 else ""
                print(f"  {fid:12} Phase {phase or '?'}  {feature['name']} {impact}")
        else:
            print("\nNo features ready to implement.")
            print("Either all features are in progress/complete, or dependencies are blocking.")

    elif subcommand == "next":
        # Suggest next feature to implement
        features_path = project_root / "planning" / "FEATURES.md"
        matrix_path = project_root / "planning" / "DEPENDENCIES.md"

        sm = StatusManager(str(features_path))
        dm = DependencyMatrix(str(matrix_path))

        suggestion = sm.suggest_next(dm)

        if suggestion:
            feature = sm.features[suggestion]
            phase = dm.get_phase(suggestion)
            dependents = dm.get_dependents(suggestion)

            print(f"\nSuggested next feature: {suggestion}")
            print(f"  Name: {feature['name']}")
            print(f"  Phase: {phase or 'Unknown'}")
            print(f"  Status: {feature['status']}")

            if dependents:
                print(f"  Unlocks {len(dependents)} feature(s):")
                for dep in sorted(dependents):
                    print(f"    - {dep}")
            else:
                print("  Unlocks: No other features directly depend on this")

            deps = dm.get_dependencies(suggestion)
            if deps:
                print(f"  Depends on ({len(deps)} complete):")
                for dep in sorted(deps):
                    print(f"    - {dep} ✓")
        else:
            print("\nNo features available to implement.")
            print("Either all features are complete, or dependencies are blocking progress.")

    else:
        print(f"Unknown subcommand: {subcommand}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
