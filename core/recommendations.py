import os
import sys
import pandas as pd

# относительный импорт:
def get_root(n=1):
    if n == 0:
        return os.path.realpath(__file__)
    else:
        return os.path.dirname(get_root(n-1))
sys.path.append(get_root(2))
from core.logger import logger


class Recommendations:

    def __init__(self):

        self._recs = {"personal": None, "default": None}
        self._stats = {
            "request_personal_count": 0,
            "request_default_count": 0,
        }
        self._dict_items = None
        self._dict_users = None

        self.col_items = None
        self.col_users = None
        self.col_rating = None


    def load(
        self,
        path_recs_personal,
        path_recs_default,
        path_dict_items,
        path_dict_users,
        col_items,
        col_users,
        col_rating,
    ):
        """
        Загружает рекомендации из файла
        """
        self.col_items = col_items
        self.col_users = col_users
        self.col_rating = col_rating

        logger.info(f"Loading dicts")
        self._dict_items = pd.read_parquet(path_dict_items)
        self._dict_items = self._dict_items.set_index("item_id")["item_id_origin"].to_dict()
        self._dict_users = pd.read_parquet(path_dict_users)
        self._dict_users = self._dict_users.set_index("user_id")["user_id_origin"].to_dict()

        logger.info("Loading default recommendations")
        self._recs["default"] = pd.read_parquet(path_recs_default, columns=[col_items, col_rating])
        self._recs["default"][col_items] = self._recs["default"][col_items].map(self._dict_items)
        self._recs["default"] = self._recs["default"].sort_values(col_rating, ascending=False)

        logger.info("Loading personal recommendations")
        self._recs["personal"] = pd.read_parquet(path_recs_personal, columns=[col_users, col_items, col_rating])
        self._recs["personal"][col_items] = self._recs["personal"][col_items].map(self._dict_items)
        self._recs["personal"][col_users] = self._recs["personal"][col_users].map(self._dict_users)
        self._recs["personal"] = self._recs["personal"].sort_values(col_rating, ascending=False)
        self._recs["personal"] = self._recs["personal"].set_index(col_users)
    
        logger.info(f"Loaded")


    def get(self, user_id: int, k: int=100):
        """
        Возвращает список рекомендаций для пользователя
        """
        try:
            recs = self._recs["personal"].loc[user_id]
            scores = recs[self.col_rating].to_list()[:k]
            recs = recs[self.col_items].to_list()[:k]
            self._stats["request_personal_count"] += 1
        except KeyError:
            recs = self._recs["default"]
            scores = recs[self.col_rating].to_list()[:k]
            recs = recs[self.col_items].to_list()[:k]
            self._stats["request_default_count"] += 1
        except:
            logger.error("No recommendations found")
            recs = []

        logger.debug(f"recs: item_id: {recs}, score: {scores}")
        return {"item_id": recs, "score": scores}


    def stats(self):

        logger.info("Stats for recommendations")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value} ")


if __name__ == "__main__":

    rec_store = Recommendations()

    rec_store.load(
        path_recs_personal="/home/mle-user/mle_projects_final/mle-project-sprint-4-v001/recommendations.parquet",
        path_recs_default="/home/mle-user/mle_projects_final/mle-project-sprint-4-v001/top_popular.parquet",
        path_dict_items="/home/mle-user/mle_projects_final/mle-project-sprint-4-v001/id_dict_items.parquet",
        path_dict_users="/home/mle-user/mle_projects_final/mle-project-sprint-4-v001/id_dict_users.parquet",
        col_items="item_id",
        col_users="user_id",
        col_rating="score",
    )

    print(rec_store.get(user_id=0, k=10))
    print(rec_store.get(user_id=1359367, k=3))
    print(rec_store.get(user_id="default", k=5))
