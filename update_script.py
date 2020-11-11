import json
import os
from datetime import date

from dateutil import relativedelta
from github import Github
from pytablewriter import MarkdownTableWriter

GITHUB_URL = "http://github.com"
HEADERS = ("Package", "Author", "Description", "Created at", "Last commit", "Stars")
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
                f"[{repo.name}]({repo.homepage})",
                f"[{repo.owner.name}]({repo.owner.html_url})",
                repo.description,
                repo.created_at.strftime(DATA_FORMAT),
                "Up-to-date" if month_diff < 2 else f"{month_diff} months ago",
                repo.stargazers_count,
            ]
        )

value_matrix.sort(key=lambda x: x[3], reverse=True)
writer = MarkdownTableWriter(
    table_name="FastAPI Packages", headers=HEADERS, value_matrix=value_matrix, margin=1
)
writer.write_table()
