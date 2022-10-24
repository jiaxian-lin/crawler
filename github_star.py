import json

import requests

def get_github_star(group, repos):
    data = []
    base_url = f"https://api.github.com/repos/{group}/{repos}/stargazers"
    page = 1
    header = {
        "Accept": "application/vnd.github.v3.star+json",
        "Authorization": "Bearer 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"
    }

    while True:
        url = f"{base_url}?page={page}"
        response = requests.get(url, headers=header)
        new_data = json.loads(response.text)
        if new_data and new_data[0] not in data:
            data.extend(new_data)
        else:
            break
        page += 1
    print(1)



if __name__ == '__main__':
    get_github_star("EMResearch", "EvoMaster")