# import asyncio
# import sys
# import random
# import time
# import os
# from playwright.sync_api import sync_playwright
# import urllib.parse
# import re
# # import pandas as pd
# from datetime import datetime
# from utils.save_to_excel import save_to_excel
#
#
# # --- НЕ МЕНЯЕМ: Функция получения ID городов ---
# def get_city_ids():
#     """Возвращает словарь с ID городов"""
#     return {
#         'санкт-петербург': 4491,
#         'москва': 4140,
#         'казань': 3792,
#         'сочи': 4575,
#         'ростов-на-дону': 4456,
#         'кириши': 7753,
#         'екатеринбург': 3689, # Нет на Busfor
#         'новосибирск': 5096, # Нет на Busfor
#         'краснодар': 3935,
#         'уфа': 4718,
#         'красноярск': 5061, # Нет на Busfor
#         'владивосток': 2341,
#         'рыбинск': 5127,
#         'великий новгород': 3474,
#         'нижний новгород': 4188,
#         'волгоград': 3512,
#         'воронеж': 3527,
#         'смоленск': 4556,
#         'брянск': 3436,
#         'весьегонск': 5201,
#         'кострома': 3915, # Только из Москвы на Busfor
#         'ярославль': 4863, # Только из Москвы на Busfor
#         'псков': 4398,
#         'мурманск': 4149,  # нет билетов вообще
#     }
#
# # --- НЕ МЕНЯЕМ: Функция извлечения номера рейса ---
# def extract_trip_number(text):
#     """Извлекает номер рейса из текста, используя несколько паттернов."""
#     if not text:
#         return ""
#     text = text.strip()
#
#     # Паттерн 1: "Рейс № <число>" (наиболее распространенный)
#     # Учитываем разные варианты написания №
#     match = re.search(r'Рейс\s*[#№]\s*(\d+)', text, re.IGNORECASE)
#     if match:
#         return match.group(1)
#
#     # Паттерн 2: "<число> <Город1> - <Город2>" в начале строки
#     # Например: "856 Санкт-Петербург (м. Волковская) - Кириши (Привокзальная) 19:15"
#     match = re.search(r'^(\d+)\s+\S+\s*[-–—]\s*\S+', text)
#     if match:
#         return match.group(1)
#
#     # Паттерн 3: Просто первые цифры в строке, если они есть
#     lines = text.split('\n')
#     first_line = lines[0] if lines else text
#     match = re.search(r'^(\d+)', first_line.strip())
#     if match:
#         candidate = match.group(1)
#         # Добавим базовую проверку длины
#         if 1 <= len(candidate) <= 6:
#             return candidate
#
#     return ""
#
# # --- НЕ МЕНЯЕМ: Основная функция парсинга ---
# def parse_busfor(date, from_city, to_city):
#     if sys.platform == "win32":
#         asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
#
#     results = []
#     city_ids = get_city_ids()
#
#     try:
#         # --- ИСПРАВЛЕНИЕ 1: Надежный поиск ID городов ---
#         # Функция для нормализации названия города перед поиском в словаре
#         # Убираем потенциальные примечания типа "*" или "**" и приводим к нижнему регистру
#         def normalize_city_name(name):
#             cleaned_name = re.split(r'\s*[*]+', name)[0].strip()
#             return cleaned_name.lower()
#
#         from_city_normalized = normalize_city_name(from_city)
#         to_city_normalized = normalize_city_name(to_city)
#
#         from_id = city_ids.get(from_city_normalized)
#         to_id = city_ids.get(to_city_normalized)
#
#         if not from_id or not to_id:
#             print(f"Не найдены ID для городов: '{from_city}' ({from_city_normalized}) -> '{to_city}' ({to_city_normalized})")
#             print(f"Доступные города в словаре: {list(city_ids.keys())}")
#             return results
#         # --- КОНЕЦ ИСПРАВЛЕНИЯ 1 ---
#
#         # --- ИСПРАВЛЕНИЕ 2: Правильное формирование URL ---
#         # Функция для форматирования названия города для URL-пути
#         # Убираем примечания и заменяем пробелы на дефисы
#         def format_city_for_url_path(city_name):
#             # Убираем примечания типа "*" или "**"
#             cleaned_name = re.split(r'\s*[*]+', city_name)[0].strip()
#             # Заменяем пробелы на дефисы
#             hyphenated_name = cleaned_name.replace(" ", "-")
#             return hyphenated_name
#
#         # Формируем путь URL с дефисами вместо пробелов
#         from_city_url_path = format_city_for_url_path(from_city)
#         to_city_url_path = format_city_for_url_path(to_city)
#
#         # Строим URL вручную, используя отформатированные названия городов
#         # urllib.parse.quote будет применен только к самим названиям городов в пути,
#         # но так как мы уже заменили пробелы на дефисы, кодирование будет корректным для кириллицы.
#         # Однако, на практике браузеры часто не кодируют кириллицу в URL-адресной строке для удобочитаемости,
#         # но сервер должен корректно обработать UTF-8.
#         # Чтобы быть ближе к тому, что видит пользователь, мы можем вообще не кодировать путь,
#         # или кодировать его с разрешенными символами кириллицы и дефиса.
#         # Простейший и эффективный способ: собрать путь напрямую.
#         path_part = f"/автобусы/{from_city_url_path}/{to_city_url_path}"
#         # Если сайт строгий к кодированию, можно закодировать, но разрешить ряд символов:
#         # path_part_encoded = urllib.parse.quote(path_part, safe='/-')
#
#         # Для параметров запроса используем стандартное кодирование
#         query_params = f"from_id={from_id}&to_id={to_id}&on={date}&passengers=1&search=true"
#
#         # Собираем полный URL
#         # url = f"https://busfor.ru{path_part_encoded}?{query_params}" # Если решили кодировать путь
#         url = f"https://busfor.ru{path_part}?{query_params}" # Прямая сборка
#
#         print(f"Переход по адресу: {url}")
#         # --- КОНЕЦ ИСПРАВЛЕНИЯ 2 ---
#
#         with sync_playwright() as p:
#             # Используем постоянный контекст с профилем пользователя
#             user_data_dir = "./user_data_busfor"
#             os.makedirs(user_data_dir, exist_ok=True)
#             browser = p.chromium.launch_persistent_context(
#                 user_data_dir=user_data_dir,
#                 headless=False,  # Всегда показываем браузер для отладки
#                 args=[
#                     '--no-sandbox',
#                     '--disable-dev-shm-usage',
#                     '--disable-blink-features=AutomationControlled',
#                     '--disable-extensions',
#                     '--no-first-run',
#                     '--lang=ru-RU'
#                 ]
#             )
#
#             page = browser.new_page()
#
#             # Реалистичные заголовки
#             page.set_extra_http_headers({
#                 "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
#                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#                 "Accept-Encoding": "gzip, deflate, br",
#                 "Upgrade-Insecure-Requests": "1",
#                 "Sec-Fetch-Dest": "document",
#                 "Sec-Fetch-Mode": "navigate",
#                 "Sec-Fetch-Site": "none",
#                 "Sec-Fetch-User": "?1"
#             })
#
#             # Анти-детект скрипт
#             page.add_init_script("""
#                 Object.defineProperty(navigator, 'webdriver', {
#                     get: () => undefined
#                 });
#                 window.chrome = {
#                     runtime: {}
#                 };
#                 Object.defineProperty(navigator, 'languages', {
#                     get: () => ['ru-RU', 'ru', 'en-US', 'en']
#                 });
#                 Object.defineProperty(navigator, 'plugins', {
#                     get: () => [1, 2, 3, 4, 5]
#                 });
#             """)
#
#             page.set_viewport_size({"width": 1920, "height": 1080})
#             page.set_default_timeout(60000)  # 1 минута
#
#             # 1. Загрузка главной страницы
#             print("Загрузка главной страницы...")
#             page.goto("https://busfor.ru/")
#             # Используем page.wait_for_timeout вместо time.sleep для совместимости
#             # page.wait_for_timeout(random.uniform(2000, 4000))
#             page.wait_for_timeout(1000)
#
#             # 2. Переход к результатам поиска
#             print("Переход к результатам поиска...")
#             # page.wait_for_timeout(random.uniform(3000, 7000)) # Убираем, так как сразу переходим
#             response = page.goto(url)
#             print(f"Статус ответа: {response.status if response else 'Нет ответа'}")
#
#             if response and response.status == 403:
#                 print("❌ Доступ запрещен (403). Возможно, требуется ручное решение капчи.")
#                 print("Пожалуйста, решите капчу в браузере вручную и нажмите Enter...")
#                 input("Готово? Нажмите Enter для продолжения...")
#                 # Повторная попытка
#                 response = page.goto(url)
#                 print(f"Повторный статус: {response.status if response else 'Нет ответа'}")
#
#             # 3. Ожидание загрузки страницы и результатов
#             print("Ожидание загрузки результатов...")
#             # Ждем появления основного контейнера с результатами
#             try:
#                 page.wait_for_selector("[class*='TripWrappers'], .ticket", timeout=30000)
#                 print("Контейнер с рейсами загружен.")
#             except:
#                 print("Контейнер с рейсами не загрузился за 30 секунд.")
#
#             # Используем page.wait_for_timeout
#             page.wait_for_timeout(random.uniform(3000, 5000))  # Дополнительное ожидание для JS
#
#             # 4. Проверка на блокировку
#             try:
#                 if page.query_selector("text=Please enable JS") or page.query_selector("[class*='captcha']"):
#                     print("⚠️ Требуется ручное вмешательство!")
#                     print("Решите капчу/включите JS в браузере и нажмите Enter...")
#                     input("Готово? Нажмите Enter для продолжения...")
#                     page.wait_for_timeout(random.uniform(2000, 3000))
#             except:
#                 pass
#
#             # 5. Сохранение для анализа
#             try:
#                 content = page.content()
#                 # Создаем папку data, если её нет
#                 os.makedirs("data", exist_ok=True)
#                 filename = f"data/debug_busfor_{from_city}_{to_city}_{date}.html"
#                 with open(filename, "w", encoding="utf-8") as f:
#                     f.write(content)
#                 print(f"Страница сохранена в {filename}")
#             except Exception as e:
#                 print(f"Ошибка сохранения страницы: {e}")
#
#             # 6. Поиск и парсинг рейсов
#             print("Поиск рейсов...")
#             # Ищем все билеты
#             tickets = page.query_selector_all(".ticket")
#             print(f"Найдено {len(tickets)} билетов")
#
#             for i in range(len(tickets)): # Используем range(len(...)) для индексации
#                 try:
#                     print(f"Обработка билета {i + 1}/{len(tickets)}")
#
#                     # --- КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Перезапрос билета ПЕРЕД каждым действием ---
#                     # Это помогает избежать ошибки "Element is not attached to the DOM"
#                     # Получаем текущий список билетов
#                     current_tickets = page.query_selector_all(".ticket")
#                     # Проверяем, существует ли билет с таким индексом
#                     if i >= len(current_tickets):
#                          print(f"  Билет {i + 1} больше не существует на странице.")
#                          continue # Переходим к следующему билету
#
#                     # Получаем "свежий" элемент билета
#                     ticket_element = current_tickets[i]
#                     # --- КОНЕЦ КРИТИЧЕСКОГО ИСПРАВЛЕНИЯ ---
#
#                     # --- Клик на "Детали рейса" ---
#                     # Снова перезапрашиваем кнопку внутри "свежего" билета
#                     details_button = ticket_element.query_selector("[class*='Style__Toggle-sc-13gvs4g-1']")
#                     if details_button:
#                         # Проверяем, нужно ли кликать (стрелка вниз)
#                         toggle_icon = details_button.query_selector("[class*='ToggleIcon']")
#                         icon_class = toggle_icon.get_attribute("class") if toggle_icon else ""
#                         if "down-arrow" in icon_class:
#                             print(f"  Клик на 'Детали рейса' для билета {i + 1}")
#                             details_button.click()
#                             # Ждем, пока детали загрузятся или DOM изменится
#                             # page.wait_for_timeout может быть не самым надежным
#                             # Лучше дождаться появления элемента внутри деталей
#                             try:
#                                 # Ждем появления любого элемента внутри Details
#                                 ticket_element.wait_for_selector("[class*='Details'] *", timeout=3000)
#                                 print(f"    Детали для билета {i + 1} загружены.")
#                             except:
#                                 print(f"    Таймаут ожидания деталей для билета {i + 1}, продолжаем...")
#                             # Или короткий фиксированный таймаут
#                             # page.wait_for_timeout(random.uniform(800, 1500))
#                             page.wait_for_timeout(500)
#                         else:
#                             print(f"  Детали для билета {i + 1} уже открыты или кнопка неактивна.")
#                     # else:
#                     #     print(f"  Кнопка 'Детали рейса' не найдена для билета {i + 1}.")
#
#                     # --- Извлечение данных ---
#                     # СНОВА перезапрашиваем билет и все элементы внутри него ПОСЛЕ клика и ожидания
#                     refreshed_tickets = page.query_selector_all(".ticket")
#                     if i >= len(refreshed_tickets):
#                          print(f"  Билет {i + 1} исчез после клика.")
#                          continue
#                     working_ticket = refreshed_tickets[i] # Этот элемент должен быть "живым"
#
#                     # 1. Время отправления
#                     time_text = "N/A"
#                     time_element = working_ticket.query_selector("[type='from'] .Style__Time-sc-1n9rkhj-0")
#                     if time_element:
#                         full_time_text = time_element.inner_text().strip()
#                         # Обычно время идет первой строкой, дата - второй
#                         lines = full_time_text.split('\n')
#                         time_text = lines[0] if lines else "N/A"
#                     else:
#                         # Альтернативный поиск
#                         time_elements = working_ticket.query_selector_all("[class*='TimeStart'] [class*='Time'], [type='from'] [class*='Time']")
#                         for elem in time_elements:
#                             text = elem.inner_text().strip()
#                             time_match = re.search(r'\b\d{1,2}:\d{2}\b', text)
#                             if time_match:
#                                 time_text = time_match.group(0)
#                                 break
#
#                     # 2. Перевозчик
#                     carrier_text = "N/A"
#                     # Ищем в деталях рейса после клика
#                     # Уточняем селекторы, основываясь на структуре из debug файла
#                     carrier_selectors = [
#                         "[class*='DetailsRouteColumn'] p:has(span:contains('Бренд:')) strong",
#                         "[class*='DetailsRouteColumn'] p:has(span:contains('Перевозчик:')) strong",
#                         "[class*='Details'] p:has(strong:contains('Бренд'))",
#                         "[class*='Details'] p:has(strong:contains('Перевозчик'))",
#                         "[class*='Details'] p strong",
#                         "[class*='Details'] div:has(strong)" # Очень общий, проверим последним
#                     ]
#
#                     found_carrier = False
#                     for selector in carrier_selectors:
#                         try:
#                             # Используем более безопасный способ поиска
#                             elems = working_ticket.query_selector_all(selector)
#                             for elem in elems:
#                                 text = elem.inner_text().strip()
#                                 # Проверяем, похоже ли это на название компании
#                                 # Упрощенная проверка
#                                 if text and any(org in text for org in ["ООО", "АО", "ИП", "ФТК", "ECOLINES", "Сотранс", "Круиз", "ВОЛГА", "БЕРКУТ", "Яцунов"]):
#                                     carrier_text = text
#                                     found_carrier = True
#                                     # print(f"      Найден перевозчик по '{selector}': {carrier_text}") # Отладка
#                                     break
#                         except Exception:
#                             # Игнорируем ошибки отдельных селекторов
#                             pass
#                         if found_carrier:
#                             break
#
#                     # Если в деталях не нашли, ищем в основном блоке билета
#                     if not found_carrier or carrier_text == "N/A":
#                         carrier_element = working_ticket.query_selector("[class*='CarrierTitle'] + span")
#                         if carrier_element:
#                             carrier_text = carrier_element.inner_text().strip()
#                         else:
#                             carrier_elements = working_ticket.query_selector_all("[class*='Carrier'] span:last-child")
#                             for elem in carrier_elements:
#                                 text = elem.inner_text().strip()
#                                 if text and any(org in text for org in ["ООО", "АО", "ИП", "ФТК", "ECOLINES", "Сотранс"]):
#                                     carrier_text = text
#                                     # print(f"      Найден перевозчик в основном блоке: {carrier_text}") # Отладка
#                                     break
#
#                     # if carrier_text == "N/A":
#                     #     print(f"      Перевозчик не найден для билета {i + 1}")
#
#                     # 3. Цена
#                     price = 0.0
#                     price_element = working_ticket.query_selector(".price")
#                     if price_element:
#                         price_text = price_element.inner_text().strip()
#                         price_digits = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
#                         if price_digits:
#                             price = float(price_digits)
#
#                     # 4. Свободные места
#                     free_seats_display = "N/A"
#                     free_seats_numeric = None
#                     seats_element = working_ticket.query_selector("[class*='Seats']")
#                     if seats_element:
#                         seats_text = seats_element.inner_text().strip()
#                         if any(word in seats_text.lower() for word in ["10+", "много"]):
#                             free_seats_display = "10+"
#                             free_seats_numeric = 10
#                         elif "осталось" in seats_text.lower() and "1" in seats_text:
#                             free_seats_display = "1"
#                             free_seats_numeric = 1
#                         else:
#                             seats_digits = ''.join(filter(str.isdigit, seats_text))
#                             if seats_digits:
#                                 free_seats_display = seats_digits
#                                 free_seats_numeric = int(seats_digits)
#
#                     # 5. Общее количество мест
#                     total_seats_text = "N/A"
#                     total_seats_numeric = 50 # По умолчанию
#
#                     # Ищем в деталях рейса
#                     bus_info_selectors = [
#                         "[class*='DetailsRouteColumn'] p:has(span:contains('Автобус:'))",
#                         "[class*='Details'] p:has(strong:contains('Автобус'))",
#                         "[class*='Details'] p:has(strong:contains('Мест'))",
#                         "[class*='Details'] p"
#                     ]
#                     found_seats_in_details = False
#                     for selector in bus_info_selectors:
#                         try:
#                             elems = working_ticket.query_selector_all(selector)
#                             for elem in elems:
#                                 text = elem.inner_text().strip()
#                                 if "Мест" in text or "мест" in text.lower():
#                                     total_seats_match = re.search(r'(\d+)\s*(?:мест|Мест)', text)
#                                     if total_seats_match:
#                                         total_seats_text = total_seats_match.group(1)
#                                         total_seats_numeric = int(total_seats_match.group(1))
#                                         # print(f"      Найдено мест по '{selector}': {total_seats_text}") # Отладка
#                                         found_seats_in_details = True
#                                         break
#                         except:
#                             pass
#                         if found_seats_in_details:
#                             break
#
#                     # Если в деталях не нашли, ищем в основном блоке
#                     if not found_seats_in_details:
#                         bus_model_element = working_ticket.query_selector("[class*='BusModel']")
#                         if bus_model_element:
#                             bus_model_text = bus_model_element.inner_text().strip()
#                             total_seats_match = re.search(r'(\d+)\s*(?:мест|Мест)', bus_model_text)
#                             if total_seats_match:
#                                 total_seats_text = total_seats_match.group(1)
#                                 total_seats_numeric = int(total_seats_match.group(1))
#                                 # print(f"      Найдено мест в основном блоке: {total_seats_text}") # Отладка
#
#                     # 6. Количество проданных билетов (расчет)
#                     sold_tickets = "N/A"
#                     if total_seats_numeric is not None and free_seats_numeric is not None:
#                         sold_tickets = total_seats_numeric - free_seats_numeric
#
#                     # 7. Номер рейса - УЛУЧШЕННЫЙ ПОИСК
#                     trip_number = ""
#
#                     # Сначала ищем в деталях, где он чаще всего находится
#                     # Собираем тексты из различных элементов внутри Details
#                     details_texts = []
#                     # Более общие селекторы для поиска текста в деталях
#                     details_text_elements = working_ticket.query_selector_all("[class*='DetailsRouteInfo'] p, [class*='DetailsRouteColumn'] p, [class*='Details'] p, [class*='Details'] div")
#                     for elem in details_text_elements:
#                         txt = elem.inner_text().strip()
#                         if txt:
#                             details_texts.append(txt)
#
#                     # print(f"  Тексты из деталей для поиска номера: {details_texts[:2]}") # Отладка первых 2х
#
#                     for text in details_texts:
#                         if "Рейс" in text or re.search(r'^\d+\s+\S+\s*[-–—]', text):
#                             trip_number = extract_trip_number(text)
#                             if trip_number:
#                                 # print(f"    Найден номер рейса в деталях: '{trip_number}' из текста: '{text[:50]}...'") # Отладка
#                                 break
#
#                     # Если в деталях не нашли, ищем в основном блоке билета
#                     if not trip_number:
#                         # print(f"    Номер рейса в деталях не найден, ищу в основном блоке...") # Отладка
#                         number_elements = working_ticket.query_selector_all("[class*='TripNumber'], [class*='number'], .ticket-header .route-info")
#                         for elem in number_elements:
#                             text = elem.inner_text().strip()
#                             if text and re.search(r'\d+', text):
#                                 trip_number = extract_trip_number(text)
#                                 if trip_number:
#                                     # print(f"    Найден номер рейса в основном блоке: '{trip_number}' из текста: '{text[:50]}...'") # Отладка
#                                     break
#
#                     # if not trip_number:
#                     #     print(f"    Номер рейса не найден для билета {i + 1}")
#
#                     # --- Добавление результата ---
#                     if time_text != "N/A" and time_text != "0:00":
#                         results.append({
#                             'time': time_text,
#                             'trip_number': trip_number,
#                             'departure_point': from_city, # Используем оригинальное название из аргумента
#                             'arrival_point': to_city,     # Используем оригинальное название из аргумента
#                             'carrier': carrier_text if carrier_text != "N/A" else "Не определен",
#                             'free_seats': free_seats_display,
#                             'total_seats': total_seats_text,
#                             'sold_tickets': sold_tickets,
#                             'price': price if price > 0 else 0.0,
#                             'source': 'busfor'
#                         })
#                         print(
#                             f"  Добавлен рейс {i + 1}: {time_text} - {carrier_text} - {price}₽ - Свободно: {free_seats_display}, Всего: {total_seats_text}, Продано: {sold_tickets}, № рейса: '{trip_number}'")
#                 except Exception as e:
#                     print(f"  Ошибка парсинга билета {i + 1}: {e}")
#                     # import traceback
#                     # traceback.print_exc() # Раскомментируйте для полной трассировки
#                     continue # Продолжаем со следующим билетом
#
#             browser.close()
#             print(f"Парсинг завершен. Найдено {len(results)} результатов")
#
#             # Сохранение в Excel
#             if results:
#                 excel_filename = "data/history.xlsx"
#                 save_to_excel(results, filename=excel_filename, search_date=date)
#
#     except Exception as e:
#         print(f"Ошибка: {e}")
#         import traceback
#         traceback.print_exc()
#
#     return results

