# import re
# import time
# from playwright.sync_api import sync_playwright, TimeoutError
# from datetime import datetime
# import os
#
# # Импортируем утилиту сохранения
# from utils.save_to_excel import save_to_excel
#
#
# # Имя источника
# SOURCE_NAME = "tutu"
#
# # Базовый URL для поиска автобусов
# BASE_SEARCH_URL = "https://bus.tutu.ru/raspisanie"
#
# # Словарь ID городов на tutu.ru
# CITY_IDS = {
#     'санкт-петербург': 1447624,
#     'москва': 1447874,
#     'казань': 1330021,
#     'сочи': 1447978,
#     'ростов-на-дону': 1391657,
#     'кириши': 1358042,
#     'екатеринбург': 1322775,
#     'новосибирск': 1302713,
#     'краснодар': 1447972,
#     'уфа': 1333152,
#     'красноярск': 1307744,
#     'владивосток': 1297864,
#     'рыбинск': 1397803,
#     'великий новгород': 1317690,
#     'нижний новгород': 1427804,
#     'волгоград': 1412651,
#     'воронеж': 1381189,
#     'смоленск': 1403603,
#     'брянск': 1410741,
#     'весьегонск': 1369142,
#     'кострома': 1395289,
#     'ярославль': 1397799,
#     'псков': 1360894,
#     'мурманск': 1322570,
#
# }
#
# # Словарь английских названий для формирования URL
# CITY_EN_NAMES = {
#     'санкт-петербург': 'Sankt-Peterburg',
#     'москва': 'Moskva',
#     'казань': 'Kazan',
#     'кириши': 'Kirishi',
#     'сочи': 'Sochi',
#     'ростов-на-дону': 'Rostov-na-Donu',
#     'екатеринбург': 'Ekaterinburg',
#     'новосибирск': 'Novosibirsk',
#     'краснодар': 'Krasnodar',
#     'уфа': 'Ufa',
#     'красноярск': 'Krasnoyarsk',
#     'владивосток': 'Vladivostok',
#     'рыбинск': 'Rybinsk',
#     'великий новгород': 'Novgorod-Velikij',
#     'нижний новгород': 'Nizhnij-Novgorod',
#     'волгоград': 'Volgograd',
#     'воронеж': 'Voronezh',
#     'смоленск': 'Smolensk',
#     'брянск': 'Bryansk',
#     'весьегонск': 'Vesegonsk',
#     'кострома': 'Kostroma',
#     'ярославль': 'Yaroslavl',
#     'псков': 'Pskov',
#     'мурманск': 'Murmansk',
#
# }
#
#
# def normalize_city_name(name: str) -> str:
#     """Нормализует название города для поиска в словаре."""
#     cleaned = re.split(r'\s*[*]+', name.strip())[0].lower()
#     replacements = {
#         'спб': 'санкт-петербург',
#         'мск': 'москва',
#         'н.новгород': 'нижний новгород',
#         'нижний н-д': 'нижний новгород',
#     }
#     return replacements.get(cleaned, cleaned)
#
#
# def get_city_id_tutu(city_name: str) -> int | None:
#     """
#     Получает ID города на tutu.ru.
#     """
#     normalized_name = normalize_city_name(city_name)
#     return CITY_IDS.get(normalized_name)
#
#
# def get_city_en_name(city_name: str) -> str | None:
#     """
#     Получает английское название города для формирования URL.
#     """
#     normalized_name = normalize_city_name(city_name)
#     return CITY_EN_NAMES.get(normalized_name)
#
#
# def convert_date_format(date_str: str) -> str:
#     """Конвертирует дату из YYYY-MM-DD в DD.MM.YYYY"""
#     try:
#         date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#         return date_obj.strftime("%d.%m.%Y")
#     except ValueError:
#         print(f"❌ Неверный формат даты: {date_str}")
#         return date_str
#
#
# def parse_tutu(date: str, from_city: str, to_city: str) -> list[dict]:
#     """
#     Парсит расписание автобусов/поездов с tutu.ru
#
#     Args:
#         date (str): Дата в формате YYYY-MM-DD
#         from_city (str): Город отправления
#         to_city (str): Город прибытия
#
#     Returns:
#         list[dict]: Список словарей с информацией о рейсах
#     """
#     results = []
#     print(f"🚀 Начинаем парсинг tutu.ru для маршрута {from_city} → {to_city} на {date}")
#
#     # Получаем ID городов и их английские названия
#     from_id = get_city_id_tutu(from_city)
#     to_id = get_city_id_tutu(to_city)
#     from_en_name = get_city_en_name(from_city)
#     to_en_name = get_city_en_name(to_city)
#
#     if not from_id:
#         print(f"❌ Не найден ID для города отправления: {from_city}")
#         return results
#
#     if not to_id:
#         print(f"❌ Не найден ID для города прибытия: {to_city}")
#         return results
#
#     if not from_en_name:
#         print(f"❌ Не найдено английское название для города отправления: {from_city}")
#         return results
#
#     if not to_en_name:
#         print(f"❌ Не найдено английское название для города прибытия: {to_city}")
#         return results
#
#     # Конвертируем дату
#     formatted_date = convert_date_format(date)
#     if formatted_date == date:  # Если конвертация не удалась
#         return results
#
#     # Формируем URL с использованием английских названий для путей
#     search_url = f"{BASE_SEARCH_URL}/gorod_{from_en_name}/gorod_{to_en_name}/?from={from_id}&to={to_id}&date={formatted_date}&travelers=1&amount=1"
#     print(f"🌐 Переход по URL: {search_url}")
#
#     with sync_playwright() as p:
#         # Используем persistent context для обхода капчи
#         user_data_dir = os.path.join(os.getcwd(), "userdata_tutu")
#         print(f"🔧 Используем пользовательский профиль: {user_data_dir}")
#
#         browser = p.chromium.launch_persistent_context(
#             user_data_dir,
#             headless=False,  # Можем переключить в True после тестов
#             args=[
#                 "--no-sandbox",
#                 "--disable-blink-features=AutomationControlled",
#                 "--disable-extensions"
#             ]
#         )
#
#         try:
#             page = browser.new_page()
#             print("📄 Создана новая страница")
#
#             # Устанавливаем таймаут для навигации
#             page.set_default_navigation_timeout(90000)  # 90 секунд для навигации
#             page.set_default_timeout(60000)  # 60 секунд для других операций
#
#             # Переходим на страницу поиска
#             print("🌐 Начинаем переход на страницу поиска...")
#             print("    (Это может занять до 90 секунд)")
#             response = page.goto(search_url, wait_until="load")  # Используем "load" вместо "networkidle"
#             print(f"✅ Страница загружена. Статус ответа: {response.status if response else 'Нет ответа'}")
#
#             # Проверим URL после перехода
#             current_url = page.url
#             print(f"📍 Текущий URL после перехода: {current_url}")
#
#             # Проверим заголовок страницы
#             title = page.title()
#             print(f"🏷️ Заголовок страницы: {title}")
#
#             # Ждем загрузки результатов
#             print("⏳ Ожидание результатов поиска...")
#             max_wait = 45  # Увеличиваем время ожидания
#             found_offers = False
#
#             for i in range(max_wait):
#                 print(f"  🔍 Попытка {i + 1}/{max_wait} проверить наличие результатов...")
#
#                 # Проверяем на наличие капчи или ошибок
#                 try:
#                     if page.locator("text=Проверка безопасности").count() > 0:
#                         print("⚠️ Обнаружена капча 'Проверка безопасности'")
#                     if page.locator("text=капча").count() > 0:
#                         print("⚠️ Обнаружен текст 'капча'")
#                     if page.locator("iframe[src*='captcha']").count() > 0:
#                         print("⚠️ Обнаружен iframe с капчей")
#
#                     if (page.locator("text=Проверка безопасности").count() > 0 or
#                             page.locator("text=капча").count() > 0 or
#                             page.locator("iframe[src*='captcha']").count() > 0):
#                         print("⚠️ Обнаружена капча. Пожалуйста, пройдите проверку вручную.")
#                         print("⏳ Ждем 45 секунд для ручного прохождения...")
#                         time.sleep(45)
#                         continue
#                 except Exception as e:
#                     print(f"    ℹ️ Ошибка при проверке капчи: {e}")
#
#                 # Проверяем на сообщение об отсутствии рейсов
#                 try:
#                     if page.locator("text=Рейсов не найдено").count() > 0:
#                         print("ℹ️ Найдено сообщение: 'Рейсов не найдено'")
#                     if page.locator("text=Ничего не найдено").count() > 0:
#                         print("ℹ️ Найдено сообщение: 'Ничего не найдено'")
#
#                     if page.locator("text=Рейсов не найдено").count() > 0 or \
#                             page.locator("text=Ничего не найдено").count() > 0:
#                         print("ℹ️ Рейсов по данному направлению не найдено")
#                         browser.close()
#                         return results
#                 except Exception as e:
#                     print(f"    ℹ️ Ошибка при проверке отсутствия рейсов: {e}")
#
#                 # Проверяем наличие элементов с расписанием
#                 try:
#                     offers = page.query_selector_all("[data-ti='offer-card']")
#                     print(f"    📊 Найдено элементов [data-ti='offer-card']: {len(offers)}")
#                     if len(offers) > 0:
#                         print(f"✅ Найдено {len(offers)} предложений")
#                         found_offers = True
#                         break
#                 except Exception as e:
#                     print(f"    ℹ️ Ошибка при поиске предложений: {e}")
#
#                 time.sleep(1)
#
#             if not found_offers:
#                 print("❌ Предложения не загрузились за отведенное время")
#                 print("📄 Сохраняем содержимое страницы для анализа...")
#                 # Сохраняем HTML для отладки
#                 debug_file = f"debug_tutu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
#                 try:
#                     with open(debug_file, "w", encoding="utf-8") as f:
#                         f.write(page.content())
#                     print(f"💾 Сохранен файл отладки: {debug_file}")
#                 except Exception as e:
#                     print(f"⚠️ Ошибка при сохранении файла отладки: {e}")
#                 browser.close()
#                 return results
#
#             # Извлекаем данные о рейсах
#             offers = page.query_selector_all("[data-ti='offer-card']")
#             print(f"📊 Начинаем парсинг {len(offers)} предложений")
#
#             for idx, offer in enumerate(offers, 1):
#                 try:
#                     print(f"  🔄 Парсинг предложения {idx}...")
#
#                     # Время отправления
#                     departure_time_elem = offer.query_selector("[data-ti='departure-time']")
#                     departure_time = (departure_time_elem.inner_text()).strip() if departure_time_elem else "N/A"
#                     print(f"    ⏰ Время отправления: {departure_time}")
#
#                     # Время прибытия
#                     arrival_time_elem = offer.query_selector("[data-ti='arrival-time']")
#                     arrival_time = (arrival_time_elem.inner_text()).strip() if arrival_time_elem else "N/A"
#                     print(f"    ⏰ Время прибытия: {arrival_time}")
#
#                     # Продолжительность поездки
#                     duration_elem = offer.query_selector("[data-ti='duration-time']")
#                     duration = (duration_elem.inner_text()).strip() if duration_elem else "N/A"
#                     print(f"    ⏱️ Продолжительность: {duration}")
#
#                     # Место отправления
#                     departure_place_elem = offer.query_selector("[data-ti='departure'] [data-ti='place']")
#                     departure_place = (departure_place_elem.inner_text()).strip() if departure_place_elem else "N/A"
#                     print(f"    📍 Место отправления: {departure_place}")
#
#                     # Город отправления
#                     departure_city_elem = offer.query_selector("[data-ti='departure'] [data-ti='city']")
#                     departure_city = (departure_city_elem.inner_text()).strip() if departure_city_elem else from_city
#                     print(f"    🏙️ Город отправления: {departure_city}")
#
#                     # Место прибытия
#                     arrival_place_elem = offer.query_selector("[data-ti='arrival'] [data-ti='place']")
#                     arrival_place = (arrival_place_elem.inner_text()).strip() if arrival_place_elem else "N/A"
#                     print(f"    📍 Место прибытия: {arrival_place}")
#
#                     # Город прибытия
#                     arrival_city_elem = offer.query_selector("[data-ti='arrival'] [data-ti='city']")
#                     arrival_city = (arrival_city_elem.inner_text()).strip() if arrival_city_elem else to_city
#                     print(f"    🏙️ Город прибытия: {arrival_city}")
#
#                     # Перевозчик
#                     carrier_elem = offer.query_selector("[data-ti='carrier-badge'] .o-text-inline")
#                     carrier = (carrier_elem.inner_text()).strip() if carrier_elem else "N/A"
#                     print(f"    🚌 Перевозчик: {carrier}")
#
#                     # Цена
#                     price_elem = offer.query_selector("[data-ti='price']")
#                     price_text = (price_elem.inner_text()).strip() if price_elem else "N/A"
#                     print(f"    💰 Цена (текст): {price_text}")
#                     # Очищаем цену от символов
#                     price = 0.0
#                     if price_text != "N/A":
#                         try:
#                             # Убираем неразрывные пробелы и другие спецсимволы
#                             clean_price = re.sub(r'[^\d.,]', '', price_text.replace('\u202f', '').replace('\xa0', ''))
#                             price = float(clean_price.replace(',', '.'))
#                         except ValueError:
#                             price = 0.0
#                             print(f"    ⚠️ Не удалось распарсить цену: {price_text}")
#                     print(f"    💰 Цена (число): {price}")
#
#                     # Номер рейса (в tutu его может не быть, ставим N/A)
#                     trip_number = "N/A"
#                     print(f"    #️⃣ Номер рейса: {trip_number}")
#
#                     # Статус мест
#                     free_seats = "N/A"
#                     total_seats = "N/A"
#                     sold_tickets = "N/A"
#
#                     # Проверяем наличие кнопки "Купить"
#                     buy_button = offer.query_selector("[data-ti='order-button-slot-content']")
#                     if buy_button:
#                         button_text = (buy_button.inner_text()).strip()
#                         print(f"    🎫 Текст кнопки: {button_text}")
#                         if "Купить" in button_text:
#                             free_seats = "Есть места"
#                     print(f"    🪑 Свободные места: {free_seats}")
#
#                     # Формируем результат
#                     result = {
#                         'time': departure_time,
#                         'trip_number': trip_number,
#                         'departure_point': f"{departure_city}, {departure_place}",
#                         'arrival_point': f"{arrival_city}, {arrival_place}",
#                         'carrier': carrier,
#                         'total_seats': total_seats,
#                         'free_seats': free_seats,
#                         'sold_tickets': sold_tickets,
#                         'price': price,
#                         'source': SOURCE_NAME
#                     }
#
#                     results.append(result)
#                     print(f"  ✅ Предложение {idx} успешно обработано")
#                     print(f"    📦 Результат: {result}")
#
#                 except Exception as e:
#                     print(f"  ⚠️ Ошибка при парсинге предложения {idx}: {e}")
#                     import traceback
#                     traceback.print_exc()
#                     continue
#
#         except TimeoutError:
#             print("❌ Таймаут при загрузке страницы")
#             # Попробуем сохранить содержимое даже при таймауте
#             try:
#                 debug_file = f"debug_tutu_timeout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
#                 with open(debug_file, "w", encoding="utf-8") as f:
#                     f.write(page.content())
#                 print(f"💾 Сохранен файл отладки таймаута: {debug_file}")
#             except Exception as e:
#                 print(f"⚠️ Ошибка при сохранении файла отладки таймаута: {e}")
#         except Exception as e:
#             print(f"❌ Произошла ошибка при парсинге tutu.ru: {e}")
#             import traceback
#             traceback.print_exc()
#             # Сохраняем HTML для отладки
#             debug_file = f"debug_tutu_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
#             try:
#                 with open(debug_file, "w", encoding="utf-8") as f:
#                     f.write(page.content())
#                 print(f"💾 Сохранен файл отладки ошибки: {debug_file}")
#             except Exception as e2:
#                 print(f"⚠️ Ошибка при сохранении файла отладки ошибки: {e2}")
#         finally:
#             browser.close()
#             print("🔒 Браузер закрыт")
#
#     # Сохраняем результаты в Excel
#     # Сохранение в Excel
#     if results:
#         excel_filename = "data/history.xlsx"
#         save_to_excel(results, filename=excel_filename, search_date=date)
#
#     print(f"✅ Парсинг tutu.ru завершён. Найдено {len(results)} рейсов.")
#     return results

