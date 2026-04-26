---
name: wiki
description: "Use whenever creating or updating documentation in a GitHub Wiki, deciding whether content belongs there, or setting up the wiki for a repo. Triggers on phrases like 'add to the wiki', 'create a wiki page', 'document this for users', 'document the architecture pattern', 'where should this go', and on any edit to files under wiki/. Enforces a strict gate: pages exist only when they help an end user use the product OR a contributor write code in this project's style, follow a five-category taxonomy (Tutorials / How-to / Reference / Explanations / Development), and exclude churn-prone implementation details (module layout, file paths), Claude/agent rules, and auto-generated API docs. If Claude is about to add docs to a repo with no wiki submodule, the skill stops and asks before bootstrapping one."
---

# Wiki (project documentation)

The wiki is the project's documentation home. It serves **two audiences**:

- **Users** learning the product — what it does, how to use it, how to solve specific tasks.
- **Contributors** writing code in this project — what patterns and conventions to follow.

Both audiences land here, but each page targets only one of them. The five-category taxonomy below keeps the two audiences from accidentally writing the same kind of mush.

The README is still a different artifact: it's for a developer getting this codebase **running** on day one. The wiki is for *what to do once it's running* — either as a user or as a contributor going deeper.

This skill targets **GitHub Wikis** specifically. The wiki repo (`<owner>/<repo>.wiki.git`) is mounted as a git submodule at `wiki/` in the project. GitHub auto-provisions that repo once wikis are enabled on the project and the first page is created through the GitHub UI.

## When to apply

Use this skill when:

- Creating or updating any file under `wiki/`
- The user asks to "add to the wiki", "document this for users", "make a wiki page"
- A request would produce user-facing documentation but no wiki submodule exists yet

If user-facing documentation seems wanted but the repo has no `wiki/` submodule, **stop and ask before creating one**. Don't auto-bootstrap. The user might prefer a different doc destination (a separate site, Notion, Confluence) or might not need user docs at all (internal tools, libraries used only by their author).

The `/wiki-init` command is the explicit way to bootstrap.

## Page taxonomy

