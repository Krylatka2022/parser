import asyncio
import sys
import time
import os
import re
from playwright.sync_api import sync_playwright
from datetime import datetime
from utils.save_to_excel import save_to_excel


# --- УСТАНОВКА ПОЛИТИКИ ЦИКЛА — САМАЯ ПЕРВАЯ СТРОКА ---
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# Имя источника
SOURCE_NAME = "avtovokzalspb"

# Базовый URL
BASE_URL = "https://avtovokzalspb.ru"

# Словари для формирования URL
CITY_SLUGS = {
    'санкт-петербург': 'sankt-peterburg',
    'спб': 'sankt-peterburg',
    'москва': 'moskva',
    'мск': 'moskva',
    'ростов-на-дону': 'rostov-na-donu',
    'великий новгород': 'velikij-novgorod',
    'кириши': 'kirishi',
    'выборг': 'vqborg',
    'псков': 'pskov',
    'мурманск': 'murmansk',
}


# Коды автовокзалов: отправление и прибытие могут отличаться
DEPARTURE_CODES = {
    'санкт-петербург': 76844,  # Автовокзал 2 (Обводный канал)
    'москва': 32749,
    'казань': 75451,
    'сочи': 32804,
    'ростов-на-дону': 32787,
    'кириши': 37115,
    'екатеринбург': 25595,
    'новосибирск': 37914,
    'краснодар': 27362,
    'уфа': 77360,
    'красноярск': 27356,
    'владивосток': 000, # Нет на avtovokzal
    'рыбинск': 15069,
    'великий новгород': 37824,
    'нижний новгород': 32757,
    'волгоград': 24461,
    'воронеж': 32674,
    'смоленск': 15267,
    'брянск': 32662,
    'весьегонск': 14698,
    'кострома': 14506,
    'ярославль': 18244,
    'псков': 29976,
    'мурманск': 000, # Нет на avtovokzal
    'выборг': 24486,
}

