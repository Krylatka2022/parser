# import requests
# from bs4 import BeautifulSoup
#
# def parse_sksauto(date, from_city, to_city):
#     print(f"[sks-auto] Парсим {date} | {from_city} → {to_city}")
#     url = f" https://sks-auto.ru/raspisanie/?date={date}"
#     try:
#         response = requests.get(url, timeout=10)
#         if response.status_code != 200:
#             return []
#
#         soup = BeautifulSoup(response.text, 'html.parser')
#         rows = soup.select('#schedule-table tr')
#         buses = []
#
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) < 6:
#                 continue
#
#             time = cols[0].text.strip()
#             route = cols[1].text.strip()
#             if to_city.lower() not in route.lower():
#                 continue
#
#             try:
#                 free_seats = int(cols[4].text.strip())
#                 price = float(cols[5].text.strip().replace(' ', '').replace('руб.', ''))
#             except:
#                 continue
#
#             buses.append({
#                 'time': time,
#                 'route': route,
#                 'carrier': cols[2].text.strip(),
#                 'free_seats': free_seats,
#                 'price': price,
#                 'source': 'sks-auto'
#             })
#
#         return buses
#     except Exception as e:
#         print(f"[sks-auto] Ошибка: {e}")
#         return []

# from selenium import webdriver
# from bs4 import BeautifulSoup
# import time
#
# def parse_sksauto(date, from_city, to_city):
#     print(f"[sks_auto] Парсим {date} | {from_city} → {to_city}")
#     url = " https://sks-auto.ru/raspisanie/ "
#
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     driver = webdriver.Chrome(options=options)
#
#     try:
#         driver.get(url)
#         time.sleep(5)
#
#         html = driver.page_source
#         with open(f"debug_sks_auto_{date}.html", "w", encoding="utf-8") as f:
#             f.write(html)
#         print(f"[sks_auto] HTML сохранён: debug_sks_auto_{date}.html")
#
#         soup = BeautifulSoup(html, 'html.parser')
#         rows = soup.select('#schedule-table tr')
#         buses = []
#
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) < 6:
#                 continue
#
#             time = cols[0].text.strip()
#             route = cols[1].text.strip()
#             if to_city.lower() not in route.lower():
#                 continue
#
#             try:
#                 free_seats = int(cols[4].text.strip())
#                 price = float(cols[5].text.replace(' ', '').replace('руб.', ''))
#             except Exception as e:
#                 print(f"[sks_auto] Ошибка извлечения: {e}")
#                 continue
#
#             buses.append({
#                 'time': time,
#                 'route': route,
#                 'carrier': cols[2].text.strip(),
#                 'free_seats': free_seats,
#                 'price': price,
#                 'source': 'sks-auto'
#             })
#
#         print(f"[sks_auto] Спаршено рейсов: {len(buses)}")
#         return buses
#
#     except Exception as e:
#         print(f"[sks_auto] Ошибка: {e}")
#         return []
#
#     finally:
#         driver.quit()
import requests
from bs4 import BeautifulSoup

def parse_sksauto(date, from_city, to_city):
    print(f"[sks-auto] Парсим {date} | {from_city} → {to_city}")
    url = " https://sks-auto.ru/raspisanie/ "
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.select('#schedule-table tr')
        buses = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue
            if to_city.lower() not in cols[1].text.strip().lower():
                continue

            try:
                free_seats = int(cols[4].text.strip())
                price = float(cols[5].text.replace(' ', '').replace('руб.', ''))
            except:
                continue

            buses.append({
                'time': cols[0].text.strip(),
                'route': cols[1].text.strip(),
                'carrier': cols[2].text.strip(),
                'free_seats': free_seats,
                'price': price,
                'source': 'sks-auto'
            })

        return buses

    except Exception as e:
        print(f"[sks-auto] Ошибка: {e}")
        return []