# Personal Knowledge Base Cleanup Implementation Plan

> **For agentic workers:** This plan is executed inline in the current session with verification checkpoints.

**Goal:** Reduce clutter in `D:\学习资源\my-wiki`, preserve recoverable source material, and organize the core AI knowledge into fast-to-scan navigation and archive sections.

**Architecture:** Keep `AI知识库` as the curated knowledge layer, keep `09-项目分类索引.md` as the generated full index, and move temporary/runtime artifacts into a dated archive instead of deleting them immediately. Add one cleanup report so deletion candidates are explicit and reviewable.

**Tech Stack:** Obsidian Markdown, PowerShell read-only inventory, Git diff/checks.

**Spec:** User request in the current conversation.

## Global Constraints

- Do not delete files until their exact paths and recoverability are documented.
- Preserve online links; remove unnecessary dates from curated knowledge prose.
- Keep only core knowledge in the quick-view documents; retain raw/operational material in archive areas.
- Preserve unrelated pre-existing Git changes.

---

### Task 1: Inventory and classify existing files

**Files:**
- Read: `D:\学习资源\my-wiki\AI知识库\*.md`
- Read: `D:\学习资源\my-wiki\scripts\*`
- Read: `D:\学习资源\my-wiki\state\*`

- [x] Record file categories: curated notes, generated indexes, raw captures, runtime state, caches, secrets/configuration.
- [x] Identify duplicates and files that can be regenerated.
- [x] Do not mutate files during inventory.

### Task 2: Create a cleanup report

**Files:**
- Create: `AI知识库/00-overview/知识库清理建议.md`

- [x] List each deletion/archive candidate by exact path and reason.
- [x] Mark secrets, runtime state, caches, and logs as high-risk for accidental deletion or version control.
- [x] State which files are core and must remain.

### Task 3: Organize the curated knowledge layer

**Files:**
- Modify: `AI知识库/00-overview/知识库导航.md`
- Modify: curated topical files only when needed for navigation/duplication control.
- Create/archive: `AI知识库/99-归档/`

- [x] Keep stable core topics in numbered files.
- [x] Keep full project records in `09-项目分类索引.md`.
- [x] Keep human-selected projects in `08-开源项目收藏.md`.
- [x] Keep the AI project map as a concise cross-category overview.
- [x] Keep raw historical snapshots in `99-归档`; no additional move was needed.

### Task 4: Verify the result

- [x] Check all Markdown links in changed navigation files for target existence.
- [x] Run `git diff --check` on changed files.
- [x] Recount files and inspect the final tree.
- [x] Report what was changed, what was only recommended for deletion, and what remains untouched.
