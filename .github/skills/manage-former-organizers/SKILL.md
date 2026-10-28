---
name: manage-former-organizers
description: "Manage former organizers in wrocnet.org. Use when adding or updating entries in _data/former_organizers.yml, including portraits needed for those entries."
---

# Managing Former Organizers

Use this procedure for the former organizers list, not for unrelated organizer or speaker portraits.

## 1. Prepare the Photo
- Follow the shared [profile photo and missing-photo rules](../../../AGENTS.md#known-pitfalls).
- Reuse the person's existing local portrait when available.

## 2. Update Data File
Edit [_data/former_organizers.yml](../../../_data/former_organizers.yml).

### Entry Format:
```yaml
- name: "Jan Kowalski"
  photo: "/assets/images/organizers/jan-kowalski.jpg"
  linkedin: "https://www.linkedin.com/in/jankowalski/" # Optional
```

### Sorting Rule:
Entries **MUST** be sorted alphabetically by **surname**.

## 3. Validation
- Run the standard [YAML lint, strict build and HTML/image checks](../../../README.md#ci-validation-checks-local).
- Verify the alphabetical order.
- Check the person's name, portrait and optional LinkedIn link on the [organizers page](../../../_pages/organizatorzy.md).
