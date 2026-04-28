---
name: ci-cd
description: "Use whenever writing, reviewing, or modifying CI/CD pipeline configuration — GitHub Actions workflows (.github/workflows/*.yml), GitLab CI (.gitlab-ci.yml), Jenkinsfiles, CircleCI (.circleci/config.yml), Azure Pipelines, Buildkite, Drone — or designing the structure of a build/test/deploy pipeline. Triggers on phrases like 'add a workflow', 'set up CI', 'pipeline is slow', 'cache the build', 'why is this running twice', 'add a deploy step', 'pin this action', 'required check', and on any edit under .github/workflows, .gitlab-ci.yml, Jenkinsfile, .circleci/, azure-pipelines.yml, .buildkite/, .drone.yml. Core principle: DRTT — Don't Run Things Twice. Build the artifact in one job, consume it in downstream jobs via cache or upload. Plus version pinning, least-privilege permissions, secrets discipline, fail-fast parallelism, every-step-has-a-verdict, concurrency control, timeouts, OIDC for cloud auth, reproducibility, and auto-updates."
---

# CI/CD

## Overview

Personal conventions for CI/CD pipelines. Rules are written platform-agnostically; per-platform notes give concrete syntax for GitHub Actions, GitLab CI, Jenkins, and CircleCI. If the project uses a platform not covered, ASK before guessing the equivalent syntax.

The single biggest principle is **DRTT — Don't Run Things Twice.** Every other rule in this skill either implements DRTT, prevents you from accidentally violating it, or addresses a different class of pipeline footgun.

**Boundary with the `build-tools` skill:** this skill governs *pipeline shape* — what runs in which job, how artifacts move between jobs, when jobs cancel, what permissions they get. The actual build invocation inside any single job (`./mvnw package -DskipTests`, `./gradlew assemble`, `npm run build`, `cargo build`) is the `build-tools` skill's territory. Use both; they don't overlap.

## Rule themes

The 16 rules below cluster into six themes. When skimming, jump to the theme that matches the change:

- **Don't repeat work** — rules 1 (DRTT) and 2 (cache key correctness).
- **Pin everything** — rules 3 (action/image versions) and 16 (auto-update those pins).
- **Permissions and secrets** — rules 4 (least-privilege), 5 (secrets discipline), 13 (OIDC for cloud auth), 14 (`pull_request_target` gotcha).
- **Pipeline shape** — rules 6 (path filtering), 7 (fail-fast and parallelism), 8 (every step has a verdict), 11 (required-check naming stability).
- **Reliability** — rules 9 (concurrency / cancel-in-progress), 10 (timeouts everywhere), 12 (pipeline speed budget).
- **Reproducibility** — rule 15 (deterministic builds).

## Rules

### 1. DRTT — Don't Run Things Twice

If the pipeline produced an artifact in job A and job B needs it, **job B consumes A's output**. It does not rebuild from source.

**Build once, deploy many.** A pipeline run typically has one *build* phase that produces an artifact (jar, container image, npm tarball, binary, static site bundle), and downstream jobs (test, scan, deploy to staging, deploy to prod) all consume that same artifact. Never:

- Rebuild the jar in the deploy job because "it's quick".
- Recompile the TypeScript in both the lint job and the test job.
- Re-pull and re-tag the same Docker image in three deploy jobs.

**How to share artifacts between jobs:**

| Platform | Mechanism |
|---|---|
| GitHub Actions | `actions/upload-artifact` → `actions/download-artifact`, or `actions/cache` for derived state |
| GitLab CI | `artifacts:` (passed automatically to downstream stages) and `cache:` for derived state |
| Jenkins | `stash` / `unstash` within a pipeline, or an external artifact repository (Nexus, Artifactory) for cross-pipeline reuse |
| CircleCI | `persist_to_workspace` → `attach_workspace`, plus `save_cache` / `restore_cache` |

**Cache dependencies, not just artifacts.** Maven `~/.m2`, Gradle `~/.gradle/caches`, `node_modules`, Cargo `~/.cargo/registry`, Go module cache, pip wheel cache — all of these get re-resolved on every job by default. Cache them, keyed on the lockfile/manifest hash.

