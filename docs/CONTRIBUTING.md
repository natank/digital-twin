# Contributing Guide

Thanks for helping build Digital Twin. This document covers how we collaborate
on the monorepo.

## Code of conduct

- Be respectful and constructive in reviews and discussions.
- Assume good intent; prefer clarifying questions over assumptions.
- Do not commit secrets, production credentials, or personal data.
- Keep PRs focused; large unrelated refactors belong in their own PR.

## How to contribute

1. **Pick work** from the current phase plan
   ([phase-0/PR_BREAKDOWN.md](./phase-0/PR_BREAKDOWN.md) or later phase docs)
   or an open GitHub issue.
2. **Branch** from an up-to-date `main`:
   ```bash
   git checkout main && git pull
   git checkout -b phase-0/006-development-tooling
   ```
3. **Implement** with tests and docs as needed.
4. **Validate locally** (see [DEVELOPMENT.md](./DEVELOPMENT.md)):
   ```bash
   pnpm format:check
   pnpm lint
   pnpm typecheck
   pnpm nx run-many --target=test,build --all
   ```
5. **Open a PR** with the template filled in.
6. **Address review**; keep the branch rebased/up to date with `main` when
   branch protection requires it.
7. **Merge** via squash when approved and CI is green.

## Pull request process

### Title

Prefer phase/epic context:

```text
[Phase-0] PR-006 Development Tooling
feat(auth): register owner with email/password
```

### Body

Use `.github/pull_request_template.md`. Include:

- Summary of _what_ and _why_
- Type of change
- How you tested
- Checklist (secrets, migrations, docs)
- Links to phase breakdown / issues

Local PR notes (optional, gitignored) can live under:

```text
pr-work/PHASE0-006-…/PR_DESCRIPTION.md
```

### Size

Aim for reviewable diffs. Prefer stacking or splitting when a change spans
unrelated concerns (schema + UI + CI).

### Checks required on `main`

Branch protection expects:

- `quality`, `test`, `build`
- `docker-backend`, `docker-frontend`
- At least **1 approving review**
- Conversation resolution
- Branch up to date with `main`

Admins may bypass in emergencies (`enforce_admins: false`); do not rely on
that for normal work.

## Commit conventions

[Conventional Commits](https://www.conventionalcommits.org/):

| Type       | Use for                            |
| ---------- | ---------------------------------- |
| `feat`     | User-facing feature                |
| `fix`      | Bug fix                            |
| `chore`    | Tooling, deps, Phase 0 scaffolding |
| `docs`     | Documentation only                 |
| `test`     | Tests only                         |
| `refactor` | No behavior change                 |
| `ci`       | CI/CD workflows                    |
| `perf`     | Performance                        |

Examples:

```text
chore(phase-0): PR-006 Development tooling
feat(auth): add password reset token model
fix(chat): handle empty visitor message
docs: clarify Podman setup in DEVELOPMENT.md
```

## Review process

### Authors

- Keep the PR description accurate as the diff evolves.
- Respond to comments or mark resolved with a short note.
- Do not force-push over commits others are reviewing without coordination
  (rebase onto `main` is fine when requested).

### Reviewers

- Check correctness, tests, security (authz, secrets, injection), and clarity.
- Prefer suggesting alternatives over pure style nits when Prettier/Black
  already own formatting.
- Approve when you would be comfortable owning the change in production.

### Merge

```bash
gh pr merge {number} --squash --delete-branch
```

After phase PRs merge, update `docs/phase-0/PR_BREAKDOWN.md` status notes
(same pattern as prior Phase 0 merges).

## Security & secrets

- Never commit `.env.local` or real API keys.
- Use placeholders in `.env.example` only.
- If a secret is leaked, rotate it immediately and treat the commit as
  compromised even if history is rewritten.

## License

Proprietary / UNLICENSED unless otherwise stated in the repository root.
