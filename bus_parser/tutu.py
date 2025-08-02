# from selenium import webdriver
# from bs4 import BeautifulSoup
# import time
#
# def parse_tutu(date):
#     print(f"🟢 Парсим tutu.ru за {date}...")
#     url = f"https://www.tutu.ru/poisk?from=spb&to=novgorod&date={date}"
#
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')  # фоновый режим
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')
#
#     driver = webdriver.Chrome(options=options)
#     try:
#         driver.get(url)
#         time.sleep(5)  # Ждём загрузки JS
#         html = driver.page_source
#         driver.quit()
#
#         soup = BeautifulSoup(html, 'html.parser')
#         items = soup.select('.result-item')
#         buses = []
#
#         for item in items:
#             time_elem = item.select_one('.departure-time')
#             carrier_elem = item.select_one('.company-name')
#             price_elem = item.select_one('.price')
#             seats_elem = item.select_one('.available-seats')
#
#             if not all([time_elem, carrier_elem, price_elem, seats_elem]):
#                 continue
#
#             try:
#                 free_seats = int(seats_elem.text.strip())
#                 price = float(price_elem.text.replace(' ', '').strip())
#             except:
#                 continue
#
#             buses.append({
#                 'time': time_elem.text.strip(),
#                 'route': 'СПб - В. Новгород',
#                 'carrier': carrier_elem.text.strip(),
#                 'free_seats': free_seats,
#                 'price': price,
#                 'source': 'tutu',
#                 'date': date
#             })
#
#         print(f"[tutu] Спаршено рейсов: {len(buses)}")
#         return buses
#
#     except Exception as e:
#         print(f"🔴 Ошибка при парсинге tutu: {e}")
#         driver.quit()
#         return []
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def parse_tutu(date, from_city, to_city):
    print(f"[tutu] Парсим {date} | {from_city} → {to_city}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://www.tutu.ru/poisk?from=spb&to=novgorod")
            page.fill("#from", from_city)
            page.fill("#to", to_city)
            page.fill("#date", date)
            page.click(".search-button")
            page.wait_for_timeout(5000)

            html = page.content()
            browser.close()

            soup = BeautifulSoup(html, 'html.parser')
            items = soup.select('.result-item')
            buses = []

            for item in items:
                time_elem = item.select_one('.departure-time')
                carrier_elem = item.select_one('.company-name')
                price_elem = item.select_one('.price')
                seats_elem = item.select_one('.available-seats')

                if not all([time_elem, carrier_elem, price_elem, seats_elem]):
                    continue

                try:
                    free_seats = int(seats_elem.text.strip())
                    price = float(price_elem.text.replace(' ', '').strip())
                except:
                    continue

                buses.append({
                    'time': time_elem.text.strip(),
                    'route': f"{from_city} → {to_city}",
                    'carrier': carrier_elem.text.strip(),
                    'free_seats': free_seats,
                    'price': price,
                    'source': 'tutu'
                })

            return buses

        except Exception as e:
            print(f"[tutu] Ошибка: {e}")
            return []