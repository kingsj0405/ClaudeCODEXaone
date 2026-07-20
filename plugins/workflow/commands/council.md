---
description: Run a round-based council across several models (Codex / K-EXAONE / Claude self) for writing, planning, or brainstorming. Claude moderates; the user can steer between rounds.
---

Usage: `/council [--mode discuss|critique|plan] [--rounds N] [--roster codex,kexaone,claude-self] [--no-stop] <topic-or-question>`

Defaults:
- `--mode discuss` (divergent brainstorming)
- `--rounds 1` (run one round, then check in with the user; `--no-stop` proceeds automatically)
- `--roster codex,kexaone` (two members + moderator = you)

## Roster key → subagent mapping

| roster key | subagent_type | model / source | requires |
|---|---|---|---|
| `codex` | `codex:codex-rescue` | Codex | the `codex` plugin from the `openai-codex` marketplace |
| `kexaone` | `exaone-friendli:k-exaone` | K-EXAONE 236B / FriendliAI | the `exaone-friendli` plugin in this repo + a Friendli token |
| `claude-self` | `general-purpose` | Claude, fresh context | nothing |

`claude-self` is a Claude subagent with no memory of this conversation. It is a genuinely useful
member — it reads the prompt cold, so it catches assumptions the moderator has already absorbed —
but it is not an independent *model*. When the roster is `claude-self` alone, say so plainly in the
synthesis rather than presenting it as a multi-model result.

If a plugin is not installed, the corresponding subagent_type will not resolve. Drop that member,
warn once, and continue with the rest.

## Modes

| mode | purpose | flow |
|------|---------|------|
| `discuss` | brainstorming, generating options | each member answers independently → moderator synthesizes |
| `critique` | sharpening a draft | attach draft → each member critiques + offers alternatives → moderator proposes a merge |
| `plan` | reviewing an implementation plan | attach plan → each member names risks and gaps → moderator revises |

## Output

Each round is written to `output/council-{YYMMDD-HHMM}-{slug}/round-{N}.md`:

```
# Round N — {mode}
## Prompt
...
## Codex
...
## K-EXAONE
...
## Moderator Synthesis
...
## User Decision
(next round / finish / revised instruction)
```

Session state lives in `.claude/council-state.json` — current session dir, round number, mode,
roster, and the previous synthesis. This is what lets a council survive `/clear`.

## Procedure

1. **Parse arguments.** If no topic is given, ask the user (AskUserQuestion).

2. **Initialize the session** (first round only):
   - create `output/council-{YYMMDD-HHMM}-{slug}/`
   - initialize `.claude/council-state.json`:
     ```json
     {
       "version": 1,
       "session_dir": "output/council-260720-1530-cache-eviction-design",
       "mode": "discuss",
       "roster": ["codex", "kexaone"],
       "round": 0,
       "topic": "...",
       "attachments": [],
       "last_synthesis": null,
       "started_at": "2026-07-20T15:30:00+09:00",
       "status": "active"
     }
     ```
   - for `critique` / `plan`, require attachment paths. If none were given, ask.

3. **Compose the round prompt**:
   - `discuss`: the original topic + (if any) the previous round's synthesis
   - `critique`: the draft text + the previous critique synthesis
   - `plan`: the plan file + four review axes (feasibility / resources / risk / omissions)
   - Same base prompt for every member, plus a one-line role prefix per model:
     - Codex: "logic, technical accuracy, independent diagnosis"
     - K-EXAONE: "Korean-language phrasing and Korean-domain reasoning, practitioner's view"
     - Claude self: "cold read — what does this assume that it never states?"
   - Every prompt must be self-contained: subagents cannot see this conversation.

4. **Call members in parallel**: issue one Agent tool call per roster member **in the same
   message**. That parallelism is the point — serial calls waste the wall-clock and let earlier
   answers leak into later ones. Skip members not in the roster.

5. **Collect and synthesize**:
   - write all responses verbatim into `round-N.md` (one Write call)
   - as moderator, synthesize:
     - **agreements** (2–3)
     - **conflicts** (if any)
     - **recommended adoption** (concrete actions)
     - **deferred / needs more** (candidates for the next round)
   - append the synthesis to the same file and store it in `state.last_synthesis`.

6. **User checkpoint** (always, unless `--no-stop`; use AskUserQuestion):
   - one-screen summary: 1–2 lines per model, then 3–5 lines of synthesis
   - options: **next round** (previous synthesis feeds the next prompt) / **finish** (step 7) /
     **revised instruction** (free-form input folded into the next prompt)
   - record the choice in `round-N.md` under `## User Decision`.

7. **Finish**:
   - in **every** mode, write the final merge to `output/.../final.md` — even for `discuss`, where
     it is just the last synthesis
   - set `.claude/council-state.json` to `status: "archived"` and record `ended_at`
   - tell the user the path, plus one line: **"From here on, only `final.md` matters — attach
     `@output/.../final.md` in a follow-up session and skip the round files."**

## Effort escalation

Council rounds themselves run at the session's current effort; N members × M rounds is expensive,
so medium is the sensible default. Raise effort only at the moderator's heavy judgment moments.

At two points the moderator should suggest it regardless of other conditions — **before the first
round** and **before the final merge**:

> "[council bookend] Consider `model: opus` + `/effort xhigh` for this step — framing the topic
> (or merging the final answer) is where the return is largest. Middle rounds can stay at medium."

- **First round** — how the topic is interpreted and how the member prompts are written determines
  everything downstream.
- **Final round + final.md** — the one artifact the user actually reads. It has to be right once.

Also worth suggesting mid-council when:

1. the members conflict on a core axis and the moderator has to pick a side;
2. three rounds have passed without convergence (ask about cost at the same time);
3. the user's revised instruction is abstract ("go deeper", "get at the essence") and needs a
   meta-judgment.

Do **not** suggest it for ordinary `discuss` rounds (divergence is the goal), for the first
round's synthesis (too little information yet), or when the user is already at xhigh — in that
case just say "already at xhigh, proceeding" and move on.

The moderator cannot change effort itself; ask the user to type `/effort xhigh`, and after the
heavy step say once: "synthesis done — `/effort medium` is enough for the next round."

## Safeguards

- **Past three rounds**, confirm once: "cost is accumulating — keep going?"
- **If one member fails**, continue with the rest and name the failure in the synthesis
  ("Codex unavailable: <short error>"). Never substitute your own answer for a member's.
- **If an external CLI is missing or unauthenticated**, drop it from the roster with a warning.
- **If an attachment path is missing or unreadable**, do not start the round; ask for a correction.

## Examples

```
/council how should we shard this cache?
/council --mode critique docs/design/draft.md
/council --mode plan --rounds 2 docs/plans/migration.md
/council --roster codex,kexaone,claude-self --no-stop discuss API versioning strategy
```

## Resume

If `.claude/council-state.json` has `status: "active"`, calling `/council` with no arguments should
offer: "Session in progress: {session_dir} (round {N}). Continue?"
