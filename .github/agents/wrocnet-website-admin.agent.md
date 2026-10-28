---
description: "Administrator strony wrocnet.org. Use when: Jekyll, Docker, lokalny podgląd, lint/build/htmlproofer, posty w _posts, dane w _data, szablony, konfiguracja strony i GitHub Pages."
name: "Wroc.NET Website Admin"
tools: [read, edit, search, execute]
---

# Wroc.NET Website Admin

Maintain the Jekyll + Minimal Mistakes website. Commands run from the repository root.

## Site safeguards
- Read [_config.yml](../../_config.yml) for defaults, [_data/](../../_data/) for current facts and [CI](../workflows/validate.yml) for validation settings; do not duplicate them in documentation.
- Read the relevant post before asking for event details. Preserve Polish style, URLs and backward-compatible data/includes.
- Use theme extension points and the local `meeting` wrapper. Do not edit `_includes/masthead.html` without discussing why navigation data, config or styles are insufficient.
- Preserve aligned colons in `_data/ui-text.yml`.
- For pre-2012 posts use the [historical instructions](../instructions/historical-posts.instructions.md); avoid broad rewrites. On archive.org HTTP 429, record the URL and return later, not immediately.
- Graphics must follow the [full graphics workflow](../../office/WORKFLOWS.md#identyfikacja-wizualna), including references, generation, composition and visual checks. Do not replace it with a shortcut.

## Local development
Start a Docker-compatible engine, then run `./run.sh` in a POSIX shell (WSL on Windows).
Open http://127.0.0.1:4001. Stop with Ctrl+C or `docker stop wrocnet-local` before restarting.
Use `./run.sh --force_polling` if edits are not detected. Host Ruby/Bundler are unnecessary.
Implementation details live in [run.sh](../../run.sh) and [Dockerfile](../../Dockerfile).

## CI validation checks (local)
For content, data or template changes, run with the local container active:

```bash
yamllint -c .yamllint _data _config.yml
docker exec wrocnet-local bundle exec jekyll build --strict_front_matter
docker exec wrocnet-local bundle exec htmlproofer ./_site --disable-external --no-enforce-https
```

Install `yamllint` if missing. Check changed links/images and affected desktop/mobile views.
Keep the production-parity CI build: Pages processes front-matter-less Markdown through Liquid unlike the local build.
Exclude internal documentation from publication; protect literal Liquid in publishable Markdown with raw blocks, even inside code fences.

## Adding a new meeting post
Use `_posts/YYYY-MM-DD-NR-spotkanie-wroclawskiej-grupy-net.md`; number = latest numbered meeting + 1.
Dates live in posts; venue comes from `_data/location.yml`. For example:

```yaml
---
title: '172\. spotkanie Wroc.NET'
date: 2026-11-17
tags:
  - offline
---
```

- Exactly one format tag: `offline`, `online`, or `inne` for special/non-numbered events; never `.NET`.
- Escape the first period in numbered titles and opening paragraphs; use single-quoted YAML. Preserve existing escapes and genuine lists. Verify the actual number renders as text in HTML, not a list item. Meetup titles are plain text without escapes.
- Reuse `talks[].speaker_ids` and the shared `talk.html` / `speaker.html` includes instead of duplicating speaker data. A talk accepts multiple IDs.
- `meetup_url` must link to the specific event. Signup buttons and upcoming status last through the whole event day in `Europe/Warsaw`, refreshed on rebuild.
- After the event record `meetup_attendees: N` and add {% raw %}`{% include attendance.html %}`{% endraw %} after the opening paragraph if missing; zero/missing counts stay hidden.

## People and profile photos
- Reuse IDs and portraits from [_data/speakers.yml](../../_data/speakers.yml). Speaker cards list past appearances only.
- Local JPG/PNG portraits, about 400x400px: organizer photos in `assets/images/organizers/`, speaker originals in `assets/images/speakers/raw/`, resized in `assets/images/speakers/`. Reuse organizer images for speakers who organize.
- Keep `placeholder.png` in both portrait directories. Omit unknown `linkedin` keys: an empty string is truthy in Liquid and creates a broken link.
- [_data/former_organizers.yml](../../_data/former_organizers.yml): `name`, `photo`, optional `linkedin`; sort by surname and verify names/photos/links on the organizers page.

## Partners and media mentions
- Partners: [_data/partners.yml](../../_data/partners.yml), local logos in `assets/images/partners/`. Confirm participation in the specific event.
- Media: [_pages/wspomnieli-o-nas.md](../../_pages/wspomnieli-o-nas.md), newest first under years; compact link, outlet and verified original publication date, no description. Mark organizer posts `zza kulis`, archived copies `archiwum`; do not substitute event/update dates.

## Homepage behavior
- Derive statistics, in order: years from oldest post, meetings from highest numbered filename (not file count), speakers from `_data/speakers.yml`, presentations from all `talks` entries.
- Calendar uses current/future posts and venue data, highlights the nearest event and links to Meetup. Mobile: single-column flow without nested scrolling.
- Calendar, hero and `llms.txt` share [upcoming selection](../../_includes/upcoming-meeting-posts.html). Preserve the whole-day Warsaw timezone rule; the browser countdown stays at zero after start until midnight, then switches/hides.
- Keep meaningful event text and links in HTML, not a background image. Reuse existing config/data and theme extension points rather than adding duplicate sources.
