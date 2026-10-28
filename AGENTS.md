# Agent guidance for wrocnet.org

## Start here
- For website work, follow [Website Admin](.github/agents/wrocnet-website-admin.agent.md): development, content/data conventions, safeguards and validation.
- For communication, follow [office/AGENTS.md](office/AGENTS.md). Read its technical workflows only for graphics or presentations.

## Changes and Git
- Keep changes small, content-safe and compatible with existing data schemas, URLs and Polish content style.
- Link to existing documentation instead of duplicating rules. Do not turn task-specific workarounds into permanent global instructions.
- Never commit directly to main. Run `git fetch origin main`, then `git switch --no-track -c <branch-name> origin/main` for each task.
- Preserve unrelated local changes; cherry-pick only task-specific commits when moving work.
- Before pushing, verify `git log origin/main..HEAD` and `git diff --stat origin/main...HEAD` contain only the intended task. Merge via Pull Request.
