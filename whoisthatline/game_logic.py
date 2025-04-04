import os
import random
import subprocess
from pathlib import Path


def select_code_snippet(repo_path: str) -> tuple[list[str] | None, str | None]:
    files: list[str] = []
    for root, _, filenames in os.walk(repo_path):
        for filename in filenames:
            if filename.endswith(".go"):
                files.append(os.path.join(root, filename))

    while files:
        file_path = random.choice(files)
        with open(file_path, "r") as file:
            lines = file.readlines()

        if len(lines) < 10:
            files.remove(file_path)
            continue

        start_line = random.randint(0, len(lines) - 10)
        code_snippet: list[str] | None = lines[start_line : start_line + 10]

        authors = get_authors(file_path, start_line, start_line + 10)
        if len(authors) == 1:
            return code_snippet, authors[0]
        elif len(authors) > 1:
            code_snippet, author = select_fewer_lines(
                file_path, lines, start_line, start_line + 10
            )
            if code_snippet:
                return code_snippet, author

        files.remove(file_path)

    return None, None


def get_authors(file_path: str, start_line: int, end_line: int) -> list[str]:
    result = subprocess.run(
        ["git", "blame", "-L", f"{start_line + 1},{end_line}", file_path],
        cwd=Path(file_path).parent,
        capture_output=True,
        text=True,
    )
    lines = result.stdout.split("\n")
    authors: set[str] = set()
    for line in lines:
        if line:
            author = line.split("(")[1].split(" ")[0]
            authors.add(author)
    return list(authors)


def select_other_members(repo_path: str, author: str) -> list[str]:
    result = subprocess.run(
        ["git", "shortlog", "-s", "-n"], cwd=repo_path, capture_output=True, text=True
    )
    lines = result.stdout.split("\n")
    members = [line.split("\t")[1] for line in lines if line]
    if author in members:
        members.remove(author)
    return random.sample(members, min(3, len(members)))


def handle_multiline_comments(code_snippet: list[str]) -> list[str]:
    return code_snippet


def handle_multiple_authors(repo_path: str) -> tuple[list[str] | None, str | None]:
    return select_code_snippet(repo_path)


def select_fewer_lines(
    file_path: str, lines: list[str], start_line: int, end_line: int
) -> tuple[list[str] | None, str | None]:
    for length in range(9, 0, -1):
        for i in range(start_line, end_line - length + 1):
            snippet = lines[i : i + length]
            authors = get_authors(file_path, i, i + length)
            if len(authors) == 1:
                return snippet, authors[0]
    return None, None
