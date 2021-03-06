import itertools

from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.urls import reverse
from pytils.translit import slugify


class Post(models.Model):

    class Meta:
        ordering = ('-published_date', )

    POSTS_ON_PAGE = 7

    author = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    category = models.ForeignKey(to='news.Category', on_delete=models.PROTECT, blank=True, null=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, db_index=True, unique=True)
    text = RichTextUploadingField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(to='news.Tag')

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def view(self):
        self.views += 1
        self.save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        name = 'news_page' if self.published_date else 'draft_page'
        return reverse(name, kwargs={'slug': self.slug})

    # https://keyerror.com/blog/automatically-generating-unique-slugs-in-django
    def save(self, **kwargs):

        if not self.slug:
            max_length = Post._meta.get_field('slug').max_length
            self.slug = orig = slugify(self.title)[:max_length]

            for x in itertools.count(1):
                if not Post.objects.filter(slug=self.slug).exists():
                    break

                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        super(Post, self).save(**kwargs)

    @classmethod
    def get_hot_news(cls, count=settings.SIDEBAR_POST_COUNT):
        return cls.objects.filter(published_date__isnull=False).order_by('-views')[:count]


class CategoryQueryset(models.QuerySet):

    def parents(self):
        return self.filter(parent__isnull=True)


class Category(models.Model):

    class Meta:
        ordering = ('parent__title', )

    parent = models.ForeignKey(to='self', on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, db_index=True, unique=True)

    objects = CategoryQueryset.as_manager()

    def __str__(self):
        return self.title

    def children(self):
        return self.category_set.all()

    def get_absolute_url(self):
        return reverse('category_news', kwargs={'slug': self.slug})


class Tag(models.Model):

    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32, db_index=True, unique=True)

    def __str__(self):
        return self.name
