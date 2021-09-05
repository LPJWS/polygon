import re
from django.contrib.auth import password_validation
from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout


from polygon.models import User
from polygon.serializers import *

from polygon import utils
from django.template import loader

import json
from datetime import datetime


@action(methods=['POST'], detail=False, url_path='signup', url_name='Sign Up User', permission_classes=(AllowAny,))
def signup(request):
    if request.method == 'GET':
        context = {}
        return render(request, 'signup.html', context)
    else:
        data = request.POST
        user, created = User.objects.get_or_create(username=data['login'])
        if created:
            user.name = data['name']
            group, created = Group.objects.get_or_create(title=data['group'])
            if created:
                group.save()
            user.group = group
            user.set_password(data['psw'])
            user.save()
            login(request, user)
            return redirect('/')
        else:
            context = {'message': 'Пользователь с таким логином уже существует'}
            return render(request, 'signup.html', context)


@action(methods=['GET', 'POST'], detail=False, url_path='signin', url_name='Sign In User', permission_classes=(AllowAny,))
def signin(request):
    if request.method == 'GET':
        context = {}
        return render(request, 'signin.html', context)
    else:
        data = request.POST
        user = authenticate(username=data['login'], password=data['psw'])
        if user is None:
            context = {'message': 'Неверный логин и/или пароль'}
            return render(request, 'signin.html', context)
        login(request, user)
        return redirect('/')


@action(methods=['GET'], detail=False, url_path='logout', url_name='Logout', permission_classes=(IsAuthenticated,))
def logout_(request):
    logout(request)
    return redirect("/signin")


