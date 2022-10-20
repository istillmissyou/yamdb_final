from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import validate_year


SCORE_CHOICES = (
    (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'),
    (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')
)

ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'
ROLES = (
    (ADMIN, 'Admin'),
    (MODERATOR, 'Moderator'),
    (USER, 'User'),
)


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Имя категории',
        help_text='Введите название категории',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг категории',
        help_text='Введите слаг категории',
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Имя жанра',
        help_text='Введите имя жанра',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг жанра',
        help_text='Введите слаг жанра',
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения',
        help_text='Введите название произведения',
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска произведения',
        help_text='Введите год выпуска произведения',
        validators=(validate_year, )
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения',
        help_text='Введите год описание произведения',
    )
    rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Рейтинг произведения',
        help_text='Рейтинг вычисляется на основании score отзывов',
        validators=(
            MaxValueValidator(10, 'Максимальная оценка - 10'),
            MinValueValidator(1, 'Минимальная оценка - 1'),
        )
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр произведения',
        help_text='Выберите жанр произведения',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles', null=True,
        verbose_name='Категория произведения',
        help_text='Выберите категорию произведения',
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        help_text='Введите имя пользователя',
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='e-mail адрес',
        help_text='Введите e-mail адрес',
        unique=True,
        max_length=254
    )
    bio = models.TextField(
        verbose_name='Биография',
        help_text='Напишите биографию пользователя',
        blank=True,
        null=True,
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        help_text='Выберите роль пользователя',
        choices=ROLES,
        max_length=max(len(role[1]) for role in ROLES),
        default=USER
    )
    first_name = models.CharField(
        verbose_name='Имя',
        help_text='Укажите свое имя',
        max_length=150,
        blank=True)
    last_name = models.CharField(
        verbose_name='Фамилия',
        help_text='Укажите свою фамилию',
        max_length=150,
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=255,
        verbose_name='Код подтверждения',
        help_text='Введите свое код подтверждения',
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email',),
                name='unique_user'
            ),
        )

    @property
    def is_admin(self):
        return (self.role == ADMIN or self.is_staff
                or self.is_superuser)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        help_text='Выберите произведение',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
        help_text='Напишите ваш отзыв',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
        help_text='Выберите автора отзыва',
    )
    score = models.PositiveSmallIntegerField(
        choices=SCORE_CHOICES,
        null=True,
        verbose_name='Оценка произведения',
        help_text='Выберите оценку от 1 до 10',
        validators=(
            MaxValueValidator(10, 'Максимальная оценка - 10'),
            MinValueValidator(1, 'Минимальная оценка - 1'),
        )
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Выберите дату опубликования отзыва',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            ),
        )
        ordering = ('-pub_date', )
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв на произведение',
        help_text='Выберите отзыв на произведение',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Выберите автора комментария',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Выберите дату публикации',
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self):
        return self.text
