import os
import pathlib
import random
import subprocess


def select_code_snippet(repo_path):
    files = []
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
        code_snippet = lines[start_line : start_line + 10]

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


def get_authors(file_path, start_line, end_line):
    result = subprocess.run(
        ["git", "blame", "-L", f"{start_line + 1},{end_line}", file_path],
        cwd=pathlib.Path(file_path).parent,
        capture_output=True,
        text=True,
    )
    lines = result.stdout.split("\n")
    authors = set()
    for line in lines:
        if line:
            author = line.split("(")[1].split(" ")[0]
            authors.add(author)
    return list(authors)


def select_other_members(repo_path, author):
    result = subprocess.run(
        ["git", "shortlog", "-s", "-n"], cwd=repo_path, capture_output=True, text=True
    )
    lines = result.stdout.split("\n")
    members = [line.split("\t")[1] for line in lines if line]
    if author in members:
        members.remove(author)
    return random.sample(members, 3)


def handle_multiline_comments(code_snippet):
    return code_snippet


def handle_multiple_authors(repo_path):
    return select_code_snippet(repo_path)


def select_fewer_lines(file_path, lines, start_line, end_line):
    for length in range(9, 0, -1):
        for i in range(start_line, end_line - length + 1):
            snippet = lines[i : i + length]
            authors = get_authors(file_path, i, i + length)
            if len(authors) == 1:
                return snippet, authors[0]
    return None, None
