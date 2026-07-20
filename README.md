# ClaudeCODEXaone (클코덱사원)

Claude Code 안에서 **Claude · Codex · K-EXAONE** 세 모델을 함께 쓰기 위한 플러그인 묶음.

- `/k-exaone` — K-EXAONE 236B(LG AI Research, FriendliAI 서빙)에게 물어본다
- `/council` — 여러 모델을 라운드 단위로 돌리고 Claude가 사회를 본다
- `korean-report` 스킬 — 영어 초안을 **좋은 한국어 리포트**로 다시 쓴다

> 개인이 만든 비공식 프로젝트입니다. Anthropic · OpenAI · LG AI Research · FriendliAI 어디와도
> 제휴 관계가 없고, 각 상표는 해당 소유자의 것입니다.

---

## 왜 모델을 섞나

Claude Code는 혼자서도 잘 하지만, 두 가지 상황에서 다른 모델을 붙이면 결과가 눈에 띄게 달라진다.

**첫째, 한국어.** 한국어 문서·주석·네이밍을 다룰 때, 그리고 한국 맥락의 도메인 추론이 필요할 때
한국어를 주 언어로 학습한 모델의 감각이 더 낫다. `/k-exaone`은 그 자리를 위한 것이다.

**둘째, 독립적인 두 번째 의견.** 같은 모델에게 "다시 검토해줘"라고 하면 대개 자기 답을 방어한다.
설계를 검토하거나 초안을 다듬을 때는 서로 다른 계열의 모델에게 **동시에, 서로 모르게** 물어보고
그 차이를 보는 편이 훨씬 유용하다. `/council`이 그 절차를 자동화한다.

---

## K-EXAONE 236B — 이 플러그인이 부르는 모델

