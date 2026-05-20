---
myst:
  html_meta:
    "description": "Reference for the Poll browser views in experimental.doodle"
    "property=og:description": "Reference for the Poll browser views"
    "property=og:title": "Poll views"
    "keywords": "Plone, experimental.doodle, poll, view, results, browser"
---

# Poll views

`experimental.doodle` ships two browser views for `Poll` objects, both
registered against `IPoll` on `IBrowserLayer`.

## Vote form (`@@poll_view`)

**Class:** `experimental.doodle.browser.poll.PollView`
**Permission:** `zope2.View` (no login required)
**Default view:** yes (`default_view` on the FTI since profile version `1002`)

The vote form renders the poll title, description, and a `<form>` with:

- a text field for the participant's name;
- one `yes`/`no` radio pair per proposed time slot;
- a submit button.

### Form submission

On submit the view:

1. Strips the `name` field; returns a form error if the result is empty.
2. Reads `votes_0`, `votes_1`, … from the request; absent values default
   to `"false"`.
3. Calls `IVoteStorage(context).cast_vote(name, votes)`.
4. Redirects to `@@poll_view` (Post/Redirect/Get pattern).

Any `ValueError` from `cast_vote` is caught and shown as an inline error
without a redirect.

### Template helpers

| Property | Returns |
|---|---|
| `options` | `[(index, label), ...]` where `label` is a human-readable date/time string. |
| `error` | The current error string, or `None`. |
| `participant_count` | Number of participants who have already voted. |

## Results (`@@results`)

**Class:** `experimental.doodle.browser.poll.PollResultsView`
**Permission:** `zope2.View`

The results view shows the aggregated tally and a participant list. It
is read-only; there is no form or POST handling.

### Template helpers

| Property | Returns |
|---|---|
| `rows` | `[(label, yes_count, max_count), ...]`, one row per slot. `max_count` is the highest yes-count across all slots, used to compute proportional bar widths. |
| `participants` | `list[str]`, participant names sorted alphabetically. |

A `@@results` link appears on the vote form. A "Back to poll" link
returns to `@@poll_view` from the results.

## Styles

Both views include `++plone++experimental.doodle/poll.css` from
`src/experimental/doodle/browser/static/`. The stylesheet covers only
poll-specific elements and makes no global overrides.

## Profile version

The FTI change (`default_view` set to `poll_view`, `results` added to
`view_methods`) ships at profile version `1002`. Sites on `1001` can
upgrade through the {guilabel}`Add-ons` control panel or
programmatically:

```python
from plone import api

api.portal.get_tool("portal_setup").upgradeProfile(
    "experimental.doodle:default"
)
```

## Related

- {doc}`vote-storage`: the adapter the views delegate to.
- {doc}`poll-content-type`: the content type the views render.
- {doc}`/how-to-guides/vote-on-a-poll`: step-by-step voting guide.
