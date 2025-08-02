# import pandas as pd
# from bus_parser.avtovokzalspb import parse_avtovokzalspb
# from bus_parser.busfor import parse_busfor
# from bus_parser.tutu import parse_tutu
# from bus_parser.sks_auto import parse_sksauto
# from bus_parser.avokzal53 import parse_avokzal53
# from merger import merge_data
#
# def collect_data(date, from_city, to_city, sources):
#     all_data = []
#
#     if "avtovokzalspb" in sources:
#         all_data.extend(parse_avtovokzalspb(date, from_city, to_city))
#     if "busfor" in sources:
#         all_data.extend(parse_busfor(date, from_city, to_city))
#     if "sks-auto" in sources:
#         all_data.extend(parse_sksauto(date, from_city, to_city))
#     if "avokzal53" in sources:
#         all_data.extend(parse_avokzal53(date, from_city, to_city))
#
#     merged = merge_data(all_data)
#     return merged
#
# if __name__ == "__main__":
#     collect_data()
#
#     data.extend(parse_avtovokzalspb(test_date))
#     data.extend(parse_busfor(test_date))
#     data.extend(parse_sksauto(test_date))
#     data.extend(parse_avokzal53(test_date))
#
#     print("\n🔍 Результат парсинга:")
#     for item in data:
#         print(item)

from bus_parser.avtovokzalspb import parse_avtovokzalspb
from bus_parser.busfor import parse_busfor
from bus_parser.sks_auto import parse_sksauto
from bus_parser.avokzal53 import parse_avokzal53
# from merger import merge_data
import pandas as pd
from streamlit_app import merge_data

# def collect_data(date, from_city, to_city, sources):
#     all_data = []
#
#     if "avtovokzalspb" in sources:
#         all_data.extend(parse_avtovokzalspb(date, from_city, to_city))
#     if "busfor" in sources:
#         all_data.extend(parse_busfor(date, from_city, to_city))
#     if "sks-auto" in sources:
#         all_data.extend(parse_sksauto(date, from_city, to_city))
#     if "avokzal53" in sources:
#         all_data.extend(parse_avokzal53(date, from_city, to_city))
#
#     return all_data

def collect_data(from_city, to_city, date, sources):
    all_data = []

    if "busfor" in sources:
        from_id = get_busfor_stop_id(from_city)
        to_id = get_busfor_stop_id(to_city)
        if from_id and to_id:
            all_data.extend(get_busfor_routes(from_id, to_id, date))

    if "avtovokzalspb" in sources:
        all_data.extend(parse_avtovokzalspb(date, from_city, to_city))

    return merge_data(all_data)