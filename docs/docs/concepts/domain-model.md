---
myst:
  html_meta:
    "description": "The Doodle-style domain model used by experimental.doodle"
    "property=og:description": "The Doodle-style domain model used by experimental.doodle"
    "property=og:title": "Domain model"
    "keywords": "Plone, Experimental Doodle, domain, model, poll, vote"
---

# Domain model

`experimental.doodle` provides a Doodle-style service to find the best time
for an appointment among several people. This page explains the building
blocks of that model.

## Poll

A **Poll** is the central object. It represents one scheduling question
("Lunch this week, when?") and carries:

- a **title** and an optional **description**, both provided by the
  standard Plone Dublin Core behavior;
- a list of **proposed time slots**: at least two date/time options that
  participants can vote on.

A Poll is a leaf content type and holds no sub-content. The Poll stores
its own voting data directly, rather than relying on separate content
objects.

## Options

The **options** form an ordered list of timezone-aware date/time values.
The order matters: each vote refers to options by their position in this
list. Editing or reordering options after participants have voted will
therefore break existing votes. Treat options as fixed once you share the
poll with participants.

The current version enforces a minimum of two options at the schema level.
A single-option poll isn't a poll.

## Participants and votes

A **participant** identifies themselves with a free-text name. Voting
requires no Plone account, which matches how Doodle itself works: you
share a poll by link, and anyone with the link can respond.

A **vote** is one participant's response to a poll. It contains a `yes` or
`no` choice for each option. The current version intentionally omits a
`maybe` value.

Votes are stored through the {doc}`vote-storage adapter
</reference/vote-storage>`, an annotation-backed Python API on each Poll.
HTTP endpoints and a vote form arrive in later steps.

## Tally

The **tally** is the aggregated result of all votes: for each option, the
number of `yes` responses. The package computes it on demand from the
stored votes and doesn't persist it.

## Why these choices

- A single Dexterity content type keeps the data flat and easy to reason
  about. There are no per-option or per-vote objects polluting the catalog.
- Votes live as annotations on the Poll because they belong to that poll
  and have no independent lifecycle.
- Free-text participant names match Doodle's actual product behavior and
  keep the current version usable without authentication infrastructure.
