# notion_steam_game_list

Language: English/[中文](./README_zh_cn.md)

## description

this project use notion integration to import a steam user's game library to notion database via steam api and notion api.

You can also automated this workflow with Github Actions to daily update your notion pages!

the results are as follows:

![1724727271538](./image/README_zh_cn/1724727271538.png)

import these data：

| name                        | type   |
| --------------------------- | ------ |
| name                        | title  |
| playtime(h)                 | number |
| last play                   | date   |
| store url                   | url    |
| game logo                   | image  |
| game cover                  | image  |
| completion                  | number |
| achieved achievements count | number |
| total achievements count    | number |

## Automated with Github Action

### Fork this repository

click fork.

![1724727797319](./image/README_zh_cn/1724727797319.png)

### Configure variables

github action workflowed used these variables.

```yaml
        env:
          STEAM_API_KEY: ${{ secrets.STEAM_API_KEY }}
          STEAM_USER_ID: ${{ secrets.STEAM_USER_ID }}
          NOTION_DATABASE_API_KEY: ${{ secrets.NOTION_API_KEY }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
          #OPTIONAL
          enable_item_update: ${{secrets.enable_item_update}}
```

| name                      | type   | description                                    |
| ------------------------- | ------ | ---------------------------------------------- |
| STEAM_API_KEY             | string | steam api key                                  |
| STEAM_USER_ID             | string | steam user id you want fetch data from         |
| NOTION_DATABASE_API_KEY   | string | notion api key                                 |
| NOTION_DATABASE_ID        | string | the notion data base id you wanted to imported |
| enable_item_update        | string | whether to include item update                 |

The detailed of these variables and what they do are at next chpter.(deployed local -> modify config)

And you should create and connect your database to the notion intergration, Details are at [Build your first integration (notion.com)](https://developers.notion.com/docs/create-a-notion-integration), and in next chpater.

open the repository you just forked, press settings->Secrets and Variables->Actions->New repository screct，add these variables. note that include_played_free_games，enable_item_update，enable_filter variable should be set to 'true' or 'false'

![1724728563407](./image/README_zh_cn/1724728563407.png)

### Done！

This should work now! I set github action to run daily at 12am UTC time, you can change that at main.yml. If you want to trigger mannually, click Actions->Update Notion with Steam Data->Run workflow！

![1724728824789](./image/README_zh_cn/1724728824789.png)

## Deploy Locally

### modify config

Modify configuration in main.py, the configurations are as follows:

```python
# CONFIG
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_USER_ID = os.environ.get("STEAM_USER_ID")
NOTION_DATABASE_API_KEY = os.environ.get("NOTION_DATABASE_API_KEY")
NOTION_DATABASE_ID = "63b4fd39830b4946b1c91d65b90a7848"
# OPTIONAL
enable_item_update = 'true'
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
enable_item_update = 'false'
```

#### STEAM_API_KEY

You can get it from https://steamcommunity.com/dev/apikey

#### STEAM_USER_ID

The steam user you want to get steam game library data from, The user is could get from steam profile permanent link, the link looks like this:

[https://steamcommunity.com/profiles/{STEAM_USER_ID}](https://steamcommunity.com/profiles/%7BSTEAM_USER_ID%7D)

#### NOTION_DATABASE_API_KEY

NOTION integration apikey，you should create a intergration, and create a connection at the page where your database at.

follows the instruction as notion develop documents shows in "getting start" chapter [Build your first integration (notion.com)](https://developers.notion.com/docs/create-a-notion-integration)

This “API secret”  the document refer to  is NOTION_DATABASE_API_KEY。

#### NOTION_DATABASE_ID

the database you want to import to's id, before import you should make sure this database's page is added to connection with the itergration you created.

the database should contains these item with exact name and data type as the bracket shows.

- name(title)
- playtime(number)
- last play(date)
- store url(url)
- compeletion(number)
- total achievements(number)
- achieved achievements(number)

the database id could get from its share link.

open the database as a full page, and click share->copy link, this link's format is as follows:

[https://www.notion.so/{workspacename}/{database_id}?v={viewID}](https://www.notion.so/%7Bworkspacename%7D/%7Bdatabase_id%7D?v=%7BviewID%7D)

this {database_id} is the database id.

#### enable_item_update（OPTIONAL）

choose to update or to skip when encounter repeated item, set to 'true' or 'false'. Set to true by default.

### install requests library

assume you have already installed python environment.

if not install python 3.6+ at www.python.org

```shell
pip install requests
```

### run the program

```
python main.py
```
