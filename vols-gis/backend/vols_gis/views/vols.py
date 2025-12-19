"""Views для управления ВОЛС маршрутами"""
from pyramid.view import view_config
from sqlalchemy import func
from geoalchemy2.shape import to_shape
from ..models.vols import Vols
from ..schemas.vols import VolsCreate, VolsUpdate
import json


@view_config(route_name='api_vols_list', request_method='GET')
def vols_list(request):
    """Список всех ВОЛС маршрутов"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    
    try:
        logger.info('Запрос списка маршрутов')
        
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
        
        # Параметры поиска и фильтрации
        query = db.query(Vols)
        
        # Фильтр по статусу
        status = request.params.get('status')
        if status:
            query = query.filter(Vols.status == status)
        
        # Поиск по имени
        search = request.params.get('search')
        if search:
            query = query.filter(Vols.name.ilike(f'%{search}%'))
        
        try:
            vols_list = query.all()
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
        logger.info(f'Найдено маршрутов: {len(vols_list)}')
        
        result = []
        for vols in vols_list:
            try:
                vols_dict = vols.to_dict()
                # Преобразуем геометрию в координаты
                if vols.path:
                    shape = to_shape(vols.path)
                    vols_dict['path'] = [[coord[0], coord[1]] for coord in shape.coords]
                result.append(vols_dict)
            except Exception as e:
                logger.warning(f'Ошибка при обработке маршрута {vols.id}: {e}')
                continue
        
        logger.info('Список маршрутов успешно сформирован')
        from pyramid.response import Response
        return Response(
            json_body={'vols': result, 'count': len(result)},
            content_type='application/json'
        )
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f'Ошибка при получении списка маршрутов: {str(e)}')
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


@view_config(route_name='api_vols_list', request_method='POST', renderer='json')
def vols_create(request):
    """Создание нового ВОЛС маршрута"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        data = request.json_body
        logger.info(f'Получены данные для создания маршрута: {data}')
        
        # Валидация данных через Pydantic
        try:
            schema = VolsCreate(**data)
        except Exception as validation_error:
            logger.error(f'Ошибка валидации данных: {validation_error}')
            from pyramid.response import Response
            return Response(
                json_body={'error': f'Ошибка валидации: {str(validation_error)}'},
                status=400
            )
        
        db = request.db
        
        # Проверяем формат координат
        if not schema.path or len(schema.path) < 2:
            logger.error(f'Недостаточно координат в path: {schema.path}')
            from pyramid.response import Response
            return Response(
                json_body={'error': 'Маршрут должен содержать минимум 2 точки'},
                status=400
            )
        
        # Создаем LineString из координат
        try:
            coords_str = ', '.join([f'{lon} {lat}' for lon, lat in schema.path])
            logger.info(f'Создание LineString из координат: {coords_str[:200]}...')
            
            linestring = func.ST_SetSRID(
                func.ST_GeomFromText(f'LINESTRING({coords_str})', 4326),
                4326
            )
        except Exception as geom_error:
            logger.error(f'Ошибка создания геометрии: {geom_error}')
            from pyramid.response import Response
            return Response(
                json_body={'error': f'Ошибка создания геометрии: {str(geom_error)}'},
                status=400
            )
        
        # Создаем объект Vols
        try:
            vols = Vols(
                name=schema.name,
                description=schema.description,
                start_node_id=schema.start_node_id,
                end_node_id=schema.end_node_id,
                path=linestring,
                length_km=schema.length_km,
                status=schema.status,
                meta_data=schema.meta_data
            )
            db.add(vols)
            db.commit()
            logger.info(f'Маршрут успешно создан с ID: {vols.id}')
        except Exception as db_error:
            db.rollback()
            logger.error(f'Ошибка сохранения в БД: {db_error}')
            from pyramid.response import Response
            return Response(
                json_body={'error': f'Ошибка сохранения в БД: {str(db_error)}'},
                status=500
            )
        
        # Формируем ответ
        vols_dict = vols.to_dict()
        if vols.path:
            shape = to_shape(vols.path)
            vols_dict['path'] = [[coord[0], coord[1]] for coord in shape.coords]
        
        from pyramid.response import Response
        return Response(json_body={'vols': vols_dict}, status=201)
        
    except Exception as e:
        request.db.rollback()
        logger.error(f'Неожиданная ошибка при создании маршрута: {e}', exc_info=True)
        from pyramid.response import Response
        return Response(
            json_body={'error': f'Внутренняя ошибка сервера: {str(e)}'},
            status=500
        )


