"""Views для управления волокнами"""
from pyramid.view import view_config
from ..models.fibers import Fiber
from ..schemas.fibers import FiberCreate, FiberUpdate


@view_config(route_name='api_fibers_list', request_method='GET')
def fibers_list(request):
    """Список всех волокон"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    
    try:
        logger.info('Запрос списка волокон')
        
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
        query = db.query(Fiber)
        
        # Фильтр по маршруту
        vols_id = request.params.get('vols_id')
        if vols_id:
            try:
                query = query.filter(Fiber.vols_id == int(vols_id))
            except ValueError:
                pass
        
        # Фильтр по статусу
        status = request.params.get('status')
        if status:
            query = query.filter(Fiber.status == status)
        
        # Поиск по имени
        search = request.params.get('search')
        if search:
            query = query.filter(Fiber.name.ilike(f'%{search}%'))
        
        try:
            fibers = query.all()
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
        logger.info(f'Найдено волокон: {len(fibers)}')
        
        # Безопасное преобразование в словари
        fibers_list = []
        for f in fibers:
            try:
                fibers_list.append(f.to_dict())
            except Exception as e:
                logger.warning(f'Ошибка при преобразовании волокна {f.id}: {e}')
                continue
        
        result = {'fibers': fibers_list, 'count': len(fibers_list)}
        logger.info(f'Список волокон успешно сформирован: {len(fibers_list)} элементов')
        from pyramid.response import Response
        return Response(
            json_body=result,
            content_type='application/json'
        )
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f'Ошибка при получении списка волокон: {str(e)}')
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


@view_config(route_name='api_fibers_list', request_method='POST', renderer='json')
def fibers_create(request):
    """Создание нового волокна"""
    try:
        data = request.json_body
        schema = FiberCreate(**data)
        
        db = request.db
        fiber = Fiber(
            name=schema.name,
            cable_type=schema.cable_type,
            fiber_count=schema.fiber_count,
            status=schema.status,
            vols_id=schema.vols_id,
            meta_data=schema.meta_data
        )
        db.add(fiber)
        db.commit()
        
        from pyramid.response import Response
        return Response(json_body={'fiber': fiber.to_dict()}, status=201)
    except Exception as e:
        request.db.rollback()
        return {'error': str(e)}, 400


@view_config(route_name='api_fibers_get', request_method='GET', renderer='json')
def fibers_get(request):
    """Получить волокно по ID"""
    fiber_id = int(request.matchdict['id'])
    db = request.db
    fiber = db.query(Fiber).filter(Fiber.id == fiber_id).first()
    
    if not fiber:
        return {'error': 'Fiber not found'}, 404
    
    return {'fiber': fiber.to_dict()}


@view_config(route_name='api_fibers_get', request_method='PUT', renderer='json')
def fibers_update(request):
    """Обновить волокно"""
    try:
        fiber_id = int(request.matchdict['id'])
        data = request.json_body
        schema = FiberUpdate(**data)
        
        db = request.db
        fiber = db.query(Fiber).filter(Fiber.id == fiber_id).first()
        
        if not fiber:
            return {'error': 'Fiber not found'}, 404
        
        if schema.name is not None:
            fiber.name = schema.name
        if schema.cable_type is not None:
            fiber.cable_type = schema.cable_type
        if schema.fiber_count is not None:
            fiber.fiber_count = schema.fiber_count
        if schema.status is not None:
            fiber.status = schema.status
        if schema.vols_id is not None:
            fiber.vols_id = schema.vols_id
        if schema.meta_data is not None:
            fiber.meta_data = schema.meta_data
        
        db.commit()
        
        return {'fiber': fiber.to_dict()}
    except Exception as e:
        request.db.rollback()
        return {'error': str(e)}, 400


@view_config(route_name='api_fibers_by_vols', request_method='GET', renderer='json')
def fibers_by_vols(request):
    """Получить волокна по ВОЛС маршруту"""
    vols_id = int(request.matchdict['vols_id'])
    db = request.db
    fibers = db.query(Fiber).filter(Fiber.vols_id == vols_id).all()
    return {'fibers': [f.to_dict() for f in fibers], 'count': len(fibers)}

