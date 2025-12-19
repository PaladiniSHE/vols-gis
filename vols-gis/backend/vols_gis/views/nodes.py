"""Views для управления узлами"""
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy import func
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from ..models.nodes import Node
from ..schemas.nodes import NodeCreate, NodeUpdate
import json


@view_config(route_name='api_nodes_list', request_method='GET')
def nodes_list(request):
    """Список всех узлов"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    
    try:
        logger.info('Запрос списка узлов')
        
        # Проверяем доступность БД
        if not hasattr(request, 'db') or request.db is None:
            logger.error('DB сессия не доступна')
            from pyramid.response import Response
            return Response(
                json_body={
                    'error': 'Database session not available',
                    'message': 'PostgreSQL не запущен или недоступен. Убедитесь, что PostgreSQL запущен на порту 5433.',
                    'hint': 'Запустите PostgreSQL и перезапустите сервер'
                },
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        logger.info('DB сессия получена, выполняем запрос')
        
        try:
            nodes = db.query(Node).all()
        except Exception as query_error:
            logger.error(f'Ошибка выполнения запроса: {query_error}')
            from pyramid.response import Response
            return Response(
                json_body={
                    'error': 'Database query error',
                    'message': f'Ошибка при выполнении запроса: {str(query_error)}'
                },
                status=500,
                content_type='application/json'
            )
        logger.info(f'Найдено узлов: {len(nodes)}')
        
        result = []
        for node in nodes:
            try:
                node_dict = node.to_dict()
                # Преобразуем геометрию в координаты
                if node.geom:
                    shape = to_shape(node.geom)
                    node_dict['lat'] = shape.y
                    node_dict['lon'] = shape.x
                    node_dict.pop('geom', None)
                result.append(node_dict)
            except Exception as e:
                logger.warning(f'Ошибка при обработке узла {node.id}: {e}')
                continue
        
        logger.info('Список узлов успешно сформирован')
        from pyramid.response import Response
        return Response(
            json_body={'nodes': result, 'count': len(result)},
            content_type='application/json'
        )
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f'Ошибка при получении списка узлов: {str(e)}')
        logger.error(traceback.format_exc())
        if hasattr(request, 'db'):
            try:
                request.db.rollback()
            except:
                pass
        from pyramid.response import Response
        return Response(
            json_body={'error': f'Internal Server Error: {str(e)}'},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_nodes_list', request_method='POST')
def nodes_create(request):
    """Создание нового узла"""
    try:
        data = request.json_body
        schema = NodeCreate(**data)
        
        db = request.db
        # Создаем точку из координат
        point = func.ST_SetSRID(func.ST_MakePoint(schema.lon, schema.lat), 4326)
        
        node = Node(
            name=schema.name,
            description=schema.description,
            node_type=schema.node_type,
            status=schema.status,
            geom=point,
            meta_data=schema.meta_data
        )
        db.add(node)
        db.commit()
        
        node_dict = node.to_dict()
        shape = to_shape(node.geom)
        node_dict['lat'] = shape.y
        node_dict['lon'] = shape.x
        node_dict.pop('geom', None)
        
        from pyramid.response import Response
        return Response(json_body={'node': node_dict}, status=201, content_type='application/json')
    except Exception as e:
        if hasattr(request, 'db') and request.db is not None:
            try:
                request.db.rollback()
            except:
                pass
        from pyramid.response import Response
        return Response(
            json_body={'error': str(e)},
            status=400,
            content_type='application/json'
        )


@view_config(route_name='api_nodes_get', request_method='GET')
def nodes_get(request):
    """Получить узел по ID"""
    node_id = int(request.matchdict['id'])
    db = request.db
    node = db.query(Node).filter(Node.id == node_id).first()
    
    if not node:
        return {'error': 'Node not found'}, 404
    
    node_dict = node.to_dict()
    if node.geom:
        shape = to_shape(node.geom)
        node_dict['lat'] = shape.y
        node_dict['lon'] = shape.x
        node_dict.pop('geom', None)
    
    from pyramid.response import Response
    return Response(
        json_body={'node': node_dict},
        content_type='application/json'
    )


@view_config(route_name='api_nodes_get', request_method='PUT')
def nodes_update(request):
    """Обновить узел"""
    try:
        node_id = int(request.matchdict['id'])
        data = request.json_body
        schema = NodeUpdate(**data)
        
        db = request.db
        node = db.query(Node).filter(Node.id == node_id).first()
        
        if not node:
            return {'error': 'Node not found'}, 404
        
        # Обновляем поля
        if schema.name is not None:
            node.name = schema.name
        if schema.description is not None:
            node.description = schema.description
        if schema.node_type is not None:
            node.node_type = schema.node_type
        if schema.status is not None:
            node.status = schema.status
        if schema.meta_data is not None:
            node.meta_data = schema.meta_data
        
        # Обновляем геометрию если указаны координаты
        if schema.lat is not None and schema.lon is not None:
            point = func.ST_SetSRID(func.ST_MakePoint(schema.lon, schema.lat), 4326)
            node.geom = point
        
        db.commit()
        
        node_dict = node.to_dict()
        if node.geom:
            shape = to_shape(node.geom)
            node_dict['lat'] = shape.y
            node_dict['lon'] = shape.x
            node_dict.pop('geom', None)
        
        from pyramid.response import Response
        return Response(
            json_body={'node': node_dict},
            content_type='application/json'
        )
    except Exception as e:
        if hasattr(request, 'db') and request.db is not None:
            try:
                request.db.rollback()
            except:
                pass
        from pyramid.response import Response
        return Response(
            json_body={'error': str(e)},
            status=400,
            content_type='application/json'
        )


@view_config(route_name='api_nodes_get', request_method='DELETE')
def nodes_delete(request):
    """Удалить узел"""
    node_id = int(request.matchdict['id'])
    db = request.db
    node = db.query(Node).filter(Node.id == node_id).first()
    
    if not node:
        return {'error': 'Node not found'}, 404
    
    db.delete(node)
    db.commit()
    
    from pyramid.response import Response
    return Response(
        json_body={'message': 'Node deleted'},
        content_type='application/json'
    )


@view_config(route_name='api_nodes_nearby', request_method='GET')
def nodes_nearby(request):
    """Поиск узлов поблизости"""
    try:
        lat = float(request.params.get('lat'))
        lon = float(request.params.get('lon'))
        distance = float(request.params.get('distance', 5))  # км по умолчанию
        
        db = request.db
        point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        
        # Поиск в радиусе (distance в метрах)
        nodes = db.query(Node).filter(
            func.ST_DWithin(
                Node.geom,
                point,
                distance * 1000  # конвертируем км в метры
            )
        ).all()
        
        result = []
        for node in nodes:
            node_dict = node.to_dict()
            if node.geom:
                shape = to_shape(node.geom)
                node_dict['lat'] = shape.y
                node_dict['lon'] = shape.x
                node_dict.pop('geom', None)
            result.append(node_dict)
        
        from pyramid.response import Response
        return Response(
            json_body={'nodes': result, 'count': len(result)},
            content_type='application/json'
        )
    except Exception as e:
        from pyramid.response import Response
        return Response(
            json_body={'error': str(e)},
            status=400,
            content_type='application/json'
        )

