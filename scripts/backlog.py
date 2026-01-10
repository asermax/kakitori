#!/usr/bin/env python3
"""
Backlog Management Tool

Manage backlog items: bugs, ideas, improvements, tech-debt, and questions.

Usage:
    # Adding items
    python scripts/backlog.py add bug "Title" [--related X,Y] [--priority N] [--notes "..."]
    python scripts/backlog.py add idea "Title" [--related X] [--priority N] [--notes "..."]
    python scripts/backlog.py add improvement "Title" ...
    python scripts/backlog.py add tech-debt "Title" ...
    python scripts/backlog.py add question "Title" ...

    # Listing and querying
    python scripts/backlog.py list                      # Open items, sorted by priority
    python scripts/backlog.py list --type bug           # Filter by type
    python scripts/backlog.py list --priority 1-2       # Priority range (1-2 means 1 and 2)
    python scripts/backlog.py list --related DICT-002   # Items related to feature
    python scripts/backlog.py list --all                # Include resolved items

    # Show details
    python scripts/backlog.py show BUG-001              # Show single item details

    # Check for duplicates (fuzzy title match)
    python scripts/backlog.py check "clipboard issue"   # Find similar items

    # Update items
    python scripts/backlog.py priority BUG-001 2        # Change priority
    python scripts/backlog.py relate BUG-001 CTX-001    # Add related feature
    python scripts/backlog.py note BUG-001 "More info"  # Add note

    # Resolve items
    python scripts/backlog.py fix BUG-001 [--commit abc123]
    python scripts/backlog.py promote IDEA-001 [--feature FEAT-ID]
    python scripts/backlog.py dismiss DEBT-001 "reason"
    python scripts/backlog.py duplicate BUG-003 BUG-001
"""

import re
import sys
from datetime import date
from pathlib import Path
from typing import NamedTuple


class BacklogItem(NamedTuple):
    """Represents a backlog item."""

    id: str
    type: str
    title: str
    priority: int
    related: list[str]
    status: str
    added: str
    resolved: str | None = None
    resolution: str | None = None
    commit: str | None = None
    notes: str | None = None


# Type prefixes
TYPE_PREFIXES = {
    "bug": "BUG",
    "idea": "IDEA",
    "improvement": "IMP",
    "tech-debt": "DEBT",
    "question": "Q",
}

# Reverse mapping
PREFIX_TO_TYPE = {v: k for k, v in TYPE_PREFIXES.items()}


