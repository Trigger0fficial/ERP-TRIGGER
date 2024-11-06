from django.db import models
from django.contrib.auth.models import AbstractUser


class TransactionPayment(models.Model):
    class Meta:
        verbose_name = 'Зарплатный проект'
        verbose_name_plural = 'Зарплатный проект'

    FIELD_CAT = [
        ('1', 'Зарплата'),
        ('2', 'Оплата заказчика'),
    ]

    data_salary = models.DateField(verbose_name='Дата оплаты')
    category = models.CharField(verbose_name='Категория', choices=FIELD_CAT, max_length=1)
    payment = models.IntegerField(verbose_name='Оплата')


class Department(models.Model):
    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
    name = models.CharField('Должность', max_length=155)
    bet = models.IntegerField(verbose_name='Ставка')
    bet_local = models.IntegerField(verbose_name='Внутренняя ставка')


class Staff(AbstractUser):
    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователь'

    FIELD_BANK = [
        ('t-bank', 'Т-банк'),
        ('sber', 'Сбербанк'),
        ('alpha', 'Альфа'),
        ('vtb', 'ВТБ'),
        ('other', 'Другое')
    ]

    FIELD_CAT = [
        ('1', 'Руководитель'),
        ('2', 'Сотрудник'),
        ('3', 'Заказчик')
    ]

    name = models.CharField('ФИО', max_length=155)
    category = models.CharField(verbose_name='Категория', choices=FIELD_CAT, max_length=1)
    department = models.ForeignKey(Department, verbose_name='Должность', on_delete=models.PROTECT, null=True, blank=True)
    transaction = models.ManyToManyField(TransactionPayment, verbose_name='Финансовая транзакция', blank=True, null=True)
    account_bank = models.CharField(verbose_name='Номер счета', max_length=30, null=True, blank=True)
    bank = models.CharField(verbose_name='Банк', max_length=20, choices=FIELD_BANK, default='null', null=True, blank=True)


class FileTask(models.Model):
    class Meta:
        verbose_name = 'Файл к задаче'
        verbose_name_plural = 'Файлы к задачам'

    file = models.FileField(verbose_name='Файл', upload_to='project/task/%Y/%m/%d/')


class Task(models.Model):
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    name = models.CharField(verbose_name='Наименование задачи', max_length=155)
    dsc = models.TextField(verbose_name='Описание задачи')
    files = models.ManyToManyField(FileTask, verbose_name='Файлы', blank=True, null=True)


class ReportingChapter(models.Model):
    class Meta:
        verbose_name = 'Отчет о разделе'
        verbose_name_plural = 'Отчет о разделах'

    STATUS_FIELD = [
        ('verification', 'На проверке'),
        ('adopted', 'Принят'),
        ('rejected', 'Отклонен')
    ]

    data_start = models.DateTimeField(verbose_name='Дата подачи')
    data_end = models.DateTimeField(verbose_name='Дата обратной связи', blank=True, null=True)
    report_executor = models.CharField(verbose_name='Отчет от исполнителя', max_length=500)
    comment_customer = models.CharField(verbose_name='Комментарий от заказчика', max_length=500, blank=True, null=True)
    status = models.CharField(verbose_name='Статус', max_length=20, choices=STATUS_FIELD, default='verification')


class Chapter(models.Model):
    class Meta:
        verbose_name = 'Раздел задачи'
        verbose_name_plural = 'Разделы задач'

    STATUS_FIELD = [
        ('Not_started', 'Не начат'),
        ('Started', 'Начат'),
        ('verification', 'На проверке'),
        ('adopted', 'Принят'),
        ('rejected', 'Отклонен')
    ]

    name = models.CharField(verbose_name='Наименование раздела', max_length=155)
    tasks = models.ManyToManyField(Task, verbose_name='Задачи')
    reporting = models.ManyToManyField(ReportingChapter, verbose_name='Отчеты', null=True, blank=True)
    status = models.CharField(verbose_name='Статус', max_length=30, choices=STATUS_FIELD, default='Not_started')


class ReportingTask(models.Model):
    class Meta:
        verbose_name = 'Отчет о задаче'
        verbose_name_plural = 'Отчет о задачах'

    STATUS_FIELD = [
        ('verification', 'На проверке'),
        ('adopted', 'Принят'),
        ('rejected', 'Отклонен')
    ]

    data_start = models.DateTimeField(verbose_name='Дата подачи')
    data_end = models.DateTimeField(verbose_name='Дата обратной связи', blank=True, null=True)
    report_stuff = models.CharField(verbose_name='Отчет от сотрудника', max_length=500)
    comment_director = models.CharField(verbose_name='Комментарий от директора', max_length=500, blank=True, null=True)
    status = models.CharField(verbose_name='Статус', max_length=20, choices=STATUS_FIELD, default='verification')


