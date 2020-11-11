import json
import os
from datetime import date
from typing import List

from dateutil import relativedelta
from github import Github
from pytablewriter import MarkdownTableWriter


def kludex_sort(table: List[List[str]]):
    return sorted(
        table,
        key=lambda x: (
            -x[HEADERS.index("Stars")] // 100,
            x[HEADERS.index("Last commit")],
        ),
    )


GITHUB_URL = "http://github.com"
HEADERS = ("Package", "Description", "Created at", "Last commit", "Stars")
DATA_FORMAT = "%B %d, %Y"

github_access_token = os.getenv("ACCESS_TOKEN_GITHUB")
g = Github(github_access_token)

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
                repo.created_at.strftime(DATA_FORMAT),
                month_diff,
                repo.stargazers_count,
            ]
        )

value_matrix = kludex_sort(value_matrix)
for value in value_matrix:
    idx = HEADERS.index("Last commit")
    month_diff = value[idx]
    value[idx] = "Up-to-date" if month_diff < 2 else f"{month_diff} months ago"
writer = MarkdownTableWriter(
    table_name="FastAPI Packages", headers=HEADERS, value_matrix=value_matrix, margin=1
)

css = """
<style>
    table th:nth-of-type(1) {width: 10%;}
    table th:nth-of-type(2) {width: 20%;}
    table th:nth-of-type(3) {width: 35%;}
    table th:nth-of-type(4) {width: 25%;}
    table th:nth-of-type(5) {width: 10%;}
</style>"""
print(css)
writer.write_table()
