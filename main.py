import argparse
import requests
import time
import os
import logging
from features.review import get_steam_review_info
from features.steamstore import get_steam_store_info

# CONFIG
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
# get from https://steamcommunity.com/dev/apikey
STEAM_USER_ID = os.environ.get("STEAM_USER_ID")
# get from your steam profile https://steamcommunity.com/profiles/{STEAM_USER_ID}
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
# https://developers.notion.com/docs/create-a-notion-integration
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
# https://developers.notion.com/reference/retrieve-a-database
# OPTIONAL
include_played_free_games = os.environ.get("include_played_free_games") or 'true'
#set to 'true' by default
enable_item_update = os.environ.get("enable_item_update") or 'true'
#set to 'true' by default
enable_filter = os.environ.get("enable_filter") or 'false'
#set to 'false' by default 

# MISC
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
            logger.error(f"Request Exception occurred: <{e}> .Error: {response.text},Retring....")
            retries -= 1
            if retries > 0:
                time.sleep(RETRY_DELAY)  # 等待一段时间后再重试
            else:
                logger.error(f"Max retries exceeded .Error: {response.text},Giving up.")
                return {}


# steamapi
def get_owned_game_data_from_steam():
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?"
    url = url + "key=" + STEAM_API_KEY
    url = url + "&steamid=" + STEAM_USER_ID
    url = url + "&include_appinfo=True"
    if include_played_free_games == "true":
        url = url + "&include_played_free_games=True"

    logger.info("fetching data from steam..")

    try:
        response = send_request_with_retry(url, method="get")
        logger.info("fetching data success!")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send request: {e},Error: {response.text}")


def query_achievements_info_from_steam(game):
    url = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?"
    url = url + "key=" + STEAM_API_KEY
    url = url + "&steamid=" + STEAM_USER_ID
    url = url + "&appid=" + f"{game['appid']}"
    logger.info(f"querying for {game['name']} achievements counts...")

    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查HTTP错误状态码（非2XX/3XX会抛出异常）
        return response.json()
    except requests.exceptions.RequestException as e:
        # 捕获所有requests库抛出的异常（如连接错误、超时、HTTP错误等）
        logger.error(f"Request failed for {game['name']}: {str(e)} .Error: {response.text}")
    except ValueError as e:
        # 捕获JSON解析错误（如返回非JSON数据）
        logger.error(f"Failed to parse JSON response for {game['name']}: {str(e)} .Error: {response.text}")

    return None


# notionapi
def add_item_to_notion_database(game, achievements_info, review_text, steam_store_data):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    logger.info(f"adding game {game['name']} to notion...")

    playtime = round(float(game["playtime_forever"]) / 60, 1)
    last_played_time = time.strftime(
        "%Y-%m-%d", time.localtime(game["rtime_last_played"])
    )
    store_url = f"https://store.steampowered.com/app/{game['appid']}"
    icon_url = f"https://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game['img_icon_url']}.jpg"
    cover_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{game['appid']}/header.jpg"
    total_achievements = achievements_info["total"]
    achieved_achievements = achievements_info["achieved"]

    if total_achievements > 0:
        completion = round(
            float(achieved_achievements) / float(total_achievements) * 100, 1
        )
    else:
        completion = -1

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
            "completion": {"type": "number", "number": completion},
            "total achievements": {"type": "number", "number": total_achievements},
            "achieved achievements": {
                "type": "number",
                "number": achieved_achievements,
            },
            "review": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": review_text},
                    }
                ],
            },
            "info": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": steam_store_data["info"]},
                    }
                ],
            },
            "tags": {
                "type": "multi_select",
                "multi_select": steam_store_data['tag']
            }
        },
        "cover": {"type": "external", "external": {"url": f"{cover_url}"}},
        "icon": {"type": "external", "external": {"url": f"{icon_url}"}},
    }

    try:
        response = send_request_with_retry(
            url, headers=headers, json_data=data, method="post"
        )
        logger.info(f"{game['name']} added!")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send request: {e} .Error: {response.text}")


def query_item_from_notion_database(game):
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    logger.info(f"querying {game['name']} from database")
    data = {"filter": {"property": "name", "rich_text": {"equals": f"{game['name']}"}}}

    try:
        response = send_request_with_retry(
            url, headers=headers, json_data=data, method="post"
        )
        logger.info(f"query complete!")
    except Exception as e:
        logger.error(f"Failed to send request: {e} .Error: {response.text}")
    finally:
        return response.json()



