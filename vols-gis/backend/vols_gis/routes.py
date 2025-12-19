"""Маршруты приложения"""
from pyramid.config import Configurator


def includeme(config: Configurator):
    """Подключает все маршруты приложения"""
    
    # Frontend
    config.add_route('frontend', '/')
    
    # API: Nodes
    config.add_route('api_nodes_list', '/api/nodes')
    config.add_route('api_nodes_get', '/api/nodes/{id}')
    config.add_route('api_nodes_nearby', '/api/nodes/nearby')
    
    # API: VOLS
    config.add_route('api_vols_list', '/api/vols')
    config.add_route('api_vols_get', '/api/vols/{id}')
    config.add_route('api_vols_path', '/api/vols/{id}/path')
    
    # API: Fibers
    config.add_route('api_fibers_list', '/api/fibers')
    config.add_route('api_fibers_get', '/api/fibers/{id}')
    config.add_route('api_fibers_by_vols', '/api/fibers/by-vols/{vols_id}')
    
    # API: Links
    config.add_route('api_links_list', '/api/links')
    config.add_route('api_links_get', '/api/links/{id}')
    config.add_route('api_links_search', '/api/links/search')
    
    # API: Users
    config.add_route('api_users_list', '/api/users')
    config.add_route('api_users_get', '/api/users/{id}')
    
    # API: WebMaps
    config.add_route('api_webmaps_list', '/api/webmaps')
    config.add_route('api_webmaps_get', '/api/webmaps/{id}')
    
    # Views для API
    config.scan('vols_gis.views')
