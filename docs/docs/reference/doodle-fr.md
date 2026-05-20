---
myst:
  html_meta:
    "description": "Functional requirements for the Experimental Doodle add-on"
    "property=og:description": "Functional requirements for the Experimental Doodle add-on"
    "property=og:title": "Experimental Doodle Functional Requirements"
    "keywords": "Plone, Doodle, functional requirements, scheduling"
---

# ⚙️ Functional Requirements

This document defines the functional requirements for a Doodle-like scheduling add-on implemented in Plone.
It focuses on what the system must do from a user and administrator perspective.
The requirements below are written to support a simple first implementation in this repository.

## 🎯 Functional objective

The add-on must support scheduling workflows that reduce manual coordination.
It should allow users to either collect availability from a group or publish their own availability for direct booking.

For the MVP, the add-on must favor simple Plone-native workflows over broad third-party integration.

## 👤 User roles

- Organizer: creates and manages polls or booking pages.
- Participant: votes in polls.
- Booker: reserves an available slot on a booking page.
- Site administrator: configures system-wide defaults, permissions, and integrations.

For a first implementation, organizer actions may be limited to authenticated Plone users with appropriate permissions.

## 🗳️ Functional requirements for group polls

### 🧱 Poll creation

- FR-01: The system must provide a dedicated Plone content type for a poll or an equivalent add-on managed object with an add form.
- The system must allow an organizer to create a new poll.
- The system must allow the organizer to enter a title and description.
- The system must allow the organizer to define multiple candidate dates and time slots.
- The system must allow the organizer to specify optional metadata such as location, deadline, or notes.
- The system must allow the organizer to publish or close a poll.

### 🙋 Participation and voting

- The system must allow participants to access a poll through a shared link or Plone view.
- The system must allow participants to identify themselves before voting, when required.
- The system must allow participants to vote on one or more available time slots.
- The system must store each participant response.
- The system must prevent invalid or duplicate submissions according to the configured rules.

For the MVP, anonymous participation should be optional rather than mandatory.

### 📊 Poll results

- The system must aggregate votes per proposed slot.
- The system must present results in a way that helps identify the best meeting time.
- The system must allow the organizer to select a final slot.
- The system must display the final decision when a poll is concluded.

- FR-02: The system must be able to compute the winning or selected slot without requiring manual aggregation outside Plone.

## 📆 Functional requirements for booking pages

### 🛠️ Availability management

- FR-03: The system must provide a dedicated Plone content type for a booking page or an equivalent add-on managed object with an edit form.
- The system must allow an organizer to create a booking page.
- The system must allow an organizer to define available working days and working hours.
- The system must allow an organizer to configure meeting duration.
- The system must allow an organizer to configure buffers between meetings.
- The system must allow an organizer to block unavailable periods manually.

### 📥 Booking workflow

- The system must allow a visitor to view open appointment slots.
- The system must allow a visitor to select one available slot.
- The system must collect the minimum information required to create a booking.
- The system must create a booking record after successful submission.
- The system must mark the selected slot as unavailable after booking.
- The system must allow the organizer to confirm or cancel a booking.

- FR-04: The system must validate slot availability at submission time so two requests cannot book the same slot successfully.

## 🔄 Functional requirements for calendar integration

- The system must support connecting the organizer schedule with external calendars when integration is enabled.
- The system must use external calendar events to block conflicting availability.
- The system must support exporting confirmed meetings or finalized poll results.
- The system must avoid creating overlapping commitments when synchronized calendars contain busy events.

For the MVP, export of selected dates or bookings is sufficient. Full two-way synchronization should remain optional for a later phase.

## 🔐 Functional requirements for permissions and administration

- The system must respect Plone security and role-based permissions.
- The system must allow administrators to decide who can create polls.
- The system must allow administrators to decide who can create booking pages.
- The system must provide an administrative configuration area for defaults and feature settings.
- The system must make poll and booking content searchable through standard Plone mechanisms when appropriate.

- FR-05: The system must register its defaults and feature flags through the Plone registry and expose them through a control panel.
- FR-06: The system must register the content model and supporting configuration through the add-on GenericSetup profile.

## 📢 Functional requirements for notifications

- The system should notify organizers when new votes are submitted, if notifications are enabled.
- The system should notify organizers when a new booking is created.
- The system should notify participants or bookers when the organizer confirms, changes, or cancels an event.

Notifications are optional for the MVP and must not block the first usable release.

## 🌍 Functional requirements for usability

- The system must provide views that work on desktop and mobile devices.
- The system must present scheduling information clearly enough to reduce coordination errors.
- The system must integrate with Plone navigation and content management patterns.

- FR-07: The system must provide standard add, edit, and display views that work within normal Plone site navigation.

## 🚀 Minimum viable functional scope

The first release should include the following minimum functional set:

- Create a poll with multiple time slots.
- Vote on poll options.
- View aggregated poll results.
- Create a booking page with manually configured availability.
- Book a free slot and prevent double booking.

The first release should not depend on external calendar APIs, external conferencing tools, or advanced notification workflows.

## 🧪 Functional requirements for implementation readiness

- FR-08: The poll and booking page features must be testable through the existing Plone integration test layer.
- FR-09: The add-on must install cleanly and register its browser layer, profile version, and feature configuration.
- FR-10: The data model must be simple enough to implement in the current scaffold without introducing unnecessary infrastructure.

## 📌 Summary

The functional scope of the add-on is to support two primary scheduling models: poll-based coordination and direct booking.
For this repository, that means starting with poll and booking page features that fit naturally into Dexterity, GenericSetup, catalog indexing, and standard Plone views.