@action(methods=['GET'], detail=False, url_path='', url_name='Admin page', permission_classes=(IsAuthenticated,))
def admin_page(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/signin')
    if not user.is_superuser:
        template = 'home.html'
        tasks = Task.objects.all().order_by('order')
        res = []
        ptr = -1
        t = True
        for task in tasks:
            print(task.material)
            if t:
                res.append([])
                ptr += 1
                t = False
                res[ptr].append(task)
            else:
                t = True
                res[ptr].append(task)
        context = {'user': user, 'tasks': res}
    else:
        template = 'admin.html'
        context = {'user': user}
    return render(request, template, context)


@action(methods=['GET'], detail=False, url_path='w_get_pass', url_name='Lab 1 get pass', permission_classes=(IsAuthenticated,))
def w_get_pass(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponse(json.dumps({'status': 'error', 'error': 'Permission denied'}), status=403)

    return HttpResponse(utils.get_pass())


@csrf_exempt
@action(methods=['POST'], detail=False, url_path='w_change_pass', url_name='Lab 1 change pass', permission_classes=(IsAuthenticated,))
def w_change_pass(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponse(json.dumps({'status': 'error', 'error': 'Permission denied'}), status=403)
    task = Task.objects.get(title="Подключение к роутеру по WiFi без пароля")
    data = json.loads(utils.change_pass())
    if data['status'] == 'error':
        return HttpResponse(json.dumps(data))
    new_pass = data['response']['password']
    task.flag = new_pass
    task.save()
    return HttpResponse(json.dumps(data))


def b_get_count(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponse(json.dumps({'status': 'error', 'error': 'Permission denied'}), status=403)
    count = utils.get_count()
    return HttpResponse(json.dumps({"status": "ok", "response": {"count": count}}))


@csrf_exempt
def b_clear(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponse(json.dumps({'status': 'error', 'error': 'Permission denied'}), status=403)
    task = Task.objects.get(title="Эксплуатация Bash-уязвимости")
    task.flag = utils.clear()
    task.save()
    return HttpResponse(json.dumps({"status": "ok", "response": {"count": 1}}))


@csrf_exempt
@action(methods=['POST'], detail=False, url_path='send_flag', url_name='Send flag', permission_classes=(IsAuthenticated,))
def send_flag(request, task_id):
    user = request.user
    if not user.is_authenticated:
        return HttpResponse(json.dumps({"status": "error", "error": "Вы не авторизованы"}))
    data = request.POST
    task = Task.objects.get(id=task_id)

    # if task.title == "Подключение к роутеру по WiFi без пароля":
    #     data_ = json.loads(utils.get_pass())
    #     if data_['status'] == 'ok':
    #         flag = data_['response']['password']
    #         if data['flag'] == flag:
    #             utils.change_pass()
    #             ts, created = TaskSolve.objects.get_or_create(task=task, student=user)
    #             if created:
    #                 ts.save()
    #                 return HttpResponse(json.dumps({"status": "ok", "response": "correct"}))
    #         else:
    #             return HttpResponse(json.dumps({"status": "ok", "response": "wrong"}))
    #     else:
    #         return HttpResponse(json.dumps(data_))

    if task.flag == data['flag']:
        if task.title == "Эксплуатация Bash-уязвимости":
            task.flag = utils.clear()
            task.save()
        elif task.title == "Подключение к роутеру по WiFi без пароля":
            task.flag = json.loads(utils.change_pass())['response']['password']
            task.save()
        ts, created = TaskSolve.objects.get_or_create(task=task, student=user)
        if created:
            ts.save()
        return HttpResponse(json.dumps({"status": "ok", "response": "correct"}))
    else:
        return HttpResponse(json.dumps({"status": "ok", "response": "wrong"}))


def results(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/signin')
    if not user.is_superuser:
        template = 'results.html'
        tasks_solved = TaskSolve.objects.filter(student=user)
        context = {'user': user, 'tasks': tasks_solved}
    else:
        template = 'admin_results.html'
        tasks_solved = TaskSolve.objects.all().order_by('student__group', 'student__name')
        students = User.objects.all().exclude(id=user.id)
        tasks = Task.objects.all()
        context = {'user': user, 'tasks': tasks_solved, 'students': students, 'tasks_raw': tasks}
    return render(request, template, context)


def results_student(request, student_id):
    user = request.user
    if not user.is_superuser:
        return HttpResponse(json.dumps({'status': 'error', 'error': 'Permission denied'}), status=403)
    template = 'admin_results.html'
    student = User.objects.get(id=student_id)
    tasks_solved = TaskSolve.objects.filter(student=student)
    students = User.objects.filter(id=student_id)
    tasks = Task.objects.all()
    context = {'user': user, 'tasks': tasks_solved, 'students': students, 'tasks_raw': tasks, 'message': f'{student.name}'}
    return render(request, template, context)


def results_group(request, group_id):
    user = request.user
    if not user.is_superuser:
        return HttpResponse(json.dumps({'status': 'error', 'error': 'Permission denied'}), status=403)
    template = 'admin_results.html'
    group = Group.objects.get(id=group_id)
    tasks_solved = TaskSolve.objects.filter(student__group=group)
    students = User.objects.all().exclude(id=user.id).filter(group=group)
    tasks = Task.objects.all()
    context = {'user': user, 'tasks': tasks_solved, 'students': students, 'tasks_raw': tasks, 'message': f'{group.title}'}
    return render(request, template, context)


def results_task(request, task_id):
    user = request.user
    if not user.is_superuser:
        return HttpResponse(json.dumps({'status': 'error', 'error': 'Permission denied'}), status=403)
    template = 'admin_results.html'
    task = Task.objects.get(id=task_id)
    tasks_solved = TaskSolve.objects.filter(task=task)
    students = User.objects.all().exclude(id=user.id)
    tasks = Task.objects.filter(id=task_id)
    context = {'user': user, 'tasks': tasks_solved, 'students': students, 'tasks_raw': tasks, 'message': f'{task.title}'}
    return render(request, template, context)


@csrf_exempt
def accept(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponse(json.dumps({'status': 'error', 'error': 'Permission denied'}), status=403)
    data = request.POST
    task = TaskSolve.objects.get(id=data['task'])
    task.date_accepted = datetime.now()
    task.save()
    return HttpResponse(json.dumps({"status": "ok", "response": ""}))


@csrf_exempt
def accept_manual(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponse(json.dumps({'status': 'error', 'error': 'Permission denied'}), status=403)
    data = request.POST
    task = Task.objects.get(id=data['task'])
    student = User.objects.get(id=data['student'])
    task_solved, created = TaskSolve.objects.get_or_create(task=task, student=student)
    if created:
        task_solved.save()
    return HttpResponse(json.dumps({"status": "ok", "response": ""}))
