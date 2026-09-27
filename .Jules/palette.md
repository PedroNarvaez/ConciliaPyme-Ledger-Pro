## 2024-05-18 - Header Controls Missing Accessible Labels
**Learning:** Icon-only buttons (like LogOut) and inline `<select>` components in the header navigation pattern lacked associated `<label>` elements or ARIA attributes, making them inaccessible to screen readers. Similarly, login inputs relied solely on placeholders.
**Action:** Always verify that header controls, `<select>` inputs without visible labels, and form inputs without labels have appropriate `aria-label` and/or `title` attributes implemented.
