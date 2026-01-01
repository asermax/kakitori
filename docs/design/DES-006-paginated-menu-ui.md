# DES-006: Two-Level Paginated Menu UI

**Scope**: Project-wide
**Date**: 2026-01-01
**Last Updated**: 2026-01-01

## Pattern

For interactive selection from large datasets, use a two-level menu:
1. **Main menu**: Shows aggregated items (e.g., speakers, categories)
2. **Detail menu**: Shows paginated items within selection (e.g., segments)

## Rationale

Single flat lists become unusable with 100+ items. Two-level structure:
- Main menu provides overview and quick navigation
- Detail menu provides pagination for deep exploration
- Users can jump between items without scrolling through everything

## Examples

### Do This

```python
ITEMS_PER_PAGE = 10

def show_main_menu(items: list[ItemGroup]) -> str | None:
    """Display summary of all groups, return selected group ID."""
    display_summary_table(items)

    choices = [Choice(title=item.name, value=item.id) for item in items]
    choices.append(Separator())
    choices.append(Choice("Confirm", value="confirm"))

    return questionary.select("Select item:", choices=choices).ask()


def show_detail_menu(item: ItemGroup, all_data: list) -> str | None:
    """Paginated view of items within group."""
    page = 0

    while True:
        page_items, total_pages = display_page(item, all_data, page)

        choices = [
            Choice("View item (enter number)", value="view"),
            Separator(),
        ]

        if page < total_pages - 1:
            choices.append(Choice("Next page →", value="next"))
        if page > 0:
            choices.append(Choice("← Previous page", value="prev"))

        choices.append(Separator())
        choices.append(Choice("Back to main menu", value="back"))

        result = questionary.select("Action:", choices=choices).ask()

        if result == "next":
            page += 1
        elif result == "prev":
            page -= 1
        elif result == "back":
            return None
        # ... handle other actions


# Main loop
while True:
    selection = show_main_menu(groups)
    if selection == "confirm":
        break
    if selection:
        show_detail_menu(groups[selection], all_data)
```

**Why**: 3 speakers with 100 segments each is navigable (3 items → 10 pages). A flat list of 300 items is not.

### Don't Do This

```python
def show_all_items(items: list):
    """Single flat menu with all items."""
    choices = [Choice(title=item.name, value=item.id) for item in items]
    return questionary.select("Select:", choices=choices).ask()
```

**Why**: 300+ choices in a single menu is unusable. Users can't find what they need.

## Exceptions

- Small datasets (< 20 items) can use single-level menus
- Tree structures may need more than two levels
- Search-based interfaces may eliminate pagination need

---

## Evolution

### Version 1 (2026-01-01)

Initial pattern established from PROCESS-001 retrofit (speaker identification UI).

---

## Related

- Promoted from: [../designs/PROCESS-001.md](../designs/PROCESS-001.md)
- Applied in: `src/kakitori/process/speaker.py`
