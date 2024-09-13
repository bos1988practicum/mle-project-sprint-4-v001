# Подготовка виртуальной машины

## Склонируйте репозиторий

Склонируйте репозиторий проекта:

```
git clone https://github.com/yandex-praktikum/mle-project-sprint-4-v001.git
```

## Активируйте виртуальное окружение

Используйте то же самое виртуальное окружение, что и созданное для работы с уроками. Если его не существует, то его следует создать.

Создать новое виртуальное окружение можно командой:

```
$ python3.10 -m venv .env_recsys_start
```

После его инициализации следующей командой

```
$ source .env_recsys_start/bin/activate
```

установите в него необходимые Python-пакеты следующей командой

```
$ pip install -r requirements.txt
```

### Скачайте файлы с данными

Для начала работы понадобится три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Скачайте их в директорию локального репозитория. Для удобства вы можете воспользоваться командой wget:

```
wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet

wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet

wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet
```

## Запустите Jupyter Lab

Запустите Jupyter Lab в командной строке

```
jupyter lab --ip=0.0.0.0 --no-browser
```

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`. Изначально, это шаблон. Используйте его для выполнения первой части проекта.

# Сервис рекомендаций

**Стратегия смешивания онлайн- и офлайн-рекомендаций:**
- онлайн-рекомендации занимают нечётные места,
- офлайн-рекомендации занимают чётные места.

---

Подготовленные файлы с рекомендациями находятся в S3:

```
S3_BUCKET_NAME=s3-student-mle-20240525-e85d25cb1f
```

Пути к подготовленным фалам:

```
recsys/data/items.parquet
recsys/data/id_dict_items.parquet
recsys/data/id_dict_users.parquet
recsys/recommendations/recommendations.parquet
recsys/recommendations/similar.parquet
recsys/recommendations/top_popular.parquet
```

- Код сервиса событий находится в файле `events_service.py`.
- Код сервиса похожих объектов находится в файле `features_service.py`.
- Код сервиса рекомендаций находится в файле `recommendations_service.py`.

Запуск сервиса событий
```bash
$ uvicorn events_service:app --port 8020
```

Запуск сервиса похожих объектов
```bash
$ uvicorn features_service:app --port 8010
```

Запуск сервиса рекомендаций
```bash
$ uvicorn recommendation_service:app 
```

# Инструкции для тестирования сервиса

## Ручные тесты

- Код для тестирования сервиса событий находится в файле `tests/manual/manual_test_service_events.py`.
- Код для тестирования сервиса похожих объектов находится в файле `tests/manual/manual_test_service_features.py`.
- Код для тестирования сервиса рекомендаций находится в файле `tests/manual/manual_test_service.py`.

Тест сервиса событий
```bash
$ python -m tests.manual.manual_test_service_events
```

Тест сервиса похожих объектов
```bash
$ python -m tests.manual.manual_test_service_features
```

Тест сервиса рекомендаций
```bash
$ python -m tests.manual.manual_test_service
```

Лог из `manual_test_service.py` в файле `tests/manual/manual_test_service.log`

Ключевые тесты:

- для пользователя с персональными рекомендациями, но без онлайн-истории:
  - ***test 1 (personal answer offline)***
- для пользователя без персональных рекомендаций:
  - ***test 2 (default answer offline)***
- для пользователя с персональными рекомендациями и онлайн-историей:
  - ***test 7 (online + offline)***

## Автотесты

Запуск тестов
```bash
$ python -m pytest -vv --cov
```

Запуск тестов с записью резльтатов в файл
```bash
python -m pytest -vv --cov > tests/test_service.log
```
