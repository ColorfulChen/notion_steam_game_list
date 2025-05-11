from bs4 import BeautifulSoup
from urllib import request, parse
def get_steam_review_info(appid,userid):
    # 构造请求 URL 和 Headers
    url = f"https://steamcommunity.com/profiles/{userid}/recommended/{appid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    req = request.Request(url, headers=headers)

    try:
        with request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        #print(f"请求失败: AppID {appid}, 错误: {e}")
        return ''

    soup = BeautifulSoup(html, 'html.parser')
    review_text = ''

    try:
        review_text_element = soup.find('div', {'id': 'ReviewText'})
        if review_text_element:
            review_text = review_text_element.get_text(strip=True)
    except Exception as e:
        #print(f"游戏名提取失败: AppID {appid}, 错误: {e}")
        return ''

    return review_text
