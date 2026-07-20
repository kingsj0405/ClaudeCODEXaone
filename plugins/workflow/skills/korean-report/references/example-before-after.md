# 예시 — 영어 초안과 한국어 리포트

아래 내용은 **이 스킬을 설명하기 위해 지어낸 가상의 실험**이다. 실제 제품이나 측정치가 아니다.

---

## 입력 (영어 초안)

전형적인 형태다. 배경부터 시작하고, 명사구가 길고, 숫자가 조건 없이 떠다니고, 결론이 맨 끝에
한 줄로 붙어 있다.

```markdown
# Prefetch Experiment Notes

## Background

Our search service performs a synchronous index lookup on every request. Prior profiling
suggested that the tail latency is dominated by cold cache misses on the posting-list shards,
which motivated an investigation into speculative prefetching as a mitigation strategy for the
observed p99 degradation under bursty traffic.

## Method

We implemented a prefetcher that, upon receiving a query, issues asynchronous reads for the
shards predicted by a simple bigram model trained on one week of production query logs. The
prefetcher was evaluated in a shadow deployment against a control group. Note that the shadow
environment has roughly 40% of production traffic volume.

## Results

Prefetching improved p99 latency by 23%. p50 was essentially unchanged. Cache hit rate went
from 71% to 88%. However, we observed a 2.4x increase in read IOPS on the storage tier, and
during one 15-minute window the storage tier hit its provisioned IOPS ceiling, at which point
p99 for the prefetch group became *worse* than control.

An ablation removing the bigram model (prefetching a fixed set of the most popular shards
instead) recovered most of the benefit — p99 improved 19% — at 1.6x IOPS.

## Discussion

It is worth noting that the IOPS headroom question is the central blocker here. The bigram
model is not obviously worth its provenance and maintenance cost given the ablation result.

## Conclusion

Prefetching works but is IOPS-bound. Recommend proceeding with the static variant.
```

---

## 출력 (한국어 리포트)

같은 사실을 하나도 빼지 않았지만, 결론이 앞으로 나오고, 숫자마다 조건이 붙고, 영어 낱말이
풀렸고, 논증이 문단으로 이어진다.

