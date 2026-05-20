---
myst:
  html_meta:
    "description": "Step-by-step planning for building the Experimental Doodle Plone add-on"
    "property=og:description": "Step-by-step planning for building the Experimental Doodle Plone add-on"
    "property=og:title": "Experimental Doodle Development Planning"
    "keywords": "Plone, Doodle, planning, addon development, UI"
---

# 🛠️ Doodle Development Planning

This document is a step-by-step implementation plan for building a simple Doodle-like scheduling add-on for Plone.
It is written to match the current repository scaffold and to help a developer move from a fresh add-on skeleton to a usable feature set at `http://localhost:8080/Plone`.

## 🎯 Planning goal

The goal is to build a small but usable Plone add-on that supports:

- Poll-based scheduling.
- Simple personal booking pages.
- A basic user interface in Plone Classic UI.
- Clean installation in a local development site.

The first implementation should favor maintainability and fast feedback over full feature parity with Doodle.

## 🧭 Development guidelines for Plone add-ons

According to the Plone documentation, a maintainable add-on should follow the standard Plone extension model.
For this project, that means:

- Model business objects as Dexterity content types.
- Keep add-on setup in GenericSetup profiles under `profiles/default`.
- Use the Plone registry and a control panel for configurable defaults.
- Register add-on-specific views against the existing browser layer.
- Keep UI logic in browser views and keep page templates simple.
- Use behaviors for reusable field groups or reusable business logic.
- Add only the catalog indexes and metadata columns that are required.
- Cover features with integration tests in the existing test layer.
- Keep the first release independent from large external integrations.

## 🧱 Target architecture for this add-on

The recommended first architecture is:

- `Poll` as a Dexterity content type.
- `Booking Page` as a Dexterity content type.
- One or more browser views for voting, booking, and results.
- Registry settings for defaults such as slot duration, whether anonymous voting is allowed, and basic booking behavior.
- Catalog indexes for looking up polls, booking pages, and selected states efficiently.

For the MVP, avoid a large data model. Start with two main content types and the minimum supporting data needed for votes and bookings.

## 🚀 Step 1: Prepare the local environment

Use the repository-provided commands instead of ad hoc setup.

### ✅ Tasks

- Install the development environment with `make install`.
- Start Plone with `make start`.
- Create the site with `make create-site` if the `Plone` site does not already exist.
- Confirm that the site is reachable at `http://localhost:8080/Plone`.

### 📌 Expected result

- The Plone instance starts locally.
- The `Plone` site exists.
- The add-on profile is applied by the site creation script.

## 🔍 Step 2: Verify the current add-on baseline

Before adding new features, verify the existing scaffold.

### ✅ Tasks

- Confirm the install profile version in `profiles/default/metadata.xml`.
- Confirm the browser layer registration in `profiles/default/browserlayer.xml`.
- Confirm that the add-on install test passes.
- Run `make test` to establish the current baseline.

### 📌 Expected result

- The package installs cleanly.
- The browser layer is active after installation.
- Existing tests pass before feature work begins.

## 🧩 Step 3: Define the MVP content model

According to the Plone documentation, custom business data should be modeled with Dexterity content types and behaviors where appropriate.

### ✅ Tasks

- Define a `Poll` content type.
- Define a `Booking Page` content type.
- Decide whether votes and bookings will be stored as child content items, annotations, or serialized structured fields.
- Keep the storage model simple enough to implement and test quickly.

### 📋 Recommended MVP fields

For `Poll`:

- Title.
- Description.
- Organizer reference or creator ownership.
- Poll state.
- Deadline.
- Optional location.
- Proposed slots.
- Final selected slot.

For `Booking Page`:

- Title.
- Description.
- Organizer reference or creator ownership.
- Working days.
- Working hours.
- Slot duration.
- Buffer duration.
- Availability exceptions.
- Booking state.

### 📌 Expected result

- A developer can point to a concrete schema for each type.
- The model is small enough to support a first usable release.

