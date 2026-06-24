#!/usr/bin/env python3
"""Randomly quiz questions from the Markdown question bank."""

from __future__ import annotations

import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_COUNT = 10
MIN_COUNT = 10
MAX_COUNT = 20
QUESTION_HEADING = re.compile(r"^## \d{4}-\d{2}-\d{2}：.+", re.MULTILINE)
ANSWER_MARKERS = (
    "**批改**",
    "**记住**",
)


@dataclass(frozen=True)
class Question:
    source: Path
    heading: str
    prompt: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_count(argv: list[str]) -> int:
    if len(argv) < 2:
        return DEFAULT_COUNT

    try:
        requested = int(argv[1])
    except ValueError:
        print(f"题目数量必须是数字，已使用默认值 {DEFAULT_COUNT}。")
        return DEFAULT_COUNT

    if requested < MIN_COUNT:
        print(f"题目数量最少是 {MIN_COUNT}，已按 {MIN_COUNT} 道处理。")
        return MIN_COUNT

    if requested > MAX_COUNT:
        print(f"题目数量最多是 {MAX_COUNT}，已按 {MAX_COUNT} 道处理。")
        return MAX_COUNT

    return requested


def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.glob("*.md")
        if path.name != "README.md" and path.is_file()
    )


def split_question_blocks(text: str) -> list[str]:
    matches = list(QUESTION_HEADING.finditer(text))
    blocks: list[str] = []

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append(text[start:end].strip())

    return blocks


def hide_answers(block: str) -> tuple[str, str]:
    lines = block.splitlines()
    heading = lines[0].removeprefix("## ").strip()
    body = "\n".join(lines[1:]).strip()

    cutoff = len(body)
    for marker in ANSWER_MARKERS:
        marker_index = body.find(marker)
        if marker_index != -1:
            cutoff = min(cutoff, marker_index)

    prompt = body[:cutoff].strip()
    if not prompt:
        prompt = "这道题没有找到可展示的问题内容，请回到原文件查看。"

    return heading, prompt


def load_questions(root: Path) -> list[Question]:
    questions: list[Question] = []

    for path in markdown_files(root):
        text = path.read_text(encoding="utf-8")
        for block in split_question_blocks(text):
            heading, prompt = hide_answers(block)
            questions.append(
                Question(
                    source=path.relative_to(root),
                    heading=heading,
                    prompt=prompt,
                )
            )

    return questions


def print_question(index: int, question: Question) -> None:
    print(f"## {index}. {question.heading}")
    print(f"来源：{question.source}")
    print()
    print(question.prompt)
    print()


def main(argv: list[str]) -> int:
    count = parse_count(argv)
    root = repo_root()
    questions = load_questions(root)

    if not questions:
        print("没有找到题目。请确认题库文件中使用了 `## YYYY-MM-DD：问题标题` 格式。")
        return 1

    if len(questions) < count:
        print(f"当前题库只有 {len(questions)} 道题，已展示全部题目。")
        count = len(questions)

    selected = random.sample(questions, count)

    print(f"# 随机抽题：{count} / {len(questions)}")
    print("先自己回答，再回到原文件查看 `批改` 和 `记住`。")
    print()

    for index, question in enumerate(selected, start=1):
        print_question(index, question)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
