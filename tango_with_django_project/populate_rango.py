import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tango_with_django_project.settings')

import django
django.setup()
from rango.models import Category, Page


def populate():
    # Сначала мы создадим списки словарей, содержащие страницы,
    # которые мы хотим добавить в каждую категорию.
    # Затем мы создадим словарь словарей для наших категорий.
    # Это может показаться немного запутанным, но это позволяет нам перебирать
    # каждую структуру данных и добавлять данные в наши модели.

    python_pages = [
        {'title': 'Official Python Tutorial',
         'url': 'http://docs.python.org/3/tutorial/',
         'views': 3},
        {'title': 'How to Think like a Computer Scientist',
         'url': 'http://www.greenteapress.com/thinkpython/',
         'views': 3},
        {'title': 'Learn Python in 10 Minutes',
         'url': 'http://www.korokithakis.net/tutorials/python/',
         'views': 3}]

    django_pages = [
        {'title': 'Official Django Tutorial',
         'url': 'https://docs.djangoproject.com/en/2.1/intro/tutorial01/',
         'views': 3},
        {'title': 'Django Rocks',
         'url': 'http://www.djangorocks.com/',
         'views': 3},
        {'title': 'How to Tango with Django',
         'url': 'http://www.tangowithdjango.com/',
         'views': 3}]

    other_pages = [
        {'title': 'Bottle',
         'url': 'http://bottlepy.org/docs/dev/',
         'views': 3},
        {'title': 'Flask',
         'url': 'http://flask.pocoo.org',
         'views': 3}]

    no_pages = []

    cats = {'Python': {'pages': python_pages, 'views': 128, 'likes': 64},
            'Django': {'pages': django_pages, 'views': 64, 'likes': 32},
            'Other Frameworks': {'pages': other_pages, 'views': 32, 'likes': 16},
            'Pascal': {'pages': no_pages, 'views': 0, 'likes': 0},
            'Perl': {'pages': no_pages, 'views': 0, 'likes': 0},
            'PHP': {'pages': no_pages, 'views': 0, 'likes': 0},
            'Prolog': {'pages': no_pages, 'views': 0, 'likes': 0},
            'PostScript': {'pages': no_pages, 'views': 0, 'likes': 0},
            'Programming': {'pages': no_pages, 'views': 0, 'likes': 0}, }

    # Если вы хотите добавить больше категорий или страниц,
    # добавьте их в словари выше.

    # Приведенный ниже код просматривает словарь кошек, затем добавляет каждую категорию,
    # а затем добавляет все связанные страницы для этой категории.
    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data['views'], cat_data['likes'])
        for p in cat_data['pages']:
            add_page(c, p['title'], p['url'], p['views'])

    # Распечатать добавленные нами категории.
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print(f' - {c}: {p}')


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p


def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


# Начните выполнение здесь!
if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()
