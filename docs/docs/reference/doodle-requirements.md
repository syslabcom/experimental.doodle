---
myst:
  html_meta:
    "description": "Requirements for a Doodle-like Plone add-on"
    "property=og:description": "Requirements for a Doodle-like Plone add-on"
    "property=og:title": "Experimental Doodle Requirements"
    "keywords": "Plone, Doodle, scheduling, requirements"
---

# 📋 Doodle Requirements

This document captures the baseline requirements for replicating core Doodle functionality as a Plone add-on.
It also narrows those requirements into a realistic first implementation for the current repository scaffold.

## 🎯 Product goal

The add-on should allow Plone site editors and members to coordinate meetings without relying on long email threads.
The first target is to support the two central Doodle workflows:

- Group scheduling through polls with multiple date and time options.
- Personal booking through an availability page that others can use to reserve a slot.

For this repository, the immediate goal should be a simple Plone-native add-on that works well inside one site before adding advanced third-party integrations.

## 👥 Primary users

- Site editors who create and manage polls or booking pages.
- Participants who vote on proposed meeting times.
- Visitors, colleagues, students, or clients who book available time slots.
- Administrators who configure defaults, permissions, and calendar integration.

## ✅ Core functional requirements

### 🗳️ Group polls

- A user can create a poll with a title, description, organizer, and optional location.
- A poll can contain multiple proposed dates and time slots.
- Participants can open a public or shared link and vote for the slots that work for them.
- A participant can select one or more acceptable slots.
- The poll view shows aggregated availability so the organizer can identify the best option.
- The organizer can close the poll and mark one slot as the final decision.

### 📆 Booking pages

- A user can maintain a booking page that represents personal availability.
- A booking page can define working hours, meeting duration, buffer times, and unavailable periods.
- Visitors can book one of the available time slots directly.
- A booked slot becomes unavailable to avoid double booking.
- The organizer can review, confirm, or cancel bookings.

### 🔄 Calendar sync

- The add-on should support synchronization with existing calendars such as Google Calendar, Outlook, or iCloud.
- Existing calendar events should block availability in booking pages.
- Confirmed bookings and finalized poll decisions should be exportable or synchronizable to external calendars.

For a simple first release, calendar sync should be treated as a later phase unless an export-only approach is chosen first.

## 🧩 Plone-specific requirements

- The feature set must be delivered as a Plone add-on.
- Polls and booking pages should be manageable through Plone content or dedicated add-on views.
- Permissions should follow Plone roles so sites can control who may create, vote on, or manage schedules.
- Site managers should have a control panel to configure default behavior.
- The add-on should integrate cleanly with Plone navigation, security, and indexing.

### 🏗️ Recommended implementation baseline

According to the Plone documentation, custom business objects in an add-on are typically modeled as Dexterity content types, while add-on settings are managed through GenericSetup and registry-backed control panels.
For this repository, the simplest maintainable implementation path is:

- Create a Dexterity content type for a poll.
- Create a Dexterity content type for a booking page.
- Use the existing browser layer for add-on-specific views, forms, and overrides.
- Use the existing GenericSetup profile to register types, control panel entries, and catalog indexes.
- Store configurable defaults in the Plone registry and expose them through a control panel.

### 🧱 Suggested content model for the MVP

- Poll: title, description, organizer, state, and one or more proposed time slots.
- Booking Page: title, description, organizer, meeting rules, and availability rules.
- Booking or response records: stored in a way that supports validation, conflict checks, and later reporting.

For a simple implementation, the add-on should avoid a large object model and instead start with two main content types and minimal supporting records.

### 🔍 Catalog and indexing requirements

- Polls should be indexable by state, organizer, and relevant dates.
- Booking pages should be indexable by organizer and visibility.
- The data model should support looking up booked or chosen slots efficiently enough to prevent conflicts.

### 🧪 Development requirements for this repository

- The implementation should extend the existing install profile instead of bypassing it.
- New functionality should be covered by integration tests in the existing test layer.
- The first milestone should keep workflow and permissions simple enough to validate quickly.
- The MVP should work in classic Plone forms and views before broader UI refinement.

## 🔐 Non-functional requirements

- The UI should make scheduling possible with minimal back-and-forth communication.
- The add-on should prevent scheduling conflicts and double bookings.
- The add-on should be usable by students, businesses, and professional teams.
- The implementation should remain maintainable and extensible for future features such as reminders or notifications.
- The add-on should work with current supported Plone 6 versions.

For this repository, maintainability is more important than feature completeness in the first iteration.

## 🚀 Suggested first implementation scope

To keep the first iteration small, the initial release can focus on:

- Creating and publishing a `Poll` content item.
- Allowing participants to vote on proposed slots through a Plone view.
- Showing poll results with a clear winning option.
- Providing a basic `Booking Page` content item with manually defined availability.
- Reserving booked time slots to prevent overlap.
- Adding only the minimum catalog indexes and control panel settings needed for the MVP.

## 📝 Out of scope for the first iteration

- Advanced payment workflows.
- Complex meeting workflows with multiple hosts.
- Deep integrations with external conferencing platforms.
- Full two-way calendar synchronization.
- Full parity with every premium Doodle feature.

## 📌 Summary

The add-on should replicate the essential Doodle experience inside Plone: propose times, collect responses, expose availability, and prevent conflicts.
For this repository, the correct next step is to build a small, Plone-native MVP around Dexterity types, add-on views, registry settings, and tests.