import re
import time
from playwright.sync_api import sync_playwright, TimeoutError
from datetime import datetime

# --- Словарь псевдонимов для города отправления ---
DEPOT_SLUGS = {
    'санкт-петербург': 'spb',
    'москва': 'moscow',
    'великий новгород': 'veliky_novgorod',
    'выборг': 'vyborg',
    'псков': 'pskov',
    'мурманск': 'murmansk',
    'кириши': 'kirishi'
}

# --- Словарь ID направлений ---
STATION_IDS = {
    ('moscow', 'санкт-петербург'): 128713,
    ('spb', 'москва'): 5107,
    ('moscow', 'казань'): 85833, # только из Москвы на e-traffic
    ('moscow', 'сочи'): 42622, # только из Москвы на e-traffic
    ('spb', 'ростов-на-дону'): 3536,
    ('kirishi', 'санкт-петербург'): 128713, #только из Кириши на e-traffic
    ('moscow', 'екатеринбург'): 0000, #Нет на e-traffic
    ('moscow', 'новосибирск'): 0000, #Нет на e-traffic
    ('moscow', 'краснодар'): 131120, # только из Москвы на e-traffic
    ('moscow', 'уфа'): 8972, # только из Москвы на e-traffic
    ('moscow', 'красноярск'): 0000, #Нет на e-traffic
    ('moscow', 'владивосток'): 0000, #Нет на e-traffic
    ('moscow', 'рыбинск'): 57765, # только из Москвы на e-traffic
    ('spb', 'великий новгород'): 22937, # только из СПб на e-traffic
    ('moscow', 'нижний новгород'): 125662, # только из Москвы на e-traffic
    ('moscow', 'волгоград'): 41054, # только из Москвы на e-traffic
    ('moscow', 'воронеж'): 86502,  # только из Москвы на e-traffic
    ('spb', 'смоленск'): 32828,
    ('moscow', 'брянск'): 83646,  # только из Москвы на e-traffic
    ('spb', 'весьегонск'): 74988,
    ('moscow', 'кострома'): 54300,  # только из Москвы на e-traffic
    ('moscow', 'ярославль'): 3298,  # только из Москвы на e-traffic
}

def normalize_city_name(name: str) -> str:
    cleaned = re.split(r'\s*[*]+', name.strip())[0].lower()
    replacements = {
        'спб': 'санкт-петербург',
        'мск': 'москва',
        'н.новгород': 'нижний новгород',
        'нижний н-д': 'нижний новгород',
    }
    return replacements.get(cleaned, cleaned)

