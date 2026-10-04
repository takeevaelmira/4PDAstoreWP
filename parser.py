import json
import re
import time
import cloudscraper
from bs4 import BeautifulSoup

FORUM_URL = "https://4pda.to/forum/index.php?showforum=356"
MAX_TOPICS = 10  # Количество тем для проверки

# Создаем scraper для обхода защиты Cloudflare/4PDA
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

def fetch_page(url):
    """Безопасное скачивание страницы с обходом защиты"""
    try:
        response = scraper.get(url, timeout=20)
        response.encoding = 'windows-1251' # 4PDA использует cp1251[cite: 2]
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"[!] Ошибка загрузки {url}: Статус {response.status_code}")
            return None
    except Exception as e:
        print(f"[!] Исключение при запросе к {url}: {e}")
        return None

def get_topic_links(forum_url, limit=MAX_TOPICS):
    """Сбор ссылок на темы из раздела"""
    html = fetch_page(forum_url)
    if not html:
        print("[!] Не удалось загрузить страницу форума. Проверьте блокировку.")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    topics = []
    seen_ids = set()

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if 'showtopic=' in href:
            match = re.search(r'showtopic=(\d+)', href)
            if match:
                topic_id = match.group(1)
                if topic_id not in seen_ids:
                    seen_ids.add(topic_id)
                    full_url = f"https://4pda.to/forum/index.php?showtopic={topic_id}"
                    
                    title = a_tag.get_text(strip=True)
                    if not title or len(title) < 2:
                        continue
                        
                    topics.append({
                        'id': topic_id,
                        'url': full_url,
                        'list_title': title
                    })
                    
                    if len(topics) >= limit:
                        break

    return topics

def parse_single_topic(topic_info):
    """Парсинг деталей темы"""
    url = topic_info['url']
    html = fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    # Заголовок
    maintitle = soup.find('div', class_='maintitle') or soup.find('h1')
    title = maintitle.get_text(strip=True) if maintitle else topic_info['list_title']

    # Первое сообщение (шапка)
    first_post = soup.find('div', class_='post_body')
    description = ""
    if first_post:
        for tag in first_post(["script", "style"]):
            tag.extract()
        description = first_post.get_text(separator="\n", strip=True)
        if len(description) > 1200:
            description = description[:1200] + "...\n(Читать полностью на 4PDA)"

    # Комментарии
    posts = soup.find_all('div', class_='post_body')
    comments = []
    for post in posts[1:5]:
        for tag in post(["script", "style"]):
            tag.extract()
        text = post.get_text(strip=True)
        if len(text) > 15:
            comments.append(text[:250] + ("..." if len(text) > 250 else ""))

    return {
        "id": topic_info['id'],
        "title": title,
        "forum_url": url,
        "description": description if description else "Описание отсутствует.",
        "comments": comments
    }

def main():
    print(f"[*] Запуск парсера с cloudscraper для {FORUM_URL}")
    topics_list = get_topic_links(FORUM_URL, limit=MAX_TOPICS)
    print(f"[*] Найдено тем: {len(topics_list)}")

    parsed_apps = []
    for index, topic in enumerate(topics_list, 1):
        print(f"[{index}/{len(topics_list)}] Обработка темы {topic['id']}...")
        app_data = parse_single_topic(topic)
        if app_data:
            parsed_apps.append(app_data)
        time.sleep(2) # Задержка между запросами

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_apps, f, ensure_ascii=False, indent=2)

    print(f"[+] Готово! Сохранено элементов: {len(parsed_apps)}")

if __name__ == '__main__':
    main()
