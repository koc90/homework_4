# text1 = "aaa"
# text2 = "bbb"

# joined_text = "&".join([text1, text2])

# print(joined_text)


import logging
import json


logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")

data_parse = "2024-01-15 18:45:45.139360&username=krabaton&message=gfbvhebvhr jerngjenguen unerugeugn"
data_list = data_parse.split("&")
logging.debug(f"Data_list = {data_list}")

time_received = data_list[0]
user_data = data_list[1:]

logging.debug(f"time_received = {time_received}\nuser_data = {user_data}")

data_dict = {key: value for key, value in [el.split("=") for el in user_data]}


with open("storage//data.json", "r") as f:
    data_json = json.load(f)

data_json[time_received] = data_dict

logging.debug(f"data_json = {data_json}")

with open("storage//data.json", "w") as f:
    json.dump(data_json, f)
