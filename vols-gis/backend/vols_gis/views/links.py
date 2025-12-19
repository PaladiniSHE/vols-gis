"""Views для управления связями"""
from pyramid.view import view_config
from ..models.links import Link
from ..schemas.links import LinkCreate, LinkUpdate


@view_config(route_name='api_links_list', request_method='GET')
def links_list(request):
    """Список всех связей"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    
    try:
        logger.info('Запрос списка связей')
        
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
            links = db.query(Link).all()
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
        logger.info(f'Найдено связей: {len(links)}')
        
        # Безопасное преобразование в словари
        links_list = []
        for l in links:
            try:
                links_list.append(l.to_dict())
            except Exception as e:
                logger.warning(f'Ошибка при преобразовании связи {l.id}: {e}')
                continue
        
        result = {'links': links_list, 'count': len(links_list)}
        logger.info(f'Список связей успешно сформирован: {len(links_list)} элементов')
        from pyramid.response import Response
        return Response(
            json_body=result,
            content_type='application/json'
        )
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f'Ошибка при получении списка связей: {str(e)}')
        logger.error(traceback.format_exc())
        
        # Безопасный rollback
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


@view_config(route_name='api_links_list', request_method='POST', renderer='json')
def links_create(request):
    """Создание новой связи"""
    try:
        data = request.json_body
        schema = LinkCreate(**data)
        
        db = request.db
        link = Link(
            fiber_id=schema.fiber_id,
            start_node_id=schema.start_node_id,
            end_node_id=schema.end_node_id,
            start_port=schema.start_port,
            end_port=schema.end_port,
            status=schema.status,
            capacity_gbps=schema.capacity_gbps,
            meta_data=schema.meta_data
        )
        db.add(link)
        db.commit()
        
        from pyramid.response import Response
        return Response(json_body={'link': link.to_dict()}, status=201)
    except Exception as e:
        request.db.rollback()
        return {'error': str(e)}, 400


@view_config(route_name='api_links_get', request_method='GET', renderer='json')
def links_get(request):
    """Получить связь по ID"""
    link_id = int(request.matchdict['id'])
    db = request.db
    link = db.query(Link).filter(Link.id == link_id).first()
    
    if not link:
        return {'error': 'Link not found'}, 404
    
    return {'link': link.to_dict()}


@view_config(route_name='api_links_get', request_method='PUT', renderer='json')
def links_update(request):
    """Обновить связь"""
    try:
        link_id = int(request.matchdict['id'])
        data = request.json_body
        schema = LinkUpdate(**data)
        
        db = request.db
        link = db.query(Link).filter(Link.id == link_id).first()
        
        if not link:
            return {'error': 'Link not found'}, 404
        
        if schema.fiber_id is not None:
            link.fiber_id = schema.fiber_id
        if schema.start_node_id is not None:
            link.start_node_id = schema.start_node_id
        if schema.end_node_id is not None:
            link.end_node_id = schema.end_node_id
        if schema.start_port is not None:
            link.start_port = schema.start_port
        if schema.end_port is not None:
            link.end_port = schema.end_port
        if schema.status is not None:
            link.status = schema.status
        if schema.capacity_gbps is not None:
            link.capacity_gbps = schema.capacity_gbps
        if schema.meta_data is not None:
            link.meta_data = schema.meta_data
        
        db.commit()
        
        return {'link': link.to_dict()}
    except Exception as e:
        request.db.rollback()
        return {'error': str(e)}, 400


@view_config(route_name='api_links_search', request_method='GET', renderer='json')
def links_search(request):
    """Поиск связей"""
    db = request.db
    query = db.query(Link)
    
    fiber_id = request.params.get('fiber_id')
    if fiber_id:
        query = query.filter(Link.fiber_id == int(fiber_id))
    
    node_id = request.params.get('node_id')
    if node_id:
        query = query.filter(
            (Link.start_node_id == int(node_id)) |
            (Link.end_node_id == int(node_id))
        )
    
    links = query.all()
    return {'links': [l.to_dict() for l in links], 'count': len(links)}

