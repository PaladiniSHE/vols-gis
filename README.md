# Vols GIS - Система учета ВОЛС

Минималистичный аналог NextGIS Web для учета волоконно-оптических линий связи (ВОЛС).

## Описание проекта

Vols GIS - это веб-приложение для управления и учета волоконно-оптических сетей связи. Система позволяет:
- Отслеживать узлы связи на карте
- Создавать и редактировать маршруты ВОЛС
- Управлять волокнами и связями
- Визуализировать сетевую инфраструктуру на интерактивной карте

## Технологии

- **Backend**: Python 3.x, Pyramid Framework, SQLAlchemy, PostgreSQL/PostGIS
- **Frontend**: JavaScript (ES6+), OpenLayers 8.2, Bootstrap 5.3.0
- **Database**: PostgreSQL 12+ с расширением PostGIS

## Структура проекта

```
vols-gis/
├── backend/          # Backend приложение (Pyramid)
│   ├── vols_gis/    # Основной пакет приложения
│   ├── development.ini
│   └── run_server.py
└── frontend/         # Frontend приложение
    ├── index.html
    ├── js/          # JavaScript модули
    └── css/         # Стили
```

## Установка и запуск

### Требования

- Python 3.8+
- PostgreSQL 12+ с PostGIS
- Node.js (опционально, для разработки)

### Установка зависимостей

```bash
cd backend
pip install -e .
```

### Настройка базы данных

1. Создайте базу данных PostgreSQL:
```sql
CREATE DATABASE vols_gis;
CREATE EXTENSION postgis;
```

2. Обновите настройки подключения в `backend/development.ini`:
```ini
sqlalchemy.url = postgresql://user:password@localhost:5433/vols_gis
```

3. Инициализируйте таблицы:
```bash
python init_db.py
```

### Запуск сервера

```bash
cd backend
python run_server.py
```

Сервер будет доступен по адресу: http://localhost:6543

## API Endpoints

- `GET /api/nodes` - Список узлов
- `POST /api/nodes` - Создание узла
- `GET /api/vols` - Список маршрутов ВОЛС
- `POST /api/vols` - Создание маршрута
- `GET /api/fibers` - Список волокон
- `POST /api/fibers` - Создание волокна
- `GET /api/links` - Список связей
- `POST /api/links` - Создание связи

## Разработка

### Структура кода

- `vols_gis/models/` - SQLAlchemy модели данных
- `vols_gis/views/` - API views (контроллеры)
- `vols_gis/schemas/` - Pydantic схемы валидации
- `vols_gis/middleware/` - Middleware (CORS, DB session)
- `frontend/js/` - Frontend JavaScript модули

### Логирование

Логи настраиваются в `development.ini`. Уровень логирования: DEBUG для разработки.

## Лицензия

Проект разработан для внутреннего использования.

## Автор

ShutovAV


