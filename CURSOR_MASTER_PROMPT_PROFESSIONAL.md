# 🚀 Master Prompt: Доработка VOLS-GIS до профессионального решения

## Для использования в Cursor AI

---

## 📋 КОНТЕКСТ ПРОЕКТА

Ты работаешь над проектом **VOLS-GIS** — системой учета волоконно-оптических линий связи (ВОЛС) для ГАУ ТО ТРТЦ (Тюменская область).

### Текущее состояние проекта (MVP):

```
vols-gis/
├── backend/                    # Python + Pyramid Framework
│   ├── vols_gis/
│   │   ├── models/            # SQLAlchemy модели (Node, Vols, Fiber, Link, User, WebMap)
│   │   ├── views/             # REST API endpoints
│   │   ├── schemas/           # Pydantic схемы валидации
│   │   ├── auth/              # JWT авторизация
│   │   └── middleware/        # CORS
│   ├── development.ini        # Конфигурация Pyramid
│   └── docker-compose.yml     # PostgreSQL + PostGIS
├── frontend/                   # Vanilla JS + OpenLayers + Bootstrap
│   ├── js/
│   │   ├── map.js            # Управление картой OpenLayers
│   │   ├── api.js            # REST API клиент
│   │   ├── ui.js             # UI компоненты
│   │   └── app.js            # Главное приложение
│   └── index.html            # Единственная HTML страница (SPA)
└── init-db.sql               # Схема БД
```

### Технологический стек:
- **Backend**: Python 3.11, Pyramid 2.0, SQLAlchemy 2.0, GeoAlchemy2, Pydantic
- **Database**: PostgreSQL 15 + PostGIS 3.3
- **Frontend**: OpenLayers 8.2, Bootstrap 5.3, Vanilla JavaScript
- **Auth**: JWT токены
- **Deploy**: Docker Compose

### Что уже реализовано:
✅ Базовые модели данных (Nodes, VOLS, Fibers, Links, Users, WebMaps)
✅ CRUD операции для всех сущностей
✅ JWT авторизация
✅ Интерактивная карта OpenLayers
✅ Рисование узлов и маршрутов на карте
✅ Экспорт в GeoJSON и CSV
✅ Поиск и фильтрация
✅ Docker Compose для PostgreSQL

---

## 🎯 ЦЕЛЬ ДОРАБОТКИ

Превратить MVP в **профессиональное решение операторского класса** для учета инфраструктуры ВОЛС, сравнимое по функциональности с TACL Pro и NextGIS Web.

---

## 📊 ПРИОРИТЕТНЫЕ ЗАДАЧИ ДОРАБОТКИ

### 🔴 КРИТИЧЕСКИЕ (Неделя 1-2)

#### 1. Учет кабельной инфраструктуры