@view_config(route_name='api_vols_get', request_method='GET', renderer='json')
def vols_get(request):
    """Получить ВОЛС маршрут по ID"""
    vols_id = int(request.matchdict['id'])
    db = request.db
    vols = db.query(Vols).filter(Vols.id == vols_id).first()
    
    if not vols:
        return {'error': 'VOLS not found'}, 404
    
    vols_dict = vols.to_dict()
    if vols.path:
        shape = to_shape(vols.path)
        vols_dict['path'] = [[coord[0], coord[1]] for coord in shape.coords]
    
    return {'vols': vols_dict}


@view_config(route_name='api_vols_get', request_method='PUT', renderer='json')
def vols_update(request):
    """Обновить ВОЛС маршрут"""
    try:
        vols_id = int(request.matchdict['id'])
        data = request.json_body
        schema = VolsUpdate(**data)
        
        db = request.db
        vols = db.query(Vols).filter(Vols.id == vols_id).first()
        
        if not vols:
            return {'error': 'VOLS not found'}, 404
        
        # Обновляем поля
        if schema.name is not None:
            vols.name = schema.name
        if schema.description is not None:
            vols.description = schema.description
        if schema.start_node_id is not None:
            vols.start_node_id = schema.start_node_id
        if schema.end_node_id is not None:
            vols.end_node_id = schema.end_node_id
        if schema.length_km is not None:
            vols.length_km = schema.length_km
        if schema.status is not None:
            vols.status = schema.status
        if schema.meta_data is not None:
            vols.meta_data = schema.meta_data
        
        # Обновляем геометрию если указан путь
        if schema.path is not None:
            coords_str = ', '.join([f'{lon} {lat}' for lon, lat in schema.path])
            linestring = func.ST_SetSRID(
                func.ST_GeomFromText(f'LINESTRING({coords_str})', 4326),
                4326
            )
            vols.path = linestring
        
        db.commit()
        
        vols_dict = vols.to_dict()
        if vols.path:
            shape = to_shape(vols.path)
            vols_dict['path'] = [[coord[0], coord[1]] for coord in shape.coords]
        
        return {'vols': vols_dict}
    except Exception as e:
        request.db.rollback()
        return {'error': str(e)}, 400


@view_config(route_name='api_vols_get', request_method='DELETE', renderer='json')
def vols_delete(request):
    """Удалить ВОЛС маршрут"""
    vols_id = int(request.matchdict['id'])
    db = request.db
    vols = db.query(Vols).filter(Vols.id == vols_id).first()
    
    if not vols:
        return {'error': 'VOLS not found'}, 404
    
    db.delete(vols)
    db.commit()
    
    return {'message': 'VOLS deleted'}


@view_config(route_name='api_vols_path', request_method='GET', renderer='json')
def vols_path(request):
    """Получить геометрию маршрута в формате GeoJSON"""
    vols_id = int(request.matchdict['id'])
    db = request.db
    vols = db.query(Vols).filter(Vols.id == vols_id).first()
    
    if not vols:
        return {'error': 'VOLS not found'}, 404
    
    if not vols.path:
        return {'error': 'Path not found'}, 404
    
    # Преобразуем в GeoJSON
    shape = to_shape(vols.path)
    coords = [[coord[0], coord[1]] for coord in shape.coords]
    
    geojson = {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': coords
        },
        'properties': {
            'id': vols.id,
            'name': vols.name,
            'description': vols.description,
            'status': vols.status
        }
    }
    
    return geojson

