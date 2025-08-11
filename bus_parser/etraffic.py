# import re
# import time
# from playwright.sync_api import sync_playwright, TimeoutError
# from datetime import datetime
#
# # --- Словарь псевдонимов для города отправления ---
# DEPOT_SLUGS = {
#     'санкт-петербург': 'spb',
#     'москва': 'moscow',
#     # 'выборг': #нет slug
#     'псков': 'pskov',
#     'мурманск': 'murmansk',
#     'казань': 'kazan',
#     'сочи': 'sochi',
#     'ростов-на-дону': 'rostov-na-donu',
#     'кириши': 'kirishi',
#     'екатеринбург': 'ekaterinburg',
#     'новосибирск': 'novosibirsk-all',
#     'краснодар': 'krasnodar',
#     'уфа': 'ufa',
#     'красноярск': 'krasnoyarsk-all',
#     'владивосток': 'vladivostok',
#     'рыбинск': 'rybinsk',
#     'великий новгород': 'v-novgorod-sksavto',
#     # 'нижний новгород': #нет slug
#     'рыбинск': 'rybinsk',
#     'волгоград': 'volgograd',
#     'воронеж': 'voronezh',
#     'смоленск': 'smolensk',
#     'брянск': 'braynsk',
#     'весьегонск': 'vesiegonsk',
#     'кострома': 'kostroma',
#     'ярославль': 'yaroslavl',
#     'псков': 'pskov',
#     'мурманск': 'murmansk',
# }
#
# # --- УНИВЕРСАЛЬНЫЙ СЛОВАРЬ: ID направлений по названию города ---
# # Ключ — нормализованное название города, значение — ID на e-traffic.ru
# # Направление "куда" всегда имеет фиксированный ID
# CITY_TO_STATION_ID = {
#     'санкт-петербург': 128713,
#     'москва': 5107,
#     'казань': 85833, # только из Москвы на e-traffic
#     'сочи': 42622, # только из Москвы на e-traffic
#     'ростов-на-дону': 3536,
#     'кириши': 0, # Нет на e-traffic из Москвы и СПб
#     'екатеринбург': 0,  # Нет на e-traffic из Москвы и СПб
#     'новосибирск': 0,   # Нет на e-traffic
#     'краснодар': 131120, # только из Москвы на e-traffic
#     'уфа': 8972, # только из Москвы на e-traffic
#     'красноярск': 0,    # Нет на e-traffic
#     'владивосток': 0,   # Нет на e-traffic
#     'рыбинск': 57765, # только из Москвы на e-traffic
#     'великий новгород': 22937, # только из СПб на e-traffic
#     'нижний новгород': 125662, # только из Москвы на e-traffic
#     'волгоград': 41054, # только из Москвы на e-traffic
#     'воронеж': 86502, # только из Москвы на e-traffic
#     'смоленск': 32828,
#     'брянск': 83646, # только из Москвы на e-traffic
#     'весьегонск': 74988,
#     'кострома': 54300, # только из Москвы на e-traffic
#     'ярославль': 3298, # только из Москвы на e-traffic
#     'псков': 73707,
#     'мурманск': 118744, # только из Киркенес на e-traffic
# }
# def normalize_city_name(name: str) -> str:
#     cleaned = re.split(r'\s*[*]+', name.strip())[0].lower()
#     replacements = {
#         'спб': 'санкт-петербург',
#         'мск': 'москва',
#         'н.новгород': 'нижний новгород',
#         'нижний н-д': 'нижний новгород',
#     }
#     return replacements.get(cleaned, cleaned)
#
# def parse_e_traffic(date: str, from_city: str, to_city: str) -> list[dict]:
#     results = []
#     from_city_norm = normalize_city_name(from_city)
#     to_city_norm = normalize_city_name(to_city)
#
#     depot_slug = DEPOT_SLUGS.get(from_city_norm)
#     if not depot_slug:
#         print(f"❌ Не найден slug для города отправления: {from_city}")
#         return results
#
#      # Получаем ID направления "куда"
#     station_id = CITY_TO_STATION_ID.get(to_city_norm)
#     if not station_id:
#         print(f"❌ Неизвестно ID направления: {to_city}")
#         print(f"Доступные направления: {list(CITY_TO_STATION_ID.keys())}")
#         return results
#
#     if station_id == 0:
#         print(f"ℹ️ Направление {from_city} → {to_city} не поддерживается на e-traffic.ru")
#         return results
#
#     try:
#         dt = datetime.strptime(date, "%Y-%m-%d")
#         formatted_date = dt.strftime("%d.%m.%Y")
#     except ValueError:
#         print(f"❌ Неверный формат даты: {date}")
#         return results
#
#     url = f"https://e-traffic.ru/depot/{depot_slug}/{station_id}/{formatted_date}"
#     print(f"🌐 Переход по URL: {url}")
#
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False, slow_mo=500)
#         context = browser.new_context(
#             viewport={"width": 1920, "height": 1080},
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#             locale="ru-RU"
#         )
#         page = context.new_page()
#
#         try:
#             # --- Переход по URL ---
#             page.goto(url, wait_until="networkidle")
#             print("✅ Страница загружена")
#
#             # --- Сохранение HTML для отладки ---
#             # with open("debug_e_traffic_pre_wait.html", "w", encoding="utf-8") as f:
#             #     f.write(page.content())
#
#             # --- Ожидание появления блока с рейсами ---
#             print("⏳ Ожидание рейсов...")
#             max_wait = 30
#             for _ in range(max_wait):
#                 rows = page.query_selector_all("div.grid-row.row")
#                 if len(rows) > 0:
#                     print("✅ Рейсы найдены")
#                     break
#                 if page.locator("text=Рейсы не найдены").is_visible():
#                     print("ℹ️ Рейсы не найдены для указанной даты.")
#                     browser.close()
#                     return results
#                 time.sleep(1)
#             else:
#                 print("❌ Рейсы не загрузились за 30 секунд")
#                 # with open("debug_e_traffic_failed.html", "w", encoding="utf-8") as f:
#                 #     f.write(page.content())
#                 browser.close()
#                 return results
#
#             # --- Извлечение данных ---
#             rows = page.query_selector_all("div.grid-row.row")
#             print(f"📊 Найдено {len(rows)} рейсов")
#
#             for row in rows:
#                 try:
#                     # Время отправления
#                     time_elem = row.query_selector("div.dispatch .time")
#                     time_text = time_elem.inner_text().strip() if time_elem else "N/A"
#
#                     if time_text == "N/A":
#                         continue
#
#                     # Номер рейса (в теге <strong> внутри .route)
#                     trip_number_elem = row.query_selector("div.route strong")
#                     trip_number = trip_number_elem.inner_text().strip() if trip_number_elem else "N/A"
#
#                     # Перевозчик
#                     carrier_elem = row.query_selector("div.carrier.info")
#                     carrier_text = carrier_elem.inner_text().strip() if carrier_elem else "N/A"
#                     if "ИНН:" in carrier_text:
#                         carrier_text = carrier_text.split("ИНН:")[0].strip().rstrip(",")
#
#                     # Свободные места (в блоке .bus.info)
#                     bus_info_elem = row.query_selector("div.bus.info")
#                     bus_info_text = bus_info_elem.inner_text().strip() if bus_info_elem else ""
#                     free_seats = "N/A"
#                     free_match = re.search(r'свободно:\s*(\d+\+?|\d+)', bus_info_text, re.IGNORECASE)
#                     if free_match:
#                         free_seats = free_match.group(1)
#                     elif "нет мест" in bus_info_text.lower() or "0" in bus_info_text:
#                         free_seats = "0"
#
#                     # Общее количество мест
#                     total_seats = "N/A"
#                     total_match = re.search(r'Мест:\s*(\d+)', bus_info_text, re.IGNORECASE)
#                     if total_match:
#                         total_seats = total_match.group(1)
#                     else:
#                         # Альтернативный паттерн: "Автобус 51 место"
#                         total_match = re.search(r'Автобус\s*(\d+)\s*мест', bus_info_text, re.IGNORECASE)
#                         if total_match:
#                             total_seats = total_match.group(1)
#
#                     # Проданные билеты
#                     sold_tickets = "N/A"
#                     if total_seats.isdigit() and free_seats.isdigit():
#                         sold_tickets = str(int(total_seats) - int(free_seats))
#
#                     # Цена
#                     price_elem = row.query_selector("div.prices .price")
#                     price_text = price_elem.inner_text().strip() if price_elem else "0"
#                     price_digits = ''.join(filter(str.isdigit, price_text))
#                     price = float(price_digits) if price_digits else 0.0
#
#                     results.append({
#                         'time': time_text,
#                         'trip_number': trip_number,
#                         'departure_point': from_city,
#                         'arrival_point': to_city,
#                         'carrier': carrier_text,
#                         'total_seats': total_seats,
#                         'free_seats': free_seats,
#                         'sold_tickets': sold_tickets,
#                         'price': price,
#                         'source': 'e-traffic'
#                     })
#
#                 except Exception as e:
#                     print(f"⚠️ Ошибка при парсинге строки: {e}")
#                     continue
#
#         except Exception as e:
#             print(f"❌ Ошибка при работе с Playwright: {e}")
#         finally:
#             browser.close()
#
#
#         # --- СОХРАНЕНИЕ В EXCEL ---
#         if results:
#             try:
#                 from utils.save_to_excel import save_to_excel
#                 excel_filename = "data/history.xlsx"
#                 save_to_excel(results, filename=excel_filename, search_date=date)
#                 print(f"✅ Данные сохранены в {excel_filename}")
#             except Exception as e:
#                 print(f"❌ Ошибка при сохранении в Excel: {e}")
#
#         print(f"✅ Парсинг e-traffic завершён. Найдено {len(results)} рейсов.")
#         return results

