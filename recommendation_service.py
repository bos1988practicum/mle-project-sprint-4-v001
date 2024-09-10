import logging
import requests

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

import pandas as pd
from itertools import chain
from core import Recommendations


logger = logging.getLogger("uvicorn.error")
features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020"

# def dedup_ids(ids):
#     """
#     Дедублицирует список идентификаторов, оставляя только первое вхождение
#     """
#     seen = set()
#     ids = [id for id in ids if not (id in seen or seen.add(id))]

#     return ids

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Service Starting")
    
    rec_store = Recommendations()
    
    rec_store.load(
        path_recs_personal="recommendations.parquet",
        path_recs_default="top_popular.parquet",
        path_dict_items="id_dict_items.parquet",
        path_dict_users="id_dict_users.parquet",
        col_items="item_id",
        col_users="user_id",
        col_rating="score",
    )
    app.state.rec_store = rec_store

    logger.info("Service Ready!")

    yield
    # этот код выполнится только один раз при остановке сервиса
    rec_store.stats()
    logger.info("Service Stopping")


# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)

@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, request: Request, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs = request.app.state.rec_store.get(user_id=user_id, k=k)

    return {"recs": recs["item_id"]}

@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """

    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    # получаем список последних событий пользователя, возьмём три последних
    params = {"user_id": user_id, "k": 3}
    resp = requests.post(events_store_url + "/get", headers=headers, params=params)
    events = resp.json()
    events = events["events"]
    logger.debug(f"3 events: {events}")

    # получаем список айтемов, похожих на последние три, с которыми взаимодействовал пользователь
    items = []
    scores = []
    for item_id in events:
        # для каждого item_id получаем список похожих в item_similar_items
        params = {"item_id": item_id, "k": k}
        resp = requests.post(features_store_url + "/similar_items", headers=headers, params=params)
        item_similar_items = resp.json()
        items += item_similar_items["sim_item_id"]
        scores += item_similar_items["score"]

    # сортируем похожие объекты по scores в убывающем порядке
    # удаляем дубликаты, чтобы не выдавать одинаковые рекомендации
    recs = (
        pd.DataFrame({
            "items": items,
            "scores": scores,
        })
        .sort_values("scores", ascending=False)
        ["items"]
        .drop_duplicates(keep="first")
        .to_list()
    )

    return {"recs": recs[:k]} 

@app.post("/recommendations")
async def recommendations(user_id: int, request: Request, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs_offline = await recommendations_offline(user_id, request, k)
    recs_online = await recommendations_online(user_id, k)

    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]

    # чередуем элементы из списков, пока позволяет минимальная длина
    recs_blended = list(chain(*zip(recs_online, recs_offline)))

    # добавляем оставшиеся элементы в конец
    min_length = min(len(recs_offline), len(recs_online))
    recs_blended += recs_online[min_length:]
    recs_blended += recs_offline[min_length:]

    # удаляем дубликаты
    recs_blended = pd.Series(recs_blended).drop_duplicates(keep="first").to_list()
    
    # оставляем только первые k рекомендаций
    recs_blended = recs_blended[:k]

    return {"recs": recs_blended}
