# 🎮 Notion Steam Game List

🌐 **Languages**: [English](./README_en.md) / [中文](./README.md)

---

2025.5.27 Update：Added the functionality to fetch game info and game tags from steam store. The previous version will no longer work and requires adding a "info" (text) and "tags"(multi-select) field to the database in order to work.

2025.5.11 Update：Added the functionality to fetch Steam reviews, which will now fetch user reviews from Steam into the Notion database. The previous version will no longer work and requires adding a "review" (text) field to the database in order to work.

## 📖 Description

This project allows you to import a specified Steam user's public game library data into a specified Notion database using the Steam API. Additionally, you can automate updates to your database via **GitHub Actions**.

The table format in Notion will look like this:

![Notion Table Example](./image/README_zh_cn/1724727271538.png)

### 📊 Imported Data Fields:

| Field Name       | Data Type |
| ----------------- | --------- |
| 🎮 Game Name      | `title`   |
| ⏱️ Playtime (h)   | `number`  |
| 📅 Last Played    | `date`    |
| 🔗 Store Link     | `url`     |
| 🖼️ Game Logo      | `image`   |
| 🖼️ Game Cover     | `image`   |
| ✅ Completion     | `number`  |
| 🏆 Achieved Achievements | `number` |
| 🏅 Total Achievements | `number` |
| ✍️ review | `text` |
| 📟 info      | `text` |
| 🎨 tags      | `multi-select` |

---

## 🚀 Automate with GitHub Actions

### 1️⃣ **Fork this repository**

Click the **Fork** button on the repository page:

![Fork Example](./image/README_zh_cn/1724727797319.png)

---
### 2️⃣ **Ceate a notion database with these data field**

Ensure your Notion database includes the following fields:

| Field Name               | Data Type |
| ------------------------ | --------- |
| `name`                   | `title`   |
| `playtime`               | `number`  |
| `last play`              | `date`    |
| `store url`              | `url`     |
| `completion`             | `number`  |
| `achieved achievements`  | `number`  |
| `total achievements`     | `number`  |
| `review`     | `text`  |
| `info`      | `text` |
| `tags`      | `multi-select` |




### 3️⃣ **Configure GitHub Action Variables**

GitHub Actions require the following variables to be set up:

```yaml
env:
  STEAM_API_KEY: ${{ secrets.STEAM_API_KEY }}
  # Get from https://steamcommunity.com/dev/apikey
  STEAM_USER_ID: ${{ secrets.STEAM_USER_ID }}
  # Get from your Steam profile: https://steamcommunity.com/profiles/{STEAM_USER_ID}
  NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
  # https://developers.notion.com/docs/create-a-notion-integration
  NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
  # https://developers.notion.com/reference/retrieve-a-database
  include_played_free_games: ${{ secrets.include_played_free_games }}
  # Set to 'true' by default
  enable_item_update: ${{ secrets.enable_item_update }}
  # Set to 'true' by default
  enable_filter: ${{ secrets.enable_filter }}
  # Set to 'false' by default
```

| Variable Name              | Data Type | Description                     |
| -------------------------- | --------- | ------------------------------- |
| `STEAM_API_KEY`            | `string`  | Steam API key                   |
| `STEAM_USER_ID`            | `string`  | Steam user ID                   |
| `NOTION_API_KEY`           | `string`  | Notion API key                  |
| `NOTION_DATABASE_ID`       | `string`  | Notion database ID              |
| `include_played_free_games`| `string`  | Include free games (`'true'/'false'`)(quoto included) |
| `enable_item_update`       | `string`  | Enable item updates (`'true'/'false'`) |
| `enable_filter`            | `string`  | Enable filters (`true/false`)   |

💡 **Note**: Add these variables in your forked repository under `Settings -> Secrets and Variables -> Actions -> New repository secret`.

![Secrets Example](./image/README_zh_cn/1724728563407.png)

---



### 4️⃣ **Done!**

Once configured, GitHub Actions will automatically update your Notion database daily at **12:00 UTC**. You can also manually trigger the workflow by navigating to:

**Actions -> Update Notion with Steam Data -> Run workflow**

![Run Workflow Example](./image/README_zh_cn/1724728824789.png)

---

## 🖥️ Local Deployment

### 1️⃣ **Modify Configuration Parameters**

Update the configuration parameters in `main.py`:

```python
# CONFIG
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_USER_ID = os.environ.get("STEAM_USER_ID")
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DATABASE_ID = "NOTION_DATABASE_ID"
# OPTIONAL
include_played_free_games = 'true'
enable_item_update = 'true'
enable_filter = 'false'
```

Replace the placeholders with your own keys:

```python
# CONFIG
STEAM_API_KEY = 'your_steam_api_key'
STEAM_USER_ID = 'your_steam_user_id'
NOTION_API_KEY = 'your_notion_api_key'
NOTION_DATABASE_ID = 'your_notion_database_id'
# OPTIONAL
include_played_free_games = 'true'
enable_item_update = 'false'
enable_filter = 'true'
```

---

### 2️⃣ **Install Required Libraries**

Ensure you have Python 3.6+ installed. If not, download it from the [Python official website](http://www.python.org).

Install the required library:

```bash
pip install requests
```

---

### 3️⃣ **Run the Program**

Run the program locally:

```bash
python main.py
```

---

## 🔑 Configuration Details

### 🔑 **STEAM_API_KEY**

Get your Steam API key from:  
[Steam API Key Registration](https://steamcommunity.com/dev/apikey)

---

### 🔑 **STEAM_USER_ID**

Find your Steam User ID from your profile URL:  
`https://steamcommunity.com/profiles/{STEAM_USER_ID}`

---

### 🔑 **NOTION_API_KEY**

Create a Notion integration and get your API key:  
[Notion Integration Guide](https://developers.notion.com/docs/create-a-notion-integration)

---

### 🔑 **NOTION_DATABASE_ID**

Find your Notion database ID by copying the link to your database:  
`https://www.notion.so/{workspace_name}/{database_id}?v={view_id}`

---

### 🔑 **Optional Parameters**

- `include_played_free_games`: Include free games (`true/false`)
- `enable_item_update`: Enable item updates (`true/false`)
- `enable_filter`: Enable filters (`true/false`)

---

## 🛠️ Troubleshooting

If you encounter any issues, ensure:

1. All required variables are correctly set.
2. Your Notion database is properly configured and linked to your integration.
3. Python and required libraries are installed.

---

🎉 **Enjoy automating your Notion Steam game list!**