#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import xmlrpc.client
import base64, time, re
from urllib.parse import urljoin

ODOO_URL  = "http://odoo:8069"
ODOO_DB   = "odoo19-db3"
ODOO_USER = "alilya.3108@gmail.com"
ODOO_PASS = "Alikhan31pro"

BASE_URL  = "https://po.qr-pib.kz"
LIST_URL  = "https://po.qr-pib.kz/ru/post/?page={}"
MAX_PAGES = 100
DELAY     = 0.8
HEADERS   = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def odoo_connect():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    if not uid:
        raise Exception("Неверный логин/пароль")
    return uid, xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

def odoo_exists(uid, models, title):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, "news.post",
        "search_count", [[["name", "=", title]]]) > 0

def odoo_create_news(uid, models, title, date_str, content_html, images_b64):
    from datetime import datetime
    try:
        date_iso = datetime.strptime(date_str.strip(), "%d.%m.%Y").strftime("%Y-%m-%d")
    except:
        date_iso = datetime.today().strftime("%Y-%m-%d")
    post_id = models.execute_kw(ODOO_DB, uid, ODOO_PASS, "news.post", "create",
        [{"name": title, "date": date_iso, "content": content_html, "is_published": True}])
    for idx, img in enumerate(images_b64):
        models.execute_kw(ODOO_DB, uid, ODOO_PASS, "news.post.image", "create",
            [{"post_id": post_id, "image": img, "sequence": idx}])
    return post_id

def get_links_from_page(page_num):
    try:
        r = requests.get(LIST_URL.format(page_num), headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"  ✗ {e}"); return []
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if re.match(r"^/ru/p/\d+$", href):
            full = urljoin(BASE_URL, href)
            if full not in links:
                links.append(full)
    return links

def parse_detail(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        r.raise_for_status()
    except Exception as e:
        print(f"  ✗ {e}"); return None

    soup = BeautifulSoup(r.text, "html.parser")

    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "Без заголовка"

    article = soup.find("article")
    date_str = ""
    if article:
        t = article.find("time")
        if t:
            date_str = t.get_text(strip=True)

    # ── Чистим article: удаляем time, img, слайдер ──
    content_html = "<p>Нет содержимого</p>"
    if article:
        import copy
        clean = copy.copy(article)

        # Удаляем все теги которые не должны быть в тексте
        for tag in clean.find_all(["time", "img", "picture", "source"]):
            tag.decompose()

        # Удаляем div со слайдером (кнопки prev/next, thumbnails)
        for tag in clean.find_all("div", class_=lambda c: c and any(
            x in " ".join(c) for x in ["carousel", "slider", "swiper", "gallery",
                                        "splide", "owl", "glide"]
        )):
            tag.decompose()

        # Берём только текстовые блоки
        text_blocks = []
        for tag in clean.find_all(["p", "h2", "h3", "h4", "ul", "ol", "blockquote"]):
            text = tag.get_text(strip=True)
            if text and len(text) > 5:
                text_blocks.append(str(tag))

        content_html = "\n".join(text_blocks) if text_blocks else clean.get_text(strip=True)

    # ── Изображения ──
    images_b64 = []
    if article:
        for img in article.find_all("img"):
            src = img.get("src", "")
            if not src or src.startswith("data:"):
                continue
            try:
                ir = requests.get(urljoin(BASE_URL, src), headers=HEADERS, timeout=8)
                if "image" in ir.headers.get("Content-Type", ""):
                    images_b64.append(base64.b64encode(ir.content).decode())
            except Exception:
                pass

    return {"title": title, "date": date_str, "content": content_html, "images": images_b64}
def main():
    print("Подключение к Odoo...")
    uid, models = odoo_connect()
    print(f"✓ uid={uid}\n")

    all_links = []
    empty_streak = 0
    for page in range(1, MAX_PAGES + 1):
        print(f"  Страница {page}...", end=" ", flush=True)
        links = get_links_from_page(page)
        new = [l for l in links if l not in all_links]
        if not new:
            empty_streak += 1
            print(f"+0 (всего {len(all_links)}) [{empty_streak}/3]")
            if empty_streak >= 3:
                print("  → Стоп"); break
        else:
            empty_streak = 0
            all_links.extend(new)
            print(f"+{len(new)} (всего {len(all_links)})")
        time.sleep(DELAY)

    print(f"\nНайдено: {len(all_links)}\n")
    ok = 0
    skipped = 0
    errors = 0

    for i, url in enumerate(all_links, 1):
        print(f"[{i}/{len(all_links)}] {url}")
        data = parse_detail(url)
        if not data:
            errors += 1; continue
        try:
            if odoo_exists(uid, models, data["title"]):
                print(f"  ⏭  Дубль: '{data['title'][:55]}'")
                skipped += 1; continue
        except Exception as e:
            print(f"  ✗ Проверка дубля: {e}")
        try:
            pid = odoo_create_news(uid, models, data["title"], data["date"],
                                   data["content"], data["images"])
            print(f"  ✓ ID={pid} | img={len(data['images'])}")
            ok += 1
        except Exception as e:
            print(f"  ✗ {e}"); errors += 1
        time.sleep(DELAY)

    print(f"\n{'='*40}")
    print(f"✓ Создано:    {ok}")
    print(f"⏭  Дублей:    {skipped}")
    print(f"✗ Ошибок:    {errors}")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
