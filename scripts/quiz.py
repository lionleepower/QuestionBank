#!/usr/bin/env python3
"""Randomly quiz questions from the Markdown question bank."""

from __future__ import annotations

import random
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


DEFAULT_COUNT = 10
MIN_COUNT = 10
MAX_COUNT = 20
OUTPUT_DIR = "quizzes"
QUESTION_HEADING = re.compile(r"^## (?:\d{4}-\d{2}-\d{2}：|\d{3}\. ).+")
FENCE_START = re.compile(r"^\s*(```|~~~)")
STRUCTURED_ANSWER_MARKERS = (
    "**我的回答**",
    "**我的理解 / 回答**",
    "**批改**",
    "**记住**",
)
ANSWER_MARKERS = (
    "**我的回答**",
    "**我的理解 / 回答**",
    "**批改**",
    "**记住**",
)


@dataclass(frozen=True)
class Question:
    source: Path
    heading: str
    prompt: str
    answer: str


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


def question_heading_offsets(text: str) -> list[int]:
    offsets: list[int] = []
    in_fence = False
    offset = 0

    for line in text.splitlines(keepends=True):
        if FENCE_START.match(line):
            in_fence = not in_fence
        elif not in_fence and QUESTION_HEADING.match(line):
            offsets.append(offset)

        offset += len(line)

    return offsets


def split_question_blocks(text: str) -> list[str]:
    offsets = question_heading_offsets(text)
    blocks: list[str] = []

    for index, start in enumerate(offsets):
        end = offsets[index + 1] if index + 1 < len(offsets) else len(text)
        blocks.append(text[start:end].strip())

    return blocks


def split_prompt_and_answer(block: str) -> tuple[str, str, str]:
    lines = block.splitlines()
    heading = lines[0].removeprefix("## ").strip()
    body = "\n".join(lines[1:]).strip()

    if not any(marker in body for marker in STRUCTURED_ANSWER_MARKERS):
        prompt = "请根据题目作答。"
        answer = body or "这道题没有找到答案内容，请回到原文件查看。"
        return heading, prompt, answer

    cutoff = len(body)
    for marker in ANSWER_MARKERS:
        marker_index = body.find(marker)
        if marker_index != -1:
            cutoff = min(cutoff, marker_index)

    prompt = body[:cutoff].strip()
    if not prompt:
        prompt = "请根据题目作答。"

    answer = body
    if not answer:
        answer = "这道题没有找到答案内容，请回到原文件查看。"

    return heading, prompt, answer


def load_questions(root: Path) -> list[Question]:
    questions: list[Question] = []

    for path in markdown_files(root):
        text = path.read_text(encoding="utf-8")
        for block in split_question_blocks(text):
            heading, prompt, answer = split_prompt_and_answer(block)
            questions.append(
                Question(
                    source=path.relative_to(root),
                    heading=heading,
                    prompt=prompt,
                    answer=answer,
                )
            )

    return questions


def question_block(index: int, question: Question) -> str:
    return "\n".join(
        [
            f"## {index}. {question.heading}",
            f"来源：{question.source}",
            "",
            question.prompt,
            "",
        ]
    )


def answer_block(index: int, question: Question) -> str:
    return "\n".join(
        [
            f"## {index}. {question.heading}",
            f"来源：{question.source}",
            "",
            question.answer,
            "",
        ]
    )


def output_paths(root: Path) -> tuple[Path, Path]:
    output_dir = root / OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)

    today = date.today().isoformat()
    suffix = ""
    counter = 1

    while True:
        questions_path = output_dir / f"{today}{suffix}_questions.md"
        answers_path = output_dir / f"{today}{suffix}_answers.md"

        if not questions_path.exists() and not answers_path.exists():
            return questions_path, answers_path

        counter += 1
        suffix = f"_{counter}"


def render_questions(selected: list[Question], total: int) -> str:
    parts = [
        f"# 随机抽题：{len(selected)} / {total}",
        "",
        "先自己回答，再打开答案文件查看 `批改` 和 `记住`。",
        "",
    ]

    for index, question in enumerate(selected, start=1):
        parts.append(question_block(index, question))

    return "\n".join(parts).rstrip() + "\n"


def render_answers(selected: list[Question], total: int) -> str:
    parts = [
        f"# 随机抽题答案：{len(selected)} / {total}",
        "",
        "这个文件保存对应题目的答案、批改和记忆重点。",
        "",
    ]

    for index, question in enumerate(selected, start=1):
        parts.append(answer_block(index, question))

    return "\n".join(parts).rstrip() + "\n"


def write_quiz_files(root: Path, selected: list[Question], total: int) -> tuple[Path, Path]:
    questions_path, answers_path = output_paths(root)
    questions_path.write_text(render_questions(selected, total), encoding="utf-8")
    answers_path.write_text(render_answers(selected, total), encoding="utf-8")
    return questions_path, answers_path


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
    questions_path, answers_path = write_quiz_files(root, selected, len(questions))

    print(f"已生成随机抽题：{count} / {len(questions)}")
    print(f"题目文件：{questions_path.relative_to(root)}")
    print(f"答案文件：{answers_path.relative_to(root)}")
    print("先打开题目文件作答，再打开答案文件检查。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
