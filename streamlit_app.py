import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta

# Импорты парсеров (пока только busfor)
from bus_parser.busfor import parse_busfor
from bus_parser.etraffic import parse_e_traffic
from bus_parser.tutu import parse_tutu
from bus_parser.avtovokzalspb import parse_avtovokzalspb



# Импорт универсальной функции сохранения
from utils.save_to_excel import save_to_excel

# Создаем папку для данных
os.makedirs("data", exist_ok=True)

st.set_page_config(
    page_title="Парсер транспорта",
    page_icon="🚌",
    layout="wide"
)

# Стилизация
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚌 Парсер транспортных расписаний")
st.markdown("---")

# Боковая панель
st.sidebar.header("⚙️ Параметры поиска")

# Словарь городов из busfor с примечаниями
# Ключ - это значение, которое будет передано в парсер (полное название)
# Значение - это то, что отображается пользователю
CITY_DISPLAY_MAP = {
    "Санкт-Петербург": "Санкт-Петербург",
    "Москва": "Москва",
    "Казань": "Казань ***", # только из Москвы на e-traffic
    "Сочи": "Сочи ***", # только из Москвы на e-traffic
    "Ростов-на-Дону": "Ростов-на-Дону",
    "Кириши": "Кириши", #только обратный рейс из Кириши на e-traffic
    "Екатеринбург": "Екатеринбург *",  # Нет на Busfor, нет на e-traffic
    "Новосибирск": "Новосибирск *",  # Нет на Busfor, нет на e-traffic
    "Краснодар": "Краснодар ***", # только из Москвы на e-traffic
    "Уфа": "Уфа ***", # только из Москвы на e-traffic
    "Красноярск": "Красноярск *",  # Нет на Busfor, нет на e-traffic
    "Владивосток": "Владивосток *", # Нет на Busfor, нет на e-traffic
    "Рыбинск": "Рыбинск ***", # только из Москвы на e-traffic
    "Великий Новгород": "Великий Новгород",
    "Нижний Новгород": "Нижний Новгород ***",  # только из Москвы на e-traffic
    "Волгоград": "Волгоград ***", # только из Москвы на e-traffic
    "Воронеж": "Воронеж ***", # только из Москвы на e-traffic
    "Смоленск": "Смоленск",
    "Брянск": "Брянск ***", # только из Москвы на e-traffic
    "Весьегонск": "Весьегонск",
    "Кострома": "Кострома **",  # Только из Москвы на Busfor и на e-traffic
    "Ярославль": "Ярославль **",  # Только из Москвы на Busfor и на e-traffic
    "Псков": "Псков",
    'Мурманск': 'Мурманск', # только из Киркенес на e-traffic
}

# Создаем список для отображения (значения словаря)
CITY_OPTIONS_DISPLAY = list(CITY_DISPLAY_MAP.values())
# Создаем список ключей для внутреннего использования
CITY_OPTIONS_KEYS = list(CITY_DISPLAY_MAP.keys())

# Ввод данных с дефолтными значениями
# Найдем индексы для значений по умолчанию
default_from_display = "Санкт-Петербург"
default_to_display = "Москва"

default_from_index = CITY_OPTIONS_DISPLAY.index(
    default_from_display) if default_from_display in CITY_OPTIONS_DISPLAY else 0
default_to_index = CITY_OPTIONS_DISPLAY.index(default_to_display) if default_to_display in CITY_OPTIONS_DISPLAY else 0

# Используем список с примечаниями для отображения
from_city_display_selected = st.sidebar.selectbox("🏙️ Город отправления", CITY_OPTIONS_DISPLAY,
                                                  index=default_from_index)
to_city_display_selected = st.sidebar.selectbox("🏢 Город прибытия", CITY_OPTIONS_DISPLAY, index=default_to_index)

# Получаем ключи (полные названия городов) для передачи в парсер
# Ищем ключ по значению
from_city = next((k for k, v in CITY_DISPLAY_MAP.items() if v == from_city_display_selected),
                 from_city_display_selected)
to_city = next((k for k, v in CITY_DISPLAY_MAP.items() if v == to_city_display_selected), to_city_display_selected)

# Ограничение выбора даты: только сегодня и будущие даты
min_date = date.today()
search_date = st.sidebar.date_input("📅 Дата поездки", value=min_date, min_value=min_date)

# Выбор источников
all_sources = {
    "busfor": "Busfor.ru",
    'etraffic': 'E-traffic.ru',
    "tutu": "Tutu.ru",
    "avtovokzalspb": "AvtovokzalSPb.ru",
    # "sks-auto": "SKS-Auto.ru (заглушка)",
    # "mos_metro": "MosMetro.ru (заглушка)"
}
# Для демонстрации включим только busfor
default_sources = ["busfor"]
selected_sources = st.sidebar.multiselect(
    "📡 Источники данных",
    options=list(all_sources.keys()),
    format_func=lambda x: all_sources[x],
    default=default_sources
)

