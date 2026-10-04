import json
import os
import requests
from bs4 import BeautifulSoup

# Список ссылок на темы 4PDA, которые нужно спарсить
TOPIC_URLS = [
    "https://4pda.to/forum/index.php?showtopic=123456" # Замените на реальные ссылки
]

def parse_topic(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'windows-1251' # 4PDA использует cp1251
        
        if response.status_code != 200:
            print(f"Ошибка загрузки {url}: статус {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Получаем заголовок
        title_tag = soup.find('div', class_='maintitle')
        title = title_tag.text.strip() if title_tag else "Неизвестное приложение"
        
        # Собираем комментарии
        comments = []
        post_blocks = soup.find_all('div', class_='post_body', limit=5)
        for post in post_blocks:
            text = post.get_text(strip=True)
            if len(text) > 10:
                comments.append({"text": text[:200] + "..."})

        app_data = {
            "id": url.split('=')[-1],
            "title": title,
            "version": "1.0",
            "icon": "",
            "forum_url": url,
            "comments": comments
        }
        
        return app_data
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return None

def main():
    apps = []
    for url in TOPIC_URLS:
        data = parse_topic(url)
        if data:
            apps.append(data)
            
    # Сохраняем в корень проекта под именем data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(apps, f, ensure_ascii=False, indent=2)
        
    print(f"Успешно сохранено приложений: {len(apps)}")

if __name__ == '__main__':
    main()