import re
import time
from datetime import datetime
import os

# Импорты Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Импортируем утилиту сохранения
from utils.save_to_excel import save_to_excel


# Имя источника
SOURCE_NAME = "tutu"

# Базовый URL для поиска автобусов
BASE_SEARCH_URL = "https://bus.tutu.ru/raspisanie"

# Словарь ID городов на tutu.ru
CITY_IDS = {
    'санкт-петербург': 1447624,
    'москва': 1447874,
    'казань': 1330021,
    'сочи': 1447978,
    'ростов-на-дону': 1391657,
    'кириши': 1358042,
    'екатеринбург': 1322775,
    'новосибирск': 1302713,
    'краснодар': 1447972,
    'уфа': 1333152,
    'красноярск': 1307744,
    'владивосток': 1297864,
    'рыбинск': 1397803,
    'великий новгород': 1317690,
    'нижний новгород': 1427804,
    'волгоград': 1412651,
    'воронеж': 1381189,
    'смоленск': 1403603,
    'брянск': 1410741,
    'весьегонск': 1369142,
    'кострома': 1395289,
    'ярославль': 1397799,
    'псков': 1360894,
    'мурманск': 1322570,
}

# Словарь английских названий для формирования URL
CITY_EN_NAMES = {
    'санкт-петербург': 'Sankt-Peterburg',
    'москва': 'Moskva',
    'казань': 'Kazan',
    'кириши': 'Kirishi',
    'сочи': 'Sochi',
    'ростов-на-дону': 'Rostov-na-Donu',
    'екатеринбург': 'Ekaterinburg',
    'новосибирск': 'Novosibirsk',
    'краснодар': 'Krasnodar',
    'уфа': 'Ufa',
    'красноярск': 'Krasnoyarsk',
    'владивосток': 'Vladivostok',
    'рыбинск': 'Rybinsk',
    'великий новгород': 'Novgorod-Velikij',
    'нижний новгород': 'Nizhnij-Novgorod',
    'волгоград': 'Volgograd',
    'воронеж': 'Voronezh',
    'смоленск': 'Smolensk',
    'брянск': 'Bryansk',
    'весьегонск': 'Vesegonsk',
    'кострома': 'Kostroma',
    'ярославль': 'Yaroslavl',
    'псков': 'Pskov',
    'мурманск': 'Murmansk',
}


