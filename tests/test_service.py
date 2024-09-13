import requests

from settings import (
    EventsServiceSettings,
    FeaturesServiceSettings,
    RecommendationServiceSettings,
)


events_store_settings = EventsServiceSettings()
features_store_settings = FeaturesServiceSettings()
recommendation_settings = RecommendationServiceSettings()

events_store_settings.EVENTS_PATH = ""
features_store_settings.FEATURES_PATH = ""


def request_with_params(settings, url_path, params):
    return requests.post(
        settings.url + url_path,
        headers=settings.headers,
        params=params
    )


class TestEventsService:

    def test_settings(self):
        assert events_store_settings.url == 'http://localhost:8020/'

    def test_put_method(self):
        for i in range(20):
            params = {"user_id": 1337055, "item_id": 1000+i}
            resp = request_with_params(events_store_settings, "put", params)
            assert resp.status_code == 200
            recs = resp.json()
            assert recs == {'result': 'ok'}

    def test_get_method(self):
        params = {"user_id": 1337055}
        resp = request_with_params(events_store_settings, "get", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'events': [1019, 1018, 1017, 1016, 1015, 1014, 1013, 1012, 1011, 1010]}
    
    def test_get_method_with_param(self):
        params = {"user_id": 1337055, "k": 3}
        resp = request_with_params(events_store_settings, "get", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'events': [1019, 1018, 1017]}


class TestFeaturesService:

    def test_settings(self):
        assert features_store_settings.url == 'http://localhost:8010/'

    def test_good_item(self):
        params = {"item_id": 33311009, 'k': 3}
        resp = request_with_params(features_store_settings, "similar_items", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'sim_item_id': [34976783, 42197229, 29544272], 'score': [0.9326101541519165, 0.8953233361244202, 0.8548532128334045]}

    def test_bad_item(self):
        params = {"item_id": 1, 'k': 3}
        resp = request_with_params(features_store_settings, "similar_items", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'sim_item_id': [], 'score': {}}


class TestRecommendationService:

    def test_personal_answer_offline(self):
        params = {"user_id": 1359367, 'k': 5}
        resp = request_with_params(recommendation_settings, "recommendations_offline", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'recs': [14235025, 51516485, 40548548, 257150, 23330779]}

    def test_default_answer_offline(self):
        params = {"user_id": 2_000_000, 'k': 3}
        resp = request_with_params(recommendation_settings, "recommendations_offline", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'recs': [60292250, 65851540, 33311009]}

        params = {"user_id": 2_000_001, 'k': 3}
        resp = request_with_params(recommendation_settings, "recommendations_offline", params)
        assert resp.status_code == 200
        recs_2 = resp.json()
        assert recs == recs_2

    def test_empty_answer_online(self):
        params = {"user_id": 100, 'k': 3}
        resp = request_with_params(recommendation_settings, "recommendations_online", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'recs': []}

    def test_add_events(self):
        params = {"user_id": 1291248, "item_id": 33311009}
        resp = request_with_params(events_store_settings, "put", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'result': 'ok'}

    def test_good_answer_online(self):
        params = {"user_id": 1291248, 'k': 2}
        resp = request_with_params(recommendation_settings, "recommendations_online", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'recs': [34976783, 42197229]}

    def test_good_answer_online_with_events(self):
        user_id = 1291248
        event_item_ids = [65851540, 45499814, 57921154, 35505245]
        for event_item_id in event_item_ids:
            params={"user_id": user_id, "item_id": event_item_id}
            resp = request_with_params(events_store_settings, "put", params)
        
        params = {"user_id": user_id, 'k': 7}
        resp = request_with_params(recommendation_settings, "recommendations_online", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'recs': [39946957, 49961817, 51452575, 56920241, 45130892, 54798445, 48801315]}

    def test_both_offline_online(self):
        user_id = 1291250
        event_item_ids = [178529, 328683, 37384]
        for event_item_id in event_item_ids:
            params={"user_id": user_id, "item_id": event_item_id}
            resp = request_with_params(events_store_settings, "put", params)
        
        params = {"user_id": 1291250, 'k': 10}
        resp = request_with_params(recommendation_settings, "recommendations", params)
        assert resp.status_code == 200
        recs = resp.json()
        assert recs == {'recs': [178495, 34071554, 170252, 29674911, 34608, 31315099, 328683, 30380200, 178529, 582507]}
