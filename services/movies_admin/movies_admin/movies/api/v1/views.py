from django.http import JsonResponse
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, FilmworkPersons, ProfessionType


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        return Filmwork.objects.values(
            'id', 'title', 'description', 'creation_date', 'rating', 'type'
        ).annotate(
            genres=ArrayAgg(
                'genres__name',
                distinct=True
            ),
            actors=ArrayAgg(
                'persons__name',
                filter=Q(filmworkpersons__role=ProfessionType.ACTOR),
                distinct=True
            ),
            directors=ArrayAgg(
                'persons__name',
                filter=Q(filmworkpersons__role=ProfessionType.DIRECTOR),
                distinct=True
            ),
            writers=ArrayAgg(
                'persons__name',
                filter=Q(filmworkpersons__role=ProfessionType.WRITER),
                distinct=True
            )
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    model = Filmwork
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, object_list, _ = self.paginate_queryset(self.get_queryset(), self.paginate_by)
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            'results': list(object_list),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    model = Filmwork

    def get_object(self, queryset=None):
        qs = super().get_queryset()
        return qs.filter(pk=self.kwargs['pk']).first()

    def get_context_data(self, **kwargs):
        return kwargs['object']
