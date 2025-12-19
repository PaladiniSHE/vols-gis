"""Views для экспорта данных"""
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy import func
from geoalchemy2.shape import to_shape
from ..models.nodes import Node
from ..models.vols import Vols
from ..models.fibers import Fiber
from ..models.links import Link
from ..auth.decorators import require_auth
import logging
import traceback
import json
import csv
import io

logger = logging.getLogger(__name__)


def nodes_to_geojson(nodes):
    """Преобразует узлы в GeoJSON"""
    features = []
    for node in nodes:
        if node.geom:
            shape = to_shape(node.geom)
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [shape.x, shape.y]
                },
                "properties": {
                    "id": node.id,
                    "name": node.name,
                    "description": node.description,
                    "node_type": node.node_type,
                    "status": node.status,
                    "meta_data": node.meta_data
                }
            })
    return {
        "type": "FeatureCollection",
        "features": features
    }


def vols_to_geojson(vols_list):
    """Преобразует маршруты в GeoJSON"""
    features = []
    for vols in vols_list:
        if vols.path:
            shape = to_shape(vols.path)
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[coord[0], coord[1]] for coord in shape.coords]
                },
                "properties": {
                    "id": vols.id,
                    "name": vols.name,
                    "description": vols.description,
                    "status": vols.status,
                    "length_km": float(vols.length_km) if vols.length_km else None,
                    "meta_data": vols.meta_data
                }
            })
    return {
        "type": "FeatureCollection",
        "features": features
    }


@view_config(route_name='api_export_nodes_geojson', request_method='GET')
@require_auth
def export_nodes_geojson(request):
    """Экспорт узлов в GeoJSON"""
    try:
        if not hasattr(request, 'db') or request.db is None:
            return Response(
                json_body={'error': 'Database session not available'},
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        nodes = db.query(Node).all()
        
        geojson = nodes_to_geojson(nodes)
        
        return Response(
            body=json.dumps(geojson, ensure_ascii=False, indent=2),
            content_type='application/geo+json',
            headers={
                'Content-Disposition': 'attachment; filename="nodes.geojson"'
            }
        )
    except Exception as e:
        logger.error(f'Ошибка экспорта узлов: {e}')
        return Response(
            json_body={'error': str(e)},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_export_vols_geojson', request_method='GET')
@require_auth
def export_vols_geojson(request):
    """Экспорт маршрутов в GeoJSON"""
    try:
        if not hasattr(request, 'db') or request.db is None:
            return Response(
                json_body={'error': 'Database session not available'},
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        vols_list = db.query(Vols).all()
        
        geojson = vols_to_geojson(vols_list)
        
        return Response(
            body=json.dumps(geojson, ensure_ascii=False, indent=2),
            content_type='application/geo+json',
            headers={
                'Content-Disposition': 'attachment; filename="vols.geojson"'
            }
        )
    except Exception as e:
        logger.error(f'Ошибка экспорта маршрутов: {e}')
        return Response(
            json_body={'error': str(e)},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_export_nodes_csv', request_method='GET')
@require_auth
def export_nodes_csv(request):
    """Экспорт узлов в CSV"""
    try:
        if not hasattr(request, 'db') or request.db is None:
            return Response(
                json_body={'error': 'Database session not available'},
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        nodes = db.query(Node).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Заголовки
        writer.writerow(['ID', 'Name', 'Description', 'Type', 'Status', 'Latitude', 'Longitude'])
        
        # Данные
        for node in nodes:
            if node.geom:
                shape = to_shape(node.geom)
                writer.writerow([
                    node.id,
                    node.name or '',
                    node.description or '',
                    node.node_type or '',
                    node.status or '',
                    shape.y,
                    shape.x
                ])
        
        return Response(
            body=output.getvalue(),
            content_type='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': 'attachment; filename="nodes.csv"'
            }
        )
    except Exception as e:
        logger.error(f'Ошибка экспорта узлов в CSV: {e}')
        return Response(
            json_body={'error': str(e)},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_export_fibers_csv', request_method='GET')
@require_auth
def export_fibers_csv(request):
    """Экспорт волокон в CSV"""
    try:
        if not hasattr(request, 'db') or request.db is None:
            return Response(
                json_body={'error': 'Database session not available'},
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        fibers = db.query(Fiber).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Заголовки
        writer.writerow(['ID', 'Name', 'Cable Type', 'Fiber Count', 'Status', 'Vols ID'])
        
        # Данные
        for fiber in fibers:
            writer.writerow([
                fiber.id,
                fiber.name or '',
                fiber.cable_type or '',
                fiber.fiber_count or '',
                fiber.status or '',
                fiber.vols_id or ''
            ])
        
        return Response(
            body=output.getvalue(),
            content_type='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': 'attachment; filename="fibers.csv"'
            }
        )
    except Exception as e:
        logger.error(f'Ошибка экспорта волокон в CSV: {e}')
        return Response(
            json_body={'error': str(e)},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_export_all_json', request_method='GET')
@require_auth
def export_all_json(request):
    """Экспорт всех данных в JSON"""
    try:
        if not hasattr(request, 'db') or request.db is None:
            return Response(
                json_body={'error': 'Database session not available'},
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        # Получаем все данные
        nodes = db.query(Node).all()
        vols_list = db.query(Vols).all()
        fibers = db.query(Fiber).all()
        links = db.query(Link).all()
        
        # Преобразуем в словари
        data = {
            'nodes': [node.to_dict() for node in nodes],
            'vols': [],
            'fibers': [fiber.to_dict() for fiber in fibers],
            'links': [link.to_dict() for link in links]
        }
        
        # Обрабатываем маршруты с геометрией
        for vols in vols_list:
            vols_dict = vols.to_dict()
            if vols.path:
                shape = to_shape(vols.path)
                vols_dict['path'] = [[coord[0], coord[1]] for coord in shape.coords]
            data['vols'].append(vols_dict)
        
        return Response(
            body=json.dumps(data, ensure_ascii=False, indent=2),
            content_type='application/json',
            headers={
                'Content-Disposition': 'attachment; filename="vols_gis_export.json"'
            }
        )
    except Exception as e:
        logger.error(f'Ошибка экспорта всех данных: {e}')
        return Response(
            json_body={'error': str(e)},
            status=500,
            content_type='application/json'
        )

