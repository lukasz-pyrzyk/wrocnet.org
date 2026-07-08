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

1. Install Ruby via [RubyInstaller for Windows](https://rubyinstaller.org/downloads/) (choose the **Ruby+Devkit** version ≥ 3.0). Run the `ridk install` step at the end of the installer.

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
| `_data/` | Static data: navigation, organizers, schedule |
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
header:
  teaser: /assets/images/logo.png
---
```
