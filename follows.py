# download json or html data from IG and run this to see who unfollowed you

# followings = open('following.txt', 'r', encoding="utf-8")
# followers = open('followers.txt', 'r', encoding="utf-8")
# fis = [following for following in followings][::2]
# fes = [follower for follower in followers][::2]
# fis.sort()
# fes.sort()
# unfollowed = []
# backfollow = []

# for fi in fis:
#     if fi not in fes:
#         unfollowed.append(fi)
# for fe in fes:
#     if fe not in fis:
#         backfollow.append(fe)

# print("Unfollowed:", unfollowed)
# print("Me not following back:", backfollow)

import json

with open("followers_and_following/following.json", "r") as following:
    parsed_following = json.load(following)

with open("followers_and_following/followers_1.json", "r") as followers:
    parsed_followers = json.load(followers)

following_list, followers_list = [], []

for var_following in parsed_following["relationships_following"]:
    following_list.append(((var_following["string_list_data"])[0])["value"])

for user in parsed_followers:
    followers_list.append(((user["string_list_data"])[0])["value"])

for investment in following_list:
    if investment not in followers_list:
        print(investment)