def update_item_to_notion_database(page_id, game, achievements_info, review_text, steam_store_data):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
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
    total_achievements = achievements_info["total"]
    achieved_achievements = achievements_info["achieved"]

    if total_achievements > 0:
        completion = round(
            float(achieved_achievements) / float(total_achievements) * 100, 1
        )
    else:
        completion = -1

    logger.info(f"updating {game['name']} to notion...")

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
            "completion": {"type": "number", "number": completion},
            "total achievements": {"type": "number", "number": total_achievements},
            "achieved achievements": {
                "type": "number",
                "number": achieved_achievements,
            },
            "review": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": review_text},
                    }
                ],
            },
            "info": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": steam_store_data["info"]},
                    }
                ],
            },
            "tags": {
                "type": "multi_select",
                "multi_select": steam_store_data['tag']
            }
        },
        "cover": {"type": "external", "external": {"url": f"{cover_url}"}},
        "icon": {"type": "external", "external": {"url": f"{icon_url}"}},
    }

    try:
        response = send_request_with_retry(
            url, headers=headers, json_data=data, method="patch"
        )
        logger.info(f"{game['name']} updated!")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send request: {e} .Error: {response.text}")


def database_create(page_id):
    url = "https://api.notion.com/v1/databases/"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
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
            "completion": {"number": {}},
            "playtime": {"number": {}},
            "last play": {"date": {}},
            "total achievements": {"number": {}},
            "achieved achievements": {"number": {}},
            "store url": {"url": {}},
        },
    }

    try:
        response = send_request_with_retry(
            url, headers=headers, json_data=data, method="post"
        )
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send request: {e} .Error: {response.text}")


# MISC
def is_record(game, achievements):
    not_record_time = "2020-01-01 00:00:00"
    time_tuple = time.strptime(not_record_time, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(time_tuple)
    playtime = round(float(game["playtime_forever"]) / 60, 1)

    if (playtime < 0.1 and achievements["total"] < 1) or (
        game["rtime_last_played"] < timestamp
        and achievements["total"] < 1
        and playtime < 6
    ):
        logger.info(f"{game['name']} does not meet filter rule!")
        return False

    return True


def get_achievements_count(game):
    game_achievements = query_achievements_info_from_steam(game)
    achievements_info = {}
    achievements_info["total"] = 0
    achievements_info["achieved"] = 0

    if game_achievements is None or game_achievements["playerstats"]["success"] is False:
        achievements_info["total"] = -1
        achievements_info["achieved"] = -1
        logger.info(f"no info for game {game['name']}")

    elif "achievements" not in game_achievements["playerstats"]:
        achievements_info["total"] = -1
        achievements_info["achieved"] = -1
        logger.info(f"no achievements for game {game['name']}")

    else:
        achievments_array = game_achievements["playerstats"]["achievements"]
        for achievement_dict in achievments_array:
            achievements_info["total"] = achievements_info["total"] + 1
            if achievement_dict["achieved"]:
                achievements_info["achieved"] = achievements_info["achieved"] + 1

        logger.info(f"{game['name']} achievements count complete!")

    return achievements_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='启用调试日志输出')
    args = parser.parse_args()

    # 配置日志
    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)

    # 移除所有现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    if args.debug:
        # 添加文件处理器
        file_handler = logging.FileHandler("app.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    owned_game_data = get_owned_game_data_from_steam()

    for game in owned_game_data["response"]["games"]:
        is_add = True
        achievements_info = {}
        achievements_info = get_achievements_count(game)
        review_text = get_steam_review_info(game["appid"], STEAM_USER_ID)
        steam_store_data = get_steam_store_info(game["appid"])
        logger.info(f"{game['name']} ' review is {review_text}")

        if "rtime_last_played" not in game:
            logger.info(f"{game['name']} have no last play time! setting to 0!")
            game["rtime_last_played"] = 0

        if enable_filter == "true" and is_record(game, achievements_info) == False:
            continue

        queryed_item = query_item_from_notion_database(game)
        if "results" not in queryed_item:
            logger.error(f"{game['name']} queryed failed! skipping!")
            continue

        if queryed_item["results"] != []:
            if enable_item_update == "true":
                logger.info(f"{game['name']} already exists! updating!")
                update_item_to_notion_database(
                    queryed_item["results"][0]["id"], game, achievements_info, review_text, steam_store_data
                )
            else:
                logger.info(f"{game['name']} already exists! skipping!")
        else:
            logger.info(f"{game['name']} does not exist! creating new item!")
            add_item_to_notion_database(game, achievements_info, review_text, steam_store_data)
