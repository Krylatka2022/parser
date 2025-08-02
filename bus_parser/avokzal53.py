# import requests
# from bs4 import BeautifulSoup
#
# def parse_avokzal53(date, from_city, to_city):
#     print(f"[avokzal53] Парсим {date} | {from_city} → {to_city}")
#     url = f" https://avokzal53.ru/raspisanie/?date={date}"
#     try:
#         response = requests.get(url, timeout=10)
#         if response.status_code != 200:
#             return []
#
#         soup = BeautifulSoup(response.text, 'html.parser')
#         rows = soup.select('.schedule-table tr')
#         buses = []
#
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) < 5:
#                 continue
#
#             time = cols[0].text.strip()
#             route = cols[1].text.strip()
#             if to_city.lower() not in route.lower():
#                 continue
#
#             try:
#                 free_seats = int(cols[4].text.strip())
#                 price = float(cols[3].text.strip().replace(' ', '').replace('руб.', ''))
#             except:
#                 continue
#
#             buses.append({
#                 'time': time,
#                 'route': route,
#                 'carrier': cols[2].text.strip(),
#                 'free_seats': free_seats,
#                 'price': price,
#                 'source': 'avokzal53'
#             })
#
#         return buses
#     except Exception as e:
#         print(f"[avokzal53] Ошибка: {e}")
#         return []

# from selenium import webdriver
# from bs4 import BeautifulSoup
# import time
#
# def parse_avokzal53(date, from_city, to_city):
#     print(f"[avokzal53] Парсим {date} | {from_city} → {to_city}")
#     url = "https://avokzal53.ru/raspisanie/ "
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
#         with open(f"debug_avokzal53_{date}.html", "w", encoding="utf-8") as f:
#             f.write(html)
#         print(f"[avokzal53] HTML сохранён: debug_avokzal53_{date}.html")
#
#         soup = BeautifulSoup(html, 'html.parser')
#         rows = soup.select('.schedule-table tr')
#         buses = []
#
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) < 5:
#                 continue
#
#             time = cols[0].text.strip()
#             route = cols[1].text.strip()
#             if to_city.lower() not in route.lower():
#                 continue
#
#             try:
#                 free_seats = int(cols[4].text.strip())
#                 price = float(cols[3].text.strip().replace(' ', '').replace('руб.', ''))
#             except Exception as e:
#                 print(f"[avokzal53] Ошибка извлечения: {e}")
#                 continue
#
#             buses.append({
#                 'time': time,
#                 'route': route,
#                 'carrier': cols[2].text.strip(),
#                 'free_seats': free_seats,
#                 'price': price,
#                 'source': 'avokzal53'
#             })
#
#         print(f"[avokzal53] Спаршено рейсов: {len(buses)}")
#         return buses
#
#     except Exception as e:
#         print(f"[avokzal53] Ошибка: {e}")
#         return []
#
#     finally:
#         driver.quit()
import requests
from bs4 import BeautifulSoup

def parse_avokzal53(date, from_city, to_city):
    print(f"[avokzal53] Парсим {date} | {from_city} → {to_city}")
    url = "https://avokzal53.ru/raspisanie/ "
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.select('.schedule-table tr')
        buses = []

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
            if to_city.lower() not in cols[1].text.strip().lower():
                continue

            try:
                free_seats = int(cols[4].text.strip())
                price = float(cols[3].text.strip().replace(' ', '').replace('руб.', ''))
            except:
                continue

            buses.append({
                'time': cols[0].text.strip(),
                'route': cols[1].text.strip(),
                'carrier': cols[2].text.strip(),
                'free_seats': free_seats,
                'price': price,
                'source': 'avokzal53'
            })

        return buses

    except Exception as e:
        print(f"[avokzal53] Ошибка: {e}")
        return []