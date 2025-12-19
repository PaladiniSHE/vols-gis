"""View для frontend"""
from pyramid.view import view_config
from pyramid.response import FileResponse
import os


@view_config(route_name='frontend')
def frontend_view(request):
    """Отдает index.html для frontend"""
    frontend_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'frontend',
        'index.html'
    )
    return FileResponse(frontend_path, request=request)





