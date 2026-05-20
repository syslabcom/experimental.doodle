---
myst:
  html_meta:
    "description": "How to vote on a poll and read the results in experimental.doodle"
    "property=og:description": "How to vote on a poll and read the results"
    "property=og:title": "Vote on a poll"
    "keywords": "Plone, experimental.doodle, poll, vote, results"
---

# Vote on a poll

This guide explains how a visitor casts a vote on a published Poll and
reads the aggregated results.

## Prerequisites

- A Plone site with `experimental.doodle` installed.
- At least one published Poll with two or more time slots.

## Cast a vote

1. Open the Poll in your browser. The default view shows the vote form.
2. Enter your name in the **Your name** field. Any non-empty string is
   accepted; no account is needed.
3. For each proposed time slot, select **Yes** or **No**. Every slot
   defaults to **No** when the page loads.
4. Click **Cast vote**. The page reloads and confirms your vote was
   recorded. You can vote again at any time. Casting a second vote with
   the same name replaces your earlier response.

## Read the results

Click **View results** below the vote form, or navigate to the Poll's
`@@results` view directly (append `/@@results` to the Poll address). The
results page shows:

- A table with each time slot and the number of **Yes** votes it received.
- A proportional bar for each slot so you can see relative support at a
  glance.
- A list of participants who have voted.

Click **Back to poll** to return to the vote form.

## Create a poll (for editors)

1. Navigate to the folder where you want to create the poll.
2. Add a new **Poll** content item.
3. Enter a **title** and, optionally, a **description**.
4. Add at least two **time slots** using the date/time picker for each
   entry in the **Proposed time slots** field.
5. Save the item and publish it so visitors can reach it without logging
   in.

## Related references

- {doc}`/reference/poll-content-type`: the Poll schema and FTI details.
- {doc}`/reference/vote-storage`: the Python API behind the vote form.