class ActivityTask(models.Model):
    class Meta:
        verbose_name = 'Активность задачи'
        verbose_name_plural = 'Активность задач'

    data_start = models.DateTimeField(verbose_name='Начало')
    data_end = models.DateTimeField(verbose_name='Начало', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Завершена', default=False)


class SettingTask(models.Model):
    class Meta:
        verbose_name = 'Постановка задачи'
        verbose_name_plural = 'Постановка задач'

    STATUS_FIELD = [
        ('Not_started', 'Не начата'),
        ('Started', 'Начата'),
        ('verification', 'На проверке'),
        ('adopted', 'Принят'),
        ('rejected', 'Отклонен')
    ]

    staff = models.ForeignKey(Staff, verbose_name='Сотрудник', on_delete=models.PROTECT)
    task = models.ForeignKey(Task, verbose_name='Задача', on_delete=models.PROTECT)
    scheduled_hours = models.IntegerField(verbose_name='Плановые часы')
    actual_hours = models.IntegerField(verbose_name='Фактические часы', null=True, blank=True)
    scheduled_day = models.IntegerField(verbose_name='Плановые дни')
    actual_day = models.IntegerField(verbose_name='Фактические дни', null=True, blank=True)
    activity = models.ManyToManyField(ActivityTask, verbose_name='Активность проекта', blank=True, null=True)
    reportings = models.ManyToManyField(ReportingTask, verbose_name='Отчеты от сотрудника', null=True, blank=True)
    status = models.CharField(verbose_name='Статус', max_length=30, choices=STATUS_FIELD, default='Not_started')
    is_started = models.BooleanField(verbose_name='Активна', default=False)
    is_active = models.BooleanField(verbose_name='Завершена', default=False)


class AdditionalCosts(models.Model):
    class Meta:
        verbose_name = 'Дополнительные затраты'
        verbose_name_plural = 'Дополнительные затраты'

    percent = models.IntegerField(verbose_name='Процент')

    def __str__(self):
        return f'{self.percent}%'


class DocumentProject(models.Model):
    class Meta:
        verbose_name = 'Документы к проекту'
        verbose_name_plural = 'Документы к проектам'

    FIELD_CAT = [
        ('1', 'Договор'),
        ('2', 'Смета'),
        ('3', 'Локальная смета'),
        ('4', 'Доп. соглашение'),
        ('5', 'Платежные документы'),
        ('6', 'Акт о закрытии работ'),
        ('7', 'Приложение к договору'),
        ('8', 'Акт')
    ]

    name = models.CharField(verbose_name='Наименование проекта', max_length=155)
    data_load = models.DateField(verbose_name='Дата загрузки', auto_created=True)
    category = models.CharField(verbose_name='Категория', choices=FIELD_CAT, max_length=2)
    document = models.FileField(verbose_name='Документ', upload_to='project/document/%Y/%m/%d/')


class Project(models.Model):
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    FIELD_STATUS = [
        ('start', 'Оформление'),
        ('Signing_contract', 'Подписание договора'),
        ('Development', 'Разработка'),
        ('Delivery_works', 'Сдача работ'),
        ('Waiting', 'В ожидании'),
        ('Cancel', 'Отменен'),
        ('Completed', 'Завершен')
    ]

    name = models.CharField(verbose_name='Наименование проекта', max_length=155)
    staff = models.ManyToManyField(Staff, verbose_name='Сотрудники')
    data_start = models.DateField(verbose_name='Дата начала', null=True, blank=True)
    data_end = models.DateField(verbose_name='Дата окончания', null=True, blank=True)
    chapter = models.ManyToManyField(Chapter, verbose_name='Разделы')
    task = models.ManyToManyField(SettingTask, verbose_name='Поставленные задачи', null=True, blank=True)
    transaction = models.ManyToManyField(TransactionPayment, verbose_name='Финансовая транзакция', blank=True,
                                         null=True)
    additional_costs = models.ForeignKey(AdditionalCosts, verbose_name='Дополнительные затраты', on_delete=models.PROTECT)
    status = models.CharField(verbose_name='Статус', choices=FIELD_STATUS, max_length=20, default='Signing_contract')
    documents = models.ManyToManyField(DocumentProject, verbose_name='Документы', null=True, blank=True)
    payment_client = models.IntegerField(verbose_name='Оплачено клиентом', default=0)
    total_cost = models.IntegerField(verbose_name='Итоговая стоимость', null=True, blank=True)
    expected_costs = models.IntegerField(verbose_name='Ожидаемые затраты', null=True, blank=True)
    actual_costs = models.IntegerField(verbose_name='Фактические затраты', null=True, blank=True)
    expected_profits = models.IntegerField(verbose_name='Ожидаемая прибыль', null=True, blank=True)
    actual_profits = models.IntegerField(verbose_name='Фактическая прибыль', null=True, blank=True)