ARRIVAL_CODES = {
    'санкт-петербург': 76844,  # Автовокзал 2 (Обводный канал)
    'москва': 32749,
    'казань': 75451,
    'сочи': 32804,
    'ростов-на-дону': 32787,
    'кириши': 37115,
    'екатеринбург': 25595,
    'новосибирск': 37914,
    'краснодар': 27362,
    'уфа': 77360,
    'красноярск': 27356,
    'владивосток': 000, # Нет на avtovokzal
    'рыбинск': 15069,
    'великий новгород': 37824,
    'нижний новгород': 32757,
    'волгоград': 24461,
    'воронеж': 32674,
    'смоленск': 15267,
    'брянск': 32662,
    'весьегонск': 14698,
    'кострома': 14506,
    'ярославль': 18244,
    'псков': 29976,
    'мурманск': 000, # Нет на avtovokzal
    'выборг': 24486,
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


def convert_date_format(date_str: str) -> str:
    """Конвертирует YYYY-MM-DD в DD.MM.YYYY"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d.%m.%Y")
    except ValueError:
        print(f"❌ Неверный формат даты: {date_str}")
        return ""


def parse_avtovokzalspb(date: str, from_city: str, to_city: str) -> list[dict]:
    """
    Парсит расписание с avtovokzalspb.ru через прямой переход по динамическому URL.
    """
    results = []
    print(f"🚀 Начинаем парсинг {SOURCE_NAME}.ru для маршрута {from_city} → {to_city} на {date}")

    # Нормализация городов
    from_city_norm = normalize_city_name(from_city)
    to_city_norm = normalize_city_name(to_city)
    print(f"    🏙️ Нормализованные города: {from_city_norm} → {to_city_norm}")

    # Проверка на совпадение городов
    if from_city_norm == to_city_norm:
        print(f"⚠️ Город отправления и прибытия совпадают: {from_city_norm}. Пропускаем.")
        return results

    # Получаем слаги
    from_slug = CITY_SLUGS.get(from_city_norm)
    to_slug = CITY_SLUGS.get(to_city_norm)

    if not from_slug:
        print(f"❌ Неизвестный город отправления: {from_city_norm}")
        return results
    if not to_slug:
        print(f"❌ Неизвестный город прибытия: {to_city_norm}")
        return results

    # Получаем коды автовокзалов
    departure_code = DEPARTURE_CODES.get(from_city_norm)
    arrival_code = ARRIVAL_CODES.get(to_city_norm)

    if not departure_code:
        print(f"❌ Неизвестный код автовокзала отправления для: {from_city_norm}")
        return results
    if not arrival_code:
        print(f"❌ Неизвестный код автовокзала прибытия для: {to_city_norm}")
        return results

    # Форматируем дату
    formatted_date = convert_date_format(date)
    if not formatted_date:
        return results

    # Формируем URL
    url = f"{BASE_URL}/#/{from_slug}/{to_slug}?date={formatted_date}&departureBusStopCode={departure_code}&arrivalBusStopCode={arrival_code}"
    print(f"🌐 Формируем URL: {url}")

    with sync_playwright() as p:
        browser = None
        try:
            # Путь к пользовательскому профилю
            user_data_dir = os.path.join(os.getcwd(), f"user_data_{SOURCE_NAME}")
            os.makedirs(user_data_dir, exist_ok=True)
            print(f"🔧 Используем профиль: {user_data_dir}")

            # Запуск браузера
            browser = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-web-security',
                    '--lang=ru-RU'
                ],
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            page = browser.pages[0]
            page.set_default_navigation_timeout(60000)
            page.set_default_timeout(30000)

            # Анти-детект
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en-US', 'en'] });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """)

            # Загружаем базовую страницу
            print("🌐 Загружаем базовую страницу...")
            page.goto(BASE_URL, wait_until="networkidle")
            time.sleep(2)

            # Переходим по динамическому URL
            print("🌐 Переходим по динамическому URL...")
            page.goto(url)

            # Ожидание загрузки данных
            print("⏳ Ожидание загрузки расписания...")
            try:
                # Ждём изменения хэша
                page.wait_for_function(
                    "() => window.location.hash.startsWith('#/') && window.location.href.includes('date=')",
                    timeout=30000
                )
                print("✅ URL обновлён")

                # Ждём появления контейнера с результатами
                page.wait_for_selector(".bus-cards, .bus-was-found__title", timeout=20000)

                # Проверка: есть ли рейсы?
                card_count = len(page.query_selector_all(".bus-card"))
                if card_count == 0:
                    if page.locator("text=Рейсов не найдено").count() > 0 or \
                       page.locator("text=ничего не найдено").count() > 0:
                        print("ℹ️ Рейсов по данному направлению не найдено")
                        return results
                    raise TimeoutError("Контейнер найден, но карточки рейсов отсутствуют")

                print(f"✅ Найдено {card_count} рейсов")

            except Exception as e:
                print(f"❌ Не удалось дождаться данных: {e}")
                _save_debug_page(page, SOURCE_NAME)
                return results

            # === ПАРСИНГ КАРТОЧЕК РЕЙСОВ ===
            cards = page.query_selector_all(".bus-card")
            print(f"📊 Начинаем парсинг {len(cards)} карточек...")

            for idx, card in enumerate(cards, 1):
                try:
                    # Время отправления
                    time_elem = card.query_selector(".bus-track-info__time")
                    time_text = time_elem.inner_text().strip() if time_elem else "N/A"

                    # Номер рейса
                    trip_number = "N/A"
                    trip_value_elem = card.query_selector(".bus-carrier-info__value")
                    if trip_value_elem:
                        full_text = trip_value_elem.inner_text().strip()
                        match = re.search(r'\d+', full_text)
                        trip_number = match.group(0) if match else "N/A"

                    # Перевозчик — используем locator и резервный поиск
                    carrier = "N/A"
                    try:
                        # Используем locator для поиска по тексту
                        label = card.locator("text=Перевозчик:")
                        if label.count() > 0:
                            # Ищем следующий span
                            value = label.locator("xpath=..//following-sibling::span")
                            if value.count() > 0:
                                carrier = value.first.inner_text().strip()
                    except:
                        pass

                    # Резерв: ищем по ключевым словам в .bus-carrier-info__value
                    if carrier == "N/A":
                        values = card.query_selector_all(".bus-carrier-info__value")
                        for el in values:
                            txt = el.inner_text().strip()
                            if any(kw in txt for kw in ["ООО", "АО", "ФТК", "Сотранс", "Круиз", "Транс", "Автотур", "ООО", "ИП"]):
                                carrier = txt
                                break

                    # Цена
                    price_elem = card.query_selector(".bus-carrier-info__price-value")
                    price_text = price_elem.inner_text().strip() if price_elem else "0"
                    price = 0.0
                    try:
                        # Удаляем все кроме цифр и точки
                        clean_price = re.sub(r'[^\d.]', '', price_text)
                        price = float(clean_price) if clean_price else 0.0
                    except:
                        price = 0.0

                    # Свободные места
                    free_seats = "N/A"
                    seats_elem = card.query_selector(".bus-carrier-info__text")
                    if seats_elem:
                        seats_text = seats_elem.inner_text().strip()
                        match = re.search(r'(\d+)', seats_text)
                        free_seats = match.group(1) if match else "N/A"

                    total_seats = "N/A"
                    sold_tickets = "N/A"

                    result = {
                        'time': time_text,
                        'trip_number': trip_number,
                        'departure_point': from_city,
                        'arrival_point': to_city,
                        'carrier': carrier,
                        'total_seats': total_seats,
                        'free_seats': free_seats,
                        'sold_tickets': sold_tickets,
                        'price': price,
                        'source': SOURCE_NAME
                    }

                    results.append(result)
                    print(f"  ✅ Рейс {idx}: {time_text} | {carrier} | {price} ₽ | {free_seats} мест")

                except Exception as e:
                    print(f"  ⚠️ Ошибка при парсинге карточки {idx}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Ошибка при выполнении: {e}")
            _save_debug_page(page, SOURCE_NAME)
        finally:
            if browser:
                browser.close()
                print("🔒 Браузер закрыт")

    # Сохранение в Excel
    if results:
        excel_filename = "data/history.xlsx"
        save_to_excel(results, filename=excel_filename, search_date=date)
        print(f"✅ Результаты сохранены: {len(results)} рейсов")

    print(f"🏁 Парсинг {SOURCE_NAME} завершён. Обработано {len(results)} рейсов.")
    return results


def _save_debug_page(page, source: str):
    """Сохраняет HTML для отладки"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/debug_{source}_{timestamp}.html"
        os.makedirs("data", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"💾 Сохранён дебаг-файл: {filename}")
    except Exception as e:
        print(f"⚠️ Ошибка при сохранении дебаг-файла: {e}")