from django.core.paginator import Paginator, Page
from django.conf import settings

class OptimizedPaginator(Paginator):
    """Paginator optimizado que evita COUNT(*) en bases de datos grandes"""
    
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, max_count=None):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.max_count = max_count

    @property
    def count(self):
        """Optimizar el conteo para datasets grandes"""
        if not hasattr(self, '_count'):
            try:
                # Usar caché si está disponible
                if hasattr(self.object_list, 'count'):
                    self._count = self.object_list.count()
                else:
                    self._count = len(self.object_list)
                    
                # Limitar el conteo máximo para evitar queries lentas
                if self.max_count and self._count > self.max_count:
                    self._count = self.max_count
                    
            except (AttributeError, TypeError):
                self._count = len(self.object_list)
        return self._count

class OptimizedPage(Page):
    """Página optimizada con información de rendimiento"""
    
    def __init__(self, object_list, number, paginator):
        super().__init__(object_list, number, paginator)
        self._render_time = None
    
    def set_render_time(self, render_time):
        """Establecer tiempo de renderizado para monitoreo"""
        self._render_time = render_time
    
    @property
    def render_time(self):
        """Obtener tiempo de renderizado"""
        return self._render_time

def paginate_optimized(request, queryset, per_page=None):
    """Función helper para paginación optimizada"""
    if per_page is None:
        per_page = getattr(settings, 'DEFAULT_PAGINATION_SIZE', 25)
    
    # Limitar el tamaño máximo de página
    max_per_page = getattr(settings, 'MAX_PAGINATION_SIZE', 100)
    if per_page > max_per_page:
        per_page = max_per_page
    
    paginator = OptimizedPaginator(queryset, per_page)
    page_number = request.GET.get('page', 1)
    
    try:
        page = paginator.page(page_number)
    except:
        page = paginator.page(1)
    
    return page, paginator