## 🏗️ Step 4: Generate or add the content types

According to the Plone documentation, content types are commonly added with PloneCLI and registered through the add-on package.

### ✅ Tasks

- Add a `Poll` content type.
- Add a `Booking Page` content type.
- Review the generated FTI and schema files.
- Register the new types in `profiles/default/types.xml`.
- Update `profiles/default/types/` with the correct FTI definitions.

### 📝 Developer notes

- Use `Container` only if a type truly needs to contain child objects.
- Use `Item` if the type is a standalone object without child content.
- For the MVP, a `Poll` may be an `Item` if slots are stored in fields rather than child items.
- A `Booking Page` can also start as an `Item` unless child booking objects are required immediately.

### 📌 Expected result

- The new content types appear in the site after reinstalling or reapplying the profile.

## 🧠 Step 5: Add behaviors only where they reduce complexity

According to the Plone documentation, behaviors are best used for reusable fields or reusable logic.

### ✅ Tasks

- Reuse built-in behaviors where they make sense, such as title, description, or rich text.
- Add custom behaviors only if the same scheduling fields or logic are shared across multiple types.
- Avoid creating behaviors too early if plain schemas are simpler.

### 📌 Expected result

- The data model stays readable.
- Reuse happens only where it has clear value.

## ⚙️ Step 6: Add registry settings and a control panel

The repository already includes control panel scaffolding, so the next step is to make it useful.

### ✅ Tasks

- Define registry records for add-on defaults.
- Add a control panel form for site managers.
- Register the control panel entry through the install profile.

### 📋 Recommended first settings

- Default poll slot duration.
- Default booking slot duration.
- Whether anonymous poll voting is enabled.
- Whether booking confirmation is required.
- Default timezone handling.

### 📌 Expected result

- Site managers can manage add-on defaults from Plone Site Setup.

## 🧮 Step 7: Implement scheduling logic in Python

The first implementation needs reliable backend rules before UI refinement.

### ✅ Tasks

- Add helper methods to normalize date and time slot data.
- Add vote aggregation logic for polls.
- Add conflict detection logic for bookings.
- Validate availability at submission time.
- Keep domain logic out of page templates.

### 📋 Core rules

- A poll vote must be stored only once per participant according to the selected policy.
- A booking must fail if the requested slot is no longer available.
- A closed poll must reject further votes.
- A disabled or closed booking page must reject new bookings.

### 📌 Expected result

- The backend can decide whether a vote or booking is valid.
- Core business behavior is testable without relying on UI details.

## 🖥️ Step 8: Build the Plone UI in Classic UI

According to the Plone documentation, the usual pattern is to implement browser views and templates, register them in ZCML, and keep heavy logic in Python.

### ✅ Tasks

- Create a poll display view.
- Create a vote submission view or form.
- Create a results view.
- Create a booking page view that lists available slots.
- Create a booking submission view or form.
- Register these views against the add-on browser layer.

### 🎨 UI guidelines

- Keep templates simple and driven by view methods.
- Use normal Plone page templates and the main template macros.
- Keep forms understandable with clear labels and messages.
- Make the scheduling workflow obvious on mobile and desktop.
- Avoid overriding core templates until the custom views are working.

### 🧩 Static resources

- Add CSS and JavaScript only when the base form behavior is working.
- Keep UI enhancements modest for the MVP.
- Use the existing `browser/static` location for add-on assets.

### 🛠️ When to use overrides

- Use `browser/overrides` with `z3c.jbot` only when a core or third-party template really must be customized.
- Prefer custom views over broad template overrides.

### 📌 Expected result

- A user can browse to a poll or booking page and complete the main action from the Plone UI.

## 🔐 Step 9: Define permissions and access rules

The add-on must be usable inside a normal Plone site without weakening security.

### ✅ Tasks

