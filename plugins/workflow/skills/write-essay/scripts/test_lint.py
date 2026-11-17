#!/usr/bin/env python3
"""Tests for lint.py — the two bugs this file froze, plus the four hard rules.

    python3 test_lint.py

Not coverage: if a rule is added or a regex is narrowed, these six cases say whether
the parser still separates hard fails, passes, and code fences the way the skill assumes.
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.join(HERE, "lint.py")


def run(body):
    """Write body to a temp .md file and return (exit code, output)."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as f:
        f.write(body)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, LINT, path],
            capture_output=True,
            text=True,
        )
        return proc.returncode, proc.stdout + proc.stderr
    finally:
        os.unlink(path)


def expect_fail(body, rule):
    code, out = run(body)
    assert code == 1, f"하드 규칙이 exit 0으로 통과했다: {rule}\n{out}"
    assert rule in out, f"'{rule}'이 잡히지 않았다\n{out}"


def expect_pass(body, what):
    code, out = run(body)
    assert code == 0, f"{what}: 하드 위반 0이어야 하는데 exit {code}\n{out}"


# 1. 금지문자 (하드)
expect_fail("그는 《중용》을 읽었다.\n", "금지문자")

# 2. 한자 병기 (하드) — 규칙이 실제로 금지하는 모양
expect_fail("그는 신독(愼獨)을 말했다.\n", "한자 병기")

# 3. 원제 인용 (통과해야 함) — 이 스킬의 대표 예시 주제가 소학이다
expect_pass("수능을 앞둔 사람에게 小學을 권한다.\n", "원제 인용")

# 4. 각주 마커 (하드)
expect_fail("수능은 대학이 아니라 소학이다.[^1]\n", "각주 마커")

# 5. 코드 펜스 안 (통과해야 함) — 렌더링되지 않는 예시는 검사 대상이 아니다
expect_pass(
    "본문은 깨끗하다.\n\n```python\nprint(\"《코드 안》 愼獨(愼獨)\")\n```\n",
    "코드 펜스 안",
)

# 6. 깨끗한 파일 (통과해야 함)
expect_pass("# 제목\n\n수능이 사흘 남았습니다. 준비하는 시간은 대학이 아니라 소학입니다.\n", "깨끗한 파일")

print("✓ test_lint.py — 6개 케이스 모두 통과")