[K-EXAONE](https://github.com/LG-AI-EXAONE/K-EXAONE)은 LG AI Research가 공개한 대규모
Mixture-of-Experts 모델이다. 존재 자체가 아직 널리 알려지지 않아 짧게 소개해 둔다.

| | |
|---|---|
| 구조 | Hybrid Attention MoE — 총 236B 파라미터, 추론 시 23B 활성 |
| 컨텍스트 | 256K 네이티브 (FriendliAI 서빙 기준 262,144 토큰) |
| 언어 | 한국어 · 영어 · 스페인어 · 독일어 · 일본어 · 베트남어 |
| 강점 | 추론, 에이전트형 도구 사용, 긴 문서 이해, 한국어 |
| 가중치 | [huggingface.co/LGAI-EXAONE/K-EXAONE-236B-A23B](https://huggingface.co/LGAI-EXAONE/K-EXAONE-236B-A23B) |
| 서빙 | [FriendliAI Serverless](https://friendli.ai/models/LGAI-EXAONE/K-EXAONE-236B-A23B) |

3:1 하이브리드 어텐션에 128토큰 슬라이딩 윈도를 써서 긴 문서를 읽을 때 메모리를 아끼는 구조라,
긴 설계 문서나 로그를 한 번에 통째로 넣고 물어보는 용도로 쓸 만하다.

**요금**은 FriendliAI 모델 페이지에 공개되어 있다 (2026년 7월 확인 기준 입력 100만 토큰당
$0.2, 캐시된 입력 $0.1, 출력 $0.8 — 최신 값은 위 링크에서 확인할 것). 별도 인프라 없이
OpenAI 호환 API로 바로 부를 수 있다.

### FriendliAI 문서

- [Model APIs 시작하기](https://friendli.ai/docs/guides/model-apis/introduction) — 서버리스 API 사용법
- [Dedicated Endpoints](https://friendli.ai/docs/guides/dedicated-endpoints/introduction) — 전용 엔드포인트가 필요할 때
- [Container](https://friendli.ai/docs/guides/container/introduction) — 자체 인프라에 올릴 때
- [K-EXAONE 서버리스 출시 글](https://friendli.ai/blog/k-exaone-on-serverless)

플러그인을 깔기 전에 API가 살아 있는지 먼저 확인하고 싶다면:

```bash
curl https://api.friendli.ai/serverless/v1/chat/completions \
  -H "Authorization: Bearer $FRIENDLI_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "LGAI-EXAONE/K-EXAONE-236B-A23B",
    "messages": [{"role": "user", "content": "자기소개를 두 문장으로 해줘."}]
  }'
```

토큰은 [FriendliAI 콘솔](https://friendli.ai/)에서 발급한다.

---

## 설치

### 1. 사전 요구사항

이 저장소의 플러그인은 [opencode](https://opencode.ai) CLI를 통해 K-EXAONE을 호출한다.

```bash
npm install -g opencode-ai
```

### 2. 마켓플레이스 등록 + 설치

```bash
claude plugin marketplace add https://github.com/kingsj0405/ClaudeCODEXaone.git
claude plugin install exaone-friendli
claude plugin install workflow
```

### 3. Codex 플러그인 (선택)

`/council`의 기본 roster에는 Codex가 들어 있다. Codex를 부르려면 OpenAI가 공식 배포하는
[**openai/codex-plugin-cc**](https://github.com/openai/codex-plugin-cc)를 따로 설치해야
한다. 이 저장소에는 포함되어 있지 않다.

```bash
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex
```

설치하면 `codex:codex-rescue` 서브에이전트가 생기고, `/council`이 이걸 통해 Codex를 부른다.
[Codex CLI](https://github.com/openai/codex) 로그인이 되어 있어야 실제로 응답한다.

**Codex가 없어도 나머지는 그대로 동작한다** — `/council`이 roster에서 알아서 빼고 한 번
경고한 뒤 진행한다. Codex 없이 쓰려면 `--roster kexaone,claude-self`처럼 명시해도 된다.

### 4. opencode provider 설정

opencode는 **글로벌 설정**(`~/.config/opencode/opencode.json`)만 참조한다. 프로젝트 로컬
`opencode.jsonc`만 두면 동작하지 않는다.

이 저장소의 [`opencode.json.template`](./opencode.json.template)을 복사하고
`<YOUR_FRIENDLI_TOKEN>`을 본인 토큰으로 바꾼다. 이미 쓰던 설정이 있다면 `provider` 블록만
합치면 된다:

```jsonc
"friendli": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Friendli AI",
  "options": {
    "baseURL": "https://api.friendli.ai/serverless/v1",
    "apiKey": "<YOUR_FRIENDLI_TOKEN>"
  },
  "models": {
    "LGAI-EXAONE/K-EXAONE-236B-A23B": {
      "name": "K-EXAONE 236B",
      "limit": { "context": 262144, "output": 32768 }
    }
  }
}
```

> 조직 계정이라 팀 지정이 필요하다면 `options.headers`에 `"X-Friendli-Team": "<TEAM_ID>"`를
> 추가한다. 개인 토큰은 대개 필요 없다.

### 플러그인 설치가 막힐 때

`claude plugin` 명령을 쓸 수 없는 환경이면 수동 설치를 쓴다. `~/.claude/` 아래에 agents,
commands, scripts, skills를 복사한다.

```bash
git clone https://github.com/kingsj0405/ClaudeCODEXaone.git
cd ClaudeCODEXaone
bash install.sh
```

---

## 쓰는 법

### `/k-exaone` — 두 번째 의견

```
/k-exaone 이 함수의 네이밍이 한국어 도메인 용어랑 안 맞는 것 같은데 대안 좀 줘
/k-exaone --file docs/design.md 이 설계에서 빠진 예외 상황을 짚어줘
```

Claude가 직접 답하지 않고 K-EXAONE의 출력을 그대로 가져온다. **실패하면 Claude가 대신
답하지 않고 오류를 그대로 보여준다** — 다른 모델의 의견을 구했는데 조용히 같은 모델의 답이
돌아오면 의견을 구한 의미가 없기 때문이다.

### `/council` — 여러 모델을 라운드로 돌리기

```
/council 이 캐시를 어떤 기준으로 샤딩해야 할까
/council --mode critique docs/design/draft.md
/council --mode plan --rounds 2 docs/plans/migration.md
/council --roster codex,kexaone,claude-self --no-stop discuss API 버저닝 전략
```

한 라운드마다 roster의 모델을 **병렬로** 호출하고, Claude가 사회자로서 공통점 · 충돌점 ·
채택 권장 · 보류 항목으로 종합한다. 라운드 사이마다 사용자가 방향을 틀 수 있고, 결과는
`output/council-{시각}-{슬러그}/round-N.md`에 쌓인다. 끝나면 `final.md` 한 장이 떨어지므로
후속 세션에서는 그것만 첨부하면 된다.

roster 키는 세 가지다.

| 키 | 누구 | 필요한 것 |
|---|---|---|
| `codex` | Codex | [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) 별도 설치 ([설치 3단계](#3-codex-플러그인-선택)) |
| `kexaone` | K-EXAONE 236B | 이 저장소의 `exaone-friendli` 플러그인 + Friendli 토큰 |
| `claude-self` | Claude (빈 컨텍스트) | 없음 |

`claude-self`는 이 대화를 못 본 Claude 서브에이전트라 사회자가 이미 받아들인 전제를 되묻는
역할을 한다 — 유용하지만 독립된 *모델*은 아니므로 종합할 때 그렇게 표시된다.

`.claude/council-state.json`에 상태가 남아서 `/clear` 이후에도 이어갈 수 있다.

### `korean-report` 스킬 — 영어 초안을 한국어 리포트로

"이 영어 노트를 한국어 리포트로 정리해줘"처럼 요청하면 자동으로 불린다.

번역이 아니라 **다시 쓰기**다. 영어 초안은 배경부터 시작해 결론이 맨 끝에 붙는데, 한국어
리포트는 결론이 앞에 와야 읽힌다. 스킬은 원문에서 주장·근거·한계·미확정을 먼저 뽑아내고,
한국어 리포트 구조로 재배치한 뒤, 아홉 가지 문체 기준으로 문장을 다시 쓴다.

기준을 요약하면 — 결론을 앞에 두고, 영어 낱말을 문장에 그대로 박지 않되 분야 표준어는
남기고, 약칭은 첫 등장에 풀고, 판정을 한 단어 딱지로 하지 않고, **모든 숫자에 측정 조건을
붙이고**, 영어 어순 직역투를 피하고, 인용문에는 번역을 병기하고, 강조를 아끼고, 논증을
불릿으로 자르지 않는다.

실제로 어느 정도까지 손대는지는
[예시 파일](./plugins/workflow/skills/korean-report/references/example-before-after.md)에
영어 초안 한 편과 그 결과물이 나란히 들어 있다.

#### HTML 리포트

HTML로 달라고 하면 [단일 파일 템플릿](./plugins/workflow/skills/korean-report/assets/report-template.html)에
본문을 채워 준다 — 외부 자원을 전혀 안 불러오고 밝은 화면과 어두운 화면을 모두 지원해서
파일 하나를 그대로 첨부해 보낼 수 있다.

실제로 채워진 결과물이
[`examples/example-report.html`](./plugins/workflow/skills/korean-report/examples/example-report.html)에
들어 있다. GitHub·GitLab은 저장소 안의 `.html`을 렌더링하지 않고 소스로만 보여주므로,
브라우저에서 바로 보려면 아래 미리보기 링크를 쓴다.

- **[▶ 예시 리포트 미리보기 (raw.githack.com)](https://raw.githack.com/kingsj0405/ClaudeCODEXaone/main/plugins/workflow/skills/korean-report/examples/example-report.html)**
- [같은 파일 · htmlpreview.github.io 경유](https://htmlpreview.github.io/?https://github.com/kingsj0405/ClaudeCODEXaone/blob/main/plugins/workflow/skills/korean-report/examples/example-report.html)

두 링크 모두 제3자 서비스가 이 저장소의 원본 파일을 대신 서빙하는 방식이라 별도 설정이
필요 없다. 다만 서비스가 죽으면 링크도 죽으므로, 확실한 방법은 파일을 받아서 브라우저로
직접 여는 것이다:

```bash
git clone https://github.com/kingsj0405/ClaudeCODEXaone.git
open ClaudeCODEXaone/plugins/workflow/skills/korean-report/examples/example-report.html
```

> 사내 GitLab 등 외부에서 접근할 수 없는 저장소에 두면 위 미리보기 서비스는 파일을 못
> 읽는다. 그런 곳에서는 clone 후 로컬에서 열거나, GitHub Pages / GitLab Pages를 켜서
> 직접 서빙해야 한다.

---

## 구조

```
ClaudeCODEXaone/
├── .claude-plugin/marketplace.json
├── opencode.json.template          # Friendli provider 설정 견본
├── install.sh                      # 플러그인 시스템을 못 쓸 때
└── plugins/
    ├── exaone-friendli/            # /k-exaone
    │   ├── agents/k-exaone.md
    │   ├── commands/k-exaone.md
    │   └── scripts/opencode_run.sh
    └── workflow/
        ├── commands/council.md     # /council
        └── skills/korean-report/   # SKILL.md + 예시 + HTML 템플릿
```

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `Unknown command` | 플러그인 미설치 | `claude plugin install exaone-friendli workflow` |
| `opencode CLI not found` | opencode 미설치 | `npm install -g opencode-ai` |
| `Model not found` | 글로벌 opencode 설정에 provider 미등록 | `~/.config/opencode/opencode.json` 확인 (프로젝트 로컬 파일은 안 읽힘) |
| 401 Unauthorized | 토큰 만료, 또는 조직 계정인데 팀 헤더 누락 | 토큰 재발급 / `X-Friendli-Team` 추가 |
| `ProviderModelNotFoundError` | Claude Code 환경변수가 opencode 모델을 덮어씀 | 래퍼가 `--model`을 강제 주입하므로 재실행 |
| 사내 프록시 뒤에서 TLS 오류 | TLS 검사 프록시가 자체 루트 CA를 주입 | `NODE_EXTRA_CA_CERTS`에 프록시 루트 CA를 지정. 최후 수단으로 `OPENCODE_INSECURE_TLS=1` (인증서 검증이 꺼지므로 권장하지 않음) |
| `/council`에서 Codex가 빠짐 | codex 플러그인 미설치 | `claude plugin install codex` 또는 그대로 진행 |

## 라이선스

Apache-2.0. 이 저장소가 호출하는 모델과 서비스에는 각자의 약관과 라이선스가 적용된다 —
[K-EXAONE](https://huggingface.co/LGAI-EXAONE/K-EXAONE-236B-A23B),
[FriendliAI](https://friendli.ai/), [opencode](https://opencode.ai),
[codex-plugin-cc](https://github.com/openai/codex-plugin-cc) (Apache-2.0).

---

## English summary

**ClaudeCODEXaone** bundles three things for Claude Code users:

- **`/k-exaone`** — delegate a prompt to [K-EXAONE 236B](https://friendli.ai/models/LGAI-EXAONE/K-EXAONE-236B-A23B),
  LG AI Research's 236B Hybrid-Attention MoE model (23B active, 256K context, strong Korean),
  served on FriendliAI's serverless API and routed through the [opencode](https://opencode.ai) CLI.
- **`/council`** — run Codex, K-EXAONE, and a cold-context Claude in parallel over N rounds, with
  Claude moderating and the user steering between rounds. Output lands in one `final.md`.
- **`korean-report`** — a skill that rewrites an English draft as a proper Korean report:
  conclusion first, every number attached to its measurement conditions, English terms unpacked
  except where they are the field's standard vocabulary. Ships with a worked before/after example
  and a self-contained HTML template.

Install: `claude plugin marketplace add https://github.com/kingsj0405/ClaudeCODEXaone.git`, then
`claude plugin install exaone-friendli workflow`. You will need `npm i -g opencode-ai` and a
FriendliAI token. To include Codex in `/council`, also install OpenAI's
[codex-plugin-cc](https://github.com/openai/codex-plugin-cc) — it is not bundled here, and
`/council` simply drops Codex from the roster if it is missing. See [설치](#설치) above.

Unofficial personal project; not affiliated with Anthropic, OpenAI, LG AI Research, or FriendliAI.
