"""Тестирование функционала волокон и связей"""
import requests
import json

API_BASE = 'http://localhost:6543/api'

def test_fibers():
    """Тестирование API волокон"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ВОЛОКОН")
    print("="*60)
    
    # 1. Получить список всех волокон
    print("\n1. GET /api/fibers - Список всех волокон")
    try:
        response = requests.get(f'{API_BASE}/fibers')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            fibers = data.get('fibers', [])
            print(f"   Найдено волокон: {len(fibers)}")
            for fiber in fibers[:3]:  # Показываем первые 3
                print(f"   - {fiber.get('name')} (ID: {fiber.get('id')}, Тип: {fiber.get('cable_type')}, Волокон: {fiber.get('fiber_count')})")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 2. Получить волокна по маршруту ВОЛС
    print("\n2. GET /api/fibers/by-vols/{vols_id} - Волокна по маршруту")
    try:
        vols_id = 5  # ID первого маршрута
        response = requests.get(f'{API_BASE}/fibers/by-vols/{vols_id}')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            fibers = data.get('fibers', [])
            print(f"   Найдено волокон для маршрута {vols_id}: {len(fibers)}")
            for fiber in fibers:
                print(f"   - {fiber.get('name')} (ID: {fiber.get('id')})")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 3. Получить одно волокно по ID
    print("\n3. GET /api/fibers/{id} - Получить волокно по ID")
    try:
        fiber_id = 1
        response = requests.get(f'{API_BASE}/fibers/{fiber_id}')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            fiber = data.get('fiber', {})
            print(f"   Волокно: {fiber.get('name')}")
            print(f"   Тип кабеля: {fiber.get('cable_type')}")
            print(f"   Количество волокон: {fiber.get('fiber_count')}")
            print(f"   Статус: {fiber.get('status')}")
            print(f"   Маршрут ВОЛС ID: {fiber.get('vols_id')}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 4. Обновить волокно
    print("\n4. PUT /api/fibers/{id} - Обновить волокно")
    try:
        fiber_id = 1
        update_data = {
            'name': 'Кабель ОКСН-М-24 (Москва-Зеленоград) [ОБНОВЛЕНО]',
            'status': 'spare'
        }
        response = requests.put(f'{API_BASE}/fibers/{fiber_id}', json=update_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            fiber = data.get('fiber', {})
            print(f"   Обновлено: {fiber.get('name')}")
            print(f"   Новый статус: {fiber.get('status')}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")

def test_links():
    """Тестирование API связей"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ СВЯЗЕЙ")
    print("="*60)
    
    # 1. Получить список всех связей
    print("\n1. GET /api/links - Список всех связей")
    try:
        response = requests.get(f'{API_BASE}/links')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            links = data.get('links', [])
            print(f"   Найдено связей: {len(links)}")
            for link in links[:5]:  # Показываем первые 5
                print(f"   - Связь #{link.get('id')}: Узел {link.get('start_node_id')} → Узел {link.get('end_node_id')} "
                      f"(Статус: {link.get('status')}, Емкость: {link.get('capacity_gbps')} Гбит/с)")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 2. Получить связь по ID
    print("\n2. GET /api/links/{id} - Получить связь по ID")
    try:
        link_id = 1
        response = requests.get(f'{API_BASE}/links/{link_id}')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            link = data.get('link', {})
            print(f"   Связь #{link.get('id')}")
            print(f"   Волокно ID: {link.get('fiber_id')}")
            print(f"   Начальный узел: {link.get('start_node_id')}")
            print(f"   Конечный узел: {link.get('end_node_id')}")
            print(f"   Порт начала: {link.get('start_port')}")
            print(f"   Порт конца: {link.get('end_port')}")
            print(f"   Статус: {link.get('status')}")
            print(f"   Емкость: {link.get('capacity_gbps')} Гбит/с")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 3. Поиск связей по узлу
    print("\n3. GET /api/links/search?node_id={id} - Поиск связей по узлу")
    try:
        node_id = 17  # Москва-Центр
        response = requests.get(f'{API_BASE}/links/search', params={'node_id': node_id})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            links = data.get('links', [])
            print(f"   Найдено связей для узла {node_id}: {len(links)}")
            for link in links:
                print(f"   - Связь #{link.get('id')}: Узел {link.get('start_node_id')} → Узел {link.get('end_node_id')}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 4. Поиск связей по волокну
    print("\n4. GET /api/links/search?fiber_id={id} - Поиск связей по волокну")
    try:
        fiber_id = 1
        response = requests.get(f'{API_BASE}/links/search', params={'fiber_id': fiber_id})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            links = data.get('links', [])
            print(f"   Найдено связей для волокна {fiber_id}: {len(links)}")
            for link in links:
                print(f"   - Связь #{link.get('id')}: Порт {link.get('start_port')} → Порт {link.get('end_port')}")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 5. Обновить связь
    print("\n5. PUT /api/links/{id} - Обновить связь")
    try:
        link_id = 1
        update_data = {
            'status': 'spare',
            'capacity_gbps': 25.0
        }
        response = requests.put(f'{API_BASE}/links/{link_id}', json=update_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            link = data.get('link', {})
            print(f"   Обновлена связь #{link.get('id')}")
            print(f"   Новый статус: {link.get('status')}")
            print(f"   Новая емкость: {link.get('capacity_gbps')} Гбит/с")
        else:
            print(f"   Ошибка: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")

def test_create_new():
    """Тестирование создания новых волокон и связей"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ СОЗДАНИЯ НОВЫХ ОБЪЕКТОВ")
    print("="*60)
    
    # 1. Создать новое волокно
    print("\n1. POST /api/fibers - Создать новое волокно")
    try:
        fiber_data = {
            'name': 'Тестовое волокно ОКСН-М-96',
            'cable_type': 'ОКСН-М-96',
            'fiber_count': 96,
            'vols_id': 5,
            'status': 'active'
        }
        response = requests.post(f'{API_BASE}/fibers', json=fiber_data)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            fiber = data.get('fiber', {})
            print(f"   Создано волокно: {fiber.get('name')} (ID: {fiber.get('id')})")
            new_fiber_id = fiber.get('id')
        else:
            print(f"   Ошибка: {response.text}")
            new_fiber_id = None
    except Exception as e:
        print(f"   Ошибка: {e}")
        new_fiber_id = None
    
    # 2. Создать новую связь
    if new_fiber_id:
        print("\n2. POST /api/links - Создать новую связь")
        try:
            link_data = {
                'fiber_id': new_fiber_id,
                'start_node_id': 17,
                'end_node_id': 18,
                'start_port': 10,
                'end_port': 10,
                'status': 'active',
                'capacity_gbps': 100.0
            }
            response = requests.post(f'{API_BASE}/links', json=link_data)
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                link = data.get('link', {})
                print(f"   Создана связь: Узел {link.get('start_node_id')} → Узел {link.get('end_node_id')} (ID: {link.get('id')})")
                print(f"   Емкость: {link.get('capacity_gbps')} Гбит/с")
            else:
                print(f"   Ошибка: {response.text}")
        except Exception as e:
            print(f"   Ошибка: {e}")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("ПОЛНОЕ ТЕСТИРОВАНИЕ ФУНКЦИОНАЛА ВОЛОКОН И СВЯЗЕЙ")
    print("="*60)
    
    test_fibers()
    test_links()
    test_create_new()
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60 + "\n")




