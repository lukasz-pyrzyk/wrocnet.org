# AGENTS.md

Agent guidance for wrocnet.org (Jekyll + Minimal Mistakes).

## Purpose
- Keep changes small, content-safe, and compatible with the current Jekyll site structure.
- Prefer updating existing files and patterns over introducing new architecture.

## First Read
- Main project guide: [README.md](README.md)
- Jekyll config and site defaults: [_config.yml](_config.yml)
- CI validation pipeline: [.github/workflows/validate.yml](.github/workflows/validate.yml)
- YAML lint rules: [.yamllint](.yamllint)
- Navigation/content data: [_data/navigation.yml](_data/navigation.yml), [_data/schedule.yml](_data/schedule.yml), [_data/organizers.yml](_data/organizers.yml)

## Core Commands

See [README.md](README.md) for install, local dev server, and CI validation commands (yamllint, jekyll build, htmlproofer).

## Repository Conventions
- Site uses remote theme mmistakes/minimal-mistakes@4.28.0 and custom skin wrocnet.
- No custom _layouts directory: rely on theme layouts and local overrides in _includes.
- Default post category is spotkania via _config.yml defaults (post naming pattern and front matter: see [README.md](README.md#adding-a-new-meeting-post)).
- Main pages are in _pages, data-driven content is in _data.
- Default branch is main.
- Do not commit directly to main: create a topic branch for each task and merge via Pull Request.

## Known Pitfalls
- Keep aligned colons in _data/ui-text.yml. The lint config intentionally allows extra spaces before colons.
- If adding links/images in old posts, avoid empty markdown links and missing local assets because htmlproofer runs in CI.
- Prefer preserving Polish content style and existing URL/permalink patterns.
- **Images/Photos**: Do not use external URLs for profile photos. Download the image to `assets/images/organizers/`, ensure it's in JPG/PNG format, and resize it to a reasonable size (e.g., 400x400px) before committing.
- **Historical posts** (pre-2012, archival data): see [.github/instructions/historical-posts.instructions.md](.github/instructions/historical-posts.instructions.md) for anonymization and formatting rules.
- **Local build environment (macOS)**: system Ruby (2.6.x) is too old for the `bundler` version pinned in `Gemfile.lock` (requires Ruby >= 3.2). Fix: `brew install ruby@3.2`, then prefix commands with `export PATH="/opt/homebrew/opt/ruby@3.2/bin:$PATH"` before running `gem install bundler:<version>` and `bundle install`/`bundle exec jekyll ...`. This is a one-time environment fix, not a repo issue.
- **New meeting date/venue/number**: don't guess or ask the user if avoidable — check [_data/schedule.yml](_data/schedule.yml) first (`dates` list gives the next unused date, `venue` gives the current location). The meeting number is the previous post's number + 1 (check the latest file in `_posts/`).
- **Existing speakers**: check [_data/speakers.yml](_data/speakers.yml) for an existing `id` before adding a new speaker entry; reuse it in front matter `speaker_ids` and in body via `{% include speaker.html id="..." %}`.
- **Multiple speakers per talk**: `speaker_ids` in a talk's front matter accepts a list; [_includes/talk.html](_includes/talk.html) renders all of them comma-separated automatically — no extra template work needed.
- **Missing organizer photo**: [_pages/organizatorzy.md](_pages/organizatorzy.md) falls back to `/assets/images/organizers/placeholder.png` via Liquid's `default` filter when `photo` is `""`. That asset must exist locally (create with e.g. `sips` or Pillow) or htmlproofer fails the build. Omit the `linkedin` key entirely (don't set it to `""`) when unknown — Liquid treats empty strings as truthy, so `{% if person.linkedin %}` would render a broken empty link.
- **Running locally**: `bundle exec jekyll serve` skips posts dated after the current date (e.g. next month's meeting). Add `--future` to the serve/build command to include them while previewing.

## Change Strategy For Agents
- Link, do not duplicate: if details exist in README or workflow files, reference them.
- Verify with lint/build/proofer when changing content, data files, or templates.
- Avoid broad formatting rewrites in historical posts unless explicitly requested.
- Keep includes and data schema changes backward-compatible with existing pages.

## Where To Start For Typical Tasks
- Add/update meeting post: see [README.md](README.md#adding-a-new-meeting-post); optional assets under assets/images or slides.
- Update organizer or schedule info: files in _data and related page under _pages.
- Navigation or labels: _data/navigation.yml and _data/ui-text.yml.
- Theme/header behavior: _includes and _sass/minimal-mistakes/skins/_wrocnet.scss.
