import requests
import time
import os

# CONFIG
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_USER_ID = os.environ.get("STEAM_USER_ID")
NOTION_DATABASE_API_KEY = os.environ.get("NOTION_DATABASE_API_KEY")
NOTION_DATABASE_ID = "b12648be61674b4fbe2c4e925279d364"
# OPTIONAL
include_played_free_games = True
enable_item_update = True
enable_filter = True
# related to is_record() function to not record some games based on certain rules
CREATE_DATABASE = False
PAGE_ID = "a6c344eee16c46909f7525601282cdbb"


MAX_RETRIES = 20
RETRY_DELAY = 2


def send_request_with_retry(
    url, headers=None, json_data=None, retries=MAX_RETRIES, method="patch"
):
    while retries > 0:
        try:
            if method == "patch":
                response = requests.patch(url, headers=headers, json=json_data)
            elif method == "post":
                response = requests.post(url, headers=headers, json=json_data)
            elif method == "get":
                response = requests.get(url)

            response.raise_for_status()  # 如果响应状态码不是200系列，则抛出HTTPError异常
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request Exception occurred: {e}. retring")
            retries -= 1
            if retries > 0:
                time.sleep(RETRY_DELAY)  # 等待一段时间后再重试
            else:
                print("Max retries exceeded. Giving up.")
                raise
            raise


def get_owned_game_data_from_steam():
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?"
    url = url + "key=" + STEAM_API_KEY
    url = url + "&steamid=" + STEAM_USER_ID
    url = url + "&include_appinfo=True"
    if include_played_free_games:
        url = url + "&include_played_free_games=True"

    response = requests.get(url)
    if response.status_code != 200:
        print(
            f"get_owned_game_data_from_steam() Request failed with status code {response.status_code}"
        )
        exit(0)

    return response.json()


def add_item_to_notion_database(game):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    playtime = round(float(game["playtime_forever"]) / 60, 1)
    last_played_time = time.strftime(
        "%Y-%m-%d", time.localtime(game["rtime_last_played"])
    )
    store_url = f"https://store.steampowered.com/app/{game['appid']}"
    icon_url = f"https://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game['img_icon_url']}.jpg"
    cover_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{game['appid']}/header.jpg"

    data = {
        "parent": {
            "type": "database_id",
            "database_id": f"{NOTION_DATABASE_ID}",
        },
        "properties": {
            "name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": f"{game['name']}"}}],
            },
            "playtime": {"type": "number", "number": playtime},
            "last play": {"type": "date", "date": {"start": last_played_time}},
            "store url": {
                "type": "url",
                "url": store_url,
            },
        },
        "cover": {"type": "external", "external": {"url": f"{cover_url}"}},
        "icon": {"type": "external", "external": {"url": f"{icon_url}"}},
    }

    try:
        response = send_request_with_retry(
            url, headers=headers, json_data=data, method="post"
        )
        return response.json()
    except Exception as e:
        print(f"Failed to send request: {e}")


def query_item_from_notion_database(game_name):
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    data = {"filter": {"property": "name", "rich_text": {"equals": f"{game_name}"}}}

    try:
        response = send_request_with_retry(
            url, headers=headers, json_data=data, method="post"
        )
        return response.json()
    except Exception as e:
        print(f"Failed to send request: {e}")


def retreive_items_from_notion_database():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    data = {"filter": {"property": "name", "rich_text": {"is_not_empty": True}}}

    try:
        response = send_request_with_retry(
            url, headers=headers, json_data=data, method="post"
        )
        return response.json()
    except Exception as e:
        print(f"Failed to send request: {e}")


def update_item_to_notion_database(page_id, game):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    playtime = round(float(game["playtime_forever"]) / 60, 1)
    last_played_time = time.strftime(
        "%Y-%m-%d", time.localtime(game["rtime_last_played"])
    )
    store_url = f"https://store.steampowered.com/app/{game['appid']}"
    icon_url = f"https://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game['img_icon_url']}.jpg"
    cover_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{game['appid']}/header.jpg"

    data = {
        "properties": {
            "name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": f"{game['name']}"}}],
            },
            "playtime": {"type": "number", "number": playtime},
            "last play": {"type": "date", "date": {"start": last_played_time}},
            "store url": {
                "type": "url",
                "url": store_url,
            },
            "cover": {"type": "external", "external": {"url": f"{cover_url}"}},
            "icon": {"type": "external", "external": {"url": f"{icon_url}"}},
        },
    }

    try:
        response = send_request_with_retry(
            url, headers=headers, json_data=data, method="patch"
        )
        return response.json()
    except Exception as e:
        print(f"Failed to send request: {e}")


def is_record(game):
    not_record_time = "2020-01-01 00:00:00"
    time_tuple = time.strptime(not_record_time, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(time_tuple)
    playtime = round(float(game["playtime_forever"]) / 60, 1)

    if playtime < 0.1 or (game["rtime_last_played"] < timestamp and playtime < 4):
        return False

    return True


def extract_items_to_be_added(database_data, owned_game_data):
    game_to_be_added = []

    for game in owned_game_data:
        data = {}
        is_record = True

        for item in database_data["results"]:
            if item["properties"]["name"] == game["name"]:  # this item already exists
                playtime = round(float(game["playtime_forever"]) / 60, 1)
                if item["properties"]["playtime"] != playtime:
                    data["update"] = True
                    data["data"] = game
                    data["id"] = item["id"]
                    game_to_be_added.append(data)

                is_record = False
                break

        if is_record:
            data["update"] = False
            data["data"] = game
            game_to_be_added.append(data)

    return game_to_be_added


def database_create(page_id):
    url = "https://api.notion.com/v1/databases/"

    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    data = {
        "parent": {
            "type": "page_id",
            "page_id": page_id,
        },
        "title": [{"type": "text", "text": {"content": "Game List"}}],
        "properties": {
            "name": {"title": {}},
            "playtime": {"number": {}},
            "last play": {"date": {}},
            "store url": {"url": {}},
        },
    }

    try:
        response = send_request_with_retry(
            url, headers=headers, json_data=data, method="post"
        )
        return response.json()
    except Exception as e:
        print(f"Failed to send request: {e}")


if __name__ == "__main__":
    if CREATE_DATABASE:
        database_created = database_create(PAGE_ID)
        NOTION_DATABASE_ID = database_created["id"]

    database_data = retreive_items_from_notion_database()
    owned_game_data = get_owned_game_data_from_steam()
    games_to_be_added = extract_items_to_be_added(
        database_data, owned_game_data["response"]["games"]
    )

    # print(games_to_be_added)

    # cnt = 0
    # total = owned_game_data["response"]["game_count"]

    with open("log.txt", "w+", encoding="utf-8") as file:

        for game in games_to_be_added:
            # cnt = cnt + 1
            # print(f"process now at {cnt}/{total}...")
            print(f"process now at {game['data']['name']}...")

            if enable_filter == True and is_record(game["data"]) == False:
                file.write(f'{game["data"]["name"]},{game["data"]["appid"]}\n')
                continue

            if game["update"] == False:
                added_item = add_item_to_notion_database(game["data"])
            elif enable_item_update:
                update_item_to_notion_database(game["id"], game["data"])
