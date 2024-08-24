# notion_steam_library_database

## description

A tool to import your steam library to notion database.

![1724501890766](image/README/1724501890766.png)

import the following data from steam api to notion:

+ game name(text)
+ playtime(hour)
+ last play time(date)
+ steam store url(url)
+ cover and icon(image)

To use this tool, you need:

1. replace the following parameter with your own api key.

   ```python
   STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
   STEAM_USER_ID = os.environ.get("STEAM_USER_ID")
   NOTION_DATABASE_API_KEY = os.environ.get("NOTION_DATABASE_API_KEY")
   NOTION_DATABASE_ID = "079b0dbfdf9049ab8e2373532babcc94"
   ```

+ STEAM_API_KEY : this is your steam api key, you can get from [Steam 社区 :: Steam Web API 密钥 (steamcommunity.com)](https://steamcommunity.com/dev/apikey)
+ STEAM_USER_ID: this is the user id you want to get the steam library data from, you can get it from your steam profile permanent link: https://steamcommunity.com/profiles/{STEAM_USER_ID}
+ NOTION_DATABASE_API_KEY: this is notion api key, you can get it from [Notion – The all-in-one workspace for your notes, tasks, wikis, and databases.](https://www.notion.so/my-integrations)
+ NOTION_DATABASE_ID: this is the data base you want to import data to. Open your database as full page, your database id looks like this: https://www.notion.so/{WORKSPACE}/{NOTION_DATABASE_ID}?v=xxxxxxx

2. Create database in notion page

    Create a database with these rows, the rows' property should be exactly as follows like the screenshots showed:

+ name, type = "title"
+ playtime, type = "number"
+ last play, type = "date"
+ store url, tupe = "url"

3. install request library

```python
pip install request
```

4. run the tools

```python
python main.py
```

## optional configue

```python
include_played_free_games = True
enable_item_update = True

MAX_RETRIES = 20  
RETRY_DELAY = 2  # 等待2秒后再重试  
```