```python
# Новые модели для backend/vols_gis/models/

# cables.py - Кабели ВОЛС
class Cable(BaseModel):
    __tablename__ = 'cables'
    
    name = Column(String(255), nullable=False)          # Название кабеля
    cable_mark = Column(String(100))                    # Марка (ОКСН-М-24, ДПТ-П-48 и т.д.)
    fiber_count = Column(Integer, nullable=False)       # Количество волокон
    construction_year = Column(Integer)                 # Год прокладки
    owner = Column(String(255))                         # Собственник
    vols_id = Column(Integer, ForeignKey('vols.id'))   # Привязка к маршруту
    length_m = Column(Numeric(12, 2))                   # Длина в метрах
    status = Column(String(50))                         # active, damaged, reserved
    laying_method = Column(String(50))                  # ground, aerial, duct, underwater
    
# splice_closures.py - Муфты
class SpliceClosure(BaseModel):
    __tablename__ = 'splice_closures'
    
    name = Column(String(255), nullable=False)
    closure_type = Column(String(50))                   # МТОК, МОПГ, МОСН и т.д.
    capacity = Column(Integer)                          # Емкость (кол-во сварок)
    node_id = Column(Integer, ForeignKey('nodes.id'))  # Привязка к узлу
    geom = Column(Geometry('POINT', srid=4326))
    installation_date = Column(Date)
    status = Column(String(50))
    
# splices.py - Сварки волокон
class Splice(BaseModel):
    __tablename__ = 'splices'
    
    closure_id = Column(Integer, ForeignKey('splice_closures.id'))
    fiber_in_id = Column(Integer, ForeignKey('fibers.id'))   # Входящее волокно
    fiber_out_id = Column(Integer, ForeignKey('fibers.id'))  # Исходящее волокно
    tube_in = Column(Integer)                                 # № модуля входящего
    tube_out = Column(Integer)                                # № модуля исходящего
    fiber_color_in = Column(String(50))                       # Цвет волокна входящего
    fiber_color_out = Column(String(50))                      # Цвет волокна исходящего
    loss_db = Column(Numeric(5, 3))                           # Потери на сварке (дБ)
    splice_date = Column(Date)
    status = Column(String(50))                               # good, attention, bad
    
# odf.py - Оптические кроссы
class ODF(BaseModel):
    __tablename__ = 'odfs'
    
    name = Column(String(255), nullable=False)
    odf_type = Column(String(100))                      # Тип кросса
    port_count = Column(Integer)                        # Количество портов
    node_id = Column(Integer, ForeignKey('nodes.id'))
    rack_position = Column(String(50))                  # Позиция в стойке
    status = Column(String(50))
    
# odf_ports.py - Порты кросса
class ODFPort(BaseModel):
    __tablename__ = 'odf_ports'
    
    odf_id = Column(Integer, ForeignKey('odfs.id'))
    port_number = Column(Integer, nullable=False)
    fiber_id = Column(Integer, ForeignKey('fibers.id'))
    connector_type = Column(String(50))                 # SC, LC, FC
    status = Column(String(50))                         # used, free, reserved
    client_name = Column(String(255))                   # Название клиента/услуги
```

#### 2. Схема сварок (Splice Schema)

```javascript
// frontend/js/splice-schema.js - Визуализация схемы сварок

class SpliceSchemaViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.canvas = null;
        this.ctx = null;
    }
    
    // Отрисовка схемы муфты с волокнами
    renderClosure(closureData, splices) {
        // Отображение:
        // - Входящие кабели слева
        // - Муфта в центре
        // - Исходящие кабели справа
        // - Линии сварок с цветовой кодировкой
    }
    
    // Интерактивное редактирование сварок
    enableSpliceEditing() {
        // Drag & drop для создания сварок
        // Цветовая маркировка модулей и волокон
    }
}
```

#### 3. Учет волокон по цветам

```python
# Стандартные цвета волокон по ГОСТ
FIBER_COLORS = {
    1: 'blue',      # Синий
    2: 'orange',    # Оранжевый
    3: 'green',     # Зеленый
    4: 'brown',     # Коричневый
    5: 'gray',      # Серый
    6: 'white',     # Белый
    7: 'red',       # Красный
    8: 'black',     # Черный
    9: 'yellow',    # Желтый
    10: 'violet',   # Фиолетовый
    11: 'pink',     # Розовый
    12: 'aqua',     # Бирюзовый
}

# Модули (tubes) в кабеле тоже имеют цвета
TUBE_COLORS = FIBER_COLORS  # Обычно те же цвета
```

---

### 🟠 ВЫСОКИЙ ПРИОРИТЕТ (Неделя 2-3)

#### 4. Расширенная модель узлов

```python
# Типы узлов связи для ВОЛС
NODE_TYPES = {
    'aps': 'АПС (Автоматическая пожарная станция)',
    'pop': 'POP (Point of Presence)',
    'nap': 'NAP (Network Access Point)',
    'manhole': 'Колодец',
    'pole': 'Опора',
    'building': 'Здание',
    'closure': 'Муфта в грунте',
    'cabinet': 'Шкаф уличный',
    'datacenter': 'ЦОД',
    'bsp': 'БСП (Базовая станция провайдера)',
    'exchange': 'АТС',
}

# Расширенная модель узла
class Node(BaseModel):
    # ... существующие поля ...
    
    # Новые поля
    address = Column(Text)                              # Адрес
    cadastral_number = Column(String(50))               # Кадастровый номер
    owner = Column(String(255))                         # Собственник
    access_info = Column(Text)                          # Информация о доступе
    contact_person = Column(String(255))                # Контактное лицо
    contact_phone = Column(String(50))                  # Телефон
    power_available = Column(Boolean, default=False)    # Наличие электричества
    climate_control = Column(Boolean, default=False)    # Климат-контроль
    security_level = Column(String(50))                 # Уровень безопасности
    photos = Column(JSON)                               # Массив URL фотографий
```

