import requests
import os

# CONFIG
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_USER_ID = os.environ.get("STEAM_USER_ID")
NOTION_DATABASE_API_KEY = os.environ.get("NOTION_DATABASE_API_KEY")
NOTION_DATABASE_ID = "079b0dbfdf9049ab8e2373532babcc94"
# OPTIONAL
include_played_free_games = True


def get_owned_game_data_from_steam():
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?"
    url = url + "key=" + STEAM_API_KEY
    url = url + "&steamid=" + STEAM_USER_ID
    url = url + "&include_appinfo"
    if include_played_free_games:
        url = url + "&include_played_free_games"

    response = requests.get(url)
    if response.status_code != 200:
        print(
            "get_owned_game_data_from_steam() Request failed with status code {response.status_code}"
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

    data = {
        "parent": {
            "type": "database_id",
            "database_id": f"{NOTION_DATABASE_ID}",
        },
        "properties": {
            "Grocery item": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": "Tomatoes"}}],
            },
            "Price": {"type": "number", "number": 1.49},
            "Last ordered": {"type": "date", "date": {"start": "2021-05-11"}},
        },
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"add_item_to_notion_database() Request failed with status code {response.status_code}"
        )


def add_cover_to_notion_database_item(page_id, cover_url):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    data = {"cover": {"type": "external", "external": {"url": f"{cover_url}"}}}

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"add_cover_to_notion_database_item() Request failed with status code {response.status_code}"
        )


def add_icon_to_notion_database_item(page_id, icon_url):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    data = {"icon": {"type": "external", "external": {"url": f"{icon_url}"}}}

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"add_cover_to_notion_database_item() Request failed with status code {response.status_code}"
        )


def query_item_from_notion_database(game_name):
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    data = {
        "filter": {"property": "Grocery item", "rich_text": {"equals": f"{game_name}"}}
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"query_item_from_notion_database() Request failed with status code {response.status_code}"
        )

    return


def update_item_to_notion_database(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_DATABASE_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    data = {"cover": {"type": "external", "external": {"url": f""}}}

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"add_cover_to_notion_database_item() Request failed with status code {response.status_code}"
        )


# TODO

if __name__ == "__main__":
    owned_game_data = get_owned_game_data_from_steam()
    # added_item = add_item_to_notion_database()
    # add_cover_to_notion_database_item(
    #     added_item["id"],
    #     "https://cdn2.steamgriddb.com/thumb/6b99e8fad6be4a4f9367c4a58059391b.jpg",
    # )
    print(query_item_from_notion_database())

    for game in owned_game_data["response"]["games"]:
        query = query_item_from_notion_database(game["name"])
        if query["result"] == []:
            add_item_to_notion_database(game)