# Информация о сервисе
st.sidebar.markdown("---")
st.sidebar.info("""
**💡 Инструкция:**
1. Выберите города отправления и прибытия
2. Выберите дату поездки (только сегодня и будущие даты)
3. Выберите источники данных
4. Нажмите кнопку "🔍 Поиск рейсов"
5. Дождитесь загрузки результатов
6. При необходимости решите капчу вручную
""")

st.sidebar.warning("""
**⚠️ Важно:**
- При первом запуске может появиться капча
- Решите её вручную в браузере
- Не закрывайте браузер во время парсинга
""")

# Основная область
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🔍 Поиск рейсов", type="primary", use_container_width=True):
        if from_city and to_city and search_date:
            search_date_str = search_date.strftime("%Y-%m-%d")

            with st.spinner("Идет поиск рейсов... Это может занять несколько минут..."):
                all_results = []

                # --- Парсинг ---
                if "busfor" in selected_sources:
                    try:
                        with st.status("Загрузка данных с Busfor...", expanded=True) as status:
                            st.write("Подключение к Busfor...")
                            # Передаем ПОЛНЫЕ названия городов
                            res = parse_busfor(search_date_str, from_city, to_city)
                            all_results.extend(res)
                            st.write(f"Найдено {len(res)} рейсов")
                            status.update(label=f"Busfor: {len(res)} рейсов", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"Ошибка при парсинге Busfor: {str(e)}")
                 # elif source == "e-traffic":
                 #    data = parse_e_traffic(date_str, from_city, to_city)

                # Заглушки для других источников
                if "etraffic" in selected_sources:
                    try:
                        with st.status("Загрузка данных с E-Traffic...", expanded=True) as status:
                            st.write("Подключение к E-Traffic...")
                            res = parse_e_traffic(search_date_str, from_city, to_city)
                            all_results.extend(res)
                            st.write(f"Найдено {len(res)} рейсов")
                            status.update(label=f"E-Traffic: {len(res)} рейсов", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"Ошибка при парсинге E-Traffic: {str(e)}")

                # Заглушки для других источников
                if "tutu" in selected_sources:
                    try:
                        with st.status("Загрузка данных с Tutu...", expanded=True) as status:
                            st.write("Подключение к Tutu...")
                            res = parse_tutu(search_date_str, from_city, to_city)
                            all_results.extend(res)
                            st.write(f"Найдено {len(res)} рейсов")
                            status.update(label=f"Tutu: {len(res)} рейсов", state="complete",
                                          expanded=False)
                    except Exception as e:
                        st.error(f"Ошибка при парсинге Tutu: {str(e)}")

                if "avtovokzalspb" in selected_sources:
                    try:
                        with st.status("Загрузка данных с AvtovokzalSPb...", expanded=True) as status:
                            st.write("Подключение к AvtovokzalSPb...")
                            res = parse_avtovokzalspb(search_date_str, from_city, to_city)
                            all_results.extend(res)
                            st.write(f"Найдено {len(res)} рейсов")
                            status.update(label=f"AvtovokzalSPb: {len(res)} рейсов", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"Ошибка при парсинге AvtovokzalSPb: {str(e)}")

                if "sks-auto" in selected_sources:
                    try:
                        with st.status("Загрузка данных с SKS-Auto...", expanded=True) as status:
                            st.write("Подключение к SKS-Auto...")
                            res = parse_sks_auto(search_date_str, from_city, to_city)
                            all_results.extend(res)
                            st.write(f"Найдено {len(res)} рейсов")
                            status.update(label=f"SKS-Auto: {len(res)} рейсов", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"Ошибка при парсинге SKS-Auto: {str(e)}")

                # if "mosmetro" in selected_sources:
                #     try:
                #         with st.status("Загрузка данных с MosMetro...", expanded=True) as status:
                #             st.write("Подключение к MosMetro...")
                #             res = parse_mosmetro(search_date_str, from_city, to_city)
                #             all_results.extend(res)
                #             st.write(f"Найдено {len(res)} рейсов")
                #             status.update(label=f"MosMetro: {len(res)} рейсов", state="complete", expanded=False)
                #     except Exception as e:
                #         st.error(f"Ошибка при парсинге MosMetro: {str(e)}")

                # --- Отображение результатов ---
                if all_results:
                    st.success(f"✅ Успешно найдено {len(all_results)} рейсов!")

                    # Отображение результатов
                    df_raw = pd.DataFrame(all_results)

                    # Фильтрация по наличию данных
                    df_filtered = df_raw[df_raw['time'] != "N/A"]

                    if not df_filtered.empty:

                        # --- НАЧАЛО: Обработка DataFrame для отображения ---
                        df_display = df_filtered.copy()

                        # Убеждаемся, что столбцы с местами и проданными билетами - строки
                        df_display['free_seats'] = df_display['free_seats'].astype(str)
                        df_display['total_seats'] = df_display['total_seats'].astype(str)
                        df_display['sold_tickets'] = df_display['sold_tickets'].astype(str)
                        # --- КОНЕЦ: Обработка DataFrame для отображения ---

                        # Отображение таблицы
                        st.subheader("📋 Результаты поиска")
                        st.dataframe(
                            df_display,
                            column_config={
                                "time": "⏰ Время",
                                "trip_number": "🔢 № рейса",
                                "departure_point": "📍 НП",
                                "arrival_point": "🎯 КП",
                                "carrier": "🚗 Перевозчик",
                                "total_seats": "💺 Всего",
                                "free_seats": "🪑 Свободно",
                                "sold_tickets": "🎟️ Продано",
                                "price": "💰 Цена (руб.)",
                                "source": "📡 Источник"
                            },
                            hide_index=True,
                            use_container_width=True
                        )

                        # Статистика (только один раз внизу)
                        st.subheader("📊 Статистика")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Всего рейсов", len(df_filtered))
                        with col2:
                            avg_price = df_filtered['price'].mean()
                            st.metric("Средняя цена", f"{avg_price:.0f} руб.")
                        with col3:
                            free_seats_numeric_for_stats = pd.to_numeric(df_filtered['free_seats'], errors='coerce')
                            avg_free_seats = free_seats_numeric_for_stats.mean()
                            if pd.notna(avg_free_seats):
                                st.metric("Среднее кол-во свободных мест", f"{avg_free_seats:.1f}")
                            else:
                                st.metric("Среднее кол-во свободных мест", "Н/Д")

                        # --- Кнопка для скачивания Excel ---
                        st.markdown("---")
                        st.subheader("💾 Скачать результаты")

                        # Проверяем, существует ли файл
                        excel_file_path = "data/history.xlsx"
                        if os.path.exists(excel_file_path):
                            try:
                                with open(excel_file_path, "rb") as file:
                                    st.download_button(
                                        label="📥 Скачать `history.xlsx`",
                                        data=file,
                                        file_name="history.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )
                                st.info("Файл `history.xlsx` готов к скачиванию. Нажмите кнопку выше.")
                            except Exception as e:
                                st.error(f"Ошибка при подготовке файла к скачиванию: {e}")
                        else:
                            st.warning("Файл результатов не найден. Попробуйте выполнить поиск заново.")

                    else:
                        st.warning("⚠️ Не удалось извлечь данные из результатов")
                        st.info("Попробуйте повторить поиск или проверьте параметры")
                else:
                    st.error("❌ Не удалось найти рейсы")
                    st.info("""
                    Возможные причины:
                    - Нет доступных рейсов на выбранную дату
                    - Требуется повторное решение капчи
                    - Изменилась структура сайта
                    - Проблемы с подключением
                    - Все выбранные источники вернули пустой результат
                    """)

        else:
            st.warning("⚠️ Пожалуйста, заполните все поля")

# Информация о сервисе и примечаниях к городам
st.markdown("---")
st.subheader("ℹ️ О сервисе и примечаниях")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    **Парсер транспортных расписаний** - это инструмент для автоматического поиска и сбора информации о рейсах 
    с различных сайтов.

    **Особенности:**
    - 🔍 Поиск рейсов по заданным параметрам
    - 📊 Отображение информации о времени, перевозчике, ценах и местах
    - 💾 Экспорт результатов в Excel формат
    - 🛡 Защита от обнаружения автоматизированных запросов
    - 📡 Поддержка нескольких источников данных

    **Поддерживаемые функции:**
    - Поиск между любыми городами России
    - Выбор даты поездки (только будущие даты)
    - Выбор источников данных
    - Отображение актуальной информации о рейсах
    """)
with col2:
    st.markdown("""
    **Примечания к городам:**
    - `*` - Города, которые могут отсутствовать на некоторых источниках (например, Busfor, e-traffic)
    - `**` - Города, доступные для поиска только из Москвы на busfor и на e-traffic
    - `***` - Города, доступные для поиска только из Москвы на e-traffic
    """)

# Футер
st.markdown("---")
st.caption("⚠️ Данный инструмент предназначен только для образовательных целей. Уважайте условия использования сайтов.")


