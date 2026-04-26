---
description: Bootstrap the project's GitHub Wiki as a git submodule at wiki/ with a minimal Home.md and a five-section _Sidebar.md template (Tutorials / How-to / Reference / Explanations / Development). Refuses if wiki/ already exists; verifies the GitHub remote and wiki-repo existence first.
argument-hint: (no arguments)
---

# /wiki-init

Add the project's GitHub Wiki as a git submodule at `wiki/` and create a minimal landing page + sidebar.

This is the explicit way to bootstrap a wiki — outside this command, the `wiki` skill stops and asks before doing this.

## Pre-flight checks

Before running `git submodule add`:

1. **Repo must be a git repo.** If not, stop and tell the user.
2. **Repo must have a GitHub `origin` remote.** Detect via `git remote get-url origin`. The URL must match `github.com[:/]<owner>/<repo>(\.git)?$`. If the remote is not GitHub, stop — this command is GitHub-specific.
3. **`wiki/` must not already exist** at the repo root. If it does, stop. Show the user a directory listing and ask: *edit existing wiki* (recommended), *replace*, or *cancel*. Default to edit (defer to the `wiki` skill). Never silently overwrite.
4. **The wiki repo must exist on GitHub.** GitHub auto-provisions `<owner>/<repo>.wiki.git` only after the repo's wiki is enabled and the first page is created via the GitHub UI. Test with `git ls-remote https://github.com/<owner>/<repo>.wiki.git` — if it fails, the wiki hasn't been initialized yet. Stop and tell the user:

   > GitHub Wikis must be initialized through the GitHub UI before they're cloneable. Visit
   > `https://github.com/<owner>/<repo>/wiki`, click "Create the first page", give it any
   > content, save. Then re-run `/wiki-init`.

## What the command does

Once pre-flight passes:

1. Run `git submodule add https://github.com/<owner>/<repo>.wiki.git wiki` from the repo root and verify it succeeded.
2. Inside `wiki/`, create `Home.md` with a minimal landing page:

   ```markdown
   # <Project name>

   Documentation for <project>. See the sidebar for the table of contents.
   ```

   Use the project name from the README's H1 if available, else the value from `package.json` `name` / `pyproject.toml` `[project] name` / `Cargo.toml` `[package] name` / equivalent, else the repo name.

3. Create `wiki/_Sidebar.md` with the five-category navigation skeleton matching the `wiki` skill's taxonomy:

   ```markdown
   ### Tutorials

   ### How-to guides

   ### Reference

   ### Explanations

   ### Development
   ```

   Empty sections — pages get linked under the appropriate heading as they're written. The headings being visible from day one remind future contributors that every page belongs to exactly one category.

4. Inside the submodule, commit the new files:

   ```bash
   cd wiki
   git add Home.md _Sidebar.md
   git commit -m "Add initial Home and sidebar"
   ```

   Do **not** push. The user pushes when they're ready.

5. Stage the submodule pointer change in the parent repo:

   ```bash
   git add .gitmodules wiki
   ```

   Do **not** commit the parent repo. The user reviews and commits.

## After running

Tell the user:

- That the submodule was added at `wiki/` and the GitHub Wiki URL it points to.
- That `Home.md` and `_Sidebar.md` were created and committed *inside the submodule*, not pushed.
- That two changes are staged in the parent repo (`.gitmodules` and the `wiki` submodule pointer) and need a commit.
- That the wiki currently has no content beyond the placeholder Home — anything the user wants added next should go through the `wiki` skill (which will ask about category and content before writing).

Don't push anything. Don't commit the parent-repo changes. The user reviews and commits.