**Don't re-run unchanged checks within a single pipeline run.** Linters, scanners, type-checks: each runs once. If you find yourself running `eslint` in the lint job *and* implicitly during `npm run build` in another job, fix the build script, don't accept the duplication.

### 2. Cache key correctness over cache hit rate

A wrong cache hit is worse than a cache miss. The miss costs minutes; the wrong hit costs hours of debugging a phantom failure that doesn't reproduce locally.

- **Cache keys must include every input that affects the output.** For `node_modules`: lockfile hash + Node version + OS. For Maven `.m2`: `pom.xml` hash + JDK version + OS. Forgetting one of these turns the cache into a source of mysterious flakes.
- **Use restore-keys conservatively.** Fallback keys (e.g. older lockfile versions) help cold starts but can pull in stale caches. If you use them, the build step must rebuild whatever doesn't match (e.g. `npm install` after a partial `node_modules` restore — not just `npm ci`).
- **Versioning the cache key is fine.** When debugging a poisoned cache, prepend a version segment (`v2-${{ hashFiles(...) }}`) and bump it to invalidate. Cheaper than reasoning about cache eviction.

### 3. Pin every action and image version

Pin to a specific version (or SHA), never to a moving tag.

- **GitHub Actions** — pin third-party actions to a SHA: `actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11` (the SHA for `v4.1.1`). At minimum, pin to a major version (`@v4`). Never `@main` or `@master` for actions you don't own — silent breakage waiting to happen.
- **Docker base images** — pin to a tag (`node:20-alpine`, `eclipse-temurin:21-jre`), not `latest`. Better: pin to a digest (`@sha256:...`) for reproducibility-critical paths.
- **Runner images** — `ubuntu-22.04` not `ubuntu-latest`. `ubuntu-latest` rolls forward across major versions and breaks pipelines unpredictably.

Pinning without updates rots — see rule 16 (auto-updates).

### 4. Least-privilege permissions

The pipeline's default credentials should be the smallest scope it needs.

- **GitHub Actions** — set `permissions: contents: read` at workflow scope, then grant additional scopes per job that needs them (e.g. `permissions: contents: write, packages: write` only on the release job). The default `GITHUB_TOKEN` permissions are too broad.
- **GitLab CI** — use `CI_JOB_TOKEN` with the project's job token allowlist; don't expose `CI_PROJECT_TOKEN` to jobs that don't need it.
- **Cloud credentials** — IAM role per pipeline / per environment, not a single deploy role with `*` permissions. Pair with OIDC (rule 13).

### 5. Secrets discipline

- **Never `echo` a secret.** Even `echo "::add-mask::$SECRET"` is fragile — a rogue `set -x` upstream prints it before the mask applies.
- **Scope secrets to the jobs that need them.** Don't put secrets in a workflow-level `env:` block; they leak into every job's process environment, including third-party actions.
- **Don't pass secrets as command-line arguments** (they show up in `ps`). Use environment variables or stdin.
- **Rotate on suspected leak.** A secret that appeared in any log, ever, is compromised — rotate it. Treat the runner's environment as semi-trusted; treat logs as public.

### 6. Path-based job filtering

Skip jobs whose inputs didn't change. The frontend test job shouldn't run when only `README.md` changed.

- **GitHub Actions** — `paths:` / `paths-ignore:` on the workflow trigger.
- **GitLab CI** — `rules: changes:` per job.
- **Caveat (important):** path filters interact with required checks. A required check that's filtered-out is *not* reported as "skipped"; it's reported as nothing, and protection rules treat that as failing. If a job is required, it has to either always run or use a "fan-out" pattern with a final aggregator job that's always required.

### 7. Fail fast + parallelism

- **Run independent jobs in parallel.** No serial dependencies between jobs that don't actually depend on each other (lint and unit-test are usually independent of each other).
- **A failure in a required path should stop dependent downstream work.** GHA jobs default to this via `needs:`; matrix builds use `fail-fast: true` (the default). Don't override unless you have a real reason (e.g. you want all matrix shards to run for a flaky-test investigation).

### 8. Every step has a verdict

