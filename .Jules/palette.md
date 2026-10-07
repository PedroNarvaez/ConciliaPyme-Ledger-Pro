## 2026-10-07 - Add accessibility labels to icon-only logout button
**Learning:** Found an icon-only button without an accessible name. For accessibility and usability, it is important to label icon-only buttons with `aria-label` and `title` to ensure they are readable by screen readers and have a tooltip on hover.
**Action:** Applied `title` and `aria-label` to the parent `<button>` element and set `aria-hidden="true"` on the child `<LogOut>` icon component. This prevents redundant or missing screen reader announcements.
