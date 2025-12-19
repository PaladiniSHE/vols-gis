"""Скрипт для создания тестовых данных"""
import requests
import json

API_BASE = 'http://localhost:6543/api'

def create_test_data():
    """Создает тестовые узлы, маршруты ВОЛС, волокна и связи"""
    
    print("Создание тестовых данных...")
    
    # Создаем узлы связи
    nodes_data = [
        {'name': 'Москва-Центр', 'lat': 55.7558, 'lon': 37.6173, 'node_type': 'cross', 'status': 'active'},
        {'name': 'Зеленоград', 'lat': 55.9825, 'lon': 37.1814, 'node_type': 'muft', 'status': 'active'},
        {'name': 'Химки', 'lat': 55.8970, 'lon': 37.4297, 'node_type': 'bsp', 'status': 'active'},
        {'name': 'Красногорск', 'lat': 55.8314, 'lon': 37.3315, 'node_type': 'muft', 'status': 'active'},
        {'name': 'Одинцово', 'lat': 55.6780, 'lon': 37.2777, 'node_type': 'cross', 'status': 'active'},
    ]
    
    node_ids = []
    for node_data in nodes_data:
        try:
            response = requests.post(f'{API_BASE}/nodes', json=node_data)
            if response.status_code in [200, 201]:
                data = response.json()
                if isinstance(data, list):
                    node = data[0]['node']
                else:
                    node = data.get('node', {})
                if node and 'id' in node:
                    node_ids.append(node['id'])
                    print(f"  Создан узел: {node['name']} (ID: {node['id']})")
                else:
                    print(f"  Неожиданный формат ответа для {node_data['name']}: {data}")
            else:
                print(f"  Ошибка создания узла {node_data['name']}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  Ошибка при создании узла {node_data['name']}: {e}")
    
    # Создаем маршруты ВОЛС
    routes_data = []
    vols_ids = []
    if len(node_ids) >= 2:
        routes_data = [
            {
                'name': 'Москва-Зеленоград',
                'start_node_id': node_ids[0],
                'end_node_id': node_ids[1],
                'path': [
                    [37.6173, 55.7558],  # Москва
                    [37.4297, 55.8970],  # Химки
                    [37.1814, 55.9825],  # Зеленоград
                ],
                'status': 'active',
                'length_km': 45.5
            },
            {
                'name': 'Москва-Одинцово',
                'start_node_id': node_ids[0],
                'end_node_id': node_ids[4],
                'path': [
                    [37.6173, 55.7558],  # Москва
                    [37.3315, 55.8314],  # Красногорск
                    [37.2777, 55.6780],  # Одинцово
                ],
                'status': 'active',
                'length_km': 32.8
            },
            {
                'name': 'Химки-Красногорск',
                'start_node_id': node_ids[2],
                'end_node_id': node_ids[3],
                'path': [
                    [37.4297, 55.8970],  # Химки
                    [37.3315, 55.8314],  # Красногорск
                ],
                'status': 'active',
                'length_km': 8.2
            },
        ]
        
        for route_data in routes_data:
            try:
                response = requests.post(f'{API_BASE}/vols', json=route_data)
                if response.status_code in [200, 201]:
                    data = response.json()
                    if isinstance(data, list):
                        vols = data[0]['vols']
                    else:
                        vols = data.get('vols', {})
                    if vols and 'id' in vols:
                        vols_ids.append(vols['id'])
                        print(f"  Создан маршрут: {vols['name']} (ID: {vols['id']})")
                    else:
                        print(f"  Неожиданный формат ответа для {route_data['name']}: {data}")
                else:
                    print(f"  Ошибка создания маршрута {route_data['name']}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"  Ошибка при создании маршрута {route_data['name']}: {e}")
    
    # Создаем волокна для маршрутов
    fiber_ids = []
    if len(vols_ids) > 0:
        fibers_data = [
            {'name': 'Кабель ОКСН-М-24 (Москва-Зеленоград)', 'cable_type': 'ОКСН-М-24', 'fiber_count': 24, 'vols_id': vols_ids[0], 'status': 'active'},
            {'name': 'Кабель ОКСН-М-12 (Москва-Зеленоград)', 'cable_type': 'ОКСН-М-12', 'fiber_count': 12, 'vols_id': vols_ids[0], 'status': 'spare'},
            {'name': 'Кабель ОКСН-М-48 (Москва-Одинцово)', 'cable_type': 'ОКСН-М-48', 'fiber_count': 48, 'vols_id': vols_ids[1], 'status': 'active'},
            {'name': 'Кабель ОКСН-М-24 (Химки-Красногорск)', 'cable_type': 'ОКСН-М-24', 'fiber_count': 24, 'vols_id': vols_ids[2], 'status': 'active'},
            {'name': 'Кабель ОКСН-М-12 (Химки-Красногорск)', 'cable_type': 'ОКСН-М-12', 'fiber_count': 12, 'vols_id': vols_ids[2], 'status': 'spare'},
        ]
        
        for fiber_data in fibers_data:
            try:
                response = requests.post(f'{API_BASE}/fibers', json=fiber_data)
                if response.status_code in [200, 201]:
                    data = response.json()
                    if isinstance(data, list):
                        fiber = data[0]['fiber']
                    else:
                        fiber = data.get('fiber', {})
                    if fiber and 'id' in fiber:
                        fiber_ids.append(fiber['id'])
                        print(f"  Создано волокно: {fiber['name']} (ID: {fiber['id']})")
                    else:
                        print(f"  Неожиданный формат ответа для {fiber_data['name']}: {data}")
                else:
                    print(f"  Ошибка создания волокна {fiber_data['name']}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"  Ошибка при создании волокна {fiber_data['name']}: {e}")
    
    # Создаем связи между узлами через волокна
    links_count = 0
    if len(fiber_ids) > 0 and len(node_ids) >= 2:
        links_data = [
            # Связи для первого маршрута (Москва-Зеленоград)
            {'fiber_id': fiber_ids[0], 'start_node_id': node_ids[0], 'end_node_id': node_ids[1], 'start_port': 1, 'end_port': 1, 'status': 'active', 'capacity_gbps': 10.0},
            {'fiber_id': fiber_ids[0], 'start_node_id': node_ids[0], 'end_node_id': node_ids[1], 'start_port': 2, 'end_port': 2, 'status': 'active', 'capacity_gbps': 10.0},
            {'fiber_id': fiber_ids[0], 'start_node_id': node_ids[0], 'end_node_id': node_ids[1], 'start_port': 3, 'end_port': 3, 'status': 'spare', 'capacity_gbps': 10.0},
            # Связи для второго маршрута (Москва-Одинцово)
            {'fiber_id': fiber_ids[2], 'start_node_id': node_ids[0], 'end_node_id': node_ids[4], 'start_port': 1, 'end_port': 1, 'status': 'active', 'capacity_gbps': 40.0},
            {'fiber_id': fiber_ids[2], 'start_node_id': node_ids[0], 'end_node_id': node_ids[4], 'start_port': 2, 'end_port': 2, 'status': 'active', 'capacity_gbps': 40.0},
            # Связи для третьего маршрута (Химки-Красногорск)
            {'fiber_id': fiber_ids[3], 'start_node_id': node_ids[2], 'end_node_id': node_ids[3], 'start_port': 1, 'end_port': 1, 'status': 'active', 'capacity_gbps': 10.0},
            {'fiber_id': fiber_ids[3], 'start_node_id': node_ids[2], 'end_node_id': node_ids[3], 'start_port': 2, 'end_port': 2, 'status': 'active', 'capacity_gbps': 10.0},
            {'fiber_id': fiber_ids[3], 'start_node_id': node_ids[2], 'end_node_id': node_ids[3], 'start_port': 3, 'end_port': 3, 'status': 'unused', 'capacity_gbps': 10.0},
        ]
        
        for link_data in links_data:
            try:
                response = requests.post(f'{API_BASE}/links', json=link_data)
                if response.status_code in [200, 201]:
                    data = response.json()
                    if isinstance(data, list):
                        link = data[0]['link']
                    else:
                        link = data.get('link', {})
                    if link and 'id' in link:
                        links_count += 1
                        print(f"  Создана связь: Узел {link['start_node_id']} → Узел {link['end_node_id']} (ID: {link['id']})")
                    else:
                        print(f"  Неожиданный формат ответа для связи: {data}")
                else:
                    print(f"  Ошибка создания связи: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"  Ошибка при создании связи: {e}")
    
    print("\n" + "="*50)
    print("Тестовые данные созданы!")
    print(f"Создано узлов: {len(node_ids)}")
    print(f"Создано маршрутов: {len(vols_ids)}")
    print(f"Создано волокон: {len(fiber_ids)}")
    print(f"Создано связей: {links_count}")
    print("="*50)

if __name__ == '__main__':
    create_test_data()

