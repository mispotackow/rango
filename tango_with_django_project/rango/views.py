from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator

from rango.bing_search import run_query
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm


def index(request):
    # Запросить в базе данных список ВСЕХ категорий, хранящихся в настоящее время.
    # Упорядочить категории по количеству лайков в порядке убывания.
    # Получить только первые 5 - или все, если меньше 5.
    # Поместите список в наш словарь context_dict (выделив жирным шрифтом!),
    # Который будет передан в механизм шаблонов.
    category_list = Category.objects.order_by('-likes')[:5]

    context_dict = dict()
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    try:
        pages_list = Page.objects.order_by('-views')[:5]
        context_dict['pages'] = pages_list
    except Page.DoesNotExist:
        context_dict['pages'] = None

    # Вызвать вспомогательную функцию для обработки файлов cookie
    visitor_cookie_handler(request)
    # context_dict['visits'] = request.session['visits']

    # Получите наш объект Response заранее, чтобы мы могли добавить информацию о cookie.
    response = render(request, 'rango/index.html', context=context_dict)
    # Вернуть ответ пользователю, обновив все файлы cookie, которые необходимо изменить.
    return response


class AboutView(View):
    def get(self, request):
        context_dict = {}

        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']

        return render(request, 'rango/about.html', context_dict)


# def about(request):
#     context_dict = {'my_name': 'MisPot'}
#     # выводит, является ли метод GET или POST
#     print(request.method)
#     # выводит имя пользователя, если никто не вошел в систему, выводит 'AnonymousUser'
#     print(request.user)
#
#     # Вызвать вспомогательную функцию для обработки файлов cookie
#     visitor_cookie_handler(request)
#     context_dict['visits'] = request.session['visits']
#
#     return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    # Создать контекстный словарь, который мы можем передать
    # механизму рендеринга шаблонов.
    context_dict = {}

    try:
        # Можем ли мы найти ярлык с названием категории с заданным именем?
        # Если мы не можем, метод .get () вызывает исключение DoesNotExist.
        # Метод .get () возвращает один экземпляр модели или вызывает исключение.
        category = Category.objects.get(slug=category_name_slug)

        # Получить все связанные страницы.
        # Filter () вернет список объектов страницы или пустой список.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Добавляет наш список результатов в контекст шаблона под страницами имен.
        context_dict['pages'] = pages
        # Мы также добавляем объект категории из
        # базы данных в контекстный словарь.
        # Мы будем использовать это в шаблоне, чтобы убедиться, что категория существует.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # Мы попадаем сюда, если не нашли указанную категорию.
        # Ничего не делайте -
        # шаблон отобразит для нас сообщение "без категории".
        context_dict['category'] = None
        context_dict['pages'] = None

    if request.method == 'POST':
        if request.method == 'POST':
            query = request.POST['query'].strip()
            if query:
                context_dict['result_list'] = run_query(query)
                context_dict['query'] = query

    # Выполните рендеринг ответа и верните его клиенту.
    return render(request, 'rango/category.html', context=context_dict)


class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
        return render(request, 'rango/add_category.html', {'form': form})


# @login_required
# def add_category(request):
#     form = CategoryForm()
#
#     # HTTP POST?
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)
#
#         # Нам предоставили действующую форму?
#         if form.is_valid():
#             # Сохраните новую категорию в базе данных.
#             form.save(commit=True)
#             # Теперь, когда категория сохранена, мы можем это подтвердить.
#             # На данный момент просто перенаправьте пользователя обратно в представление индекса.
#             return redirect(reverse('rango:index'))
#         else:
#             # Предоставленная форма содержала ошибки -
#             # просто распечатайте их в терминал.
#             print(form.errors)
#
#     # Будет обрабатывать случаи неправильной формы, новой формы или отсутствия формы.
#     # Визуализировать форму с сообщениями об ошибках (если есть).
#     return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # Вы не можете добавить страницу в категорию, которая не существует ...
    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug':
                                                category_name_slug}))

        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


