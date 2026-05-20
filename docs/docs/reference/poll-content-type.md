---
myst:
  html_meta:
    "description": "Reference for the Poll Dexterity content type"
    "property=og:description": "Reference for the Poll Dexterity content type"
    "property=og:title": "Poll content type"
    "keywords": "Plone, Dexterity, Poll, content type, experimental.doodle"
---

# `Poll` content type

The `Poll` Dexterity content type represents a single Doodle-style poll.
The `experimental.doodle:default` GenericSetup profile registers it, and
the type is globally addable to any folderish container.

## Schema

The module `experimental.doodle.content.poll` defines the `IPoll` schema.

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | `TextLine` (via `plone.dublincore`) | yes | Inherited from the standard Dublin Core behavior. |
| `description` | `Text` (via `plone.dublincore`) | no | Inherited from the standard Dublin Core behavior. |
| `options` | `List(value_type=Datetime)` | yes | Proposed time slots. A schema invariant enforces a minimum of two entries. |

The `options` field uses `defaultFactory=list` so each new Poll instance
starts with a fresh empty list rather than a shared mutable default. The
"at least two options" rule lives in a schema invariant rather than the
field's `min_length`, so the add form can render with an empty list and
only complains on submit.

## Factory type information

The package ships the Factory Type Information (FTI) at
`src/experimental/doodle/profiles/default/types/Poll.xml`.

Key properties:

- **`klass`**: `experimental.doodle.content.poll.Poll`
- **`schema`**: `experimental.doodle.content.poll.IPoll`
- **`factory`**: `Poll`
- **`add_permission`**: `cmf.AddPortalContent`
- **`global_allow`**: `True`
- **`filter_content_types`**: `True` with an empty `allowed_content_types`
  list. A Poll is a leaf and can't contain other content.
- **`default_view`** and **`immediate_view`**: `view` (the standard
  Dexterity default view; a dedicated view ships in a later step).

### Enabled behaviors

- `plone.dublincore`: title, description, dates, language, and related metadata.
- `plone.namefromtitle`: derives the id from the title.
- `plone.shortname`: supports manual override of the id when needed.
- `plone.ownership`: tracks creator and contributors.

## Creating a poll programmatically

```python
from datetime import datetime, timedelta, timezone
from plone import api


def create_lunch_poll(container):
    now = datetime.now(tz=timezone.utc)
    return api.content.create(
        container=container,
        type="Poll",
        title="Team lunch",
        description="When can everyone make it?",
        options=[
            now + timedelta(days=1, hours=12),
            now + timedelta(days=1, hours=13),
            now + timedelta(days=2, hours=12),
        ],
    )
```

The `options` list must contain at least two date/time values. Otherwise,
schema validation raises `zope.interface.Invalid`.

## Creating a poll through `plone.restapi`

```http
POST /plone/@@plone.restapi.services HTTP/1.1
Content-Type: application/json
Accept: application/json

{
    "@type": "Poll",
    "title": "Team lunch",
    "description": "When can everyone make it?",
    "options": [
        "2026-06-01T12:00:00+00:00",
        "2026-06-01T13:00:00+00:00",
        "2026-06-02T12:00:00+00:00"
    ]
}
```

`plone.restapi` handles the standard create endpoint via `POST` on the
container address with `@type: "Poll"`.

## Validation

Schema-level constraints enforced today:

- The `options` field is **mandatory**.
- Every element of `options` must be a `datetime`.
- The schema invariant `at_least_two_options` rejects a submission whose
  `options` list has fewer than two entries. The invariant runs on form
  submit, not on widget render, so the add form opens cleanly.

Other rules, for example forbidding past date/time values, removing
duplicate slots, or restricting how options can change after votes exist,
are intentionally out of scope for the current version. Follow-up steps
will address them.

## Upgrading existing sites

The `experimental.doodle:default` profile registers the `Poll` FTI at
version `1001`. Sites installed with profile version `1000` can upgrade in
place:

1. Open the Plone control panel.
2. Go to {guilabel}`Add-ons` and run the available upgrade step for
   `experimental.doodle` ("Install Poll content type").

You can run the same step programmatically:

```python
from plone import api

setup_tool = api.portal.get_tool("portal_setup")
setup_tool.upgradeProfile("experimental.doodle:default")
```

The upgrade handler lives at
`experimental.doodle.upgrades.v1001.install_poll_type` and re-imports the
GenericSetup `typeinfo` step. The step is idempotent: it's safe to run on
sites that already have the `Poll` FTI.

## Related concepts

- {doc}`/concepts/domain-model`: the overall Doodle-style domain.
