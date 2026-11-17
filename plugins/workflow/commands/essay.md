---
description: Write an essay from a one-line intent — skeleton, verified research, draft, K-EXAONE 2.5 Korean line-editing, multi-model critique, then title and per-channel share drafts.
---

Usage: `/essay [--venue blog|letter|linkedin] [--length short|long] [--no-sns] [--mode new|revise|polish] <intent or file>`

Defaults:
- `--mode new` (a fresh piece from the intent)
- `--venue blog`
- `--length long` (3,500–5,000자)
- share drafts included unless `--no-sns`

Examples:

```
/essay 수능을 소학에 비유해서 수험생에게 보내는 편지를 쓰고 싶어
/essay --venue letter --length short 자동화가 일을 줄이지 않는다는 이야기
/essay --mode revise drafts/2026-11-17-my-post.md
/essay --mode polish drafts/2026-11-17-my-post.md
```

## Procedure

1. **Parse arguments.** Everything that is not a flag or a readable file path is the intent. If both an
   intent and a file are missing, ask what to write about (AskUserQuestion) — do not invent a topic.

2. **Load the skill.** Read `skills/write-essay/SKILL.md` and follow its five stages. Do not improvise a
   shorter path: the skeleton checkpoint, the fact-check report, and the one-turn-at-a-time polishing are
   the point of this command.

3. **Report the session folder** as soon as it exists:
   `output/essay-{YYMMDD}-{slug}/`, with the intent and thesis in one line each.

4. **Modes.**
   - `new` — stages 1–5.
   - `revise` — skip stages 1–2, keep the user's draft as `04-draft.md`, then run stage 3 (structure
     check against `references/style-guide.md`), 4 (polish + critique), 5 (distribution). Never rewrite
     the whole piece from scratch when the user asked for a revision — local edits first.
   - `polish` — stage 4-1 only (K-EXAONE 2.5 line-editing), plus the fact-preservation diff. Fastest
     path; report which sentences changed and why.

5. **Stop at each checkpoint.** Skeleton approval, the list of facts that were dropped, and each polishing
   turn wait for the user. `--yes` skips them only when the user passed it explicitly.

6. **Never publish.** The command ends with `final.md` and `distribution.md` on disk. Posting to a blog,
   newsletter, or social account is a separate request.

## Safeguards

- K-EXAONE or Codex missing → drop that member, name it in the output, continue. Do not silently
  substitute another model's answer.
- A fact that cannot be verified is removed, not softened. Say which ones were removed.
- Company-internal numbers, system names, unpublished results, and colleagues' real names never enter a
  draft — public sources only.
- If the user edits a sentence, that sentence is final. Do not revert it in the next round.