import re
import time
import os
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# Импортируем утилиту сохранения
try:
    from utils.save_to_excel import save_to_excel
except ImportError:
    print("⚠️ Модуль save_to_excel не найден. Сохранение отключено.")
    save_to_excel = None


def get_city_ids():
    return {
        'санкт-петербург': 4491,
        'москва': 4140,
        'казань': 3792,
        'сочи': 4575,
        'ростов-на-дону': 4456,
        'кириши': 7753,
        'екатеринбург': 3689,
        'новосибирск': 5096,
        'краснодар': 3935,
        'уфа': 4718,
        'красноярск': 5061,
        'владивосток': 2341,
        'рыбинск': 5127,
        'великий новгород': 3474,
        'нижний новгород': 4188,
        'волгоград': 3512,
        'воронеж': 3527,
        'смоленск': 4556,
        'брянск': 3436,
        'весьегонск': 5201,
        'кострома': 3915,
        'ярославль': 4863,
        'псков': 4398,
        'мурманск': 4149,
    }


def extract_trip_number(text):
    if not text:
        return ""
    text = text.strip()
    match = re.search(r'Рейс\s*[#№]\s*(\d+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r'^(\d+)\s+\S+\s*[-–—]\s*\S+', text)
    if match:
        return match.group(1)
    match = re.search(r'^(\d+)', text.split('\n')[0].strip())
    if match and 1 <= len(match.group(1)) <= 6:
        return match.group(1)
    return ""


def normalize_city_name(name):
    cleaned_name = re.split(r'\s*[*]+', name)[0].strip()
    return cleaned_name.lower()


def format_city_for_url_path(city_name):
    cleaned_name = re.split(r'\s*[*]+', city_name)[0].strip()
    hyphenated_name = cleaned_name.replace(" ", "-")
    return hyphenated_name


def safe_get_text(element, selector):
    try:
        el = element.find_element(By.CSS_SELECTOR, selector)
        return el.text.strip()
    except (NoSuchElementException, StaleElementReferenceException):
        return "N/A"
    except Exception:
        return "N/A"


def parse_busfor(date, from_city, to_city):
    results = []
    city_ids = get_city_ids()

    from_city_normalized = normalize_city_name(from_city)
    to_city_normalized = normalize_city_name(to_city)

    from_id = city_ids.get(from_city_normalized)
    to_id = city_ids.get(to_city_normalized)

    if not from_id or not to_id:
        print(f"❌ Не найдены ID для городов: '{from_city}' → '{to_city}'")
        return results

    from_city_url_path = format_city_for_url_path(from_city)
    to_city_url_path = format_city_for_url_path(to_city)
    path_part = f"/автобусы/{from_city_url_path}/{to_city_url_path}"
    query_params = f"from_id={from_id}&to_id={to_id}&on={date}&passengers=1&search=true"
    url = f"https://busfor.ru{path_part}?{query_params}"
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
    chrome_options.add_argument("--ignore-certificate-errors")  # ✅ Игнорировать SSL
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    user_data_dir = os.path.join(os.getcwd(), "user_data_busfor")
    os.makedirs(user_data_dir, exist_ok=True)
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    print(f"🔧 Используем профиль: {user_data_dir}")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)
    actions = ActionChains(driver)

    try:
        # Анти-детект
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en-US', 'en'] });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """
        })

        # 1. Загрузка главной
        print("🌐 Загрузка главной страницы...")
        driver.get("https://busfor.ru")
        time.sleep(1)

        # 2. Переход по URL
        print("🌐 Переход к результатам поиска...")
        driver.get(url)

        # 3. Ожидание загрузки
        print("⏳ Ожидание загрузки результатов...")
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ticket")))
            print("✅ Билеты найдены")
        except TimeoutException:
            print("❌ Билеты не загрузились")
            _save_debug_page(driver, "busfor")
            return results

        time.sleep(3)

        # 4. Проверка капчи
        if "captcha" in driver.page_source.lower() or "Please enable JS" in driver.page_source:
            print("⚠️ Требуется ручное вмешательство (капча/JS)")
            input("Решите капчу и нажмите Enter...")

        # 5. Сохранение для отладки
        _save_debug_page(driver, "busfor")

        # 6. Поиск билетов
        tickets = driver.find_elements(By.CSS_SELECTOR, ".ticket")
        print(f"📊 Найдено {len(tickets)} билетов")

        for i in range(len(tickets)):
            try:
                current_tickets = driver.find_elements(By.CSS_SELECTOR, ".ticket")
                if i >= len(current_tickets):
                    continue
                ticket = current_tickets[i]

                # Клик по "Детали рейса"
                try:
                    details_button = ticket.find_element(By.CSS_SELECTOR, "[class*='Style__Toggle']")
                    if "down-arrow" in details_button.get_attribute("class"):
                        driver.execute_script("arguments[0].click();", details_button)
                        time.sleep(1.5)  # Дать время на загрузку
                except:
                    pass

                # Перезапрашиваем элемент
                refreshed_tickets = driver.find_elements(By.CSS_SELECTOR, ".ticket")
                if i >= len(refreshed_tickets):
                    continue
                working_ticket = refreshed_tickets[i]

                # Время отправления
                time_text = safe_get_text(working_ticket, "[type='from'] .Style__Time-sc-1n9rkhj-0")
                if time_text == "N/A":
                    time_text = safe_get_text(working_ticket, "[class*='TimeStart'] [class*='Time']")

                # Перевозчик
                carrier_text = "N/A"
                carrier_selectors = [
                    "[class*='DetailsRouteColumn'] p:has(span:contains('Бренд:')) strong",
                    "[class*='DetailsRouteColumn'] p:has(span:contains('Перевозчик:')) strong",
                    "[class*='Details'] p:has(strong:contains('Бренд'))",
                    "[class*='Details'] p:has(strong:contains('Перевозчик'))"
                ]
                for sel in carrier_selectors:
                    try:
                        elems = working_ticket.find_elements(By.CSS_SELECTOR, sel)
                        for el in elems:
                            txt = el.text.strip()
                            if any(org in txt for org in ["ООО", "АО", "ИП", "ФТК", "ECOLINES", "Сотранс"]):
                                carrier_text = txt
                                break
                        if carrier_text != "N/A":
                            break
                    except:
                        continue

                # Цена
                price_text = safe_get_text(working_ticket, ".price")
                price = 0.0
                try:
                    price = float(re.sub(r'[^\d.]', '', price_text))
                except:
                    price = 0.0

                # Свободные места
                seats_text = safe_get_text(working_ticket, "[class*='Seats']")
                free_seats = "N/A"
                if "10+" in seats_text:
                    free_seats = "10+"
                elif "осталось" in seats_text and "1" in seats_text:
                    free_seats = "1"
                else:
                    match = re.search(r'(\d+)', seats_text)
                    free_seats = match.group(1) if match else "N/A"

                # Номер рейса
                trip_number = ""
                details_texts = []
                detail_elements = working_ticket.find_elements(By.CSS_SELECTOR, "[class*='DetailsRouteInfo'] p")
                for el in detail_elements:
                    txt = el.text.strip()
                    if txt:
                        details_texts.append(txt)
                for txt in details_texts:
                    trip_number = extract_trip_number(txt)
                    if trip_number:
                        break

                # Только если время найдено
                if time_text and time_text != "N/A" and time_text != "0:00":
                    result = {
                        'time': time_text,
                        'trip_number': trip_number,
                        'departure_point': from_city,
                        'arrival_point': to_city,
                        'carrier': carrier_text if carrier_text != "N/A" else "Не определен",
                        'free_seats': free_seats,
                        'total_seats': "N/A",
                        'sold_tickets': "N/A",
                        'price': price,
                        'source': 'busfor'
                    }
                    results.append(result)
                    print(f"  ✅ Добавлен рейс: {time_text} | {carrier_text} | {price} ₽ | {free_seats} мест")

            except Exception as e:
                print(f"  ⚠️ Ошибка при парсинге билета {i + 1}: {e}")
                continue

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        _save_debug_page(driver, "busfor")
    finally:
        try:
            driver.quit()
        except:
            pass
        print("🔒 Браузер закрыт")

    # Сохранение
    if results and save_to_excel:
        try:
            save_to_excel(results, filename="data/history.xlsx", search_date=date)
            print(f"✅ Результаты сохранены: {len(results)} рейсов")
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")

    print(f"🏁 Парсинг busfor завершён. Обработано {len(results)} рейсов.")
    return results


def _save_debug_page(driver, source: str):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/debug_{source}_{timestamp}.html"
        os.makedirs("data", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 Сохранён дебаг-файл: {filename}")
    except Exception as e:
        print(f"⚠️ Ошибка при сохранении: {e}")