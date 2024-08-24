import requests
import time
import os
from requests.exceptions import SSLError 

# CONFIG
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_USER_ID = os.environ.get("STEAM_USER_ID")
NOTION_DATABASE_API_KEY = os.environ.get("NOTION_DATABASE_API_KEY")
NOTION_DATABASE_ID = "079b0dbfdf9049ab8e2373532babcc94"
# OPTIONAL
include_played_free_games = True
enable_item_update = False

MAX_RETRIES = 20  
RETRY_DELAY = 2  # 等待2秒后再重试  
  
def send_request_with_retry(url, headers=None, json_data=None, retries=MAX_RETRIES, method='patch'):
    while retries > 0:  
        try: 
            if method == 'patch': 
                response = requests.patch(url, headers=headers, json=json_data)
            elif method == 'post':
                response = requests.post(url, headers=headers, json=json_data)

            response.raise_for_status()  # 如果响应状态码不是200系列，则抛出HTTPError异常  
            return response  
        except SSLError as e:  
            print(f"SSL Error occurred: {e}. Retrying...")  
            retries -= 1  
            if retries > 0:  
                time.sleep(RETRY_DELAY)  # 等待一段时间后再重试  
            else:  
                print("Max retries exceeded. Giving up.")  
                raise  # 可选：如果达到最大重试次数，可以选择重新抛出异常  
        except requests.exceptions.RequestException as e:  
            # 这里也可以捕获其他类型的请求异常，如ConnectionError, Timeout等  
            print(f"Request Exception occurred: {e}. Skipping retry for this type of error.")  
            raise  # 对于非SSL错误，你可能不想重试，直接抛出异常 


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
    last_played_time = time.strftime("%Y-%m-%d", time.localtime(game["rtime_last_played"]))
    store_url = f'https://store.steampowered.com/app/{game['appid']}'

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
            "store url":{
                "type":"url",
                "url":store_url,
            },
        },
    }

    try:  
        response = send_request_with_retry(url, headers=headers, json_data=data,method='post')  
        return response.json()
    except Exception as e:  
        print(f"Failed to send request: {e}")



def add_cover_to_notion_database_item(page_id, cover_url):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    data = {"cover": {"type": "external", "external": {"url": f"{cover_url}"}}}

    try:  
        response = send_request_with_retry(url, headers=headers, json_data=data,method='patch')  
        return response.json()
    except Exception as e:  
        print(f"Failed to send request: {e}")


def add_icon_to_notion_database_item(page_id, icon_url):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    data = {"icon": {"type": "external", "external": {"url": f"{icon_url}"}}}

    try:  
        response = send_request_with_retry(url, headers=headers, json_data=data,method='patch')  
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
    data = {
        "filter": {"property": "name", "rich_text": {"equals": f"{game_name}"}}
    }

    try:  
        response = send_request_with_retry(url, headers=headers, json_data=data,method='post')  
        return response.json()
    except Exception as e:  
        print(f"Failed to send request: {e}")


def update_item_to_notion_database(page_id,game):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    playtime = round(float(game["playtime_forever"]) / 60, 1)
    last_played_time = time.strftime("%Y-%m-%d", time.localtime(game["rtime_last_played"]))
    store_url = f'https://store.steampowered.com/app/{game['appid']}'

    data = {
        "properties": {
            "name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": f"{game['name']}"}}],
            },
            "playtime": {"type": "number", "number": playtime},
            "last play": {"type": "date", "date": {"start": last_played_time}},
            "store url":{
                "type":"url",
                "url":store_url,
            },
        },
    }

    try:  
        response = send_request_with_retry(url, headers=headers, json_data=data,method='patch')  
        return response.json()
    except Exception as e:  
        print(f"Failed to send request: {e}")


# TODO
# replace steam logo with igdb api

if __name__ == "__main__":
    owned_game_data = get_owned_game_data_from_steam()
    cnt = 0
    total = owned_game_data["response"]["game_count"]

    for game in owned_game_data["response"]["games"]:
        cnt = cnt + 1
        print(f"process now at {cnt}/{total}...")

        query = query_item_from_notion_database(game["name"])
        if query["results"] == []:
            added_item = add_item_to_notion_database(game)
            icon_url = f'https://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game['img_icon_url']}.jpg'
            add_cover_to_notion_database_item(added_item['id'],icon_url)
            add_icon_to_notion_database_item(added_item['id'],icon_url)
        else:
            if enable_item_update:
                update_item_to_notion_database(query["results"][0]['id'],game)
                icon_url = f'https://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game['img_icon_url']}.jpg'
                add_cover_to_notion_database_item(query["results"][0]['id'],icon_url)
                add_icon_to_notion_database_item(query["results"][0]['id'],icon_url)