def parse_e_traffic(date: str, from_city: str, to_city: str) -> list[dict]:
    results = []
    from_city_norm = normalize_city_name(from_city)
    to_city_norm = normalize_city_name(to_city)

    depot_slug = DEPOT_SLUGS.get(from_city_norm)
    if not depot_slug:
        print(f"❌ Не найден slug для города отправления: {from_city}")
        return results

    station_id = STATION_IDS.get((depot_slug, to_city_norm))
    if not station_id:
        print(f"❌ Неизвестно ID направления: {from_city} → {to_city}")
        return results

    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = dt.strftime("%d.%m.%Y")
    except ValueError:
        print(f"❌ Неверный формат даты: {date}")
        return results

    url = f"https://e-traffic.ru/depot/{depot_slug}/{station_id}/{formatted_date}"
    print(f"🌐 Переход по URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="ru-RU"
        )
        page = context.new_page()

        try:
            # --- Переход по URL ---
            page.goto(url, wait_until="networkidle")
            print("✅ Страница загружена")

            # --- Сохранение HTML для отладки ---
            # with open("debug_e_traffic_pre_wait.html", "w", encoding="utf-8") as f:
            #     f.write(page.content())

            # --- Ожидание появления блока с рейсами ---
            print("⏳ Ожидание рейсов...")
            max_wait = 30
            for _ in range(max_wait):
                rows = page.query_selector_all("div.grid-row.row")
                if len(rows) > 0:
                    print("✅ Рейсы найдены")
                    break
                if page.locator("text=Рейсы не найдены").is_visible():
                    print("ℹ️ Рейсы не найдены для указанной даты.")
                    browser.close()
                    return results
                time.sleep(1)
            else:
                print("❌ Рейсы не загрузились за 30 секунд")
                # with open("debug_e_traffic_failed.html", "w", encoding="utf-8") as f:
                #     f.write(page.content())
                browser.close()
                return results

            # --- Извлечение данных ---
            rows = page.query_selector_all("div.grid-row.row")
            print(f"📊 Найдено {len(rows)} рейсов")

            for row in rows:
                try:
                    # Время отправления
                    time_elem = row.query_selector("div.dispatch .time")
                    time_text = time_elem.inner_text().strip() if time_elem else "N/A"

                    if time_text == "N/A":
                        continue

                    # Номер рейса (в теге <strong> внутри .route)
                    trip_number_elem = row.query_selector("div.route strong")
                    trip_number = trip_number_elem.inner_text().strip() if trip_number_elem else "N/A"

                    # Перевозчик
                    carrier_elem = row.query_selector("div.carrier.info")
                    carrier_text = carrier_elem.inner_text().strip() if carrier_elem else "N/A"
                    if "ИНН:" in carrier_text:
                        carrier_text = carrier_text.split("ИНН:")[0].strip().rstrip(",")

                    # Свободные места (в блоке .bus.info)
                    bus_info_elem = row.query_selector("div.bus.info")
                    bus_info_text = bus_info_elem.inner_text().strip() if bus_info_elem else ""
                    free_seats = "N/A"
                    free_match = re.search(r'свободно:\s*(\d+\+?|\d+)', bus_info_text, re.IGNORECASE)
                    if free_match:
                        free_seats = free_match.group(1)
                    elif "нет мест" in bus_info_text.lower() or "0" in bus_info_text:
                        free_seats = "0"

                    # Общее количество мест
                    total_seats = "N/A"
                    total_match = re.search(r'Мест:\s*(\d+)', bus_info_text, re.IGNORECASE)
                    if total_match:
                        total_seats = total_match.group(1)
                    else:
                        # Альтернативный паттерн: "Автобус 51 место"
                        total_match = re.search(r'Автобус\s*(\d+)\s*мест', bus_info_text, re.IGNORECASE)
                        if total_match:
                            total_seats = total_match.group(1)

                    # Проданные билеты
                    sold_tickets = "N/A"
                    if total_seats.isdigit() and free_seats.isdigit():
                        sold_tickets = str(int(total_seats) - int(free_seats))

                    # Цена
                    price_elem = row.query_selector("div.prices .price")
                    price_text = price_elem.inner_text().strip() if price_elem else "0"
                    price_digits = ''.join(filter(str.isdigit, price_text))
                    price = float(price_digits) if price_digits else 0.0

                    results.append({
                        'time': time_text,
                        'trip_number': trip_number,
                        'departure_point': from_city,
                        'arrival_point': to_city,
                        'carrier': carrier_text,
                        'total_seats': total_seats,
                        'free_seats': free_seats,
                        'sold_tickets': sold_tickets,
                        'price': price,
                        'source': 'e-traffic'
                    })

                except Exception as e:
                    print(f"⚠️ Ошибка при парсинге строки: {e}")
                    continue

        except Exception as e:
            print(f"❌ Ошибка при работе с Playwright: {e}")
        finally:
            browser.close()


        # --- СОХРАНЕНИЕ В EXCEL ---
        if results:
            try:
                from utils.save_to_excel import save_to_excel
                excel_filename = "data/history.xlsx"
                save_to_excel(results, filename=excel_filename, search_date=date)
                print(f"✅ Данные сохранены в {excel_filename}")
            except Exception as e:
                print(f"❌ Ошибка при сохранении в Excel: {e}")

        print(f"✅ Парсинг e-traffic завершён. Найдено {len(results)} рейсов.")
        return results