def normalize_city_name(name: str) -> str:
    """Нормализует название города для поиска в словаре."""
    cleaned = re.split(r'\s*[*]+', name.strip())[0].lower()
    replacements = {
        'спб': 'санкт-петербург',
        'мск': 'москва',
        'н.новгород': 'нижний новгород',
        'нижний н-д': 'нижний новгород',
    }
    return replacements.get(cleaned, cleaned)


def get_city_id_tutu(city_name: str) -> int | None:
    """Получает ID города на tutu.ru."""
    normalized_name = normalize_city_name(city_name)
    return CITY_IDS.get(normalized_name)


def get_city_en_name(city_name: str) -> str | None:
    """Получает английское название города для формирования URL."""
    normalized_name = normalize_city_name(city_name)
    return CITY_EN_NAMES.get(normalized_name)


def convert_date_format(date_str: str) -> str:
    """Конвертирует дату из YYYY-MM-DD в DD.MM.YYYY"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d.%m.%Y")
    except ValueError:
        print(f"❌ Неверный формат даты: {date_str}")
        return date_str


def safe_get_text(element, selector):
    """Безопасное получение текста из элемента"""
    try:
        return element.find_element(By.CSS_SELECTOR, selector).text.strip()
    except NoSuchElementException:
        return "N/A"
    except Exception:
        return "N/A"


def parse_tutu(date: str, from_city: str, to_city: str) -> list[dict]:
    """
    Парсит расписание автобусов/поездов с tutu.ru (Selenium версия)

    Args:
        date (str): Дата в формате YYYY-MM-DD
        from_city (str): Город отправления
        to_city (str): Город прибытия

    Returns:
        list[dict]: Список словарей с информацией о рейсах
    """
    results = []
    print(f"🚀 Начинаем парсинг tutu.ru для маршрута {from_city} → {to_city} на {date}")

    # Получаем ID городов и их английские названия
    from_id = get_city_id_tutu(from_city)
    to_id = get_city_id_tutu(to_city)
    from_en_name = get_city_en_name(from_city)
    to_en_name = get_city_en_name(to_city)

    if not from_id:
        print(f"❌ Не найден ID для города отправления: {from_city}")
        return results

    if not to_id:
        print(f"❌ Не найден ID для города прибытия: {to_city}")
        return results

    if not from_en_name:
        print(f"❌ Не найдено английское название для города отправления: {from_city}")
        return results

    if not to_en_name:
        print(f"❌ Не найдено английское название для города прибытия: {to_city}")
        return results

    # Конвертируем дату
    formatted_date = convert_date_format(date)
    if formatted_date == date:  # Если конвертация не удалась
        return results

    # Формируем URL с использованием английских названий для путей
    search_url = f"{BASE_SEARCH_URL}/gorod_{from_en_name}/gorod_{to_en_name}/?from={from_id}&to={to_id}&date={formatted_date}&travelers=1&amount=1"
    print(f"🌐 Переход по URL: {search_url}")

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
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Путь к профилю
    user_data_dir = os.path.join(os.getcwd(), "userdata_tutu_selenium")
    os.makedirs(user_data_dir, exist_ok=True)
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    print(f"🔧 Используем профиль: {user_data_dir}")

    service = Service()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Установка таймаутов
    wait = WebDriverWait(driver, 90)  # 90 секунд
    driver.set_page_load_timeout(90)

    try:
        print("🌐 Переходим на страницу...")
        driver.get(search_url)

        print("⏳ Ожидание результатов поиска...")

        found_offers = False
        for _ in range(45):
            # Проверка капчи
            try:
                if "captcha" in driver.page_source.lower() or "Проверка безопасности" in driver.title:
                    print("⚠️ Обнаружена капча. Ждём 45 секунд для ручного прохождения...")
                    time.sleep(45)
                    continue
            except:
                pass

            # Проверка отсутствия рейсов
            try:
                no_results = driver.find_elements(By.XPATH, "//*[contains(text(), 'Рейсов не найдено') or contains(text(), 'Ничего не найдено')]")
                if no_results:
                    print("ℹ️ Рейсов не найдено")
                    return results
            except:
                pass

            # Проверка наличия карточек
            try:
                offers = driver.find_elements(By.CSS_SELECTOR, "[data-ti='offer-card']")
                if len(offers) > 0:
                    print(f"✅ Найдено {len(offers)} предложений")
                    found_offers = True
                    break
            except:
                pass

            time.sleep(1)

        if not found_offers:
            print("❌ Предложения не загрузились")
            return results

        # Парсинг карточек
        offers = driver.find_elements(By.CSS_SELECTOR, "[data-ti='offer-card']")
        print(f"📊 Начинаем парсинг {len(offers)} предложений")

        for idx, offer in enumerate(offers, 1):
            try:
                print(f"  🔄 Парсинг предложения {idx}...")

                departure_time = safe_get_text(offer, "[data-ti='departure-time']")
                arrival_time = safe_get_text(offer, "[data-ti='arrival-time']")
                duration = safe_get_text(offer, "[data-ti='duration-time']")
                departure_place = safe_get_text(offer, "[data-ti='departure'] [data-ti='place']")
                departure_city = safe_get_text(offer, "[data-ti='departure'] [data-ti='city']") or from_city
                arrival_place = safe_get_text(offer, "[data-ti='arrival'] [data-ti='place']")
                arrival_city = safe_get_text(offer, "[data-ti='arrival'] [data-ti='city']") or to_city
                carrier = safe_get_text(offer, "[data-ti='carrier-badge'] .o-text-inline")
                price_text = safe_get_text(offer, "[data-ti='price']")

                price = 0.0
                if price_text and price_text != "N/A":
                    try:
                        clean_price = re.sub(r'[^\d.,]', '', price_text.replace('\u202f', '').replace('\xa0', ''))
                        price = float(clean_price.replace(',', '.'))
                    except:
                        price = 0.0

                free_seats = "N/A"
                try:
                    buy_button = offer.find_element(By.CSS_SELECTOR, "[data-ti='order-button-slot-content']")
                    if "Купить" in buy_button.text:
                        free_seats = "Есть места"
                except:
                    pass

                result = {
                    'time': departure_time,
                    'trip_number': "N/A",
                    'departure_point': f"{departure_city}, {departure_place}",
                    'arrival_point': f"{arrival_city}, {arrival_place}",
                    'carrier': carrier,
                    'total_seats': "N/A",
                    'free_seats': free_seats,
                    'sold_tickets': "N/A",
                    'price': price,
                    'source': SOURCE_NAME
                }

                results.append(result)
                print(f"  ✅ Предложение {idx} обработано: {result}")

            except Exception as e:
                print(f"  ⚠️ Ошибка при парсинге предложения {idx}: {e}")
                continue

    except TimeoutException:
        print("❌ Таймаут при загрузке страницы")
    except Exception as e:
        print(f"❌ Ошибка при парсинге: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
        print("🔒 Браузер закрыт")

    # Сохранение в Excel
    if results:
        excel_filename = "data/history.xlsx"
        save_to_excel(results, filename=excel_filename, search_date=date)

    print(f"✅ Парсинг tutu.ru завершён. Найдено {len(results)} рейсов.")
    return results