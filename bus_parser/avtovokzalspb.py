# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# import time
# import os
#
#
#
# def parse_avtovokzalspb(date, from_city, to_city):
#     print(f"[avtovokzalspb] Парсим {date} | {from_city} → {to_city}")
#
#     # Используем правильный URL маршрута
#     url = "https://avtovokzalspb.ru/raspisanie/sankt-peterburg-velikij-novgorod "
#
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')  # можно убрать, чтобы видеть браузер
#     driver = webdriver.Chrome(options=options)
#
#     try:
#         driver.get(url)
#         time.sleep(5)  # Ждём загрузки JS
#
#         html = driver.page_source
#
#         # Сохраняем HTML для диагностики
#         debug_path = f"debug_avtovokzalspb_{date}.html"
#         with open(debug_path, "w", encoding="utf-8") as f:
#             f.write(html)
#         print(f"[avtovokzalspb] HTML сохранён: {debug_path}")
#
#         soup = BeautifulSoup(html, 'html.parser')
#
#         # Проверяем, есть ли таблица с расписанием
#         table = soup.select_one('#shedule-table')
#         if not table:
#             print("[avtovokzalspb] ❗ Таблица с расписанием не найдена")
#             return []
#
#         rows = table.select('tr[data-route]')
#         print(f"[avtovokzalspb] Найдено строк таблицы: {len(rows)}")
#
#         buses = []
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) < 5:
#                 continue
#
#             try:
#                 time = cols[0].text.strip()
#                 route = cols[1].text.strip()
#                 carrier = cols[2].text.strip()
#                 free_seats = int(cols[3].text.strip())
#                 price = float(cols[4].text.replace(' ', '').replace('руб.', ''))
#
#                 buses.append({
#                     'time': time,
#                     'route': route,
#                     'carrier': carrier,
#                     'free_seats': free_seats,
#                     'price': price,
#                     'source': 'avtovokzalspb'
#                 })
#             except Exception as e:
#                 print(f"[avtovokzalspb] Ошибка извлечения данных: {e}")
#                 continue
#
#         print(f"[avtovokzalspb] Спаршено рейсов: {len(buses)}")
#         return buses
#
#     except Exception as e:
#         print(f"[avtovokzalspb] Критическая ошибка: {e}")
#         return []
#
#     finally:
#         driver.quit()
#
#
# # Вспомогательная функция для формирования URL
# def translit_to_url(city):
#     mapping = {
#         'санкт-петербург': 'spb',
#         'великий новгород': 'novgorod',
#         'москва': 'moskva',
#         'минск': 'minsk',
#         'вологда': 'vologda',
#         'ростов': 'rostov-na-donu',
#         'ивангород': 'ivangorod',
#         'псков': 'pskov',
#         'выборг': 'vyborg',
#         'таллин': 'tallin',
#         'рига': 'riga',
#         'могилев': 'mogilev',
#         'гомель': 'gomel',
#         'кингисепп': 'kingisepp',
#         'остров': 'ostrov',
#         'старая русса': 'staraya-russa',
#         'брянск': 'bryansk',
#         'волгоград': 'volgograd',
#         'нарва': 'narva-estoniya',
#         'эстония': 'estonija'
#     }
#     city = city.lower().strip()
#     return mapping.get(city, city)
# from selenium import webdriver
# from bs4 import BeautifulSoup
# import time

