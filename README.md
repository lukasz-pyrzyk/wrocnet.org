# Wroc.NET – website

The [wrocnet.org](https://wrocnet.org) website – Wrocław .NET User Group.

Built with [Jekyll](https://jekyllrb.com/) and the [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme.

## Local development

Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/)
or another Docker-compatible engine, then run in a POSIX shell (on Windows, use WSL):

```bash
./run.sh
```

Open http://127.0.0.1:4001. Source edits trigger a rebuild and browser refresh.
Stop with Ctrl+C or `docker stop wrocnet-local` before starting another instance.
If file watching misses edits, use `./run.sh --force_polling`.

The script builds the latest `ruby:4-alpine` image using cached layers. Separate
Docker volumes preserve this project's gems, generated pages and cache between
runs. LiveReload uses port 35730. Host Ruby, Bundler and Docker Compose are not
required.

The existing local `Gemfile.lock` is used when available; it remains ignored by
Git. A fresh checkout resolves dependencies from `Gemfile`, as before.
CI/CD continues to build directly with Ruby and Jekyll, without Docker.

## CI validation checks (local)

With the local preview running, use these commands to run the same checks as CI.
Generated pages stay in the container's `wrocnet-site` volume.

Prerequisite for step 1: install `yamllint` (for example: `python -m pip install yamllint`).

1. Lint YAML files:

   ```bash
   yamllint -c .yamllint _data _config.yml
   ```

2. Build Jekyll in strict front matter mode:

   ```bash
   docker exec wrocnet-local bundle exec jekyll build --strict_front_matter
   ```

3. Validate generated HTML, internal links, and images:

   ```bash
   docker exec wrocnet-local bundle exec htmlproofer ./_site --disable-external --no-enforce-https
   ```

## Project structure

| Path | Description |
|---|---|
| `_config.yml` | Main Jekyll and theme configuration |
| `_data/` | Static data: navigation, organizers, speakers, partners, venue |
| `_posts/` | Meeting posts (format: `YYYY-MM-DD-NR-spotkanie-*.md`) |
| `_pages/` | Static pages (about, organizers, etc.) |
| `_includes/` | Overridden theme partials (masthead, hero) |
| `_sass/` | Custom color skin (`_wrocnet.scss`) |
| `assets/` | Images, logo, presentation files (PDF/PPTX) |

## Partners and media mentions

Current partners are listed in [`_data/partners.yml`](_data/partners.yml) and
rendered on the homepage. Keep partner logos locally in `assets/images/partners/`.

Media coverage is collected in
[`_pages/wspomnieli-o-nas.md`](_pages/wspomnieli-o-nas.md), linked from the main
navigation. Add publications newest first under year headings, including the
article link, outlet, and publication date in a compact list item, without a
description. Mark organizer posts as `zza kulis` and archived copies as `archiwum`.
Verify both the mention and the original publication date on the source page;
do not substitute an event date or the page's last-updated date. Summarize in
your own words rather than reproducing the article if context is needed elsewhere.

## Adding a new meeting post

Create a file in `_posts/` following the naming convention:

```
_posts/YYYY-MM-DD-NR-spotkanie-wroclawskiej-grupy-net.md
```

Minimal front matter:

```yaml
---
title: "NR. spotkanie Wrocławskiej Grupy .NET"
date: YYYY-MM-DD
categories: spotkania
tags:
   - offline
header:
  teaser: /assets/images/logo.png
---
```

Every post must have exactly one format tag: `offline` for regular in-person meetings, `online` for regular online meetings, or `inne` for special/non-numbered events.

When a title or body paragraph starts with the meeting number, escape its period
(for example, `172\. spotkanie ...`) so Markdown does not turn it into an ordered
list displaying `1.`. Use single-quoted YAML for such titles, for example
`title: '172\. spotkanie Wroc.NET'`. Do not double-escape existing numbers or
change genuine numbered lists. Titles pasted into Meetup are plain text:
use `172. spotkanie Wroc.NET` there, without the backslash.

For meeting registration, add `meetup_url` to the post's front matter with the
specific event URL (not the group URL), for example
`meetup_url: "https://www.meetup.com/wrocnet/events/317144095/"`.
The default `meeting` layout inherits the theme's `single` layout and displays
a prominent “ZAPISZ SIĘ” button above and below the content for posts in
`spotkania` with a non-empty `meetup_url`. Posts without an event URL and past
meetings do not display signup buttons. The date check includes the entire
event day in `Europe/Warsaw` and is refreshed when the static site is rebuilt.

For event banners (AI generation, assets, rendering, partner hierarchy, and website integration), use the [single banner workflow in office/AGENTS.md](office/AGENTS.md#zasady-dla-grafik).

After an event, add or update `meetup_attendees: N` in its front matter to preserve the attendee count shown by Meetup. Also add {% raw %}`{% include attendance.html %}`{% endraw %} after the opening paragraph if it is not already present. The include displays positive counts and hides zero or missing values.

The homepage calendar, hero, and `llms.txt` share upcoming-event selection in
[`_includes/upcoming-meeting-posts.html`](_includes/upcoming-meeting-posts.html).
Events remain upcoming throughout their calendar day in the site's timezone
(`Europe/Warsaw`), regardless of the build time or event start time. This selection
is refreshed when the static site is rebuilt.
The hero also applies this timezone rule in the browser: after the start time,
the countdown stays at zero and the event's program remains visible until
midnight, when it switches to the next event or hides if none remain.
The homepage event card uses the same program and speaker names from
`_data/speakers.yml`, without portraits so single- and multi-speaker talks align.
The card presents a centered countdown, the date and venue, then the program,
with the signup button at the bottom.
Its decorative Wrocław illustration is `assets/images/home-wroclaw.webp`.
Keep the headline, event details, and signup link as HTML rather than embedding
them in the background image.
The visible homepage copy uses `hero_heading` and `hero_intro` in `index.html`,
independently of the existing SEO `title`, `excerpt`, and site description.

The administrator/organizer credit and personal website link in the footer and
`llms.txt` share `website_organizer` in `_config.yml`. The footer credit uses
the theme's `_includes/footer/custom.html` extension point.