Every wiki page belongs to **exactly one** of five categories. The first four are [Diátaxis](https://diataxis.fr) for user-facing docs; the fifth covers contributor-facing documentation.

| Category | Audience | Purpose | Example titles |
|---|---|---|---|
| **Tutorials** | Users | Learning-oriented — guide a beginner through a meaningful first task | "Getting Started", "Your first <thing>" |
| **How-to guides** | Users | Problem-oriented — show how to solve a specific real-world task | "How to enable X", "Migrating from Y" |
| **Reference** | Users | Information-oriented — describe the machinery completely and accurately | "Configuration options", "CLI commands" |
| **Explanations** | Users | Understanding-oriented — discuss concepts, design rationale, tradeoffs | "How auth works", "Why we chose X over Y" |
| **Development** | Contributors | Document the patterns and conventions a contributor must follow to write code in this project's style | "Hexagonal architecture", "Error-handling conventions", "How to file an issue" |

Each page picks one and stays in it. Mixed-mode pages (a tutorial that bleeds into reference half-way through; a pattern doc that turns into a tutorial) are the most common cause of bad wiki pages — they fail every reader because they're optimized for none.

When adding a new page, ask first: *which category?* If the answer is "all of them" or "I'm not sure", the page probably shouldn't exist yet — the writer hasn't decided what it is.

## Does this belong in the wiki?

Two-step gate. First: which audience is this for?

- **End user** — pick one of the four Diátaxis categories.
- **Contributor** — Development category.
- **Neither** — it doesn't go in the wiki.

Then the second test, which applies to *both* audiences: **is the content stable enough to live in a written page, or does it churn?**

- **Stable** → wiki is fine. Tutorials walk through public surfaces that don't break weekly. Patterns like hexagonal / repository / CQRS document a chosen architectural style and rarely change. Coding conventions, the deploy process — once decided, they sit.
- **Churn-prone** → don't put it in the wiki. It will rot, and worse, future readers will trust it. Examples: module / package layout (the file tree changes; readers should look at the tree, not the wiki), file paths in prose ("the auth code is in `src/security/auth/...`" — true today, false in three months), screenshots of generated UI elements that are themselves auto-built.

The combination of those two tests gives the rule: *user-need OR contributor-need × stable.*

Concrete categories that fail the gate, in either audience:

- **Module layout / package structure / file paths in prose.** Churn-prone (changes too often) — for the file tree, the file tree itself is the source of truth. Same logic as the README skill's anti-list.
- **Claude / agent instructions.** Not for human readers — `CLAUDE.md` is the right home. See the `persist-project-preferences` skill.
- **Auto-generated API documentation** (Javadoc, JSDoc, rustdoc, OpenAPI dumps). Lives with the code; duplicating into the wiki creates a second source of truth that immediately drifts.

These rules apply even when the content is technically true and well-written. *Different audience or different stability profile, different artifact.*

## Setup: the wiki as a git submodule

GitHub provisions a wiki repo at `<owner>/<repo>.wiki.git` once wikis are enabled on the project and a first page exists. Mount it as a submodule under `wiki/`:

```bash
git submodule add https://github.com/<owner>/<repo>.wiki.git wiki
```

After that, `wiki/` is a normal directory containing the wiki's pages. Commits inside `wiki/` are pushed to the wiki repo and show up on the GitHub Wiki UI; the parent repo tracks the submodule pointer.

The `/wiki-init` command automates the setup with all the safety checks. Don't run `git submodule add` by hand inside the wiki skill's flow — use the command.

## File and naming conventions

GitHub Wiki conventions, applied uniformly:

- **`Home.md`** — the wiki's landing page, served at the wiki root URL. Required.
- **`_Sidebar.md`** — global sidebar shown on every page. Strongly recommended once there are more than a handful of pages.
- **`_Footer.md`** — global footer. Optional.
- **Page filenames use hyphens for spaces.** `Getting-Started.md` renders as the page title "Getting Started". No underscores in filenames; no spaces.
- **Filenames are case-sensitive** in GitHub Wiki URLs. Pick a convention (Title-Case is the GitHub norm) and stick to it across the wiki.
- **One H1 per page**, the page title — should match the rendered page title from the filename. Use H2/H3 for structure inside the page.
- **Internal links** use `[[Page-Name]]` syntax (GitHub Wiki's wiki-style links) or standard `[text](Page-Name)` markdown.

## Updating an existing wiki page

1. **Read the page first** to understand its current category and shape.
2. **Apply the gate.** Does the change help an end user use the product? If no, push back: *"this looks like internal/developer content — belongs in `docs/` or `CLAUDE.md`, not the wiki. Skip it?"*
3. **Apply the taxonomy.** Is the addition consistent with the page's category? If a how-to page is sprouting reference material, propose splitting into two pages rather than letting the page drift.
4. **Scan for stale content** while you're in the page — but never delete silently:
   - Code blocks with commands that no longer exist (binary removed, flag renamed)
   - Screenshots / output snippets that don't match current behavior
   - Internal-link targets (`[[Other-Page]]`) that resolve to nothing
   - Version numbers that have advanced past what the page references
   For each suspected staleness, surface it with evidence — *"this page mentions `--legacy-flag` but the CLI no longer has that flag (checked `<source>`); suggest removing the line?"* — and **ask** before deleting. Same rule as the `readme` skill: no silent cleanup.
5. **Don't proactively add new sections** unless the user asks. If the update is for a specific reason, do that one thing.

## Creating a new page — pick the category first

Before writing a single line, declare the category. If you can't pick one cleanly, the page shouldn't exist yet.

For each category, the typical shape:

- **Tutorial** — a numbered sequence of small steps, each producing a visible result. End with the user having built or done something concrete. No optional digressions, no exhaustive parameter listings, no "you might also want to know" tangents.
- **How-to** — a focused recipe for one specific task. Assumes the user knows the basics. Numbered steps; optional variations at the end. Don't try to teach — link to a tutorial if the prerequisites aren't met.
- **Reference** — encyclopedic. Tables, lists, exhaustive parameter descriptions. No narrative; no "interesting first" ordering — sort by structure (alphabetical, hierarchical, whatever fits the material).
- **Explanation** — flowing prose discussing the *why*. No commands, no step-by-step. If you find yourself writing a command in an explanation page, that command's home is a how-to instead.
- **Development** — patterns and conventions a contributor needs to follow. Sub-shapes by content type:
  - *Architectural / design patterns* (hexagonal, CQRS, repository, ports-and-adapters, etc.) — name the pattern, state the rule, show one minimal example, link to references. No tutorial walk-through; this isn't where someone learns the pattern, it's where they learn *that this project uses it*.
  - *Coding conventions* (naming, error handling, logging style) — short rules with rationale. One rule per bullet. Cross-reference the relevant skill or external standard rather than restating it.
  - *Contributing guide* (issues, PR process) — if the repo has a `CONTRIBUTING.md`, **prefer that file** over a wiki page; link from the wiki to it, don't duplicate. Use a wiki page only when there is no `CONTRIBUTING.md` and the contributing process needs more space.
  - *Branching / release / deployment process* — checklist or numbered steps for the cut-a-release path; explanation of branch model. If most of the content is about *internals of the build*, that may belong in `docs/` instead.

After writing a new page, add it to the appropriate section in `_Sidebar.md`.

## When you spot an undocumented pattern

While working anywhere in the codebase, if you notice a pattern, convention, or architectural style that isn't already documented in the wiki's Development pages, **ask the user**:

> *"I noticed this code uses [pattern name / description]. There's no Development page for it in the wiki. Want me to add one?"*

Don't write the page unilaterally — the user may have decided not to document this pattern, or it may not yet be stable enough to write down. If the user confirms, follow the Development writing shape above.

Worth flagging:

- **Architectural styles** (hexagonal, CQRS, layered, ports-and-adapters) when they're clearly chosen, not accidental.
- **Cross-cutting conventions** that show up in multiple files (a specific error-handling pattern, a custom DI scope, a recurring DTO shape, a logging convention beyond what `java-logging` already enforces).
- **Project-specific abstractions** built in this codebase (a custom `Result` type, a domain event bus, a project-specific exception hierarchy).

Don't flag:

- One-off quirks present in a single file.
- Third-party-library patterns documented upstream.
- Anything too small to warrant a page (a single utility function isn't a pattern).

The bar: *would a new contributor want a wiki page on this to write idiomatic code in this project?* If yes, ask. If no, leave it.

## After finishing any non-trivial task

When you complete a task that changed code, configuration, or workflow, do a quick check before reporting the work done: **does the wiki need an update?**

Mental scan:

- Did this task introduce a new pattern or convention? → maybe a new Development page (apply the "spot a pattern" rule above; ask first).
- Did this task change a user-facing surface (CLI flag, config option, public API behavior)? → maybe a Reference or How-to update.
- Did this task remove or rename something the wiki currently documents? → flag the staleness with evidence, ask before deleting.
- Did this task change the deploy / release / contributing process? → maybe a Development-section update.

If any answer is yes, surface it to the user with the specific page that should change — *"[task] removed `--legacy-flag`; the `Reference/CLI-options` page still mentions it; want me to update?"* The user decides whether to act now, defer, or skip. Don't auto-edit.

The check is mandatory; the writing is gated.

See also the `readme` skill's matching post-task check for README updates — both should run after substantial work.

## Cross-references

- **`readme` skill** — the README is for getting the project running on day one. The wiki is for using it (Tutorials/How-to/Reference/Explanations) and contributing to it (Development). Don't duplicate content between them.
- **`persist-project-preferences` skill** — Claude/agent rules go in `CLAUDE.md`, never in the wiki.
- **`docs/` directory** — for documentation that lives in the main repo (architecture decision records aimed at the team, internal tooling notes that aren't yet stable enough for the wiki). When in doubt about `docs/` vs Development-on-the-wiki: the wiki is for *stable* contributor docs that survive refactors; `docs/` is for *internal* notes that may not.
