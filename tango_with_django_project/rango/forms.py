from django import forms
from django.contrib.auth.models import User
from rango.models import Page, Category, UserProfile


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                           help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Встроенный класс для предоставления дополнительной информации о форме.
    class Meta:
        # Обеспечьте связь между ModelForm и моделью
        model = Category
        fields = ('name',)


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128,
                            help_text='Please enter the title of the page.')
    url = forms.URLField(max_length=200,
                         help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        # Обеспечьте связь между ModelForm и моделью
        model = Page

        # Какие поля мы хотим включить в нашу форму?
        # Таким образом, нам не нужны все поля в модели.
        # Некоторые поля могут допускать значения NULL; мы можем не захотеть их включать.
        # Здесь мы скрываем внешний ключ.
        # мы можем либо исключить поле категории из формы,
        exclude = ('category',)
        # или укажите поля для включения (не включайте поле категории).
        # fields = ('title', 'url', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # Если url не пустой и не начинается с "http://",
        # тогда добавьте "http://".
        if url and not url.startswith("http://"):
            url = f"http://{url}"
            cleaned_data['url'] = url
        return cleaned_data


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture',)
