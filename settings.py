from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    ONLINE_COUNT_EVENTS: int = 3


class PathSettings(BaseSettings):
    PATH_RECS_PERSONAL: str = "recommendations.parquet"
    PATH_RECS_DEFAULT: str = "top_popular.parquet"
    PATH_RECS_SIMILAR: str = "similar.parquet"
    PATH_DICT_ITEMS: str = "id_dict_items.parquet"
    PATH_DICT_USERS: str = "id_dict_users.parquet"


class RecommendationServiceSettings(BaseSettings):
    RECS_HOST: str = "localhost"
    RECS_PORT: int = 8000
    RECS_PATH: str = ""
    RECS_PROTOCOL: str = "http"

    RECS_HEADERS_CONTENT_TYPE: str = "application/json"
    RECS_HEADERS_ACCEPT: str = "text/plain"

    ITEMS_COLUMN_NAME: str = "item_id"
    USERS_COLUMN_NAME: str = "user_id"
    RATING_COLUMN_NAME: str = "score"

    @property
    def url(self) -> str:
        return f"{self.RECS_PROTOCOL}://{self.RECS_HOST}:{self.RECS_PORT}/{self.RECS_PATH}"
    
    @property
    def headers(self) -> dict:
        return {"Content-type": self.RECS_HEADERS_CONTENT_TYPE, "Accept": self.RECS_HEADERS_ACCEPT}


class EventsServiceSettings(BaseSettings):
    EVENTS_HOST: str = "localhost"
    EVENTS_PORT: int = 8020
    EVENTS_PATH: str = "get"
    EVENTS_PROTOCOL: str = "http"

    EVENTS_HEADERS_CONTENT_TYPE: str = "application/json"
    EVENTS_HEADERS_ACCEPT: str = "text/plain"

    ITEMS_ORIGIN_COLUMN_NAME: str = "item_id"
    ITEMS_SIMILAR_COLUMN_NAME: str = "sim_item_id"
    SCORE_COLUMN_NAME: str = "score"

    @property
    def url(self) -> str:
        return f"{self.EVENTS_PROTOCOL}://{self.EVENTS_HOST}:{self.EVENTS_PORT}/{self.EVENTS_PATH}"
    
    @property
    def headers(self) -> dict:
        return {"Content-type": self.EVENTS_HEADERS_CONTENT_TYPE, "Accept": self.EVENTS_HEADERS_ACCEPT}


class FeaturesServiceSettings(BaseSettings):
    FEATURES_HOST: str = "localhost"
    FEATURES_PORT: int = 8010
    FEATURES_PATH: str = "similar_items"
    FEATURES_PROTOCOL: str = "http"

    FEATURES_HEADERS_CONTENT_TYPE: str = "application/json"
    FEATURES_HEADERS_ACCEPT: str = "text/plain"

    @property
    def url(self) -> str:
        return f"{self.FEATURES_PROTOCOL}://{self.FEATURES_HOST}:{self.FEATURES_PORT}/{self.FEATURES_PATH}"
    
    @property
    def headers(self) -> dict:
        return {"Content-type": self.FEATURES_HEADERS_CONTENT_TYPE, "Accept": self.FEATURES_HEADERS_ACCEPT}
