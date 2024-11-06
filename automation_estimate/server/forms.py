from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import *

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Ваш логин', max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите логин',
        'id': 'inputEmailAddress',
    }))
    password = forms.CharField(label='Ваш пароль', widget=forms.PasswordInput(attrs={
        'class': 'form-control border-end-0',
        'placeholder': 'Введите пароль',
        'id': 'inputChoosePassword',
    }))


class StaffRegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email', max_length=255, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите почту'
    }))
    username = forms.CharField(label='Логин', max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите логин'
    }))
    name = forms.CharField(label='ФИО', max_length=155, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите ФИО'
    }))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={
        'class': 'form-control border-end-0',
        'placeholder': 'Введите пароль'
    }))
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={
        'class': 'form-control border-end-0',
        'placeholder': 'Подтвердите пароль'
    }))
    category = forms.ChoiceField(label='Роль', choices=Staff.FIELD_CAT, widget=forms.Select(attrs={
        'class': 'form-select'
    }))

    class Meta:
        model = Staff
        fields = ['email', 'username', 'name', 'password1', 'password2', 'category']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'staff', 'chapter', 'task', 'total_cost',
            'additional_costs', 'data_start', 'data_end', 'customer', 'status'
        ]

    name = forms.CharField(
        label="Наименование проекта",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    staff = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.filter(category__in=['2']),
        widget=forms.SelectMultiple(attrs={'class': 'multiple-select', 'data-placeholder': 'Выберите сотрудников'}),
        label="Выбор сотрудников",
        to_field_name='id'  # Используем id для передачи в проект
    )

    # Обновлено для выбора сотрудников с должностями и ставками
    staff_display = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.filter(category__in=['2']),
        widget=forms.SelectMultiple(attrs={'class': 'multiple-select', 'data-placeholder': 'Выберите сотрудников'}),
        label="Выбор сотрудников",
        required=False
    )

    chapter = forms.ModelMultipleChoiceField(
        queryset=Chapter.objects.filter(project__isnull=True),
        widget=forms.SelectMultiple(attrs={'class': 'multiple-select', 'data-placeholder': 'Добавьте разделы'}),
        label="Добавление разделов"
    )

    task = forms.ModelMultipleChoiceField(
        queryset=SettingTask.objects.filter(project__isnull=True),
        widget=forms.SelectMultiple(attrs={'class': 'multiple-select', 'data-placeholder': 'Постановка задач'}),
        label="Постановка задач"
    )

    total_cost = forms.DecimalField(
        label="Стоимость проекта",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    additional_costs = forms.ModelChoiceField(
        queryset=AdditionalCosts.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Дополнительные затраты"
    )

    data_start = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker'}),
        input_formats=['%d %B, %Y'],
        label="Дата начала",
        required=True
    )

    data_end = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker'}),
        input_formats=['%d %B, %Y'],
        label="Дата окончания",
        required=True
    )

    customer = forms.ModelChoiceField(
        queryset=Staff.objects.filter(category__in=['3']),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Заказчик"
    )

    status = forms.ChoiceField(
        choices=Project.FIELD_STATUS,  # Используем статусы из модели Project
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Статус"
    )

    def clean_data_start(self):
        data_start = self.cleaned_data['data_start']
        return data_start

    def clean_data_end(self):
        data_end = self.cleaned_data['data_end']
        return data_end

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        # Проверки на None для отображения сотрудников
        self.fields['staff'].queryset = Staff.objects.filter(category__in=['2'])
        self.fields['staff'].label_from_instance = lambda obj: (
            f"{obj.department.name if obj.department else 'Нет отдела'} - "
            f"{obj.name} "
            f"({obj.department.bet_local if obj.department and obj.department.bet_local is not None else 'Нет ставки'} / "
            f"{obj.department.bet if obj.department and obj.department.bet is not None else 'Нет ставки'})" if obj else 'Неизвестный сотрудник'
        )

        # Проверки на None для отображения разделов
        self.fields['chapter'].queryset = Chapter.objects.all()
        self.fields['chapter'].label_from_instance = lambda obj: obj.name if obj else 'Неизвестный раздел'

        # Проверки на None для отображения задач
        self.fields['task'].queryset = SettingTask.objects.all()
        self.fields['task'].label_from_instance = lambda \
            obj: obj.task.name if obj and obj.task else 'Неизвестная задача'

        # Проверка на None для заказчика
        self.fields['customer'].queryset = Staff.objects.filter(category__in=['3'])
        self.fields['customer'].label_from_instance = lambda obj: (
            f"{obj.username if obj.department else 'Нет компании'} - "
            f"{obj.name}" if obj else 'Неизвестный заказчик'
        )

        # Установим статус по умолчанию на 'start'
        self.fields['status'].initial = 'start'