import re
import time
from datetime import datetime

# Импорты Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# Импортируем утилиту сохранения
try:
    from utils.save_to_excel import save_to_excel
except ImportError:
    print("⚠️ Модуль save_to_excel не найден. Сохранение отключено.")
    save_to_excel = None


# --- Словарь псевдонимов для города отправления ---
DEPOT_SLUGS = {
    'санкт-петербург': 'spb',
    'москва': 'moscow',
    'псков': 'pskov',
    'мурманск': 'murmansk',
    'казань': 'kazan',
    'сочи': 'sochi',
    'ростов-на-дону': 'rostov-na-donu',
    'кириши': 'kirishi',
    'екатеринбург': 'ekaterinburg',
    'новосибирск': 'novosibirsk-all',
    'краснодар': 'krasnodar',
    'уфа': 'ufa',
    'красноярск': 'krasnoyarsk-all',
    'владивосток': 'vladivostok',
    'рыбинск': 'rybinsk',
    'великий новгород': 'v-novgorod-sksavto',
    'волгоград': 'volgograd',
    'воронеж': 'voronezh',
    'смоленск': 'smolensk',
    'брянск': 'braynsk',
    'весьегонск': 'vesiegonsk',
    'кострома': 'kostroma',
    'ярославль': 'yaroslavl',
}

