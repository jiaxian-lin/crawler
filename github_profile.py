import json
import requests
import pandas as pd
result = {}
repo_list = []
with open(r"E:\wechat_file\WeChat Files\wxid_4315003150312\FileStorage\File\2022-10\ranks_开源项目榜_中国项目 (1).csv", "r", encoding="utf-8") as f:
    for line in f:
        string_list = line.split(",")
        repo_list.append(string_list[0])
for i, repo in enumerate(repo_list[1:]):
    repo_identifier = repo
    header = {"Authorization": "Bearer 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"}
    url = f"https://api.github.com/repos/{repo_identifier}/community/profile"
    data = json.loads(requests.get(url, headers=header).text)
    result[repo] = data
    print(f"{i},{len(repo_list)},{data}")

with open("./community.json", "w") as f:
    json.dump(result, f)


with open("./community.json", "r") as f:
    data = json.load(f)
with open("./community.csv", "w") as f:
    f.write("REPO, README, License, Description, Contributing, Code_of_conduct, Pull requests template, Issue template, health_percentage\n")
    for i in data:
        readme = 1 if data[i]["files"]["readme"] else 0
        license = 1 if data[i]["files"]["license"] else  0
        description = 1 if data[i]["description"] else 0
        contributing = 1 if data[i]["files"]["contributing"] else  0
        code_of_conduct = 1 if data[i]["files"]["code_of_conduct"] else  0
        pull_request_template = 1 if data[i]["files"]["pull_request_template"] else  0
        issue_template = 1 if data[i]["files"]["issue_template"] else  0
        health_percentage = data[i]["health_percentage"]

        f.write(f"{i},{readme},{license},{description},{contributing},{code_of_conduct},{pull_request_template},{issue_template}, {health_percentage}\n")

