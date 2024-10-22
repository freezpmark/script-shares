import requests
from dotenv import get_key, set_key

# test_call_refresh_generate
#     generate_new_token
#         _extract_and_save_token
#     refresh_token
#         _extract_and_save_token

URL_DOMAIN = "https://fluentenglish.odooserver.sk/api/v1"


def _extract_and_save_token(response):
    token_data = response.json()

    set_key(".env", "access_token", token_data.get("access_token"))
    set_key(".env", "refresh_token", token_data.get("refresh_token"))

    print(token_data)


def generate_new_token():
    # ##############
    token_url = f"{URL_DOMAIN}/token"
    data = {"username": "admin", "password": "secret"}
    response = requests.post(token_url, data=data, timeout=10)
    # ##############

    _extract_and_save_token(response)


def refresh_token():
    # ##############
    refresh_url = f"{URL_DOMAIN}/refresh_token"
    params = {"refresh_token": get_key(".env", "refresh_token")}
    response = requests.get(refresh_url, params=params, timeout=10)
    # ##############

    _extract_and_save_token(response)


def test_call_refresh_generate():
    read_url = f"{URL_DOMAIN}/read"
    access_token = get_key(".env", "access_token")
    if not access_token:  # token missing in .env
        generate_new_token()
        print("New Token has been generated.")
        return

    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"model": "lea.student", "id": 223, "fields": "name"}

    response = requests.get(read_url, headers=headers, params=params, timeout=10)
    if response.status_code == 401:  # token expired
        refresh_token()
        print("Token has been refreshed.")
        return

    print(response.json())
    print("Token is working properly.")


# refresh_token()  # call this to test expiration (invalidates the token cuz of old env vars for call below)
test_call_refresh_generate()
