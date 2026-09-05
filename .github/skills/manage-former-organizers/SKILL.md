---
name: manage-former-organizers
description: "How to add and manage former organizers in the wrocnet.org project. Use when adding entries to _data/former_organizers.yml or organizer photos in assets/images/organizers/."
---

# Managing Former Organizers

This skill explains how to add new entries to the former organizers list.

## 1. Prepare the Photo
- **Source**: Obtain the photo (e.g., from LinkedIn).
- **Format**: Save it in `assets/images/organizers/` using a slugified name (e.g., `jan-kowalski.jpg`).
- **Processing**: Use `sips -Z 400 <path>` to resize it to 400px width/height.
- **Rules**: Do not use external URLs. All photos must be local assets.

## 2. Update Data File
Edit `_data/former_organizers.yml`.

### Entry Format:
```yaml
- name: "Jan Kowalski"
  photo: "/assets/images/organizers/jan-kowalski.jpg"
  linkedin: "https://www.linkedin.com/in/jankowalski/" # Optional
```

### Sorting Rule:
Entries **MUST** be sorted alphabetically by **surname**.

## 3. Validation
- Run `bundle exec jekyll build` (if available) to ensure front matter is valid.
- Verify the alphabetical order.
