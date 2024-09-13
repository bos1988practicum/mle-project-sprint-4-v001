import requests
import pandas as pd

service_url = 'http://127.0.0.1:8000'
events_store_url = "http://127.0.0.1:8020"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

df_items = pd.read_parquet("items.parquet")
dict_items = pd.read_parquet("id_dict_items.parquet")
dict_items = dict_items.set_index("item_id")["item_id_origin"].to_dict()
df_items["item_id"] = df_items["item_id"].map(dict_items)

def display_items(item_ids):

    item_columns_to_use = ["item_id", "track_name", "artist_names"]
    
    items_selected = df_items.query("item_id in @item_ids")[item_columns_to_use]
    items_selected = items_selected.set_index("item_id").reindex(item_ids)
    items_selected = items_selected.reset_index()
    
    print(items_selected)


print("\ntest 1 (personal answer offline):")

params = {"user_id": 1359367, 'k': 5}
resp = requests.post(service_url + "/recommendations_offline", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)

print("\ntest 2 (default answer offline):")

params = {"user_id": 2_000_000, 'k': 3}
resp = requests.post(service_url + "/recommendations_offline", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)

print("\ntest 3 (empty answer online):")

params = {"user_id": 100, 'k': 3}
resp = requests.post(service_url + "/recommendations_online", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)

print("\ntest 4 (add events):")

params = {"user_id": 1291248, "item_id": 33311009}
resp = requests.post(events_store_url + "/put", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)

print("\ntest 5 (good answer online):")

params = {"user_id": 1291248, 'k': 3}
resp = requests.post(service_url + "/recommendations_online", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)
print("Онлайн-рекомендации")
display_items(recs["recs"])

print("\ntest 6 (few events):")

user_id = 1291248
event_item_ids = [65851540, 45499814, 57921154, 35505245]

for event_item_id in event_item_ids:
    resp = requests.post(
        events_store_url + "/put", 
        headers=headers, 
        params={"user_id": user_id, "item_id": event_item_id}
    )
                         
params = {"user_id": user_id, 'k': 7}
resp = requests.post(service_url + "/recommendations_online", headers=headers, params=params)
online_recs = resp.json()
    
print(online_recs)
print("Онлайн-события")
display_items(event_item_ids)
print("Онлайн-рекомендации")
display_items(online_recs["recs"])

print("\ntest 7 (online + offline):")

user_id = 1291250
event_item_ids = [178529, 328683, 37384]

for event_item_id in event_item_ids:
    resp = requests.post(
        events_store_url + "/put", 
        headers=headers, 
        params={"user_id": user_id, "item_id": event_item_id}
    )

params = {"user_id": 1291250, 'k': 10}
resp_offline = requests.post(service_url + "/recommendations_offline", headers=headers, params=params)
resp_online = requests.post(service_url + "/recommendations_online", headers=headers, params=params)
resp_blended = requests.post(service_url + "/recommendations", headers=headers, params=params)

recs_offline = resp_offline.json()["recs"]
recs_online = resp_online.json()["recs"]
recs_blended = resp_blended.json()["recs"]

# print("recs_offline:", recs_offline)
# print("recs_online:", recs_online)
# print("recs_blended:", recs_blended)

print("Онлайн-события")
display_items(event_item_ids)
print("Офлайн-рекомендации")
display_items(recs_offline)
print("Онлайн-рекомендации")
display_items(recs_online)
print("Рекомендации")
display_items(recs_blended)