#### 5. Трассировка маршрутов (Path Tracing)

```python
# backend/vols_gis/services/path_tracing.py

class PathTracingService:
    """Сервис для построения маршрутов и расчета оптического бюджета"""
    
    def trace_path(self, start_node_id: int, end_node_id: int) -> dict:
        """
        Построить путь между двумя узлами через все промежуточные элементы
        
        Возвращает:
        - Список узлов на пути
        - Список сегментов ВОЛС
        - Суммарную длину
        - Список муфт на пути
        - Оптический бюджет
        """
        pass
    
    def calculate_optical_budget(self, path: list) -> dict:
        """
        Расчет оптического бюджета на маршруте
        
        Учитывает:
        - Потери в волокне (0.35 дБ/км для 1310нм, 0.22 дБ/км для 1550нм)
        - Потери на сварках (0.05-0.1 дБ)
        - Потери на разъемах (0.3-0.5 дБ)
        - Запас на деградацию (3 дБ)
        """
        pass
    
    def find_alternative_paths(self, start_node_id: int, end_node_id: int, count: int = 3):
        """Найти альтернативные маршруты для резервирования"""
        pass
```

#### 6. История изменений (Audit Log)

```python
# backend/vols_gis/models/audit.py

class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'
    
    entity_type = Column(String(50), nullable=False)    # node, vols, fiber, splice
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)         # create, update, delete
    user_id = Column(Integer, ForeignKey('users.id'))
    old_values = Column(JSON)                           # Старые значения
    new_values = Column(JSON)                           # Новые значения
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

# Декоратор для автоматического логирования
def auditable(entity_type: str):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Логируем изменения
            pass
        return wrapper
    return decorator
```

---

### 🟡 СРЕДНИЙ ПРИОРИТЕТ (Неделя 3-4)

#### 7. Импорт данных

```python
# backend/vols_gis/services/import_service.py

class ImportService:
    """Сервис импорта данных из различных форматов"""
    
    def import_from_csv(self, file_path: str, entity_type: str) -> dict:
        """Импорт из CSV файла"""
        pass
    
    def import_from_geojson(self, file_path: str, entity_type: str) -> dict:
        """Импорт из GeoJSON"""
        pass
    
    def import_from_shapefile(self, file_path: str, entity_type: str) -> dict:
        """Импорт из Shapefile"""
        pass
    
    def import_from_kml(self, file_path: str, entity_type: str) -> dict:
        """Импорт из KML/KMZ"""
        pass
    
    def import_from_excel(self, file_path: str, mapping: dict) -> dict:
        """Импорт из Excel с маппингом колонок"""
        pass
```

#### 8. Расширенный экспорт

```python
# backend/vols_gis/services/export_service.py

class ExportService:
    """Расширенный сервис экспорта"""
    
    def export_to_shapefile(self, layer: str, filters: dict = None) -> bytes:
        """Экспорт в Shapefile (ZIP архив)"""
        pass
    
    def export_to_dxf(self, layer: str) -> bytes:
        """Экспорт в DXF для AutoCAD"""
        pass
    
    def export_to_kml(self, layer: str) -> str:
        """Экспорт в KML для Google Earth"""
        pass
    
    def export_splice_schema(self, closure_id: int, format: str = 'pdf') -> bytes:
        """Экспорт схемы сварок в PDF/SVG"""
        pass
    
    def generate_report(self, report_type: str, params: dict) -> bytes:
        """
        Генерация отчетов:
        - Инвентаризационная ведомость
        - Паспорт кабельной линии
        - Схема организации связи
        - Акт выполненных работ
        """
        pass
```

#### 9. Улучшенный Frontend

