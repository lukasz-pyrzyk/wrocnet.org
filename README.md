# Wroc.NET – website

The [wrocnet.org](https://wrocnet.org) website – Wrocław .NET User Group.

Built with [Jekyll](https://jekyllrb.com/) and the [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme.

## Local development

### macOS

1. Install Ruby via Homebrew (the system Ruby is too old):

   ```bash
   brew install ruby
   export PATH="$(brew --prefix ruby)/bin:$PATH"
   ```

   Add the `export PATH` line to your `~/.zshrc` to make it permanent.

2. Install Bundler and dependencies:

   ```bash
   gem install bundler
   bundle install
   ```

3. Start the dev server:

   ```bash
   bundle exec jekyll serve --livereload
   ```

### Windows

1. Install Ruby via [RubyInstaller for Windows](https://rubyinstaller.org/downloads/) (choose the **Ruby+Devkit** version ≥ 3.2, required by the pinned Bundler). Run the `ridk install` step at the end of the installer.

2. Open a new Command Prompt or PowerShell window and install dependencies:

   ```powershell
   gem install bundler
   bundle install
   ```

3. Start the dev server:

   ```powershell
   bundle exec jekyll serve --livereload
   ```

The site will be available at [http://localhost:4000](http://localhost:4000).

## CI validation checks (local)

To run the same checks as CI before opening a PR:

Prerequisite for step 1: install `yamllint` (for example: `python -m pip install yamllint`).

1. Lint YAML files:

   ```bash
   yamllint -c .yamllint _data _config.yml
   ```

2. Build Jekyll in strict front matter mode:

   ```bash
   bundle exec jekyll build --strict_front_matter
   ```

3. Validate generated HTML, internal links, and images:

   ```bash
   bundle exec htmlproofer ./_site --disable-external --no-enforce-https
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
list displaying `1.`. Use single-quoted YAML for such titles.

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
