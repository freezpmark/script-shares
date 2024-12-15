import os

import requests
from dotenv import load_dotenv
URL_DOMAIN = "https://fluentenglish.academy/api/v1"

load_dotenv()
ACCESS_TOKEN = os.getenv("access_token")
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# ############
# 1. example - read
URL1 = f"{URL_DOMAIN}/read"
params1 = {
    "model": "lea.student",
    "id": 223,
    "fields": "name,lesson_ids.expression_ids.english,lesson_ids.expression_ids.korean_translation_by_teacher",
}
read_response = requests.get(URL1, headers=headers, params=params1, timeout=10)
print(read_response.json(), end="\n\n\n")

# 2. example - search_read
URL2 = f"{URL_DOMAIN}/search_read"
params2 = {
    "model": "lea.student",
    "fields": "id,teacher_id,gdoc_link_lessons,lesson_ids",
    "domain": "[('name', '=', '김 태희')]",
}

read_response = requests.get(URL2, headers=headers, params=params2, timeout=10)
print(read_response.json(), end="\n\n\n")

# # 3. example - create
# URL3 = f"{URL_DOMAIN}/create"
# data3 = {
#     "model": "lea.student",
#     "vals": {"name": "FastAPI Test"}
# }
# read_response = requests.post(URL3, headers=headers, json=data3, timeout=10)
# print(read_response.json(), end="\n\n\n")

# # 4. example - multi_create
# URL4 = f"{URL_DOMAIN}/multi_create"
# data4 = {
#     "model": "lea.student",
#     "vals_list": [
#         {"name": "Student Name1", "quizlet_password": "1231"},
#         {"name": "Student Name2", "quizlet_password": "1234"}
#     ],
#     "fields": "id"
# }
# read_response = requests.post(URL4, headers=headers, json=data4, timeout=10)
# print(read_response.json(), end="\n\n\n")

# # 5. example - write
# URL5 = f"{URL_DOMAIN}/write"
# data5 = {
#     "model": "lea.student",
#     "ids": [349, 350],
#     "vals": {"quizlet_password": "1111", "class_monday": True},
# }
# read_response = requests.put(URL5, headers=headers, json=data5, timeout=10)
# print(read_response.json(), end="\n\n\n")

# # 6. example - unlink
# URL6 = f"{URL_DOMAIN}/unlink"
# data6 = {
#     "model": "lea.student",
#     "ids": 349,
# }
# read_response = requests.delete(URL6, headers=headers, json=data6, timeout=10)
# print(read_response.json(), end="\n\n\n")

# # 7. example - call_method (avoid for now)
# data7 = {
#     "model": "lea.schedule",
#     "ids": 1710,
#     "method": "button_generate_message"
# }
# URL7 = f"{URL_DOMAIN}/call_method"
# read_response = requests.post(URL7, headers=headers, json=data7, timeout=10)
# print(read_response.json(), end="\n\n\n")


# example of calling correction on a diary

# URL2 = f"{URL_DOMAIN}/search_read"
# params2 = {
#     "model": "lea.diary",
#     "fields": "id",
#     "domain": "[('name', '=', '문정미 - 2024 October 27')]",
# }
# read_response = requests.get(URL2, headers=headers, params=params2, timeout=10)
# diary_id = read_response.json()["result"][0]["id"]

# URL7 = f"{URL_DOMAIN}/call_method"
# data8 = {
#     "model": "lea.diary",
#     "ids": diary_id,
#     "method": "button_correct_with_ai"
# }
# read_response = requests.post(URL7, headers=headers, json=data8, timeout=10)
# print(read_response.json(), end="\n\n\n")










# user
URL4 = f"{URL_DOMAIN}/user"
read_response = requests.get(URL4, headers=headers, timeout=10)
print(read_response.json(), end="\n\n\n")