```javascript
// frontend/js/components/

// Дерево объектов (иерархическая навигация)
class ObjectTree {
    constructor(containerId) {
        // Иерархия: Регион -> Район -> Населенный пункт -> Узел -> Оборудование
    }
    
    loadTree(data) { }
    expandNode(nodeId) { }
    selectNode(nodeId) { }
}

// Таблица с сортировкой и пагинацией
class DataTable {
    constructor(containerId, columns, data) {
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.page = 1;
        this.pageSize = 50;
    }
    
    render() { }
    sort(column) { }
    filter(filters) { }
    paginate(page) { }
}

// Форма с валидацией
class SmartForm {
    constructor(formId, schema) {
        this.schema = schema;  // Pydantic-like schema
    }
    
    validate() { }
    getValues() { }
    setValues(data) { }
    showErrors(errors) { }
}

// Уведомления
class NotificationManager {
    success(message) { }
    error(message) { }
    warning(message) { }
    info(message) { }
}
```

---

### 🟢 ЖЕЛАТЕЛЬНО (Неделя 4+)

#### 10. Мониторинг и интеграции

```python
# backend/vols_gis/integrations/

# Интеграция с OTDR (рефлектометр)
class OTDRIntegration:
    def import_trace(self, file_path: str) -> dict:
        """Импорт трассы рефлектометра (.sor, .trc)"""
        pass
    
    def analyze_events(self, trace_data: dict) -> list:
        """Анализ событий на трассе (сварки, разъемы, обрывы)"""
        pass

# Интеграция с мониторингом
class MonitoringIntegration:
    def get_alarms(self) -> list:
        """Получить активные аварии"""
        pass
    
    def get_device_status(self, device_id: str) -> dict:
        """Статус активного оборудования"""
        pass
```

#### 11. Мобильное приложение (PWA)

```javascript
// Прогрессивное веб-приложение для полевых работ

// service-worker.js
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('vols-gis-v1').then((cache) => {
            return cache.addAll([
                '/',
                '/static/css/style.css',
                '/static/js/app.js',
                // Offline tiles
            ]);
        })
    );
});

// Offline-first стратегия
// Синхронизация при появлении сети
```

#### 12. Разграничение доступа (RBAC)

```python
# backend/vols_gis/auth/rbac.py

PERMISSIONS = {
    'nodes': ['view', 'create', 'edit', 'delete'],
    'vols': ['view', 'create', 'edit', 'delete'],
    'fibers': ['view', 'create', 'edit', 'delete'],
    'splices': ['view', 'create', 'edit', 'delete'],
    'reports': ['view', 'export'],
    'users': ['view', 'manage'],
    'settings': ['view', 'edit'],
}

ROLES = {
    'admin': {
        'description': 'Полный доступ',
        'permissions': ['*']
    },
    'engineer': {
        'description': 'Инженер ВОЛС',
        'permissions': [
            'nodes:*', 'vols:*', 'fibers:*', 'splices:*',
            'reports:view', 'reports:export'
        ]
    },
    'operator': {
        'description': 'Оператор',
        'permissions': [
            'nodes:view', 'vols:view', 'fibers:view',
            'reports:view'
        ]
    },
    'viewer': {
        'description': 'Только просмотр',
        'permissions': ['*:view']
    }
}
```

---

## 📐 СТАНДАРТЫ КОДА

### Python (Backend)

```python
# Используй type hints везде
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class NodeCreate(BaseModel):
    """Схема создания узла"""
    name: str = Field(..., min_length=1, max_length=255)
    node_type: str = Field(..., regex='^(aps|pop|nap|manhole|pole|building)$')
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    status: Optional[str] = Field(default='active')
    
    class Config:
        schema_extra = {
            "example": {
                "name": "АПС-001 Тюмень",
                "node_type": "aps",
                "lat": 57.1522,
                "lon": 65.5272,
                "status": "active"
            }
        }

# Логирование
import logging
logger = logging.getLogger(__name__)

def some_function():
    logger.info("Выполняется операция", extra={"user_id": 1, "action": "create"})

# Обработка ошибок
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound

def get_node(request):
    try:
        node_id = int(request.matchdict['id'])
    except ValueError:
        raise HTTPBadRequest(json_body={'error': 'Invalid node ID'})
    
    node = request.db.query(Node).get(node_id)
    if not node:
        raise HTTPNotFound(json_body={'error': 'Node not found'})
    
    return node
```

### JavaScript (Frontend)

