# 📋 Дорожная карта разработки VOLS-GIS

## Пошаговый план доработки до профессионального решения

---

## 🎯 Фаза 1: Кабельная инфраструктура (1-2 недели)

### Неделя 1: Backend

- [ ] **Task 1.1**: Создать модель `Cable` (кабели ВОЛС)
  ```
  Файл: backend/vols_gis/models/cables.py
  Поля: name, cable_mark, fiber_count, construction_year, owner, vols_id, length_m, status, laying_method
  ```

- [ ] **Task 1.2**: Создать модель `SpliceClosure` (муфты)
  ```
  Файл: backend/vols_gis/models/splice_closures.py
  Поля: name, closure_type, capacity, node_id, geom, installation_date, status
  ```

- [ ] **Task 1.3**: Создать модель `Splice` (сварки волокон)
  ```
  Файл: backend/vols_gis/models/splices.py
  Поля: closure_id, fiber_in_id, fiber_out_id, tube_in/out, fiber_color_in/out, loss_db, status
  ```

- [ ] **Task 1.4**: Создать модели ODF и ODFPort (кроссы)
  ```
  Файлы: backend/vols_gis/models/odfs.py, odf_ports.py
  ```

- [ ] **Task 1.5**: Создать Pydantic схемы валидации
  ```
  Файлы: backend/vols_gis/schemas/cables.py, splice_closures.py, splices.py, odfs.py
  ```

- [ ] **Task 1.6**: Создать REST API endpoints
  ```
  Файлы: backend/vols_gis/views/cables.py, splice_closures.py, splices.py, odfs.py
  ```

- [ ] **Task 1.7**: Обновить routes.py с новыми маршрутами

### Неделя 2: Frontend

- [ ] **Task 1.8**: Добавить интерфейс управления кабелями
  ```
  Файл: frontend/js/cables.js
  - Список кабелей с фильтрацией
  - Форма создания/редактирования
  - Привязка к маршруту ВОЛС
  ```

- [ ] **Task 1.9**: Добавить интерфейс управления муфтами
  ```
  - Отображение муфт на карте
  - Popup с информацией
  - Форма создания/редактирования
  ```

- [ ] **Task 1.10**: Создать визуализацию схемы сварок
  ```
  Файл: frontend/js/splice-schema.js
  - Canvas/SVG отрисовка схемы муфты
  - Отображение входящих/исходящих кабелей
  - Линии сварок с цветовой кодировкой
  ```

- [ ] **Task 1.11**: Обновить index.html с новыми разделами навигации

---

## 🎯 Фаза 2: Расширенный учет (1 неделя)

- [ ] **Task 2.1**: Расширить модель Node
  ```
  Добавить поля: address, cadastral_number, owner, access_info, 
  contact_person, contact_phone, power_available, climate_control, photos
  ```

- [ ] **Task 2.2**: Добавить цветовую маркировку волокон
  ```
  Константы FIBER_COLORS, TUBE_COLORS
  UI для выбора цвета волокна/модуля
  ```

- [ ] **Task 2.3**: Создать сервис трассировки маршрутов
  ```
  Файл: backend/vols_gis/services/path_tracing.py
  - trace_path(start, end)
  - calculate_optical_budget(path)
  - find_alternative_paths(start, end)
  ```

- [ ] **Task 2.4**: Добавить историю изменений (Audit Log)
  ```
  Файл: backend/vols_gis/models/audit.py
  Автоматическое логирование всех изменений
  ```

- [ ] **Task 2.5**: Создать UI для просмотра истории объекта

---

## 🎯 Фаза 3: Импорт/Экспорт (1 неделя)

- [ ] **Task 3.1**: Создать сервис импорта
  ```
  Файл: backend/vols_gis/services/import_service.py
  Форматы: CSV, GeoJSON, Shapefile, KML, Excel
  ```

- [ ] **Task 3.2**: Расширить сервис экспорта
  ```
  Файл: backend/vols_gis/services/export_service.py
  Добавить: Shapefile, DXF, KML, PDF отчеты
  ```

- [ ] **Task 3.3**: Создать UI для импорта данных
  ```
  - Drag & drop файлов
  - Маппинг колонок
  - Предпросмотр данных
  - Валидация перед импортом
  ```

- [ ] **Task 3.4**: Создать генератор отчетов
  ```
  Типы отчетов:
  - Инвентаризационная ведомость
  - Паспорт кабельной линии
  - Схема организации связи
  - Ведомость сварок
  ```

---

## 🎯 Фаза 4: Улучшения UI/UX (1 неделя)

- [ ] **Task 4.1**: Создать компонент дерева объектов
  ```
  Файл: frontend/js/object-tree.js
  Иерархия: Регион → Район → НП → Узел → Оборудование
  ```

- [ ] **Task 4.2**: Создать компонент таблицы данных
  ```
  Файл: frontend/js/data-table.js
  - Сортировка по колонкам
  - Пагинация
  - Множественный выбор
  - Экспорт выделенных
  ```

- [ ] **Task 4.3**: Улучшить карту
  ```
  - Кластеризация маркеров
  - Разные слои для разных типов объектов
  - Переключатель подложек (OSM, спутник, гибрид)
  - Измерение расстояний
  - Печать карты
  ```

- [ ] **Task 4.4**: Добавить дашборд
  ```
  - Виджеты статистики
  - Графики (протяженность ВОЛС, количество узлов по типам)
  - Последние изменения
  - Активные аварии (если есть интеграция)
  ```

- [ ] **Task 4.5**: Улучшить формы
  ```
  - Автозаполнение (поиск узлов, кабелей)
  - Валидация в реальном времени
  - Зависимые поля (выбор района → НП)
  ```

---

