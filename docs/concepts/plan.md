# MVP Plan: Doodle Addon for Plone

This document outlines the atomic steps for implementing a minimal Doodle-like addon for Plone, focusing on folderish and date content types, permissions, and a doodle-style view.

---

## Atomic Commit Steps

1. **Add schema interface for `experimental.doodle.folder`**
   - File: `src/experimental/doodle/interfaces.py`
2. **Implement `experimental.doodle.folder` content type**
   - File: `src/experimental/doodle/content/folder.py`
3. **Register `experimental.doodle.folder` in ZCML**
   - File: `src/experimental/doodle/configure.zcml`
4. **Add type info XML for folder**
   - File: `src/experimental/doodle/profiles/default/types/experimental.doodle.folder.xml`
5. **Add custom permissions for folder**
   - File: `src/experimental/doodle/permissions.zcml`
6. **Add schema interface for `experimental.doodle.date`**
   - File: `src/experimental/doodle/interfaces.py`
7. **Implement `experimental.doodle.date` content type**
   - File: `src/experimental/doodle/content/date.py`
8. **Register `experimental.doodle.date` in ZCML**
   - File: `src/experimental/doodle/configure.zcml`
9. **Add type info XML for date**
   - File: `src/experimental/doodle/profiles/default/types/experimental.doodle.date.xml`
10. **Add custom permissions for date**
    - File: `src/experimental/doodle/permissions.zcml`
11. **Implement user selection logic (`participants` field) in date type**
12. **Implement doodle-style browser view**
    - File: `src/experimental/doodle/browser/doodleview.py`
13. **Add tests for type creation and permissions**
14. **Update documentation**
    - Files: `README.md`, `docs/concepts/plan.md`

---

## Key Decisions
- Two types: `experimental.doodle.folder` (folderish), `experimental.doodle.date` (date, non-folderish)
- `participants` field for user selection
- Custom permissions for each type
- Doodle-style view for folder

---

## Verification
- Addon installs, both types available
- Permission separation works
- Dates can be added, users can select dates
- Doodle view displays sorted dates and user selections
- Tests and lint pass after each step
