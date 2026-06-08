# Progress — `.agent/PROGRESS.md`

A single-page checklist of the project's features. Shipped, in progress, planned.
This is the project tracker. Keep it tiny.

## Format

```markdown
---
last_updated: 2026-05-23
---

# Project Progress

## Shipped
- [x] User auth (2026-04-12)
- [x] Dashboard skeleton (2026-04-28)
- [x] Email notifications (2026-05-02)

## In progress
- [ ] OTP login → task: add-otp-login
- [ ] Billing webhooks → task: stripe-webhooks

## Planned
- [ ] Team workspaces
- [ ] Mobile app
- [ ] Audit log

## Archive
<details>
<summary>Older shipped (collapsed)</summary>

- [x] Initial scaffold (2026-03-10)
- [x] Database schema v1 (2026-03-15)
</details>
```

## Hard limits (skill-enforced)

| Section | Max | Rule |
|---|---|---|
| Whole file | ~80 visible lines | older Shipped collapses into Archive |
| Per item | 1 line | a bullet, not a paragraph |
| In progress | 5 items | more than 5 = too much WIP, push to Planned |

## Rules

1. **New feature introduced** → append to `## Planned` or `## In progress`.
   Link to the task slug if a task file exists.
2. **Task started** → move the item from Planned to In progress (if it was Planned).
3. **Task completed** → check the box, add `(YYYY-MM-DD)` ship date, move to Shipped.
4. **Closing a task without updating PROGRESS** → blocked by the self-review gate.
5. **Bump `last_updated` in frontmatter** on every change.
6. **Older Shipped items** roll into the `## Archive` `<details>` block once
   `## Shipped` has more than 15 items.

## What belongs as a "feature"

- A user-facing capability ("Add OTP login")
- A meaningful internal capability ("Migrate to Postgres", "Add CI pipeline")
- Anything you'd mention in a changelog

What does NOT belong:
- Individual bug fixes (those live in commits)
- Refactors with no user/operator impact
- Sub-tasks of a feature (those go in the task's Checklist)

If you're not sure: would a stakeholder ask "is this done?" — if yes, it's a feature.

## Cross-link with tasks

When a feature has a task file, use the link syntax:

```
- [ ] OTP login → task: add-otp-login
```

The preview dashboard will render this as a clickable link to the task pane.

## Anti-patterns

- Don't write paragraphs in Progress; that's MEMORY's job
- Don't track every commit; that's git's job
- Don't let In progress exceed 5 items
- Don't list "Plan the X" as a feature; planning isn't a deliverable
