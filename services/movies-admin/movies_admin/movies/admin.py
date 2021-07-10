import uuid
from django.contrib import admin
from .models import (
    Genre, FilmWorkType, Movie, TvShow, FilmworkGenres, Person, Filmwork,
    FilmworkActor, FilmworkDirector, FilmworkWriter, ProfessionType, FilmworkPersons
)


class FilmworkGenresInline(admin.TabularInline):
    model = FilmworkGenres
    extra = 0
    autocomplete_fields = ('genre',)
    verbose_name = 'жанр'
    verbose_name_plural = 'жанры'


class FilmworkPersonInline(admin.TabularInline):
    autocomplete_fields = ('person',)
    extra = 0


class FilmworkActorInline(FilmworkPersonInline):
    model = FilmworkActor
    verbose_name = 'актер'
    verbose_name_plural = 'актеры'

    def formfield_for_choice_field(self, db_field, request=None, **kwargs):
        if db_field.name == 'role':
            kwargs['choices'] = ((ProfessionType.ACTOR, 'актер'),)
        return db_field.formfield(**kwargs)


class FilmworkDirectorInline(FilmworkPersonInline):
    model = FilmworkDirector
    verbose_name = 'режиссер'
    verbose_name_plural = 'режиссеры'

    def formfield_for_choice_field(self, db_field, request=None, **kwargs):
        if db_field.name == 'role':
            kwargs['choices'] = ((ProfessionType.DIRECTOR, 'режиссер'),)
        return db_field.formfield(**kwargs)


class FilmworkWriterInline(FilmworkPersonInline):
    model = FilmworkWriter
    verbose_name = 'сценарист'
    verbose_name_plural = 'сценаристы'

    def formfield_for_choice_field(self, db_field, request=None, **kwargs):
        if db_field.name == 'role':
            kwargs['choices'] = ((ProfessionType.WRITER, 'сценарист'),)
        return db_field.formfield(**kwargs)


class PersonFilmworkInline(admin.TabularInline):
    model = FilmworkPersons
    extra = 0
    autocomplete_fields = ('filmwork',)
    verbose_name = 'кинопроизведение'
    verbose_name_plural = 'кинопроизведения'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    exclude = ('id',)
    search_fields = ['name']
    inlines = [PersonFilmworkInline]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.id = uuid.uuid4()
        super().save_model(request, obj, form, change)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    exclude = ('id',)
    search_fields = ['name']


@admin.register(Filmwork)
class FilmWorkAdmin(admin.ModelAdmin):
    exclude = ('id',)
    list_display = ('title', 'creation_date', 'rating')
    search_fields = ('title', 'description', 'id')

    inlines = [
        FilmworkGenresInline,
        FilmworkActorInline, FilmworkDirectorInline, FilmworkWriterInline
    ]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.id = uuid.uuid4()
        super().save_model(request, obj, form, change)


@admin.register(Movie)
class MovieAdmin(FilmWorkAdmin):
    fields = (
        'title', 'description', 'creation_date',
        'file_path', 'rating', 'age_limit', 'access_type'
    )

    def save_model(self, request, obj, form, change):
        obj.type = FilmWorkType.MOVIE
        super().save_model(request, obj, form, change)


@admin.register(TvShow)
class TvShowAdmin(FilmWorkAdmin):
    fields = (
        'title', 'description', 'creation_date', 'end_date',
        'file_path', 'rating', 'access_type'
    )

    def save_model(self, request, obj, form, change):
        obj.type = FilmWorkType.TV_SHOW
        super().save_model(request, obj, form, change)
