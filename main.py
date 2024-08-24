import requests
import os

# CONFIG
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_USER_ID = os.environ.get("STEAM_USER_ID")
NOTION_DATABASE_API_KEY = os.environ.get("NOTION_DATABASE_API_KEY")
# OPTIONAL
include_played_free_games = True


def get_owned_game_data_from_steam():
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?"
    url = url + "key=" + STEAM_API_KEY
    url = url + "&steamid=" + STEAM_USER_ID
    url = url + "&include_appinfo"
    if include_played_free_games:
        url = url + "&include_played_free_games"

    r = requests.get(url)
    if r.status_code != 200:
        print("steam data retrieved failed!")
        exit(0)

    return r.json()


if __name__ == "__main__":
    owned_game_data = get_owned_game_data_from_steam()
    print(owned_game_data)
