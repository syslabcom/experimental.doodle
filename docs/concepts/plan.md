# MVP Plan: Doodle Addon for Plone

A minimal Doodle-like addon for Plone with folderish and date content types, permissions, and a Bootstrap-styled doodle view with participant selection toggle.

---

## Completed MVP (All Tests Passing ✅)

### Content Types
- ✅ `experimental.doodle.folder` (folderish container type)
- ✅ `experimental.doodle.date` (date item with participants set field)

### Browser View & Interaction
- ✅ Doodle view renders sorted dates in a responsive table
- ✅ Participants displayed as Bootstrap badge pills
- ✅ Toggle button for current user participation (POST-based with CSRF protection)
- ✅ Participation redirect back to referrer or doodle view

### UI/Styling
- ✅ Bootstrap-compatible markup (card, table-striped, badge, btn-primary)
- ✅ Responsive layout with table-responsive wrapper
- ✅ Minimal custom CSS (badge flex-wrap, button nowrap)
- ✅ Bundle registration via csscompilation field (Plone 6.x pattern)

### Permissions & Access Control
- ✅ Custom add permissions for both types
- ✅ Browser layer registration active
- ✅ CSRF token validation on participation toggle
- ✅ Anonymous user rejection on toggle attempt

### Tests (15 Passed)
- ✅ 10 setup tests (install, uninstall, browser layer, permissions, type registration)
- ✅ 1 testing profile test
- ✅ 1 doodle view test (sorted dates rendering)
- ✅ 1 participation toggle test
- ✅ Code lint & quality (ruff, pyroma 10/10, zpretty, python-versions)

---

## Key Implementation Details

**Files:**
- `src/experimental/doodle/browser/doodle.pt` — Template with Bootstrap markup + tal:attributes for dynamic classes
- `src/experimental/doodle/browser/doodle.py` — View with rows() and date_label() methods
- `src/experimental/doodle/browser/participation.py` — ToggleParticipationView with CSRF check
- `src/experimental/doodle/browser/static/doodle.css` — Minimal responsive utilities
- `src/experimental/doodle/profiles/default/registry/main.xml` — Bundle registration

**Key Decisions:**
- Two separate types for structural clarity
- `participants` field as set of user IDs (not explicit selection field)
- POST-based toggle pattern for atomic updates
- Bootstrap-first styling aligned with Plone 6.x defaults
- explicit tal:attributes for class binding (not string interpolation)

---

## Next Atomic Steps (Post-MVP)

1. **Results/Summary View** — Display vote counts per date (new view method, optional aggregation UI)
2. **Control Panel** — Registry settings for participation notifications/preferences
3. **Catalog Indexing** — Add doodle-specific indexes for efficient queries (if scaling)
4. **Edge Case Tests** — Validate CSRF token reuse, anonymous rejection, data persistence
5. **Advanced Features** — Date filtering, search, results export

---

## Session Status
Session completed with all quality gates green. Ready for code review or feature expansion.
