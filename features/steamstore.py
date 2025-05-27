from bs4 import BeautifulSoup
from urllib import request, parse
from http import cookiejar
def get_steam_store_info(appid):
    # 构造请求 URL 和 Headers
    url = f"https://store.steampowered.com/app/{appid}/?l=schinese"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    # 设置 Cookies（用于绕过年龄验证）
    cj = cookiejar.CookieJar()
    opener = request.build_opener(request.HTTPCookieProcessor(cj))
    request.install_opener(opener)

    # 手动添加 Cookie
    cookies = {
        'birthtime': '568022401',
        'lastagecheckage': '1-January-1990',
        'wants_mature_content': '1'
    }

    cookie_str = "; ".join([f"{key}={value}" for key, value in cookies.items()])
    headers['Cookie'] = cookie_str

    # 创建请求
    req = request.Request(url, headers=headers)

    metainfo = {
        'info': '',
        'tag': []
    }

    try:
        with request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"请求失败: AppID {appid}, 错误: {e}")
        return metainfo

    soup = BeautifulSoup(html, 'html.parser')

    # info
    info_text = ''
    try:
        info_elements = soup.find_all('div', {'class': 'game_description_snippet'})
        if info_elements:
            info_text = info_elements[0].get_text(strip=True)
    except Exception as e:
        print(f"简介提取失败: AppID {appid}, 错误: {e}")
        return metainfo

    # tags
    tags = []
    try:
        tag_container = soup.find_all('a', {'class': 'app_tag'})
        for tag in tag_container:
            tag_text = tag.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)
    except Exception as e:
        print(f"标签提取失败: AppID {appid}, 错误: {e}")
        return metainfo

    options = constract_notion_multi_select_property(tags)

    metainfo = {
        'info': info_text,
        'tag': options
    }

    return metainfo

def constract_notion_multi_select_property(tags):
    #color = ['blue','brown','gray','green','orange','pink','purple','red','yellow']
    options = []

    for tag in tags:
        option = {}
        option['name'] = tag
        #option['color'] = color[hash(tag) % len(color)]
        options.append(option)

    return options