```javascript
// Используй JSDoc для документации
/**
 * Создает новый узел на карте
 * @param {number} lat - Широта
 * @param {number} lon - Долгота
 * @param {Object} options - Опции узла
 * @param {string} options.name - Название
 * @param {string} options.type - Тип узла
 * @returns {Promise<Object>} Созданный узел
 */
async function createNode(lat, lon, options = {}) {
    const response = await api.post('/api/nodes', {
        lat,
        lon,
        name: options.name || 'Новый узел',
        node_type: options.type || 'pop'
    });
    return response.node;
}

// Используй async/await вместо callbacks
// Обрабатывай ошибки
try {
    const node = await createNode(57.15, 65.52, { name: 'АПС-001' });
    notification.success('Узел создан');
} catch (error) {
    notification.error(`Ошибка: ${error.message}`);
    logger.error('Ошибка создания узла', error);
}
```

### SQL

```sql
-- Используй миграции (Alembic)
-- alembic/versions/001_add_cables_table.py

def upgrade():
    op.create_table(
        'cables',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('cable_mark', sa.String(100)),
        sa.Column('fiber_count', sa.Integer(), nullable=False),
        sa.Column('vols_id', sa.Integer(), sa.ForeignKey('vols.id')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    
    op.create_index('idx_cables_vols_id', 'cables', ['vols_id'])

def downgrade():
    op.drop_table('cables')
```

---

## 🧪 ТЕСТИРОВАНИЕ

```python
# tests/test_nodes.py

import pytest
from vols_gis.models import Node

class TestNodesAPI:
    
    def test_create_node(self, test_client, db_session):
        """Тест создания узла"""
        response = test_client.post('/api/nodes', json={
            'name': 'Test Node',
            'node_type': 'pop',
            'lat': 57.15,
            'lon': 65.52
        })
        
        assert response.status_code == 201
        assert response.json['node']['name'] == 'Test Node'
    
    def test_create_node_invalid_coords(self, test_client):
        """Тест валидации координат"""
        response = test_client.post('/api/nodes', json={
            'name': 'Test',
            'lat': 200,  # Invalid
            'lon': 65
        })
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_get_nodes_with_filter(self, test_client, db_session):
        """Тест фильтрации узлов"""
        # Создаем тестовые данные
        # ...
        
        response = test_client.get('/api/nodes?node_type=pop&status=active')
        
        assert response.status_code == 200
        for node in response.json['nodes']:
            assert node['node_type'] == 'pop'
            assert node['status'] == 'active'
```

---

## 📁 СТРУКТУРА ФАЙЛОВ (после доработки)

