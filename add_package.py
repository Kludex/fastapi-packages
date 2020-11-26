import argparse
import json
import subprocess

import requests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inserts a package to the list!")
    parser.add_argument("url", metavar="URL", type=str, help="repository url")
    args = parser.parse_args()
    url: str = args.url

    request = requests.get(url)
    if request.status_code != 200:
        print("Website does not exist!")
        exit(1)

    with open("package_list.json", "r+") as json_file:
        data: list = json.load(json_file)
        if url.endswith("/"):
            url = url[:-1]
        owner, repository = url.split("/")[-2:]
        data.append(f"{owner}/{repository}")
        json_file.seek(0)
        json.dump(data, json_file, indent=2)

    subprocess.check_output(["git", "checkout", "-b", f"link/{owner}-{repository}"])
    subprocess.check_output(["git", "add", "package_list.json"])
    subprocess.check_output(["git", "commit", "-m", ":memo: Add link to {repostiory}"])
    subprocess.check_output(["git", "push", "origin", "$(current_branch)"])
