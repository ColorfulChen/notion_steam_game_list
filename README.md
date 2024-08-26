# notion_steam_game_list

Language: English/[中文](./README_zh_cn.md)

## description

this project use notion integration to imported a steam user's game library to notion database via steam api and notion api.

Importerd database is as followes:

![1724501890766.png](./image/README/1724501890766.png)

imported data are as follows:

| name        | type   |
| ----------- | ------ |
| name        | title  |
| playtime(h) | number |
| last play   | date   |
| store url   | url    |
| icon        | image  |

## How to use

### modify config

Modify configuration in main.py, the configurations are as follows:

```python
# CONFIG
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_USER_ID = os.environ.get("STEAM_USER_ID")
NOTION_DATABASE_API_KEY = os.environ.get("NOTION_DATABASE_API_KEY")
NOTION_DATABASE_ID = "63b4fd39830b4946b1c91d65b90a7848"
# OPTIONAL
include_played_free_games = True
enable_item_update = False
enable_filter = True
# related to is_record() function to not record some games based on certain rules
CREATE_DATABASE = False
PAGE_ID = "a6c344eee16c46909f7525601282cdbb"
```

You should replace these config with your own api keys.

After Modified the configuration should looks like this:

```python
# CONFIG
STEAM_API_KEY = 'xxxx'
STEAM_USER_ID = 'xxxx'
NOTION_DATABASE_API_KEY = 'xxxx'
NOTION_DATABASE_ID = "xxxx"
# OPTIONAL
include_played_free_games = True
enable_item_update = False
enable_filter = True
CREATE_DATABASE = False
PAGE_ID = "xxxx'
```

#### STEAM_API_KEY

You can get it from https://steamcommunity.com/dev/apikey

#### STEAM_USER_ID

The steam user you want to get steam game library data from, The user is could get from steam profile permanent link, the link looks like this:

[https://steamcommunity.com/profiles/{STEAM_USER_ID}](https://steamcommunity.com/profiles/%7BSTEAM_USER_ID%7D)

#### NOTION_DATABASE_API_KEY

NOTION integration apikey，you should create a intergration, and create a connection at the page where your database at.

follows the instruction as notion develop documents shows in "getting start" chapter[Build your first integration (notion.com)](https://developers.notion.com/docs/create-a-notion-integration)

This “API secret”  the document refer to  is NOTION_DATABASE_API_KEY。

#### NOTION_DATABASE_ID

the database you want to import to's id, before import you should make sure this database's page is added to connection with the itergration you created.

the database should contains these item with exact name and data type as the bracket shows.

- name(title)
- playtime(number)
- last play(date)
- store url(url)

the database id could get from its share link.

open the database as a full page, and click share->copy link, this link's format is as follows:

[https://www.notion.so/{workspacename}/{database_id}?v={viewID}](https://www.notion.so/%7Bworkspacename%7D/%7Bdatabase_id%7D?v=%7BviewID%7D)

this {database_id} is the database id.

The program also provide a CREATE_DATABASE configuration to create a database and import data to that created database.

configure CREATE_DATABASE to True and the program will ignore {NOTION_DATABASE_ID} and created a database at {PAGE_ID}, and import data to that database.

#### include_played_free_games（OPTIONAL）

whether to include free games.

#### enable_item_update（OPTIONAL）

when set to True, the program will updated repeated item in database.

when set to False, the program will skip repeated item in database.

#### enable_filter（OPTIONAL）

whether to use is_record() function to filter added game

the default rules will ignore never played game, you could modified on your own.

#### CREATE_DATABASE（OPTIONAL）

whether to create new database, to use this you need to configure {PAGE_ID}.

CREATE_DATABASE to True and the program will ignore {NOTION_DATABASE_ID} and created a database at {PAGE_ID}, and import data to that database.

#### PAGE_ID（OPTIONAL）

when CREATE_DATABASE is set to False this configuration would be ignored.

to get page id is similar with database id. Open the page you want to created database to as full page, click share->copy link, the link's format is as follows:

[https://www.notion.so/{WORKSPACE}/{PAGE_TITLE}-{PAGE_ID}](https://www.notion.so/%7BWORKSPACE%7D/%7BPAGE_TITLE%7D-%7BPAGE_ID%7D)

the PAGE_ID is after the symbol '-'.

### install request library

assume you have already installed python environment.

if not install python 3.6+ at www.python.org

```shell
pip install request
```

### run the program

```
python main.py
```

## TODO
1. replace item cover with high resolution picture. (maybe from igdb api?)
