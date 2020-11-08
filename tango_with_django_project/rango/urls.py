from django.urls import path
from rango import views

app_name = 'rango'


urlpatterns = [
    path('', views.index, name='index'),
    #Обновлен путь, указывающий на новое представление на основе класса about.
    path('about/', views.AboutView.as_view(), name='about'),
    path('category/<slug:category_name_slug>/', views.show_category, name='show_category'),
    path('category/<slug:category_name_slug>/add_page/', views.add_page, name='add_page'),
    path('add_category/', views.AddCategoryView.as_view(), name='add_category'),
    # path('register/', views.register, name='register'),
    # path('login/', views.user_login, name='login'),
    # path('logout/', views.user_logout, name='logout'),
    path('restricted/', views.restricted, name='restricted'),
    # path('search/', views.search, name='search'),
    path('goto/', views.goto_url, name='goto'),
    path('register_profile/', views.register_profile, name='register_profile'),
    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
]