# def register(request):
#     # Логическое значение, сообщающее шаблону
#     # об успешной регистрации.
#     # Первоначально установите значение "Ложь". Код меняет значение на
#     # True, когда регистрация успешна.
#     registered = False
#
#     # Если это HTTP POST, нас интересует обработка данных формы.
#     if request.method == 'POST':
#         # Попытка получить информацию из необработанной информации формы.
#         # Обратите внимание, что мы используем как UserForm, так и UserProfileForm.
#         user_form = UserForm(request.POST)
#         profile_form = UserProfileForm(request.POST)
#
#         # Если две формы действительны ...
#         if user_form.is_valid() and profile_form.is_valid():
#             # Сохранение данных формы пользователя в базе данных.
#             user = user_form.save()
#
#             # Теперь хэшируем пароль с помощью метода set_password.
#             # После хеширования мы можем обновить объект пользователя.
#             user.set_password(user.password)
#             user.save()
#
#             # Теперь отсортируйте экземпляр UserProfile.
#             # Поскольку нам нужно установить атрибут пользователя самостоятельно,
#             # мы устанавливаем commit = False. Это задерживает сохранение модели
#             # пока мы не будем готовы избежать проблем с целостностью.
#             profile = profile_form.save(commit=False)
#             profile.user = user
#
#             # Пользователь предоставил изображение профиля?
#             # Если это так, нам нужно получить его из формы ввода и
#             # ввести в модель UserProfile.
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
#
#             # Теперь сохраняем экземпляр модели UserProfile.
#             profile.save()
#
#             # Обновите нашу переменную, чтобы указать, что регистрация шаблона
#             # прошла успешно.
#             registered = True
#         else:
#             # Неверная форма или формы - ошибки или что-то еще?
#             # Ошибки - печать в терминал.
#             print(user_form.errors, profile_form.errors)
#     else:
#         # Это не HTTP POST, поэтому мы визуализируем нашу форму с помощью двух экземпляров ModelForm.
#         # Эти формы будут пустыми, готовыми для ввода пользователем.
#         user_form = UserForm()
#         profile_form = UserProfileForm()
#
#     # Визуализировать шаблон в зависимости от контекста.
#     return render(request, 'rango/register.html', context={'user_form': user_form,
#                                                            'profile_form': profile_form,
#                                                            'registered': registered})
#
#
# def user_login(request):
#     # Если запрос представляет собой HTTP POST, попробуйте вытащить соответствующую информацию.
#     if request.method == 'POST':
#         # Соберите имя пользователя и пароль, предоставленные пользователем.
#         # Эта информация получена из формы входа.
#         # Мы используем request.POST.get ('<переменная>') вместо
#         # для request.POST ['<переменная>'], потому что
#         # request.POST.get ('<переменная>') возвращает None, если
#         # значение не существует, а request.POST ['<переменная>']
#         # вызовет исключение KeyError.
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         # Используйте оборудование Django, чтобы проверить, является ли комбинация имени пользователя/пароля
#         # допустимой - объект User возвращается, если это так.
#         user = authenticate(username=username, password=password)
#
#         # Если у нас есть объект User, детали верны.
#         # Если None (способ представления отсутствия значения в Python),
#         # пользователя с соответствующими учетными данными не найдено.
#         if user:
#             # Аккаунт активен? Он может быть отключен
#             if user.is_active:
#                 # Если учетная запись действительна и активна, мы можем войти в систему.
#                 # Мы отправим пользователя обратно на домашнюю страницу.
#                 login(request, user)
#                 return redirect(reverse('rango:index'))
#             else:
#                 # Использовалась неактивная учетная запись - без входа!
#                 return HttpResponse("Your Rango account is disabled.")
#         else:
#             # Были предоставлены неверные данные для входа. Итак, мы не можем авторизовать пользователя.
#             print(f'Invalid login details: {username}, {password}')
#             return HttpResponse("Invalid login details supplied.")
#
#     # Запрос не является HTTP POST, поэтому отобразите форму входа.
#     # Этот сценарий, скорее всего, будет HTTP GET.
#     else:
#         # Нет переменных контекста для передачи в систему шаблонов, поэтому
#         # пустой объект словаря ...
#         return render(request, 'rango/login.html')


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


# Используйте декоратор login_required (), чтобы гарантировать
# доступ к представлению только зарегистрированным пользователям.
# @login_required
# def user_logout(request):
#     # Поскольку мы знаем, что пользователь вошел в систему, теперь мы можем просто выйти из системы.
#     logout(request)
#     # Верните пользователя на главную страницу.
#     return redirect(reverse('rango:index'))


def visitor_cookie_handler(request):
    # Получить количество посещений сайта.
    # Мы используем функцию COOKIES.get() для получения cookie посещений.
    # Если cookie существует, возвращаемое значение приводится к целому числу.
    # Если cookie не существует, то используется значение по умолчанию 1.
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    # Если с момента последнего посещения прошло больше суток ...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Обновите cookie последнего посещения теперь, когда мы обновили счетчик
        request.session['last_visit'] = str(datetime.now())
    else:
        # Установить файл cookie последнего посещения
        request.session['last_visit'] = last_visit_cookie

    # Обновить / установить cookie посещений
    request.session['visits'] = visits


# Вспомогательный метод
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


# def search(request):
#     result_list = []
#     if request.method == 'POST':
#         query = request.POST['query'].strip()
#         if query:
#             # Запустите нашу функцию Bing, чтобы получить список результатов!
#             result_list = run_query(query)
#     return render(request, 'rango/search.html', {'result_list': result_list})


def goto_url(request):
    if request.method == 'GET':
        page_id = request.GET.get('page_id')

        try:
            selected_page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))

        selected_page.views = selected_page.views + 1
        selected_page.save()

        return redirect(selected_page.url)
    return redirect(reverse('rango:index'))


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect(reverse('rango:index'))
        else:
            print(form.errors)

    context_dict = {'form': form}
    return render(request, 'rango/profile_registration.html', context_dict)


class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': user_profile.website,
                                'picture': user_profile.picture})

        return(user, user_profile, form)

    @method_decorator(login_required)
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        contex_dict = {'user_profile': user_profile,
                       'selected_user': user,
                       'form': form}

        return render(request, 'rango/profile.html', contex_dict)

    @method_decorator(login_required)
    def post(self, requeset, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        form = UserProfileForm(requeset.POST, requeset.FILES, instance=user_profile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)

        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        return render(requeset, 'rango/profile.html', context_dict)


class ListProfilesView(View):
    @method_decorator(login_required)
    def get(self, request):
        profiles = UserProfile.objects.all()

        return render(request, 'rango/list_profiles.html', {'user_profile_list': profiles})