## 🎯 Фаза 5: Безопасность и производительность (1 неделя)

- [ ] **Task 5.1**: Реализовать RBAC
  ```
  Файл: backend/vols_gis/auth/rbac.py
  Роли: admin, engineer, operator, viewer
  ```

- [ ] **Task 5.2**: Добавить кэширование
  ```
  - Redis для сессий и кэша
  - Кэширование списков и статистики
  ```

- [ ] **Task 5.3**: Оптимизировать запросы к БД
  ```
  - Индексы для частых запросов
  - Eager loading связей
  - Пагинация на бэкенде
  ```

- [ ] **Task 5.4**: Добавить rate limiting для API

- [ ] **Task 5.5**: Настроить HTTPS и безопасные cookies

---

## 🎯 Фаза 6: Документация и тестирование (1 неделя)

- [ ] **Task 6.1**: Написать unit-тесты для моделей
- [ ] **Task 6.2**: Написать интеграционные тесты для API
- [ ] **Task 6.3**: Создать OpenAPI/Swagger документацию
- [ ] **Task 6.4**: Написать руководство пользователя
- [ ] **Task 6.5**: Написать руководство администратора
- [ ] **Task 6.6**: Создать видеоинструкции (опционально)

---

## 📊 Оценка трудозатрат

| Фаза | Длительность | Сложность | Приоритет |
|------|--------------|-----------|-----------|
| 1. Кабельная инфраструктура | 2 недели | Высокая | 🔴 Критический |
| 2. Расширенный учет | 1 неделя | Средняя | 🟠 Высокий |
| 3. Импорт/Экспорт | 1 неделя | Средняя | 🟠 Высокий |
| 4. Улучшения UI/UX | 1 неделя | Средняя | 🟡 Средний |
| 5. Безопасность | 1 неделя | Средняя | 🟠 Высокий |
| 6. Документация | 1 неделя | Низкая | 🟢 Желательно |

**Итого**: 7-8 недель до полноценного профессионального решения

---

## 🚀 Быстрый старт

### Начни с Task 1.1:

```bash
# 1. Создай файл модели
touch backend/vols_gis/models/cables.py

# 2. Реализуй модель Cable (см. CURSOR_MASTER_PROMPT_PROFESSIONAL.md)

# 3. Добавь импорт в __init__.py
echo "from .cables import Cable" >> backend/vols_gis/models/__init__.py

# 4. Создай миграцию (если используешь Alembic)
alembic revision --autogenerate -m "add_cables_table"
alembic upgrade head

# 5. Протестируй через API
curl -X POST http://localhost:6543/api/cables \
  -H "Content-Type: application/json" \
  -d '{"name": "Тюмень-Тобольск", "cable_mark": "ОКСН-М-48", "fiber_count": 48}'
```

---

## 📝 Шаблоны для разработки

### Шаблон модели SQLAlchemy

```python
# backend/vols_gis/models/NEW_MODEL.py

from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel


class NewModel(BaseModel):
    """Описание модели"""
    __tablename__ = 'new_models'
    
    name = Column(String(255), nullable=False)
    # ... другие поля
    
    # Связи
    # parent = relationship("Parent", back_populates="children")
    
    def to_dict(self):
        """Сериализация в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            # ...
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
```

### Шаблон Pydantic схемы

```python
# backend/vols_gis/schemas/NEW_MODEL.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NewModelCreate(BaseModel):
    """Схема создания"""
    name: str = Field(..., min_length=1, max_length=255)
    # ... другие поля


class NewModelUpdate(BaseModel):
    """Схема обновления"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    # ... другие поля


class NewModelResponse(BaseModel):
    """Схема ответа"""
    id: int
    name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True
```

### Шаблон View (API endpoint)

```python
# backend/vols_gis/views/NEW_MODEL.py

from pyramid.view import view_config
from pyramid.response import Response
from ..models.new_model import NewModel
from ..schemas.new_model import NewModelCreate, NewModelUpdate


@view_config(route_name='api_new_models_list', request_method='GET')
def list_items(request):
    """Список объектов"""
    db = request.db
    items = db.query(NewModel).all()
    return Response(
        json_body={'items': [i.to_dict() for i in items], 'count': len(items)},
        content_type='application/json'
    )


@view_config(route_name='api_new_models_list', request_method='POST')
def create_item(request):
    """Создание объекта"""
    try:
        data = request.json_body
        schema = NewModelCreate(**data)
        
        db = request.db
        item = NewModel(**schema.dict())
        db.add(item)
        db.commit()
        
        return Response(
            json_body={'item': item.to_dict()},
            status=201,
            content_type='application/json'
        )
    except Exception as e:
        request.db.rollback()
        return Response(
            json_body={'error': str(e)},
            status=400,
            content_type='application/json'
        )
```

---

## ✅ Чек-лист готовности к продакшену

### Backend
- [ ] Все модели созданы и протестированы
- [ ] Все API endpoints работают корректно
- [ ] Валидация входных данных
- [ ] Обработка ошибок
- [ ] Логирование
- [ ] Авторизация и права доступа
- [ ] Миграции БД
- [ ] Unit-тесты (покрытие > 70%)

### Frontend
- [ ] Все CRUD операции работают
- [ ] Валидация форм
- [ ] Обработка ошибок
- [ ] Адаптивный дизайн
- [ ] Кросс-браузерность

### Инфраструктура
- [ ] Docker Compose для development
- [ ] Dockerfile для production
- [ ] HTTPS настроен
- [ ] Бэкапы БД настроены
- [ ] Мониторинг (опционально)

### Документация
- [ ] README обновлен
- [ ] API документация
- [ ] Руководство пользователя

---

**Удачной разработки! 🚀**
