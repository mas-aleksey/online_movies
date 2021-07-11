from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class ProfessionType(models.TextChoices):
    ACTOR = 'actor', _('актер')
    DIRECTOR = 'director', _('режиссер')
    WRITER = 'writer', _('сценарист')


class FilmWorkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('шоу')


class AccessType(models.TextChoices):
    FREE = 'free', _('бесплатный доступ')
    STANDARD = 'standard', _('обычная подписка')
    EXTRA = 'extra', _('расширенная подписка')


class Filmwork(TimeStampedModel):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True, null=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True, null=True)
    type = models.CharField(_('тип'), max_length=20, choices=FilmWorkType.choices, default=FilmWorkType.MOVIE)
    creation_date = models.DateField(_('дата создания'), blank=True, null=True)
    end_date = models.DateField(_('дата окончания'), blank=True, null=True)
    age_limit = models.CharField(_('возрастной ценз'), max_length=50, blank=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True)
    access_type = models.CharField(_('тип доступа'), max_length=50, choices=AccessType.choices, default=AccessType.STANDARD)

    genres = models.ManyToManyField(
        'Genre',
        blank=True,
        through='FilmworkGenres',
        related_name='films'
    )

    persons = models.ManyToManyField(
        'Person',
        blank=True,
        through='FilmworkPersons',
        related_name='films'
    )

    class Meta:
        db_table = 'filmwork'
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

    def __str__(self):
        return self.title


class FilmworkGenres(models.Model):
    filmwork = models.ForeignKey(Filmwork, models.CASCADE)
    genre = models.ForeignKey('Genre', models.CASCADE)

    class Meta:
        db_table = 'filmwork_genres'
        unique_together = (('filmwork', 'genre'),)


class FilmworkPersons(models.Model):
    filmwork = models.ForeignKey(Filmwork, models.CASCADE)
    person = models.ForeignKey('Person', models.CASCADE)
    role = models.TextField(_('роль'), choices=ProfessionType.choices)

    class Meta:
        db_table = 'filmwork_persons'
        unique_together = (('filmwork', 'person', 'role'),)


class Genre(TimeStampedModel):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(_('название'), unique=True, max_length=50)
    description = models.TextField(_('описание'), blank=True, null=True)

    class Meta:
        db_table = 'genre'
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self):
        return self.name


class Person(TimeStampedModel):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(_('имя'), unique=True, max_length=255)

    class Meta:
        db_table = 'person'
        verbose_name = _('сотрудник')
        verbose_name_plural = _('сотрудники')

    def __str__(self):
        return self.name


class FilmworkActorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=ProfessionType.ACTOR)


class FilmworkDirectorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=ProfessionType.DIRECTOR)


class FilmworkWriterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=ProfessionType.WRITER)


class FilmworkActor(FilmworkPersons):
    objects = FilmworkActorManager()

    class Meta:
        proxy = True
        verbose_name = _('актер')
        verbose_name_plural = _('актеры')


class FilmworkDirector(FilmworkPersons):
    objects = FilmworkDirectorManager()

    class Meta:
        proxy = True
        verbose_name = _('режиссер')
        verbose_name_plural = _('режиссеры')


class FilmworkWriter(FilmworkPersons):
    objects = FilmworkWriterManager()

    class Meta:
        proxy = True
        verbose_name = _('сценарист')
        verbose_name_plural = _('сценаристы')


class MovieManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=FilmWorkType.MOVIE)


class TvShowManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=FilmWorkType.TV_SHOW)


class Movie(Filmwork):
    objects = MovieManager()

    class Meta:
        proxy = True
        verbose_name = _('Фильм')
        verbose_name_plural = _('фильмы')


class TvShow(Filmwork):
    objects = TvShowManager()

    class Meta:
        proxy = True
        verbose_name = _('Сериал')
        verbose_name_plural = _('сериалы')
