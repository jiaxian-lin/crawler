

# with open("./data/2189+ Best Java frameworks, libraries, software and resourcese.json", "r",encoding="utf-8") as f:
#     datas = json.load(f)
#     for data in datas:
#         try:
#             a = data["类别"].split("\n")[1]
#             if a not in result:
#                 result[a] = {}
#             result[a][data["组件名称"]] = {}
#             for key in data:
#                 result[a][data["组件名称"]][key] = data[key]
#
#         except:
#             print(data["组件名称"])

# number = 0
# version_number = 0
# count = 0
# cate_number = 0
# page = 0
# with open("data/reposhub_C.json", "r") as f:
#     libraries = json.load(f)
#     for lib in libraries:
#         tmp = libraries[lib]["category"].split()
#         if tmp[0] not in result:
#             result[tmp[0]] = {}
#         cate = " ".join(tmp[1:])
#         if cate not in result[tmp[0]]:
#             result[tmp[0]][cate] = {}
#         result[tmp[0]][cate][lib] = libraries[lib]
# with open("data/reposhub_C1.json", "w") as f:
#     libraries = json.dump(result, f)


# with open("./data/result_4.json", "r") as f:
#     categories = json.load(f)
# with open("./data/result_3.json", "r") as f:
#     categories3 = json.load(f)
# cate_list = []
# for cate in categories:
#     if cate in categories3:
#         cate_list.append(cate)
# for cate in cate_list:
#     categories.pop(cate)
# with open("./result_4.json", "w") as f:
#     json.dump(categories, f)

import json
import os
import xlrd
# result = {}
# with open("./data/reposhub_java.json", "r") as f:
#     a = json.load(f)
# result["java"] = a
# with open("./data/reposhub_java1.json", "w") as f:
#     json.dump(result, f)
result = {}
for file in os.listdir("./data/reposhub"):
    with open(f"./data/reposhub/{file}", "r") as f:
        lan = json.load(f)
    for key in lan:
        result[key] = lan[key]
        number = 0
        for cate in lan[key]:
            number += len(result[key][cate].keys())
        print(key, number)
with open(f"./data/reposhub/reposhub.json", "w") as f:
    json.dump(result, f)

# result = {}
# with open("./data/reposhub_js.json", "r", encoding="utf-8") as f:
#     result["javascript"] = json.load(f)
# python = result["javascript"]
# workbook=xlrd.open_workbook("./data/reposhub_js.xlsx")
#
# table = workbook.sheets()[0]
#
# lines = table.nrows
# for i in range(1, lines):
#     row = table.row_values(i)
#     if row[3] not in python:
#         python[row[3]] = {}
#     python[row[3]][row[0]] = {}
#     lib = python[row[3]][row[0]]
#     lib["watchers"] = row[4]
#     lib["stars"] = row[5]
#     lib["fork"] = row[6]
#     lib["last_update"] = row[7]
#     lib["github_link"] = row[7]
# with open("./data/reposhub_javascript.json", "w", encoding="utf-8") as f:
#     json.dump(result, f)
#
# #
# with open("./data/reposhub_javascript.json", "r", encoding="utf-8") as f:
#     result = json.load(f)
# number = 0
# result = result["javascript"]
# for cate in result:
#     number += len(result[cate].keys())
# print(number)

