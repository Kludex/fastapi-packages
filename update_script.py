import json
import os
from datetime import date
from typing import List

from dateutil import relativedelta
from github import Github
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style

GITHUB_URL = "http://github.com"
HEADERS = ("Package", "Description", "Created", "Last commit", "Stars")
DATE_FORMAT = "%B %d, %Y"

github_access_token = os.getenv("ACCESS_TOKEN_GITHUB")
g = Github(github_access_token)


def kludex_sort(table: List[List[str]]):
    return sorted(
        table,
        key=lambda x: (
            -x[HEADERS.index("Stars")] // 100,
            x[HEADERS.index("Last commit")],
        ),
    )


value_matrix = []
with open("package_list.json", "r") as f:
    for repo_full_name in json.load(f):
        repo = g.get_repo(repo_full_name)

        commits = repo.get_commits()
        last_commit_date = [commit.commit.author.date for commit in commits][0]

        month_diff = relativedelta.relativedelta(date.today(), last_commit_date).months
        value_matrix.append(
            [
                f"[{repo.name}]({repo.html_url})",
                repo.description,
                repo.created_at.strftime(DATE_FORMAT),
                month_diff,
                repo.stargazers_count,
            ]
        )

value_matrix = kludex_sort(value_matrix)
for value in value_matrix:
    idx = HEADERS.index("Last commit")
    month_diff = value[idx]
    value[idx] = "UTD" if month_diff < 2 else f"{month_diff} MA"
writer = MarkdownTableWriter(headers=HEADERS, value_matrix=value_matrix, margin=1)

writer.set_style(HEADERS.index("Package"), Style(align="center", font_weight="bold"))

with open("BEFORE_README.md", "r") as f:
    print(f.read())
writer.write_table(flavor="github")
