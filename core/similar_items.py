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


class SimilarItems:

    def __init__(self):

        self._similar_items = None
        self._dict_items = None

        self.col_id_origin = None
        self.col_id_similar = None
        self.col_score = None

    def load(
        self,
        path_similar,
        path_dict,
        col_id_origin="item_id",
        col_id_similar="sim_item_id",
        col_score="score",
    ):
        """
        Загружаем данные из файла
        """
        self.col_id_origin = col_id_origin
        self.col_id_similar = col_id_similar
        self.col_score = col_score

        logger.info(f"Loading dict")
        self._dict_items = pd.read_parquet(path_dict)
        self._dict_items = self._dict_items.set_index("item_id")["item_id_origin"].to_dict()

        logger.info(f"Loading data")
        self._similar_items = pd.read_parquet(path_similar, columns=[col_id_origin, col_id_similar, col_score])
        for col in [col_id_origin, col_id_similar]:
            self._similar_items[col] = self._similar_items[col].map(self._dict_items)
        self._similar_items = self._similar_items.set_index(col_id_origin)

        logger.info(f"Loaded")

    def get(self, item_id: int, k: int = 10):
        """
        Возвращает список похожих объектов
        """
        try:
            i2i = (
                self._similar_items
                .loc[item_id, [self.col_id_similar, self.col_score]]
                .head(k)
                .to_dict(orient="list")
            )
        except KeyError:
            logger.error("No recommendations found")
            i2i = {self.col_id_similar: [], self.col_score: {}}

        return i2i


if __name__ == "__main__":

    rec_store = SimilarItems()

    rec_store.load(
        path_similar="/home/mle-user/mle_projects_final/mle-project-sprint-4-v001/similar.parquet",
        path_dict="/home/mle-user/mle_projects_final/mle-project-sprint-4-v001/id_dict_items.parquet",
        col_id_origin="item_id",
        col_id_similar="sim_item_id",
        col_score="score",
    )

    print(rec_store.get(item_id=135, k=5))        # Noisettes, "Atticus"
    print(rec_store.get(item_id=33311009, k=5))   # Imagine Dragons, "Believer"
    print(rec_store.get(item_id=100, k=5))        # `No recommendations found`
    print(rec_store.get(item_id="default", k=5))  # `No recommendations found`