class BacklogManager:
    def __init__(self, filepath: str = "docs/planning/BACKLOG.md"):
        self.filepath = Path(filepath)
        self.items: dict[str, BacklogItem] = {}
        self._load()

    def _load(self):
        """Load backlog items from BACKLOG.md"""
        if not self.filepath.exists():
            return

        content = self.filepath.read_text()

        # Parse index for quick reference
        index_pattern = re.compile(
            r"^\| ((?:BUG|IDEA|IMP|DEBT|Q)-\d+) \| (\d) \| (.+?) \| (.+?) \| (\w+) \|$",
            re.MULTILINE,
        )

        # Parse detailed items - more flexible pattern
        item_pattern = re.compile(
            r"^### ((?:BUG|IDEA|IMP|DEBT|Q)-\d+): (.+?)$\n"
            r"- \*\*Priority\*\*: (\d)\n"
            r"- \*\*Related\*\*: (.+?)\n"
            r"- \*\*Added\*\*: ([^\n]+)"
            r"(?:\n- \*\*Resolved\*\*: ([^\n]+))?"
            r"(?:\n- \*\*Resolution\*\*: ([^\n]+))?"
            r"(?:\n- \*\*Commit\*\*: ([^\n]+))?"
            r"(?:\n- \*\*Notes\*\*: ([^\n]+))?",
            re.MULTILINE,
        )

        for match in item_pattern.finditer(content):
            item_id = match.group(1)
            title = match.group(2).strip()
            priority = int(match.group(3))
            related_str = match.group(4).strip()
            added = match.group(5).strip()
            resolved = match.group(6).strip() if match.group(6) else None
            resolution = match.group(7).strip() if match.group(7) else None
            commit = match.group(8).strip() if match.group(8) else None
            notes = match.group(9).strip() if match.group(9) else None

            # Parse related features
            related = []
            if related_str and related_str != "-":
                related = [r.strip() for r in related_str.split(",")]

            # Determine type from ID prefix
            prefix = item_id.split("-")[0]
            item_type = PREFIX_TO_TYPE.get(prefix, "unknown")

            # Determine status from section
            status = "resolved" if resolved else "open"

            self.items[item_id] = BacklogItem(
                id=item_id,
                type=item_type,
                title=title,
                priority=priority,
                related=related,
                status=status,
                added=added,
                resolved=resolved,
                resolution=resolution,
                commit=commit,
                notes=notes,
            )

    def _get_next_id(self, item_type: str) -> str:
        """Get the next available ID for a type."""
        prefix = TYPE_PREFIXES.get(item_type)
        if not prefix:
            raise ValueError(f"Unknown item type: {item_type}")

        # Find highest existing ID for this type
        max_num = 0
        for item_id in self.items:
            if item_id.startswith(f"{prefix}-"):
                num = int(item_id.split("-")[1])
                max_num = max(max_num, num)

        return f"{prefix}-{max_num + 1:03d}"

    def add(
        self,
        item_type: str,
        title: str,
        priority: int = 3,
        related: list[str] | None = None,
        notes: str | None = None,
    ) -> str:
        """Add a new backlog item. Returns the new item ID."""
        if item_type not in TYPE_PREFIXES:
            raise ValueError(
                f"Unknown item type: {item_type}. "
                f"Valid types: {', '.join(TYPE_PREFIXES.keys())}"
            )

        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")

        item_id = self._get_next_id(item_type)
        today = date.today().isoformat()

        item = BacklogItem(
            id=item_id,
            type=item_type,
            title=title,
            priority=priority,
            related=related or [],
            status="open",
            added=today,
            notes=notes,
        )

        self.items[item_id] = item
        self._save()

        return item_id

    def check_duplicates(self, title: str, threshold: float = 0.5) -> list[BacklogItem]:
        """Find items with similar titles (fuzzy match)."""
        title_words = set(title.lower().split())
        similar = []

        for item in self.items.values():
            if item.status == "resolved":
                continue

            item_words = set(item.title.lower().split())

            # Jaccard similarity
            intersection = len(title_words & item_words)
            union = len(title_words | item_words)

            if union > 0 and intersection / union >= threshold:
                similar.append(item)

        return similar

    def list_items(
        self,
        item_type: str | None = None,
        priority_range: tuple[int, int] | None = None,
        related: str | None = None,
        include_resolved: bool = False,
    ) -> list[BacklogItem]:
        """List items with optional filters."""
        results = []

        for item in self.items.values():
            # Filter by status
            if not include_resolved and item.status == "resolved":
                continue

            # Filter by type
            if item_type and item.type != item_type:
                continue

            # Filter by priority range
            if priority_range:
                min_p, max_p = priority_range
                if not (min_p <= item.priority <= max_p):
                    continue

            # Filter by related feature
            if related and related not in item.related:
                continue

            results.append(item)

        # Sort by priority (ascending), then by ID
        results.sort(key=lambda i: (i.priority, i.id))

        return results

    def get(self, item_id: str) -> BacklogItem | None:
        """Get a single item by ID."""
        return self.items.get(item_id)

    def set_priority(self, item_id: str, priority: int):
        """Update item priority."""
        if item_id not in self.items:
            raise ValueError(f"Item not found: {item_id}")

        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")

        item = self.items[item_id]
        self.items[item_id] = item._replace(priority=priority)
        self._save()

    def add_related(self, item_id: str, feature_id: str):
        """Add a related feature to an item."""
        if item_id not in self.items:
            raise ValueError(f"Item not found: {item_id}")

        item = self.items[item_id]
        if feature_id not in item.related:
            new_related = item.related + [feature_id]
            self.items[item_id] = item._replace(related=new_related)
            self._save()

    def add_note(self, item_id: str, note: str):
        """Append a note to an item."""
        if item_id not in self.items:
            raise ValueError(f"Item not found: {item_id}")

        item = self.items[item_id]
        if item.notes:
            new_notes = f"{item.notes}\n{note}"
        else:
            new_notes = note
        self.items[item_id] = item._replace(notes=new_notes)
        self._save()

    def resolve(
        self,
        item_id: str,
        resolution: str,
        commit: str | None = None,
        duplicate_of: str | None = None,
        feature_id: str | None = None,
    ):
        """Resolve an item."""
        if item_id not in self.items:
            raise ValueError(f"Item not found: {item_id}")

        item = self.items[item_id]
        today = date.today().isoformat()

        notes = item.notes or ""
        if resolution == "duplicate" and duplicate_of:
            notes = f"{notes}\nDuplicate of {duplicate_of}".strip()
        elif resolution == "promoted" and feature_id:
            notes = f"{notes}\nPromoted to {feature_id}".strip()

        self.items[item_id] = item._replace(
            status="resolved",
            resolved=today,
            resolution=resolution,
            commit=commit,
            notes=notes if notes else None,
        )
        self._save()

    def _save(self):
        """Save backlog to file."""
        # Separate open and resolved items
        open_items = [i for i in self.items.values() if i.status == "open"]
        resolved_items = [i for i in self.items.values() if i.status == "resolved"]

        # Sort: open by priority then ID, resolved by date (newest first)
        open_items.sort(key=lambda i: (i.priority, i.id))
        resolved_items.sort(key=lambda i: (i.resolved or "", i.id), reverse=True)

        # Build content
        lines = [
            "# Backlog",
            "",
            "Items not ready for full feature treatment. "
            "Managed via `/backlog` command or `scripts/backlog.py`.",
            "",
            "## Priority Scale",
            "",
            "| Priority | Meaning | When to use |",
            "|----------|---------|-------------|",
            "| 1 | Critical | Blocking work, fix ASAP |",
            "| 2 | High | Should address soon |",
            "| 3 | Medium | Address when convenient |",
            "| 4 | Low | Nice to have |",
            "| 5 | Someday | Might never do |",
            "",
            "## Item Types",
            "",
            "| Type | Prefix | Typical Resolution |",
            "|------|--------|-------------------|",
            "| Bug | `BUG-` | Fix with `/review-code`, update design |",
            "| Idea | `IDEA-` | Promote to FEATURES.md or dismiss |",
            "| Improvement | `IMP-` | Fix with `/review-code` or promote |",
            "| Tech Debt | `DEBT-` | Fix with `/review-code` |",
            "| Question | `Q-` | Resolve with `/decision` or dismiss |",
            "",
            "## Index",
            "",
            "<!-- Machine-readable index for quick queries. "
            "Keep sorted by status (open first), then priority. -->",
            "",
            "| ID | Pri | Title | Related | Status |",
            "|----|-----|-------|---------|--------|",
        ]

        # Add index rows
        for item in open_items + resolved_items:
            related_str = ", ".join(item.related) if item.related else "-"
            # Truncate title for index
            title = item.title[:50] + "..." if len(item.title) > 50 else item.title
            lines.append(
                f"| {item.id} | {item.priority} | {title} | {related_str} | {item.status} |"
            )

        lines.extend(
            [
                "",
                "## Open Items",
                "",
                "<!-- Detailed item descriptions. -->",
            ]
        )

        # Add open items
        if open_items:
            lines.append("")
            for item in open_items:
                lines.extend(self._format_item(item))
                lines.append("")

        lines.extend(
            [
                "## Resolved Items",
                "",
                "<!-- Resolved items for reference. -->",
            ]
        )

        # Add resolved items
        if resolved_items:
            lines.append("")
            for item in resolved_items:
                lines.extend(self._format_item(item))
                lines.append("")

        self.filepath.write_text("\n".join(lines))

    def _format_item(self, item: BacklogItem) -> list[str]:
        """Format a single item as markdown."""
        related_str = ", ".join(item.related) if item.related else "-"

        lines = [
            f"### {item.id}: {item.title}",
            f"- **Priority**: {item.priority}",
            f"- **Related**: {related_str}",
            f"- **Added**: {item.added}",
        ]

        if item.resolved:
            lines.append(f"- **Resolved**: {item.resolved}")

        if item.resolution:
            lines.append(f"- **Resolution**: {item.resolution}")

        if item.commit:
            lines.append(f"- **Commit**: {item.commit}")

        if item.notes:
            lines.append(f"- **Notes**: {item.notes}")

        return lines


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    # Find project root
    cwd = Path.cwd()
    project_root = cwd
    while project_root != project_root.parent:
        if (project_root / "docs" / "planning").exists():
            break
        project_root = project_root.parent
    else:
        print("Error: Could not find docs/planning/ directory")
        sys.exit(1)

    backlog_path = project_root / "docs" / "planning" / "BACKLOG.md"
    bm = BacklogManager(str(backlog_path))

    if command == "add":
        if len(sys.argv) < 4:
            print("Usage: backlog.py add <type> <title> [--priority N] [--related X,Y] [--notes '...']")
            print(f"\nTypes: {', '.join(TYPE_PREFIXES.keys())}")
            sys.exit(1)

        item_type = sys.argv[2]
        title = sys.argv[3]

        # Parse optional args
        priority = 3
        related: list[str] = []
        notes = None

        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                priority = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--related" and i + 1 < len(sys.argv):
                related = [r.strip() for r in sys.argv[i + 1].split(",")]
                i += 2
            elif sys.argv[i] == "--notes" and i + 1 < len(sys.argv):
                notes = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        try:
            item_id = bm.add(item_type, title, priority, related, notes)
            print(f"✓ Created {item_id}: {title}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "list":
        # Parse filters
        item_type = None
        priority_range = None
        related = None
        include_resolved = False

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                item_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                p_str = sys.argv[i + 1]
                if "-" in p_str:
                    parts = p_str.split("-")
                    priority_range = (int(parts[0]), int(parts[1]))
                else:
                    p = int(p_str)
                    priority_range = (p, p)
                i += 2
            elif sys.argv[i] == "--related" and i + 1 < len(sys.argv):
                related = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--all":
                include_resolved = True
                i += 1
            else:
                i += 1

        items = bm.list_items(item_type, priority_range, related, include_resolved)

        if not items:
            print("\nNo items found matching filters.")
        else:
            print(f"\nBacklog items ({len(items)}):\n")
            for item in items:
                related_str = f" [{', '.join(item.related)}]" if item.related else ""
                status_str = f" ({item.resolution})" if item.resolution else ""
                print(f"  [{item.priority}] {item.id}: {item.title}{related_str}{status_str}")

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: backlog.py show <ID>")
            sys.exit(1)

        item_id = sys.argv[2]
        item = bm.get(item_id)

        if not item:
            print(f"Error: Item not found: {item_id}")
            sys.exit(1)

        print(f"\n{item.id}: {item.title}")
        print(f"  Type: {item.type}")
        print(f"  Priority: {item.priority}")
        print(f"  Status: {item.status}")
        print(f"  Related: {', '.join(item.related) if item.related else '-'}")
        print(f"  Added: {item.added}")

        if item.resolved:
            print(f"  Resolved: {item.resolved}")

        if item.resolution:
            print(f"  Resolution: {item.resolution}")

        if item.commit:
            print(f"  Commit: {item.commit}")

        if item.notes:
            print(f"  Notes: {item.notes}")

    elif command == "check":
        if len(sys.argv) < 3:
            print("Usage: backlog.py check <title>")
            sys.exit(1)

        title = " ".join(sys.argv[2:])
        similar = bm.check_duplicates(title)

        if similar:
            print(f"\nPotential duplicates for '{title}':\n")
            for item in similar:
                print(f"  [{item.priority}] {item.id}: {item.title}")
        else:
            print(f"\nNo similar items found for '{title}'")

    elif command == "priority":
        if len(sys.argv) < 4:
            print("Usage: backlog.py priority <ID> <priority>")
            sys.exit(1)

        item_id = sys.argv[2]
        priority = int(sys.argv[3])

        try:
            bm.set_priority(item_id, priority)
            print(f"✓ Updated {item_id} priority to {priority}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "relate":
        if len(sys.argv) < 4:
            print("Usage: backlog.py relate <ID> <FEATURE-ID>")
            sys.exit(1)

        item_id = sys.argv[2]
        feature_id = sys.argv[3]

        try:
            bm.add_related(item_id, feature_id)
            print(f"✓ Added {feature_id} as related to {item_id}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "note":
        if len(sys.argv) < 4:
            print("Usage: backlog.py note <ID> <note>")
            sys.exit(1)

        item_id = sys.argv[2]
        note = " ".join(sys.argv[3:])

        try:
            bm.add_note(item_id, note)
            print(f"✓ Added note to {item_id}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "fix":
        if len(sys.argv) < 3:
            print("Usage: backlog.py fix <ID> [--commit <hash>]")
            sys.exit(1)

        item_id = sys.argv[2]
        commit = None

        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--commit" and i + 1 < len(sys.argv):
                commit = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        try:
            bm.resolve(item_id, "fixed", commit=commit)
            print(f"✓ Marked {item_id} as fixed")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "promote":
        if len(sys.argv) < 3:
            print("Usage: backlog.py promote <ID> [--feature <FEATURE-ID>]")
            sys.exit(1)

        item_id = sys.argv[2]
        feature_id = None

        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--feature" and i + 1 < len(sys.argv):
                feature_id = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        try:
            bm.resolve(item_id, "promoted", feature_id=feature_id)
            print(f"✓ Marked {item_id} as promoted")
            if feature_id:
                print(f"  → {feature_id}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "dismiss":
        if len(sys.argv) < 4:
            print("Usage: backlog.py dismiss <ID> <reason>")
            sys.exit(1)

        item_id = sys.argv[2]
        reason = " ".join(sys.argv[3:])

        try:
            bm.add_note(item_id, f"Dismissed: {reason}")
            bm.resolve(item_id, "dismissed")
            print(f"✓ Dismissed {item_id}: {reason}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "duplicate":
        if len(sys.argv) < 4:
            print("Usage: backlog.py duplicate <ID> <duplicate-of-ID>")
            sys.exit(1)

        item_id = sys.argv[2]
        duplicate_of = sys.argv[3]

        try:
            bm.resolve(item_id, "duplicate", duplicate_of=duplicate_of)
            print(f"✓ Marked {item_id} as duplicate of {duplicate_of}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
