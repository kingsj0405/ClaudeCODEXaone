#!/usr/bin/env python3
"""Mechanical style check for an essay draft.

Catches the things a writer stops seeing after the third read: punctuation the renderer
chokes on, leftovers from the research phase, lecture tone, and hype.

    python3 lint.py <file.md> [more files...]

'고칠 것' (hard) are mechanical rule breaks and fail the run (exit 1).
'볼 것' (soft) are tone flags — read them, decide, move on. They never fail the run.
"""

import re
import sys

HARD = [
    ("금지문자", re.compile(r"[《》『』「」]"), "겹납표·홑납표는 쓰지 않는다. 따옴표로 바꾼다."),
    ("각주 마커", re.compile(r"\[\^[^\]]*\]"), "본문은 [1], 끝에 참고자료."),
    # 병기 패턴만 잡는다: 한글 뒤 괄호 속 한자 (`신독(愼獨)`). 원제 인용(`小學`)은 규칙 밖이다.
    ("한자 병기", re.compile(r"[가-힣]\s*\(\s*[\u3400-\u4dbf\u4e00-\u9fff]+\s*\)"), "한자 병기를 지운다(예: 신독(愼獨) → 신독)."),
    ("초안 잔재", re.compile(r"\[(확인 필요|리서치|검증 필요|TODO|TBD|작성 예정)"), "리서치 표로 옮기고 본문에서 지운다."),
]

SOFT = [
    ("훈계조", re.compile(r"(해야\s*합니다|하시기\s*바랍니다|해야\s*한다|명심해야|잊지\s*말아야|하지\s*마세요)"), "관찰이나 고백으로 바꾼다."),
    ("과장", re.compile(r"(매우\s|정말\s|완전히|혁신적|충격적|압도적|혁명적|경이로운)"), "형용사를 지우고 사실을 남긴다."),
    ("느낌표", re.compile(r"!"), "에세이에서는 거의 쓰지 않는다."),
]


def check(path):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        print(f"{path}: 읽을 수 없음 — {exc}")
        return 1

    lines = text.splitlines()

    # YAML frontmatter is metadata, not published text.
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break

    in_fence = False
    hard_hits = []
    soft_hits = []
    bold = 0

    for no, line in enumerate(lines[start:], start + 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue  # 코드 블록 안은 렌더링되는 산문이 아니다
        if line.lstrip().startswith(("![", "http://", "https://")):
            continue  # 이미지 대체텍스트·링크는 규칙 밖
        bold += len(re.findall(r"\*\*[^*]+\*\*", line))
        for name, pattern, advice in HARD:
            if pattern.search(line):
                hard_hits.append((no, name, advice, line.strip()[:120]))
        for name, pattern, advice in SOFT:
            if pattern.search(line):
                soft_hits.append((no, name, advice, line.strip()[:120]))

    print(f"\n{path}  ({len(lines)}줄)")

    if bold > 3:
        soft_hits.append((0, "볼드 과다", "한 화면에 세 개 이하.", f"{bold}개"))

    if not hard_hits and not soft_hits:
        print("  ✓ 걸린 것 없음")
        return 0

    for no, name, advice, text in hard_hits:
        where = f"{no}:" if no else ""
        print(f"  ✗ {where}{name} — {text}\n      → {advice}")
    for no, name, advice, text in soft_hits:
        where = f"{no}:" if no else ""
        print(f"  ⚠ {where}{name} — {text}\n      → {advice}")

    print(f"  합계: 고칠 것 {len(hard_hits)}개, 볼 것 {len(soft_hits)}개")
    return 1 if hard_hits else 0


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    status = 0
    for path in argv:
        status |= check(path)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
