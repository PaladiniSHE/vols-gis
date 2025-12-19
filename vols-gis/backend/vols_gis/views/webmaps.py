"""Views для управления веб-картами"""
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import IntegrityError
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from ..models.webmaps import WebMap
from ..schemas.webmaps import WebMapCreate, WebMapUpdate
import logging
import traceback

logger = logging.getLogger(__name__)


@view_config(route_name='api_webmaps_list', request_method='GET')
def webmaps_list(request):
    """Список всех веб-карт"""
    try:
        logger.info('Запрос списка веб-карт')
        
        if not hasattr(request, 'db') or request.db is None:
            logger.error('DB сессия не доступна')
            return Response(
                json_body={
                    'error': 'Database session not available',
                    'message': 'PostgreSQL не запущен или недоступен.'
                },
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        try:
            webmaps = db.query(WebMap).all()
        except Exception as query_error:
            logger.error(f'Ошибка выполнения запроса: {query_error}')
            return Response(
                json_body={
                    'error': 'Database query error',
                    'message': f'Ошибка при выполнении запроса: {str(query_error)}'
                },
                status=500,
                content_type='application/json'
            )
        
        logger.info(f'Найдено веб-карт: {len(webmaps)}')
        
        webmaps_list = []
        for webmap in webmaps:
            try:
                webmap_dict = webmap.to_dict()
                # Преобразуем геометрию в координаты
                if webmap.center_geom:
                    shape = to_shape(webmap.center_geom)
                    webmap_dict['center_lat'] = shape.y
                    webmap_dict['center_lon'] = shape.x
                    webmap_dict.pop('center_geom', None)
                webmaps_list.append(webmap_dict)
            except Exception as e:
                logger.warning(f'Ошибка при преобразовании веб-карты {webmap.id}: {e}')
                continue
        
        result = {'webmaps': webmaps_list, 'count': len(webmaps_list)}
        logger.info(f'Список веб-карт успешно сформирован: {len(webmaps_list)} элементов')
        return Response(json_body=result, content_type='application/json')
        
    except Exception as e:
        logger.error(f'Ошибка при получении списка веб-карт: {str(e)}')
        logger.error(traceback.format_exc())
        
        if hasattr(request, 'db') and request.db is not None:
            try:
                request.db.rollback()
            except:
                pass
        
        return Response(
            json_body={'error': f'Internal Server Error: {str(e)}'},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_webmaps_list', request_method='POST')
def webmaps_create(request):
    """Создание новой веб-карты"""
    try:
        logger.info('Запрос на создание веб-карты')
        
        if not hasattr(request, 'db') or request.db is None:
            logger.error('DB сессия не доступна')
            return Response(
                json_body={
                    'error': 'Database session not available',
                    'message': 'PostgreSQL не запущен или недоступен.'
                },
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        try:
            data = request.json_body
        except Exception as e:
            logger.error(f'Ошибка парсинга JSON: {e}')
            return Response(
                json_body={'error': 'Invalid JSON', 'message': 'Неверный формат данных'},
                status=400,
                content_type='application/json'
            )
        
        # Валидация данных
        try:
            webmap_data = WebMapCreate(**data)
        except Exception as e:
            logger.error(f'Ошибка валидации: {e}')
            return Response(
                json_body={'error': 'Validation error', 'message': str(e)},
                status=400,
                content_type='application/json'
            )
        
        # Создание геометрии центра
        center_geom = None
        if webmap_data.center_lat is not None and webmap_data.center_lon is not None:
            center_geom = Point(webmap_data.center_lon, webmap_data.center_lat)
        
        # Создание веб-карты
        try:
            new_webmap = WebMap(
                name=webmap_data.name,
                description=webmap_data.description,
                visible_layers=webmap_data.visible_layers,
                center_geom=center_geom,
                zoom_level=webmap_data.zoom_level,
                permissions=webmap_data.permissions
            )
            db.add(new_webmap)
            db.commit()
            db.refresh(new_webmap)
            
            logger.info(f'Веб-карта создана: {new_webmap.id}')
            
            # Преобразуем для ответа
            webmap_dict = new_webmap.to_dict()
            if new_webmap.center_geom:
                shape = to_shape(new_webmap.center_geom)
                webmap_dict['center_lat'] = shape.y
                webmap_dict['center_lon'] = shape.x
                webmap_dict.pop('center_geom', None)
            
            return Response(
                json_body={'webmap': webmap_dict, 'message': 'Веб-карта успешно создана'},
                status=201,
                content_type='application/json'
            )
        except IntegrityError as e:
            db.rollback()
            logger.error(f'Ошибка целостности данных: {e}')
            return Response(
                json_body={
                    'error': 'Integrity error',
                    'message': 'Ошибка при создании веб-карты'
                },
                status=409,
                content_type='application/json'
            )
        except Exception as e:
            db.rollback()
            logger.error(f'Ошибка при создании веб-карты: {e}')
            return Response(
                json_body={'error': 'Database error', 'message': str(e)},
                status=500,
                content_type='application/json'
            )
            
    except Exception as e:
        logger.error(f'Ошибка при создании веб-карты: {str(e)}')
        logger.error(traceback.format_exc())
        
        if hasattr(request, 'db') and request.db is not None:
            try:
                request.db.rollback()
            except:
                pass
        
        return Response(
            json_body={'error': f'Internal Server Error: {str(e)}'},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_webmaps_get', request_method='GET')
def webmaps_get(request):
    """Получение веб-карты по ID"""
    try:
        webmap_id = int(request.matchdict['id'])
        logger.info(f'Запрос веб-карты с ID: {webmap_id}')
        
        if not hasattr(request, 'db') or request.db is None:
            logger.error('DB сессия не доступна')
            return Response(
                json_body={
                    'error': 'Database session not available',
                    'message': 'PostgreSQL не запущен или недоступен.'
                },
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        try:
            webmap = db.query(WebMap).filter(WebMap.id == webmap_id).first()
        except Exception as query_error:
            logger.error(f'Ошибка выполнения запроса: {query_error}')
            return Response(
                json_body={
                    'error': 'Database query error',
                    'message': f'Ошибка при выполнении запроса: {str(query_error)}'
                },
                status=500,
                content_type='application/json'
            )
        
        if not webmap:
            return Response(
                json_body={'error': 'Not found', 'message': 'Веб-карта не найдена'},
                status=404,
                content_type='application/json'
            )
        
        # Преобразуем для ответа
        webmap_dict = webmap.to_dict()
        if webmap.center_geom:
            shape = to_shape(webmap.center_geom)
            webmap_dict['center_lat'] = shape.y
            webmap_dict['center_lon'] = shape.x
            webmap_dict.pop('center_geom', None)
        
        logger.info(f'Веб-карта найдена: {webmap.id}')
        return Response(
            json_body={'webmap': webmap_dict},
            content_type='application/json'
        )
        
    except ValueError:
        return Response(
            json_body={'error': 'Invalid ID', 'message': 'Неверный ID веб-карты'},
            status=400,
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f'Ошибка при получении веб-карты: {str(e)}')
        logger.error(traceback.format_exc())
        
        if hasattr(request, 'db') and request.db is not None:
            try:
                request.db.rollback()
            except:
                pass
        
        return Response(
            json_body={'error': f'Internal Server Error: {str(e)}'},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_webmaps_get', request_method='PUT')
def webmaps_update(request):
    """Обновление веб-карты"""
    try:
        webmap_id = int(request.matchdict['id'])
        logger.info(f'Запрос на обновление веб-карты с ID: {webmap_id}')
        
        if not hasattr(request, 'db') or request.db is None:
            logger.error('DB сессия не доступна')
            return Response(
                json_body={
                    'error': 'Database session not available',
                    'message': 'PostgreSQL не запущен или недоступен.'
                },
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        try:
            webmap = db.query(WebMap).filter(WebMap.id == webmap_id).first()
        except Exception as query_error:
            logger.error(f'Ошибка выполнения запроса: {query_error}')
            return Response(
                json_body={
                    'error': 'Database query error',
                    'message': f'Ошибка при выполнении запроса: {str(query_error)}'
                },
                status=500,
                content_type='application/json'
            )
        
        if not webmap:
            return Response(
                json_body={'error': 'Not found', 'message': 'Веб-карта не найдена'},
                status=404,
                content_type='application/json'
            )
        
        try:
            data = request.json_body
        except Exception as e:
            logger.error(f'Ошибка парсинга JSON: {e}')
            return Response(
                json_body={'error': 'Invalid JSON', 'message': 'Неверный формат данных'},
                status=400,
                content_type='application/json'
            )
        
        # Валидация данных
        try:
            webmap_update = WebMapUpdate(**data)
        except Exception as e:
            logger.error(f'Ошибка валидации: {e}')
            return Response(
                json_body={'error': 'Validation error', 'message': str(e)},
                status=400,
                content_type='application/json'
            )
        
        # Обновление полей
        update_data = webmap_update.dict(exclude_unset=True)
        
        # Обработка геометрии центра
        if 'center_lat' in update_data or 'center_lon' in update_data:
            lat = update_data.pop('center_lat', None)
            lon = update_data.pop('center_lon', None)
            if lat is not None and lon is not None:
                update_data['center_geom'] = Point(lon, lat)
            elif 'center_lat' in data or 'center_lon' in data:
                # Если переданы координаты, но одна из них None, используем существующие
                if webmap.center_geom:
                    shape = to_shape(webmap.center_geom)
                    lat = lat if lat is not None else shape.y
                    lon = lon if lon is not None else shape.x
                    update_data['center_geom'] = Point(lon, lat)
        
        try:
            for key, value in update_data.items():
                setattr(webmap, key, value)
            
            db.commit()
            db.refresh(webmap)
            
            # Преобразуем для ответа
            webmap_dict = webmap.to_dict()
            if webmap.center_geom:
                shape = to_shape(webmap.center_geom)
                webmap_dict['center_lat'] = shape.y
                webmap_dict['center_lon'] = shape.x
                webmap_dict.pop('center_geom', None)
            
            logger.info(f'Веб-карта обновлена: {webmap.id}')
            return Response(
                json_body={'webmap': webmap_dict, 'message': 'Веб-карта успешно обновлена'},
                content_type='application/json'
            )
        except IntegrityError as e:
            db.rollback()
            logger.error(f'Ошибка целостности данных: {e}')
            return Response(
                json_body={
                    'error': 'Integrity error',
                    'message': 'Ошибка при обновлении веб-карты'
                },
                status=409,
                content_type='application/json'
            )
        except Exception as e:
            db.rollback()
            logger.error(f'Ошибка при обновлении веб-карты: {e}')
            return Response(
                json_body={'error': 'Database error', 'message': str(e)},
                status=500,
                content_type='application/json'
            )
            
    except ValueError:
        return Response(
            json_body={'error': 'Invalid ID', 'message': 'Неверный ID веб-карты'},
            status=400,
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f'Ошибка при обновлении веб-карты: {str(e)}')
        logger.error(traceback.format_exc())
        
        if hasattr(request, 'db') and request.db is not None:
            try:
                request.db.rollback()
            except:
                pass
        
        return Response(
            json_body={'error': f'Internal Server Error: {str(e)}'},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_webmaps_get', request_method='DELETE')
def webmaps_delete(request):
    """Удаление веб-карты"""
    try:
        webmap_id = int(request.matchdict['id'])
        logger.info(f'Запрос на удаление веб-карты с ID: {webmap_id}')
        
        if not hasattr(request, 'db') or request.db is None:
            logger.error('DB сессия не доступна')
            return Response(
                json_body={
                    'error': 'Database session not available',
                    'message': 'PostgreSQL не запущен или недоступен.'
                },
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        try:
            webmap = db.query(WebMap).filter(WebMap.id == webmap_id).first()
        except Exception as query_error:
            logger.error(f'Ошибка выполнения запроса: {query_error}')
            return Response(
                json_body={
                    'error': 'Database query error',
                    'message': f'Ошибка при выполнении запроса: {str(query_error)}'
                },
                status=500,
                content_type='application/json'
            )
        
        if not webmap:
            return Response(
                json_body={'error': 'Not found', 'message': 'Веб-карта не найдена'},
                status=404,
                content_type='application/json'
            )
        
        try:
            db.delete(webmap)
            db.commit()
            
            logger.info(f'Веб-карта удалена: {webmap_id}')
            return Response(
                json_body={'message': 'Веб-карта успешно удалена'},
                status=200,
                content_type='application/json'
            )
        except Exception as e:
            db.rollback()
            logger.error(f'Ошибка при удалении веб-карты: {e}')
            return Response(
                json_body={'error': 'Database error', 'message': str(e)},
                status=500,
                content_type='application/json'
            )
            
    except ValueError:
        return Response(
            json_body={'error': 'Invalid ID', 'message': 'Неверный ID веб-карты'},
            status=400,
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f'Ошибка при удалении веб-карты: {str(e)}')
        logger.error(traceback.format_exc())
        
        if hasattr(request, 'db') and request.db is not None:
            try:
                request.db.rollback()
            except:
                pass
        
        return Response(
            json_body={'error': f'Internal Server Error: {str(e)}'},
            status=500,
            content_type='application/json'
        )