# --- УНИВЕРСАЛЬНЫЙ СЛОВАРЬ: ID направлений по названию города ---
CITY_TO_STATION_ID = {
    'санкт-петербург': 128713,
    'москва': 5107,
    'казань': 85833,
    'сочи': 42622,
    'ростов-на-дону': 3536,
    'кириши': 0,
    'екатеринбург': 0,
    'новосибирск': 0,
    'краснодар': 131120,
    'уфа': 8972,
    'красноярск': 0,
    'владивосток': 0,
    'рыбинск': 57765,
    'великий новгород': 22937,
    'нижний новгород': 125662,
    'волгоград': 41054,
    'воронеж': 86502,
    'смоленск': 32828,
    'брянск': 83646,
    'весьегонск': 74988,
    'кострома': 54300,
    'ярославль': 3298,
    'псков': 73707,
    'мурманск': 118744,
}


def normalize_city_name(name: str) -> str:
    """Нормализует название города."""
    cleaned = re.split(r'\s*[*]+', name.strip())[0].lower()
    replacements = {
        'спб': 'санкт-петербург',
        'мск': 'москва',
        'н.новгород': 'нижний новгород',
        'нижний н-д': 'нижний новгород',
    }
    return replacements.get(cleaned, cleaned)


def parse_e_traffic(date: str, from_city: str, to_city: str) -> list[dict]:
    """
    Парсит расписание с e-traffic.ru (Selenium версия)
    """
    results = []
    from_city_norm = normalize_city_name(from_city)
    to_city_norm = normalize_city_name(to_city)

    depot_slug = DEPOT_SLUGS.get(from_city_norm)
    if not depot_slug:
        print(f"❌ Не найден slug для города отправления: {from_city}")
        return results

    station_id = CITY_TO_STATION_ID.get(to_city_norm)
    if not station_id:
        print(f"❌ Неизвестно ID направления: {to_city}")
        return results

    if station_id == 0:
        print(f"ℹ️ Направление {from_city} → {to_city} не поддерживается на e-traffic.ru")
        return results

    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = dt.strftime("%d.%m.%Y")
    except ValueError:
        print(f"❌ Неверный формат даты: {date}")
        return results

    url = f"https://e-traffic.ru/depot/{depot_slug}/{station_id}/{formatted_date}"
    print(f"🌐 Переход по URL: {url}")

    # Настройка Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--lang=ru-RU")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Запуск браузера
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)

    try:
        print("🌐 Переходим на страницу...")
        driver.get(url)

        print("⏳ Ожидание загрузки рейсов...")

        # Ждём появления хотя бы одного блока с рейсом
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.grid-row.row")))
            print("✅ Рейсы найдены")
        except TimeoutException:
            if "Рейсы не найдены" in driver.page_source:
                print("ℹ️ Рейсы не найдены для указанной даты.")
                return results
            print("❌ Рейсы не загрузились за 30 секунд")
            return results

        # Получаем все строки с рейсами
        rows = driver.find_elements(By.CSS_SELECTOR, "div.grid-row.row")
        print(f"📊 Найдено {len(rows)} рейсов")

        for row in rows:
            try:
                # Время отправления
                time_text = safe_get_text(row, "div.dispatch .time") or "N/A"
                if time_text == "N/A":
                    continue

                # Номер рейса
                trip_number = safe_get_text(row, "div.route strong") or "N/A"

                # Перевозчик
                carrier_text = safe_get_text(row, "div.carrier.info") or "N/A"
                if "ИНН:" in carrier_text:
                    carrier_text = carrier_text.split("ИНН:")[0].strip().rstrip(",")

                # Информация об автобусе
                bus_info_text = safe_get_text(row, "div.bus.info") or ""
                free_seats = "N/A"
                total_seats = "N/A"
                sold_tickets = "N/A"

                # Свободные места
                free_match = re.search(r'свободно:\s*(\d+\+?|\d+)', bus_info_text, re.IGNORECASE)
                if free_match:
                    free_seats = free_match.group(1)
                elif "нет мест" in bus_info_text.lower() or "0" in bus_info_text:
                    free_seats = "0"

                # Общее количество мест
                total_match = re.search(r'Мест:\s*(\d+)', bus_info_text, re.IGNORECASE)
                if total_match:
                    total_seats = total_match.group(1)
                else:
                    total_match = re.search(r'Автобус\s*(\d+)\s*мест', bus_info_text, re.IGNORECASE)
                    if total_match:
                        total_seats = total_match.group(1)

                # Проданные билеты
                if total_seats.isdigit() and free_seats.isdigit():
                    sold_tickets = str(int(total_seats) - int(free_seats))

                # Цена
                price_text = safe_get_text(row, "div.prices .price") or "0"
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

            except StaleElementReferenceException:
                print("⚠️ Элемент стал устаревшим, пропускаем...")
                continue
            except Exception as e:
                print(f"⚠️ Ошибка при парсинге строки: {e}")
                continue

    except Exception as e:
        print(f"❌ Ошибка при работе с Selenium: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
        print("🔒 Браузер закрыт")

    # Сохранение в Excel
    if results and save_to_excel:
        try:
            excel_filename = "data/history.xlsx"
            save_to_excel(results, filename=excel_filename, search_date=date)
            print(f"✅ Данные сохранены в {excel_filename}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении в Excel: {e}")

    print(f"✅ Парсинг e-traffic завершён. Найдено {len(results)} рейсов.")
    return results


def safe_get_text(element, selector):
    """Безопасное получение текста из элемента."""
    try:
        el = element.find_element(By.CSS_SELECTOR, selector)
        return el.text.strip()
    except (NoSuchElementException, StaleElementReferenceException):
        return "N/A"
    except Exception:
        return "N/A"