- Decide who can add polls.
- Decide who can add booking pages.
- Decide whether anonymous voting is allowed.
- Decide whether anonymous booking is allowed.
- Register any custom permissions only if built-in permissions are insufficient.

### 📌 Recommended MVP policy

- Authenticated users create polls and booking pages.
- Poll viewing can be public if the content is published.
- Anonymous voting can be optional and controlled by a site setting.
- Booking can start as authenticated-only if that reduces complexity.

### 📌 Expected result

- Access behavior is predictable and testable.

## 🔎 Step 10: Add catalog indexing only for real use cases

The current profile already has catalog scaffolding, so add only the indexes needed for feature support.

### ✅ Tasks

- Add indexes or metadata columns for poll state.
- Add indexes or metadata columns for organizer.
- Add any booking-related metadata needed for efficient lookup.
- Reindex after profile updates.

### 📌 Expected result

- Polls and booking pages can be queried efficiently.
- Future listing or dashboard views remain straightforward.

## 🧪 Step 11: Write tests as features are added

The current repository already contains integration test scaffolding and install tests.

### ✅ Tasks

- Add tests for type registration.
- Add tests for control panel registration.
- Add tests for poll creation.
- Add tests for vote submission.
- Add tests for vote aggregation.
- Add tests for booking availability checks.
- Add tests for double-booking prevention.
- Add tests for permission-sensitive workflows.

### 📌 Expected result

- The add-on can evolve without breaking core scheduling behavior.

## 🔁 Step 12: Keep the install profile up to date

Every new feature must be represented in GenericSetup so a site can be recreated consistently.

### ✅ Tasks

- Update `types.xml` and type FTIs.
- Update registry import files.
- Update `controlpanel.xml`.
- Update `catalog.xml` if indexes are added.
- Add upgrade steps when profile changes become versioned milestones.

### 📌 Expected result

- Installing or upgrading the add-on remains predictable.

## 🌐 Step 13: Make the add-on usable at `http://localhost:8080/Plone`

The local site should be the primary feedback loop during development.

### ✅ Tasks

- Start the instance with `make start`.
- Ensure the site exists with `make create-site`.
- Log in to `http://localhost:8080/Plone`.
- Confirm the add-on is installed in the site.
- Add a `Poll` item and verify that its add and display views work.
- Add a `Booking Page` item and verify that booking works.

### 📌 Developer workflow

- Use the browser to verify each newly added content type and view.
- Reapply the add-on profile or recreate the site when GenericSetup changes require it.
- Keep test execution and browser verification in sync.

### 📌 Expected result

- The add-on is visible and usable in your local Plone site.

## 📅 Suggested implementation order

Build in this order to reduce risk:

1. Environment and baseline validation.
2. `Poll` type and poll schema.
3. Poll add, display, vote, and results views.
4. Poll tests.
5. `Booking Page` type and booking schema.
6. Booking availability and conflict logic.
7. Booking UI and tests.
8. Registry settings and control panel.
9. Catalog indexing and listing views.
10. Nice-to-have UI improvements.

## 🚫 What not to do in the first iteration

Avoid these until the MVP works:

- Full two-way calendar synchronization.
- External conferencing integration.
- Complicated reminder workflows.
- Too many custom behaviors.
- Heavy template overrides before custom views exist.
- Premature optimization of indexing or storage.

## ✅ Definition of done for the first milestone

The first milestone is complete when:

- The add-on installs cleanly.
- `Poll` and `Booking Page` are available in Plone.
- A user can create a poll and collect votes.
- A user can create a booking page and accept a simple booking.
- Double booking is prevented.
- Basic settings exist in a control panel.
- Tests cover the main flows.
- The feature works in the local site at `http://localhost:8080/Plone`.

## 📌 Summary

The correct path for this repository is to build a small Plone-native scheduling product in layers: content model first, backend rules second, UI third, and refinements after tests are in place.
That will keep the add-on installable, testable, and usable in your local Plone environment while leaving room for deeper Doodle-like features later.