```
vols-gis/
├── backend/
│   ├── vols_gis/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── nodes.py          # ✅ Существует
│   │   │   ├── vols.py           # ✅ Существует
│   │   │   ├── fibers.py         # ✅ Существует
│   │   │   ├── links.py          # ✅ Существует
│   │   │   ├── users.py          # ✅ Существует
│   │   │   ├── webmaps.py        # ✅ Существует
│   │   │   ├── cables.py         # 🆕 ДОБАВИТЬ
│   │   │   ├── splice_closures.py # 🆕 ДОБАВИТЬ
│   │   │   ├── splices.py        # 🆕 ДОБАВИТЬ
│   │   │   ├── odfs.py           # 🆕 ДОБАВИТЬ
│   │   │   ├── odf_ports.py      # 🆕 ДОБАВИТЬ
│   │   │   └── audit.py          # 🆕 ДОБАВИТЬ
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── nodes.py          # ✅ Существует
│   │   │   ├── vols.py           # ✅ Существует
│   │   │   ├── fibers.py         # ✅ Существует
│   │   │   ├── links.py          # ✅ Существует
│   │   │   ├── cables.py         # 🆕 ДОБАВИТЬ
│   │   │   ├── splices.py        # 🆕 ДОБАВИТЬ
│   │   │   ├── odfs.py           # 🆕 ДОБАВИТЬ
│   │   │   ├── import_export.py  # 🆕 ДОБАВИТЬ
│   │   │   └── reports.py        # 🆕 ДОБАВИТЬ
│   │   ├── services/
│   │   │   ├── __init__.py       # 🆕 ДОБАВИТЬ
│   │   │   ├── path_tracing.py   # 🆕 ДОБАВИТЬ
│   │   │   ├── optical_budget.py # 🆕 ДОБАВИТЬ
│   │   │   ├── import_service.py # 🆕 ДОБАВИТЬ
│   │   │   └── export_service.py # 🆕 ДОБАВИТЬ
│   │   ├── integrations/
│   │   │   ├── __init__.py       # 🆕 ДОБАВИТЬ
│   │   │   └── otdr.py           # 🆕 ДОБАВИТЬ (опционально)
│   │   ├── schemas/              # ✅ Существует, расширить
│   │   ├── auth/                 # ✅ Существует, расширить RBAC
│   │   └── middleware/           # ✅ Существует
│   ├── alembic/                  # 🆕 ДОБАВИТЬ (миграции)
│   │   ├── versions/
│   │   └── alembic.ini
│   ├── tests/                    # 🆕 ДОБАВИТЬ
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_nodes.py
│   │   ├── test_vols.py
│   │   └── test_splices.py
│   └── requirements.txt          # Обновить
├── frontend/
│   ├── index.html                # ✅ Существует, расширить
│   ├── css/
│   │   └── style.css             # ✅ Существует, расширить
│   └── js/
│       ├── api.js                # ✅ Существует, расширить
│       ├── app.js                # ✅ Существует
│       ├── map.js                # ✅ Существует, расширить
│       ├── ui.js                 # ✅ Существует, расширить
│       ├── splice-schema.js      # 🆕 ДОБАВИТЬ
│       ├── data-table.js         # 🆕 ДОБАВИТЬ
│       ├── object-tree.js        # 🆕 ДОБАВИТЬ
│       └── reports.js            # 🆕 ДОБАВИТЬ
├── docs/
│   ├── api.md                    # 🆕 ДОБАВИТЬ
│   ├── user-guide.md             # 🆕 ДОБАВИТЬ
│   └── admin-guide.md            # 🆕 ДОБАВИТЬ
└── docker-compose.yml            # ✅ Существует
```

---

## 🔧 КОМАНДЫ ДЛЯ РАЗРАБОТКИ

```bash
# Установка зависимостей
cd backend
pip install -e ".[dev]"

# Запуск миграций
alembic upgrade head

# Запуск сервера разработки
python run_server.py

# Запуск тестов
pytest -v --cov=vols_gis

# Проверка типов
mypy vols_gis/

# Форматирование кода
black vols_gis/
isort vols_gis/

# Docker
docker-compose up -d
```

---

## 📌 ВАЖНЫЕ ЗАМЕЧАНИЯ

### При работе с картой OpenLayers:
```javascript
// Координаты всегда в формате [lon, lat] (не [lat, lon]!)
// При конвертации из API учитывай это
const coordinates = ol.proj.fromLonLat([lon, lat]);
```

### При работе с PostGIS:
```python
# Используй ST_Transform для конвертации между системами координат
# EPSG:4326 - WGS84 (lat/lon)
# EPSG:3857 - Web Mercator (для карт)

from sqlalchemy import func

# Создание точки
point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)

# Расчет расстояния в метрах
distance = func.ST_DistanceSphere(geom1, geom2)

# Поиск в радиусе
query.filter(func.ST_DWithin(
    func.ST_Transform(Node.geom, 3857),
    func.ST_Transform(point, 3857),
    distance_meters
))
```

### При работе с JSON в PostgreSQL:
```python
# Используй JSONB для индексируемых JSON полей
from sqlalchemy.dialects.postgresql import JSONB

meta_data = Column(JSONB)

# Запрос по JSON полям
query.filter(Node.meta_data['status'].astext == 'active')
```

---

## 🚀 ПРИСТУПАЙ К РАБОТЕ!

Начни с задачи **#1 Учет кабельной инфраструктуры**:

1. Создай модели `Cable`, `SpliceClosure`, `Splice` в `backend/vols_gis/models/`
2. Добавь Pydantic схемы в `backend/vols_gis/schemas/`
3. Создай REST API views в `backend/vols_gis/views/`
4. Обнови маршруты в `backend/vols_gis/routes.py`
5. Добавь UI компоненты во frontend

При возникновении вопросов запроси уточнение!
