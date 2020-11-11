import json
import os
from datetime import date, datetime

from dateutil import relativedelta
from perceval.backends.core.github import GitHubClient
from pytablewriter import MarkdownTableWriter

GITHUB_URL = "http://github.com"
HEADERS = ("Package", "Author", "Last commit", "Stars")
DATA_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

github_access_token = os.getenv("ACCESS_TOKEN_GITHUB")
today = date.today()

# Repository name, Author name, last commit, stars
value_matrix = []
with open("package_list.json", "r") as f:
    for data in json.load(f):
        repo_client = GitHubClient(**data, tokens=[github_access_token])
        values = json.loads(repo_client.repo())
        month_diff = relativedelta.relativedelta(
            today, datetime.strptime(values["pushed_at"], DATA_FORMAT)
        ).months
        value_matrix.append(
            [
                f'[{values["name"]}]({values["html_url"]})',
                f'[{values["owner"]["login"]}]({values["owner"]["html_url"]})',
                "Up-to-date" if month_diff < 2 else f"{month_diff} months ago",
                values["stargazers_count"],
            ]
        )

value_matrix.sort(key=lambda x: x[3], reverse=True)
writer = MarkdownTableWriter(
    table_name="FastAPI Packages", headers=HEADERS, value_matrix=value_matrix, margin=1
)
writer.write_table()