If a step runs in the pipeline, its result must affect the pipeline's outcome.

- **Don't use `continue-on-error: true` on linters / scanners / type-checkers you actually care about.** "Advisory only" steps become noise everyone learns to ignore. If a tool's findings should block merge, fail the build on findings; if they shouldn't, don't run the tool in CI at all (run it locally or in a separate report-only job that's not in the merge path).
- **Same for `|| true` in shell steps.** A scanner that always passes is worse than no scanner — it provides false assurance.
- **Exception:** report-only jobs that explicitly publish results elsewhere (a Slack message, a GitHub annotation) and don't gate merge — those are fine, but name them clearly so no one mistakes them for gates.

### 9. Concurrency control

A new push to a branch should cancel the in-flight pipeline for that branch.

- **GitHub Actions:**
  ```yaml
  concurrency:
    group: ${{ github.workflow }}-${{ github.ref }}
    cancel-in-progress: true
  ```
- **GitLab CI** — `interruptible: true` on jobs you want cancelled by newer commits, plus the project-level "auto-cancel redundant pipelines" setting.
- **Don't `cancel-in-progress` on deploy jobs targeting production** — interrupting a deploy mid-flight can leave it half-applied. Concurrency-group those without cancellation, so they queue.

Saves runner time and prevents the classic deploy race: two pipelines from different commits both finishing the deploy job, with the second one's "success" actually applying older state.

### 10. Timeouts everywhere

Every job declares `timeout-minutes` (or its platform equivalent). The platform default is usually too generous (GHA: 6 hours).

- **Default to a sane cap** — 15 min is a reasonable starting point for build/test jobs.
- **Override per-job when justified.** A long-running e2e suite or container build may legitimately need 30–45 min; declare it explicitly.
- **Step-level timeouts for known-flaky operations** (network calls, deploys) so a single hung step doesn't burn the whole job's budget.

### 11. Required-check naming stability

The check name is what branch protection rules and merge queues match against. Renaming a job silently un-protects the branch until someone updates the protection rule.

- **Don't rename a job without updating branch protection in the same PR.**
- **Prefer stable, generic names** (`build`, `test`, `lint`) over specifics that may churn (`build-jar-with-jdk-21`).
- **For matrix jobs, add a final aggregator job** with a stable name (`ci-required` or similar) that depends on all matrix shards. Put that one in the protection rule. Then matrix dimensions can change without breaking protection.

### 12. Pipeline speed budget

Pick a target wall-clock for the main pipeline (e.g. PR pipeline < 10 minutes; main-branch pipeline < 20 minutes including deploy). When it slips, investigate.

A slow CI is a tax on every code change. Common culprits when budget creeps:
- Tests that grew without anyone noticing — split into fast and slow suites.
- Cache misses from a wrong cache key (rule 2).
- Unnecessary serialization (rule 7).
- A flaky retry burning a full job's worth of time per attempt.

### 13. OIDC for cloud auth instead of long-lived secrets

If the pipeline deploys to AWS / GCP / Azure / similar, use OIDC federation rather than storing static credentials as secrets.

- **GitHub Actions → AWS:** `aws-actions/configure-aws-credentials` with `role-to-assume` + `audience: sts.amazonaws.com`. The runner gets a short-lived token per job; no `AWS_ACCESS_KEY_ID` in repo secrets.
- **GitHub Actions → GCP:** `google-github-actions/auth` with workload identity federation.
- **GitHub Actions → Azure:** `azure/login` with federated credential.
- **GitLab CI** — built-in OIDC ID tokens (`id_tokens:`); same pattern.

This is the single biggest CI security win available and is essentially free to adopt on a greenfield setup. On an existing setup with static credentials, migrating is a deliberate change — ASK before doing it.

### 14. `pull_request_target` gotcha (GitHub Actions)

`pull_request_target` runs with the **base branch's** workflow code and **secrets available**. Combining it with `actions/checkout` of the PR head means you're running untrusted contributor code with full repo secrets — a textbook supply-chain attack vector.

- **Don't use `pull_request_target` unless you understand the model.** The legitimate uses are narrow (labelling a PR, running a workflow that touches the PR comments).
- **Never `actions/checkout` the PR head** in a `pull_request_target` workflow without isolating it first (e.g. running it inside a container with no secrets, no network access to internal services).
- **For "I want PRs from forks to have CI",** use `pull_request` (which doesn't have secrets and runs the PR's workflow code) — not `pull_request_target`.

### 15. Reproducible / deterministic builds

Same input → same output. Foundation for SLSA / provenance and for trusting that the artifact in the deploy job is the same as the one tested earlier.

- **No embedded build timestamps.** Many tools default to embedding the wall-clock; override with `SOURCE_DATE_EPOCH` (Maven, Make, several others honor it).
- **Sorted, deterministic file orderings** in archives. `tar --sort=name`, `zip` with stable ordering, etc.
- **Locked dependency versions.** Lockfiles committed and respected (`mvn -o` + Maven enforcer; `npm ci`; `cargo build --locked`; `go mod download` before build).
- **Declared toolchain version.** JDK version, Node version, Go version pinned in repo (`.tool-versions`, `.nvmrc`, `.java-version`, etc.) and used by CI — not "whatever the runner image has today".

### 16. Auto-update pinned versions

Pinning rots without a way to keep up with upstream. Adopt one of:

- **Renovate** — most flexible; handles GitHub Actions, Docker, Maven, npm, Cargo, Go modules, Gradle, etc., in one tool. Configuration via `renovate.json`.
- **Dependabot** — built into GitHub; covers most ecosystems including GHA. Configuration via `.github/dependabot.yml`.

Either way, the result is a steady stream of small PRs bumping pinned versions, which the team reviews and merges. Without this, a "pinned" repo silently accumulates a year of out-of-date actions and base images.

## Per-platform notes

### GitHub Actions

- **Workflow files live in `.github/workflows/*.yml`.** One workflow per high-level concern (CI, release, scheduled scans) is usually clearer than one giant workflow.
- **Use `composite` actions or reusable workflows (`workflow_call`)** to share steps across workflows. Don't copy-paste 40-line setup blocks.
- **The cache action is shared across the repo by branch.** Branches inherit cache from `main`/the default branch on first run; pushes from a branch update only that branch's cache. Plan keys accordingly.
- **`if:` conditionals are powerful.** Use them for "only on tags", "only on main", "only if a specific path changed in the previous step's output". Don't gate behavior on branch names with shell `if` blocks when `if:` would do.

### GitLab CI

- **`.gitlab-ci.yml` at repo root.** Use `include:` to split large pipelines across files; one file per concern.
- **Stages are sequential; jobs within a stage are parallel.** Plan stage layout intentionally; don't put unrelated jobs in the same stage just because they're "the same kind".
- **`needs:` lets you build a DAG** (jobs from a later stage starting before earlier-stage jobs finish, when their specific dependencies are met). Use it for fail-fast parallelism (rule 7).
- **`rules:` is the modern replacement for `only:`/`except:`.** Use `rules:` exclusively in new pipelines.

### Jenkins

- **Declarative pipelines (`pipeline { ... }`) over scripted (`node { ... }`)** for new work. Declarative is more constrained but easier to read and review.
- **`stash`/`unstash` for intra-pipeline artifact passing.** For cross-pipeline reuse, push to an artifact repository (Nexus, Artifactory).
- **Shared libraries** for code reuse across jobs.
- **Don't put secrets in `Jenkinsfile`.** Use the Credentials plugin and `withCredentials { ... }`.

### CircleCI

- **`.circleci/config.yml`** — one file, but use orbs and reusable commands/jobs to keep it readable.
- **`persist_to_workspace` + `attach_workspace`** is the canonical artifact-sharing mechanism within a pipeline. Cache (`save_cache`/`restore_cache`) is for derived state across pipelines.
- **Workflows define the DAG** between jobs. Use them; don't put everything in a single linear job.

### Other platforms (Azure Pipelines, Buildkite, Drone, Tekton, Argo Workflows, …)

ASK before guessing the equivalent of any rule in this skill. Concepts (caching, fan-out/fan-in, OIDC, pinning) are universal; syntax varies enough that a wrong-syntax answer is worse than asking.
