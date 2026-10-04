import json
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

FORUM_URL = "https://4pda.to/forum/index.php?showforum=356"
MAX_TOPICS = 15  # Количество тем для парсинга за один запуск

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

def fetch_page(url):
    """Вспомогательная функция для безопасной загрузки страниц в cp1251"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = 'windows-1251' # 4PDA использует кодировку cp1251
        if response.status_code == 200:
            return response.text
        else:
            print(f"[!] Ошибка загрузки {url}: Код ответа {response.status_code}")
            return None
    except Exception as e:
        print(f"[!] Исключение при запросе к {url}: {e}")
        return None

def get_topic_links(forum_url, limit=MAX_TOPICS):
    """Сбор ссылок на темы из страницы раздела форума"""
    html = fetch_page(forum_url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    topics = []
    seen_ids = set()

    # Ищем ссылки на темы на странице форума
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if 'showtopic=' in href:
            match = re.search(r'showtopic=(\d+)', href)
            if match:
                topic_id = match.group(1)
                if topic_id not in seen_ids:
                    seen_ids.add(topic_id)
                    full_url = f"https://4pda.to/forum/index.php?showtopic={topic_id}"
                    
                    # Извлекаем название темы прямо из списка
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
    """Парсинг содержимого конкретной темы"""
    url = topic_info['url']
    html = fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    # 1. Заголовок темы
    maintitle = soup.find('div', class_='maintitle')
    if maintitle:
        title = maintitle.get_text(strip=True)
    else:
        title = topic_info['list_title']

    # 2. Первое сообщение (Шапка темы с описанием)
    first_post = soup.find('div', class_='post_body')
    description = ""
    if first_post:
        # Получаем чистый текст без лишних скриптов
        for script in first_post(["script", "style"]):
            script.extract()
        description = first_post.get_text(separator="\n", strip=True)
        # Ограничиваем длину описания для превью
        if len(description) > 1500:
            description = description[:1500] + "...\n(Читать полностью на 4PDA)"

    # 3. Сбор последних комментариев из темы
    posts = soup.find_all('div', class_='post_body')
    comments = []
    # Пропускаем первый пост (шапку), берем последующие как комментарии
    for post in posts[1:6]:
        for script in post(["script", "style"]):
            script.extract()
        text = post.get_text(strip=True)
        if len(text) > 15:
            comments.append(text[:300] + ("..." if len(text) > 300 else ""))

    return {
        "id": topic_info['id'],
        "title": title,
        "forum_url": url,
        "description": description if description else "Описание отсутствует или скрыто спойлером.",
        "comments": comments,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def main():
    print(f"[*] Начинаем сбор тем с раздела: {FORUM_URL}")
    topics_list = get_topic_links(FORUM_URL, limit=MAX_TOPICS)
    print(f"[*] Найдено тем для обработки: {len(topics_list)}")

    parsed_apps = []
    for index, topic in enumerate(topics_list, 1):
        print(f"[{index}/{len(topics_list)}] Парсим тему ID {topic['id']}...")
        app_data = parse_single_topic(topic)
        if app_data:
            parsed_apps.append(app_data)
        time.sleep(1) # Задержка, чтобы не перегружать сервер 4PDA

    # Сохраняем итоговый массив в data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_apps, f, ensure_ascii=False, indent=2)

    print(f"[+] Парсинг завершен. Сохранено элементов: {len(parsed_apps)}")

if __name__ == '__main__':
    main()
