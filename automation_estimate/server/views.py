import openpyxl
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import *
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail

import logging


logger = logging.getLogger(__name__)

def pattern_views(req):
    projects = Project.objects.exclude(status='Completed')
    customers = Staff.objects.filter(category='3')
    staffs = Staff.objects.all()
    user = Staff.objects.get(id=req.user.id)
    data = {
        'user': user,
        'customers': customers,
        'staffs': staffs,
        'projects': projects
    }

    return render(req, 'server/technical/index.html', data)


def show_login(req):
    if req.method == 'POST':
        form = CustomLoginForm(req, data=req.POST)
        if form.is_valid():
            login(req, form.get_user())
            return redirect('total_projects')
        else:
            messages.error(req, "Неправильный логин или пароль.")
    else:
        form = CustomLoginForm()

    data = {
        'form': form,
        'messages': messages.get_messages(req),
    }

    return render(req, 'server/authentication-signin.html', data)


def show_register(req):
    if req.method == 'POST':
        form = StaffRegistrationForm(req.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            if form.cleaned_data.get('category') == '3':
                messages.success(req, "Вы успешно зарегистрированы!")
                send_mail(f'ERP SYSTEM Сокол. Служба поддержки',
                          f'Здравствуйте, {user.name}!\n'
                          f'Ваш аккаунт на платформе "ERP SYSTEM - отслеживание заказов" был успешно зарегистрирован!\n'
                          f'Данные для входа:\n'
                          f'Логин: {user.username}\n'
                          f'Пароль: {form.cleaned_data.get("password1")}\n'
                          f'С наилучшими пожеланиями, команда "Сокол"',
                          'officialtriggermobile@gmail.com',
                          [user.email], fail_silently=False)
            elif form.cleaned_data.get('category') == '2':
                send_mail(f'ERP SYSTEM Сокол. Служба поддержки',
                          f'Здравствуйте, {user.name}!\n'
                          f'Твой аккаунт на платформе "ERP SYSTEM - отслеживание проектов" был успешно зарегистрирован!\n'
                          f'Данные для входа:\n'
                          f'Логин: {user.username}\n'
                          f'Пароль: {form.cleaned_data.get("password1")}',
                          'officialtriggermobile@gmail.com',
                          [user.email], fail_silently=False)
            elif form.cleaned_data.get('category') == '1':
                send_mail(f'ERP SYSTEM Сокол. Служба поддержки',
                          f'Здравствуйте, {user.name}!\n'
                          f'Ваш административный аккаунт на платформе "ERP SYSTEM - отслеживание проектов" был успешно зарегистрирован!\n'
                          f'Данные для входа:\n'
                          f'Логин: {user.username}\n'
                          f'Пароль: {form.cleaned_data.get("password1")}',
                          'officialtriggermobile@gmail.com',
                          [user.email], fail_silently=False)
            return redirect('login')
        else:
            messages.error(req, "Исправьте ошибки в форме.")
    else:
        form = StaffRegistrationForm()

    data = {
        'form': form,
    }

    return render(req, 'server/authentication-signup.html', data)

@login_required(login_url='login')
def show_total_projects(req):
    projects = Project.objects.exclude(status='Completed')

    # Инициализация сумм и счетчика проектов
    sum_payment_client = 0
    sum_total_cost = 0
    sum_expected_costs = 0
    sum_actual_costs = 0
    sum_expected_profits = 0
    sum_actual_profits = 0
    project_count = 0  # Счетчик проектов

    list_project_profit_costs = []
    total_costs = []
    project_names = []

    forecast_profit_projects = 0

    # Итерация по проектам
    for project in projects:
        sum_payment_client += project.payment_client
        sum_total_cost += project.total_cost if project.total_cost else 0  # Проверка на None
        sum_expected_costs += project.expected_costs if project.expected_costs else 0  # Проверка на None
        sum_actual_costs += project.actual_costs if project.actual_costs else 0  # Проверка на None
        sum_expected_profits += project.expected_profits if project.expected_profits else 0  # Проверка на None
        sum_actual_profits += project.actual_profits if project.actual_profits else 0  # Проверка на None
        project_count += 1  # Увеличиваем счетчик проектов

    # Расчет отклонения фактической прибыли от ожидаемой
    if sum_expected_profits != 0:
        deviation_actual_profit_expected = round(
            ((sum_actual_profits - sum_expected_profits) / sum_expected_profits) * 100, 2)
    else:
        deviation_actual_profit_expected = 0

    # Расчет отклонения суммы платежей от общей стоимости
    if sum_total_cost != 0:
        deviation_sum_total_cost = round(((sum_payment_client - sum_total_cost) / sum_total_cost) * 100, 2)
    else:
        deviation_sum_total_cost = 0

    # Расчет среднего отклонения от бюджета
    if project_count > 0:  # Проверка на наличие проектов
        total_budget_deviation = sum(
            (project.expected_costs - project.actual_costs) for project in Project.objects.exclude(status='Completed')
            if project.expected_costs is not None and project.actual_costs is not None)
        average_deviation_coefficient = round(
            (total_budget_deviation / (sum_expected_costs if sum_expected_costs > 0 else 1)), 2)
    else:
        average_deviation_coefficient = 0

    # Расчет фактической рентабельности в процентах
    if sum_actual_costs != 0:
        profitability_percentage = round((sum_actual_profits / sum_actual_costs) * 100, 2)
    else:
        profitability_percentage = 0  # Если фактические затраты отсутствуют, рентабельность равна 0

    # Расчет планируемой рентабельности в процентах
    if sum_expected_costs != 0:
        expected_profitability_percentage = round((sum_expected_profits / sum_expected_costs) * 100, 2)
    else:
        expected_profitability_percentage = 0  # Если ожидаемые затраты отсутствуют, планируемая рентабельность равна 0

    # Расчет отклонения рентабельности
    if expected_profitability_percentage != 0:  # Проверка на деление на ноль
        profitability_deviation_percentage = round((profitability_percentage / expected_profitability_percentage) * 100,
                                                   2)
    else:
        profitability_deviation_percentage = 0  # Если планируемая рентабельность равна 0, отклонение равно 0

    # Сбор статистики
    general_statistics = {
        'deviation_actual_profit_expected': [round(sum_actual_profits, 2), round(sum_expected_profits, 2),
                                             round(deviation_actual_profit_expected + 100, 2)],
        'percentage_payment_received_from_client': [round(sum_payment_client, 2), sum_total_cost,
                                                    round(deviation_sum_total_cost + 100, 2)],
        'average_deviation_from_budget': [round(average_deviation_coefficient + 1, 2),
                                          round((average_deviation_coefficient + 1)*100, 2)],
        'overall_project_profitability_percentage': [round(profitability_percentage, 2),
                                                     round(expected_profitability_percentage, 2),
                                                     round(profitability_deviation_percentage, 2)],

    }

    for project in projects:
        list_project_profit_costs.append(
            [project.name, project.total_cost, project.expected_profits, project.actual_profits]
        )
        total_costs.append(project.total_cost)
        project_names.append(project.name)

    all_task = 0
    for project in Project.objects.all():
        for chapter_task in project.chapter.all():
            for _ in chapter_task.tasks.all():
                all_task += 1

    all_count_hour = 0
    all_payment = 0
    for project in Project.objects.all():
        for task in project.task.all():
            all_count_hour += task.actual_hours
            if task.staff.department.bet_local != 0:
                all_payment += task.actual_hours * task.staff.department.bet_local

    list_projects = [
        [project.name, project.expected_profits, project.actual_profits]
        for project in projects
    ]

    list_projects_hour = []
    for index, project in enumerate(projects):
        list_projects_hour.append([project.name])
        scheduled = 0
        actual = 0
        for task in project.task.all():
            scheduled += 1
            if task.is_active:
                actual += 1
        list_projects_hour[index].extend([actual, scheduled, project.get_status_display(), project.data_start])

    list_average_hour_projects = []
    sum_plan = 0
    count_hours = 0
    sum_fact = 0
    sum_payment_plan = 0
    sum_payment_fact = 0

    for project in projects:
        for task in project.task.all():
            sum_plan += task.scheduled_hours
            sum_fact += task.actual_hours
            if task.staff.department.bet_local != 0:
                sum_payment_plan += task.scheduled_hours * task.staff.department.bet_local
                sum_payment_fact += task.actual_hours * task.staff.department.bet_local
            count_hours += 1

    # Проверки на деление на ноль
    average_hours_plan = sum_plan / count_hours if count_hours != 0 else 0
    average_hours_fact = sum_fact / count_hours if count_hours != 0 else 0
    average_payment_plan = sum_payment_plan / count_hours if count_hours != 0 else 0
    average_payment_fact = sum_payment_fact / count_hours if count_hours != 0 else 0

    deviation_hours = (average_hours_fact / average_hours_plan * 100) if average_hours_plan != 0 else 0
    deviation_payment = (average_payment_fact / average_payment_plan * 100) if average_payment_plan != 0 else 0

    list_average_hour_projects.append([
        round(average_hours_plan), round(average_hours_fact),
        round(average_payment_plan), round(average_payment_fact),
        100 - round(deviation_hours), 100 - round(deviation_payment)
    ])

    list_total_reporting_project = []
    forecast_profit_projects = 0
    for i, project in enumerate(projects):
        sum_task = 0
        sum_task_done = 0
        sum_deviation = 0
        sum_bet = 0
        total_expenses = 0

        # Начальные данные проекта
        list_total_reporting_project.append([
            project.name,
            project.get_status_display(),
            project.payment_client,
            project.total_cost,
            project.actual_profits,
            project.expected_profits,
            project.data_start,
            project.data_end
        ])

        # Проходим по задачам проекта
        for task in project.task.all():
            sum_task += 1  # Увеличиваем количество задач
            sum_bet += task.staff.department.bet_local
            total_expenses += task.staff.department.bet_local * task.actual_hours

            if task.is_active:
                sum_task_done += 1  # Увеличиваем количество завершенных задач
                if task.actual_hours != 0:
                    sum_deviation += (task.scheduled_hours / task.actual_hours) * 100

        # Проверка деления на ноль для среднего значения
        average_bet = sum_bet / sum_task if sum_task != 0 else 0
        average_deviation = sum_deviation / sum_task_done if sum_task_done != 0 else 0

        forecast_hour = 0
        for task_not_done in project.task.filter(is_active=False):
            forecast_hour += task_not_done.scheduled_hours + (task_not_done.scheduled_hours * average_deviation) / 100

        forecast_payment = project.total_cost - total_expenses - average_bet * forecast_hour
        forecast_profit_projects += round(forecast_payment)



        # Рассчитываем процент завершенных задач
        percentage_task = (sum_task_done / sum_task) * 100 if sum_task > 0 else 0

        # Расчет плановой рентабельности
        planned_profitability = (project.expected_profits / project.total_cost) * 100 if project.total_cost > 0 else 0

        # Расчет фактической рентабельности
        actual_profitability = (project.actual_profits / project.total_cost) * 100 if project.total_cost > 0 else 0

        # Обновляем данные в отчете
        list_total_reporting_project[i].append(round(percentage_task))   # Процент завершения задач
        list_total_reporting_project[i].append(round(planned_profitability, 2))  # Плановая рентабельность
        list_total_reporting_project[i].append(round(actual_profitability, 2))  # Фактическая рентабельность
        list_total_reporting_project[i].append(round(forecast_payment, 2))  # Прогнозируемая прибыль
        list_total_reporting_project[i].append(round(average_deviation, 2))  # Среднее отклонение

    total_payment_client = 0
    total_expenses = 0
    for project in projects:
        total_payment_client += project.payment_client
        for task in project.task.all():
            total_expenses += task.actual_hours * task.staff.department.bet_local


    data = {
        'data_name': f'Добро пожаловать, {req.user.name}!',
        'general_statistics': general_statistics,
        'project_profit_costs': list_project_profit_costs,
        'total_cost': total_costs,
        'project_names': project_names,
        'min_static_project': [all_task, all_payment, all_count_hour],
        'projects_expected_profits': list_projects,
        'list_projects_hour': list_projects_hour,
        'list_average_hour_projects': list_average_hour_projects,
        'list_total_reporting_project': list_total_reporting_project,
        'actual_balance': total_payment_client-total_expenses,
        'forecast_profit_projects': forecast_profit_projects
    }



    return render(req, 'server/total_projects.html', data)


def show_list_projects(req):


    data = {
        'data_name': 'Список проектов',
        'projects': Project.objects.all()
    }

    return render(req, 'server/list_projects.html', data)


def show_detail_project(req, pk):
    project = Project.objects.get(id=pk)

    # Расчёт израсходываемых средств
    allocated_money, spent_money = 0, 0
    for task in project.task.all():
        allocated_money += task.scheduled_hours * task.staff.department.bet_local
        spent_money += task.actual_hours * task.staff.department.bet_local

    remaining_money = allocated_money - spent_money
    print(f'allocated_money - {allocated_money}'
          f'spent_money - {spent_money}'
          f'percent_remaining_money - {spent_money * 100 / allocated_money if allocated_money != 0 else 0}')
    percent_remaining_money = spent_money * 100 / allocated_money if allocated_money != 0 else 0
    if percent_remaining_money < 0:
        percent_remaining_money = 0

    # Расчет выполненных задач и соотношение факт от плана
    total_fact_hour = 0
    total_plan_hour = 0
    total_is_done_task = 0
    total_task = 0
    for task in project.task.all():
        if task.is_active:
            total_is_done_task += 1
            total_fact_hour += task.actual_hours
            total_plan_hour += task.scheduled_hours
        total_task += 1

    average_fact_hour = total_fact_hour / total_is_done_task if total_is_done_task != 0 else 0
    average_plan_hour = total_plan_hour / total_is_done_task if total_is_done_task != 0 else 0
    percent_hour = round(100 - (average_fact_hour / average_plan_hour * 100) if average_plan_hour != 0 else 0, 2)

    # Расчет косвенных значений
    sum_task = 0
    sum_task_done = 0
    sum_deviation = 0
    sum_bet = 0
    total_expenses = 0
    list_total_reporting_project = []
    forecast_profit_projects = 0

    # Проходим по задачам проекта
    for task in project.task.all():
        sum_task += 1
        sum_bet += task.staff.department.bet_local
        total_expenses += task.staff.department.bet_local * task.actual_hours

        if task.is_active:
            sum_task_done += 1
            sum_deviation += (task.scheduled_hours / task.actual_hours * 100) if task.actual_hours != 0 else 0

    average_bet = sum_bet / sum_task if sum_task != 0 else 0
    average_deviation = sum_deviation / sum_task_done if sum_task_done != 0 else 0

    forecast_hour = 0
    for task_not_done in project.task.filter(is_active=False):
        forecast_hour += task_not_done.scheduled_hours + (task_not_done.scheduled_hours * average_deviation / 100 if average_deviation != 0 else 0)

    forecast_payment = project.total_cost - total_expenses - average_bet * forecast_hour
    forecast_profit_projects += round(forecast_payment)

    # Рассчитываем процент завершенных задач
    percentage_task = (sum_task_done / sum_task * 100) if sum_task > 0 else 0

    # Расчет плановой рентабельности
    planned_profitability = (project.expected_profits / project.total_cost * 100) if project.total_cost > 0 else 0

    # Расчет фактической рентабельности
    actual_profitability = (project.actual_profits / project.total_cost * 100) if project.total_cost > 0 else 0

    # Обновляем данные в отчете
    list_total_reporting_project.append(round(percentage_task))  # Процент завершения задач
    list_total_reporting_project.append(round(planned_profitability, 2))  # Плановая рентабельность
    list_total_reporting_project.append(round(actual_profitability, 2))  # Фактическая рентабельность
    list_total_reporting_project.append(round(forecast_payment))  # Прогнозируемая прибыль
    list_total_reporting_project.append(round(average_deviation) - 100)  # Среднее отклонение

    #проверка на условия Nan и int
    if type(remaining_money) != int and remaining_money < 0:
        remaining_money = 'Не определено'
    if type(percent_remaining_money) != int and remaining_money < 0:
        percent_remaining_money = 'Не определено'
    if type(allocated_money) != int and remaining_money < 0:
        allocated_money = 'Не определено'
    if type(total_is_done_task) != int and remaining_money < 0:
        total_is_done_task = 'Не определено'
    if type(total_task) != int and remaining_money < 0:
        total_task = 'Не определено'
    for el in list_total_reporting_project:
        if type(el) != int and remaining_money < 0:
            el = 'Не определено'
    if type(average_fact_hour) != int and remaining_money < 0:
        average_fact_hour = 'Не определено'
    if type(average_plan_hour) != int and remaining_money < 0:
        average_plan_hour = 'Не определено'
    if type(percent_hour) != int and remaining_money < 0:
        percent_hour = 'Не определено'

    # Таблица задач
    list_table_tasks = []
    for task in project.task.all():
        list_table_tasks.append([
            task.task.name,
            task.staff.name,
            [task.actual_hours, task.scheduled_hours],
            [task.actual_hours*task.staff.department.bet_local, task.scheduled_hours*task.staff.department.bet_local],
            [task.actual_hours*task.staff.department.bet_local-task.scheduled_hours*task.staff.department.bet_local,
             (task.actual_hours*task.staff.department.bet_local)/(task.scheduled_hours*task.staff.department.bet_local)*100-100],
            task.scheduled_hours * task.staff.department.bet,
            task.get_status_display,
            [task.scheduled_hours*task.staff.department.bet-task.actual_hours*task.staff.department.bet_local,
             task.scheduled_hours*task.staff.department.bet-task.scheduled_hours*task.staff.department.bet_local],
        ])


    data = {
        'data_name': project.name,
        'project': project,
        'remaining_money': [remaining_money, percent_remaining_money, allocated_money],
        'task_done': [total_is_done_task, total_task],
        'list_total_reporting_project': list_total_reporting_project,
        'average_plan_fact_hour': [average_fact_hour, average_plan_hour, percent_hour],
        'list_table_tasks': list_table_tasks
    }

    return render(req, 'server/detail_project.html', data)


def show_create_project(req):
    if req.method == 'POST':
        form = ProjectForm(req.POST, req.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            project.staff.set(form.cleaned_data['staff'])
            project.chapter.set(form.cleaned_data['chapter'])
            project.task.set(form.cleaned_data['task'])
            expected_costs = 0
            total_cost = 0
            for task in form.cleaned_data['task']:
                expected_costs += task.scheduled_hours * task.staff.department.bet_local
                total_cost += task.scheduled_hours * task.staff.department.bet
            project.total_cost = total_cost + (total_cost * 10 / 100)
            project.expected_costs = expected_costs
            project.expected_profits = total_cost + (total_cost * 10 / 100) - expected_costs
            project.actual_profits = 0
            project.actual_costs = 0
            project.save()
            return redirect('all_projects')
        else:
            logger.error(form.errors)  # Логируем ошибки валидации
    else:
        form = ProjectForm()  # Создаем пустую форму

    # Получаем необходимые данные для отображения в форме
    data = {
        'data_name': 'Новый проект',
        'form': form,
        'list_stuff': Staff.objects.filter(category__in=['2']),
        'list_chapter': Chapter.objects.filter(project__isnull=True),
        'list_tasks': SettingTask.objects.filter(project__isnull=True),
        'list_customer': Staff.objects.filter(category__in=['3'])
    }

    return render(req, 'server/create_project.html', data)

def generate_client_estimate(request, pk):
    # Получаем проект по ID
    project = Project.objects.get(id=pk)

    # Создаем новую книгу Excel
    wb = openpyxl.Workbook()
    ws = wb.active

    # Заголовки для таблицы (аналогично структуре, которую ты предоставил)
    headers = ['Задача', 'Сотрудник', 'План (часы)', 'Факт (часы)', 'План (дни)', 'Факт (дни)', 'Ставка',
               'Итоговая стоимость']
    ws.append(headers)

    # Идем по разделам проекта
    for chapter in project.chapter.all():
        ws.append([chapter.name])  # Добавляем название раздела

        # Идем по задачам в разделе
        for task in chapter.tasks.all():
            # Получаем задачи для каждого сотрудника
            for setting_task in task.settingtask_set.filter(staff__in=project.staff.all()):
                staff_name = setting_task.staff.name
                department_bet = setting_task.staff.department.bet  # Используем ставку для заказчика

                # Расчет итоговой стоимости по задаче
                total_cost = setting_task.scheduled_hours * department_bet

                # Заполняем строку с данными по задаче
                ws.append([
                    task.name,
                    staff_name,
                    setting_task.scheduled_hours,
                    setting_task.actual_hours or 0,
                    setting_task.scheduled_day,
                    setting_task.actual_day or 0,
                    department_bet,
                    total_cost
                ])

    # Формируем итоговые строки по проекту
    ws.append([])
    ws.append(['Итоговая стоимость проекта:', project.total_cost])

    # Генерация ответа для скачивания
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=client_estimate_{pk}.xlsx'
    wb.save(response)

    return response