# def parse_avtovokzalspb(date, from_city, to_city):
#     print(f"[avtovokzalspb] Парсим {date} | {from_city} → {to_city}")
#     url = "https://avtovokzalspb.ru/raspisanie/sankt-peterburg-velikij-novgorod "
#
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     driver = webdriver.Chrome(options=options)
#
#     try:
#         # Логируем попытку открытия URL
#         print(f"[avtovokzalspb] Открываю страницу: {url}")
#
#         driver.get(url)
#         time.sleep(5)
#
#         # Логируем успешное получение HTML
#         print("[avtovokzalspb] Страница загружена")
#
#         html = driver.page_source
#
#         # Сохраняем HTML для анализа
#         debug_path = f"debug_avtovokzalspb_{date}.html"
#         try:
#             with open(debug_path, "w", encoding="utf-8") as f:
#                 f.write(html)
#             print(f"[avtovokzalspb] HTML сохранён: {debug_path}")
#         except Exception as e:
#             print(f"[avtovokzalspb] Ошибка при сохранении HTML: {e}")
#
#         soup = BeautifulSoup(html, 'html.parser')
#
#         rows = soup.select('table tr[data-route]')
#         print(f"[avtovokzalspb] Найдено строк таблицы: {len(rows)}")
#
#         buses = []
#
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) < 5:
#                 continue
#
#             try:
#                 time = cols[0].text.strip()
#                 route = cols[1].text.strip()
#                 carrier = cols[2].text.strip()
#                 free_seats = int(cols[3].text.strip())
#                 price = float(cols[4].text.replace(' ', '').replace('руб.', ''))
#             except Exception as e:
#                 print(f"[avtovokzalspb] Ошибка извлечения данных: {e}")
#                 continue
#
#             buses.append({
#                 'time': time,
#                 'route': route,
#                 'carrier': carrier,
#                 'free_seats': free_seats,
#                 'price': price,
#                 'source': 'avtovokzalspb'
#             })
#
#         print(f"[avtovokzalspb] Спаршено рейсов: {len(buses)}")
#         return buses
#
#     except Exception as e:
#         print(f"[avtovokzalspb] Ошибка: {e}")
#         return []
#
#     finally:
#         driver.quit()
# def parse_avtovokzalspb(date, from_city, to_city):
#     print(f"[avtovokzalspb] Парсим {date} | {from_city} → {to_city}")
#     url = "https://avtovokzalspb.ru/raspisanie/ "
#
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     driver = webdriver.Chrome(options=options)
#
#     try:
#         driver.get(url)
#         time.sleep(3)
#
#         # Имитируем ввод городов (найдите поля в DOM)
#         from_input = driver.find_element("id", "from")
#         from_input.clear()
#         from_input.send_keys(from_city)
#         time.sleep(2)
#
#         to_input = driver.find_element("id", "to")
#         to_input.clear()
#         to_input.send_keys(to_city)
#         time.sleep(2)
#
#         date_input = driver.find_element("id", "date")
#         date_input.clear()
#         date_input.send_keys(date)
#         time.sleep(2)
#
#         search_button = driver.find_element("css selector", ".search-button")
#         search_button.click()
#         time.sleep(5)
#
#         html = driver.page_source
#         with open(f"debug_avtovokzalspb_{date}.html", "w", encoding="utf-8") as f:
#             f.write(html)
#
#         soup = BeautifulSoup(html, 'html.parser')
#         rows = soup.select('table tr[data-route]')
#         buses = []
#
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) < 5:
#                 continue
#
#             try:
#                 time = cols[0].text.strip()
#                 route = cols[1].text.strip()
#                 carrier = cols[2].text.strip()
#                 free_seats = int(cols[3].text.strip())
#                 price = float(cols[4].text.replace(' ', '').replace('руб.', ''))
#             except:
#                 continue
#
#             buses.append({
#                 'time': time,
#                 'route': route,
#                 'carrier': carrier,
#                 'free_seats': free_seats,
#                 'price': price,
#                 'source': 'avtovokzalspb'
#             })
#
#         return buses
#
#     except Exception as e:
#         print(f"[avtovokzalspb] Ошибка: {e}")
#         return []
#
#     finally:
#         driver.quit()
# from selenium import webdriver
# from bs4 import BeautifulSoup
# import time
#
# def parse_avtovokzalspb(date, from_city, to_city):
#     print(f"[avtovokzalspb] Парсим {date} | {from_city} → {to_city}")
#     url = f"https://avtovokzalspb.ru/raspisanie/?from={from_city}&to={to_city}&date={date}"
#
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')
#
#     driver = webdriver.Chrome(options=options)
#
#     try:
#         driver.get(url)
#         time.sleep(5)  # Ждём загрузки JS
#
#         html = driver.page_source
#         soup = BeautifulSoup(html, 'html.parser')
#         rows = soup.select('table tr[data-route]')
#         buses = []
#
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) < 5:
#                 continue
#
#             try:
#                 time = cols[0].text.strip()
#                 route = cols[1].text.strip()
#                 carrier = cols[2].text.strip()
#                 free_seats = int(cols[3].text.strip())
#                 price = float(cols[4].text.replace(' ', '').replace('руб.', ''))
#             except Exception as e:
#                 print(f"[avtovokzalspb] Ошибка извлечения данных: {e}")
#                 continue
#
#             buses.append({
#                 'time': time,
#                 'route': route,
#                 'carrier': carrier,
#                 'free_seats': free_seats,
#                 'price': price,
#                 'source': 'avtovokzalspb'
#             })
#
#         print(f"[avtovokzalspb] Найдено рейсов: {len(buses)}")
#         return buses
#
#     except Exception as e:
#         print(f"[avtovokzalspb] Ошибка: {e}")
#         return []
#
#     finally:
#         driver.quit()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def parse_avtovokzalspb(date, from_city, to_city):
    options = Options()
    options.headless = False
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://avtovokzalspb.ru"
    driver.get(url)
    time.sleep(3)

    # Пример: ввод городов и даты
    driver.find_element(By.NAME, "from").send_keys(from_city)
    driver.find_element(By.NAME, "to").send_keys(to_city)
    driver.find_element(By.NAME, "date").send_keys(date)
    driver.find_element(By.CSS_SELECTOR, ".search-button").click()
    time.sleep(5)

    results = []
    try:
        items = driver.find_elements(By.CSS_SELECTOR, ".trip-item")
        for item in items:
            time_ = item.find_element(By.CSS_SELECTOR, ".time").text
            route = f"{from_city} → {to_city}"
            carrier = item.find_element(By.CSS_SELECTOR, ".company").text
            seats = item.find_element(By.CSS_SELECTOR, ".seats").text
            price = item.find_element(By.CSS_SELECTOR, ".cost").text.replace("₽", "").strip()

            results.append({
                'time': time_,
                'route': route,
                'carrier': carrier,
                'free_seats': int(seats) if seats.isdigit() else 0,
                'price': float(price) if price.replace('.', '', 1).isdigit() else 0.0,
                'source': 'avtovokzalspb'
            })
    except Exception as e:
        print(f"[avtovokzalspb] Ошибка: {e}")
    finally:
        driver.quit()

    return results