## 2026-10-08 - Accessible Icon-Only Buttons
**Learning:** Icon-only buttons without accessible labels fail to convey their purpose to screen reader users and lack tooltips for visual users.
**Action:** Always add `aria-label` and `title` to the parent `<button>` and `aria-hidden="true"` to the child SVG/icon component to prevent redundant screen reader announcements.
