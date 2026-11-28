# Context

Repository documentation is currently split between a short root `README.md`, operational instructions in root `CLAUDE.md`, planning files (`PLAN.md`, `implementation-plan.md`), and an extracted technical guide/DOCX at the repository root. The README also describes a `docs/adr` and `docs/specs` layout that does not exist. The goal is to make the README accurate and gather project documentation under `docs/` without breaking Claude Code's discovery of the root `CLAUDE.md`.

# Recommended approach

1. **Create a documented `docs/` hierarchy.** Add `docs/README.md` as the documentation index, with links to the technical guide, architecture/planning material, and operational rules. Add `docs/adr/` and `docs/specs/` only where the repository actually has corresponding content; do not create empty placeholder documents.
2. **Organize existing documentation files.** Move the long-form technical guide source (`extracted_guide.txt`) and the DOCX guide into `docs/` with clear kebab-case names. Move `implementation-plan.md` into `docs/plans/` and preserve its content. Keep the root `PLAN.md` as the active working plan until this change is complete, then do not duplicate it as published documentation unless the final repository convention requires it.
3. **Handle `CLAUDE.md` safely.** Keep the authoritative operational `CLAUDE.md` at the repository root because Claude Code/project tooling discovers instructions from that location. Add `docs/CLAUDE.md` as a documentation copy/reference explaining that the root file is authoritative; do not relocate or replace the root file with a docs-only copy. This preserves the Vietnamese server/background-task rules while making them discoverable with the rest of the docs.
4. **Rewrite the root `README.md`.** Make it an accurate project landing page: concise product summary, current architecture, repository layout including `docs/`, prerequisites, backend/frontend installation and commands from the root `package.json`, test/build commands, documentation links, environment-variable guidance, and the rule that smoke-test servers must be stopped afterward. Remove stale claims such as guaranteed existing ADR/spec files unless the corresponding files are created.
5. **Update links and names.** Use relative links from `README.md` and `docs/README.md`; update any references to the old root locations. Preserve technical content while correcting commands and paths to match the current repository (`pnpm --prefix frontend ...`, root test scripts, and `backend/.env.example`). Do not modify source code or the existing unrelated `openrouter_adapter.py` change.
6. **Clean up only documentation artifacts.** Remove temporary/editor artifacts such as the `~$...docx` lock file if tracked or intentionally included in the documentation move, and avoid adding generated dependency files or `node_modules` content.

# Critical files

- `README.md`
- `CLAUDE.md` (retain at root; add a docs reference/copy)
- `docs/README.md` (new index)
- `docs/CLAUDE.md` (new documentation reference/copy)
- `extracted_guide.txt` and `AI_Website_Generation_Agent_Technical_Guide.docx` (move under `docs/`)
- `implementation-plan.md` (move under `docs/plans/`)
- `PLAN.md` (this working plan; leave as the active root plan during implementation)
- `package.json` and `backend/.env.example` (read-only references for accurate commands/configuration)

# Verification

- Check that `README.md` and `docs/README.md` links resolve to existing files.
- Check the final tree and `git status` to confirm only intended documentation additions/moves/edits occurred and the pre-existing adapter modification remains untouched.
- Search for stale root paths (`extracted_guide.txt`, `implementation-plan.md`) and stale `docs/adr`/`docs/specs` claims.
- Validate Markdown structure/links with repository-available tooling if present; otherwise perform a scripted existence check.
- Do not start a backend/frontend server for this documentation-only change. If a smoke test is nevertheless run, stop it immediately and verify ports 8000/5173 are free as required by root `CLAUDE.md`.
