from django.contrib import admin
from rango.models import Category, Page, UserProfile


# Добавьте в этот класс, чтобы настроить интерфейс администратора
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


# Обновите регистрацию, чтобы включить этот настраиваемый интерфейс
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