```markdown
# 검색 인덱스 미리 읽기 실험 결과

## 결론

미리 읽기(prefetch)는 꼬리 지연을 확실히 줄이지만, 줄어든 지연을 저장 계층의 읽기 IOPS로
사는 구조다. 따라서 **IOPS 여유가 있을 때만 이득**이고, 여유가 없으면 오히려 손해가 난다.
바이그램 예측 모델을 쓰지 않고 인기 샤드 고정 목록만 미리 읽는 단순한 방식이 이득의 대부분을
가져오면서 IOPS 부담은 훨씬 적었다. 이 단순한 쪽으로 진행할 것을 권한다.

## 배경

검색 서비스는 요청마다 인덱스를 동기로 조회한다. 이전 프로파일링에서 꼬리 지연(p99)의 대부분이
포스팅 리스트 샤드의 캐시 미스에서 나온다는 것이 확인됐고, 특히 트래픽이 몰릴 때 p99가
나빠졌다. 이 실험은 그 미스를 미리 읽기로 줄일 수 있는지 확인한 것이다.

## 방법

질의가 들어오면 어떤 샤드를 읽게 될지 예측해, 실제로 필요해지기 전에 비동기로 읽어 두는
장치를 붙였다. 예측에는 프로덕션 질의 로그 1주일치로 학습한 바이그램 모델을 썼다.

평가는 섀도 환경에서 대조군과 비교하는 방식으로 했다. **섀도 환경의 트래픽은 프로덕션의 약
40% 수준**이므로, 아래 IOPS 관련 수치는 프로덕션에서 그대로 재현되지 않는다.

## 결과

바이그램 모델을 쓴 미리 읽기는 대조군 대비 p99 지연을 23% 줄였고, 캐시 적중률은 71%에서
88%로 올랐다. p50은 사실상 변화가 없었다 — 미리 읽기는 평균이 아니라 꼬리를 고치는 장치이므로
예상된 결과다.

대신 저장 계층의 읽기 IOPS가 2.4배로 뛰었다. 실험 중 15분 동안 저장 계층이 할당된 IOPS
상한에 닿았고, **그 구간에서는 미리 읽기 쪽 p99가 대조군보다 오히려 나빴다.**

바이그램 모델을 빼고 가장 많이 쓰이는 샤드의 고정 목록만 미리 읽어 보니, p99는 19% 줄었고
IOPS는 1.6배에 그쳤다. 즉 모델이 만들어 낸 추가 이득은 p99 4%p인데, 그 대가로 IOPS가 0.8배
더 들었다.

| 구성 | p99 개선 | 캐시 적중률 | 읽기 IOPS |
|---|---|---|---|
| 대조군 (미리 읽기 없음) | — | 71% | 1.0배 |
| 바이그램 모델 예측 | 23% | 88% | 2.4배 |
| 인기 샤드 고정 목록 | 19% | (미측정) | 1.6배 |

## 해석

숫자가 말하는 것은 "미리 읽기가 빠르다"가 아니라 **"미리 읽기는 IOPS를 지연으로 바꾸는
환율이고, 그 환율이 구성마다 다르다"**는 것이다. 바이그램 모델의 환율은 고정 목록보다 나쁘다.
모델을 학습시키고 계속 갱신하는 비용까지 더하면 차이는 더 벌어진다.

상한에 닿았을 때 p99가 대조군보다 나빠졌다는 관측이 특히 중요하다. 이 방식은 여유가 없을 때
성능이 완만하게 나빠지는 게 아니라 이득이 뒤집힌다. 프로덕션에 넣는다면 IOPS 사용률을 보고
미리 읽기를 자동으로 끄는 장치가 함께 있어야 한다.

## 한계와 다음

섀도 환경 트래픽이 프로덕션의 40%였으므로 **프로덕션에서 IOPS 상한에 얼마나 자주 닿을지는
이 실험으로 알 수 없다.** 고정 목록 구성의 캐시 적중률은 재지 않았다. 다음으로 할 일은
프로덕션 IOPS 여유를 실측하고, 그 위에서 고정 목록 구성만 다시 재는 것이다.
```

---

## 이 예시에서 실제로 일어난 변화

무엇을 바꿨는지 항목으로 정리하면 이렇다.

- **결론이 맨 끝 한 줄에서 맨 앞 한 문단으로 올라왔다.** 영어 초안의 "Conclusion"은 두 문장이었지만,
  본문 곳곳에 흩어져 있던 판단(IOPS가 병목, 모델은 값을 못 함)을 모으니 문단이 됐다.
- **`headroom`, `blocker`, `provenance`, `ablation`은 풀었고 `p99`, `IOPS`, `bigram`은 남겼다.**
  뒤의 셋은 이 분야 사람이 한국어로 말할 때도 그대로 쓰는 말이다. `prefetch`는 "미리 읽기"로
  풀되 첫 등장에 원어를 괄호로 병기했다.
- **"섀도 환경은 프로덕션의 40%"가 방법 절의 각주에서 본문 볼드로 올라왔다.** 원문에서는
  "Note that…"으로 흘려 놓았지만, 이 사실은 뒤의 IOPS 수치 전체의 해석을 바꾼다.
- **표가 새로 생겼다.** 원문 산문에 흩어져 있던 세 구성의 수치를 모았다. 원문에 없던 숫자는
  넣지 않았고, 재지 않은 칸은 "(미측정)"으로 남겼다.
- **바이그램 모델의 추가 이득을 "4%p / IOPS 0.8배"로 명시했다.** 원문은 두 실험 결과를 각각
  적어 놓기만 했고 차이를 계산해 주지 않았다. 뺄셈은 원문의 사실에서 바로 나오므로 추가해도
  안전하다 — 원문에 없는 *주장*을 만든 게 아니라 이미 있는 두 숫자를 나란히 놓은 것이다.
- **"IOPS 여유가 없으면 이득이 뒤집힌다"가 해석 절에서 별도 문단이 됐다.** 원문에서는 결과
  절 안의 종속절("at which point…")에 묻혀 있었는데, 운영에 넣을지 결정하는 사람에게는 이게
  가장 중요한 한 줄이다.
