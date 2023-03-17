import csv
import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template import loader

from .hierarchie import unauthenticated_user
from .models import Member
from django.http import HttpResponse
from .forms import CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def accueil(request):
    return render(request, 'accueil.html')


@login_required(login_url='login')  # pour interdire l acees si tu n es pas connecte
def members(request):
    mymembers = Member.objects.all().values()
    template = loader.get_template('all_members.html')
    context = {
        'mymembers': mymembers,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login')
def details(request, id):
    mymember = Member.objects.get(id=id)
    template = loader.get_template('details.html')
    context = {
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login')  # on met cela avant chaque methode acessible avec un login
def main(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render())


def testing(request):
    mydata = Member.objects.values_list('firstname')
    template = loader.get_template('template.html')
    context = {
        'mymembers': mydata,
    }
    return HttpResponse(template.render(context, request))


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Votre compte est crée ' + user)  # source : django documentation
            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.user.is_authenticated:  # ces deux lignes interdit l acces a la page de login si on est deja connecte
        return redirect('main')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('main')  # main est le nom dens urls.py
            else:
                messages.info(request, 'Erreur dans le nom ou dans le mot de passe')
        context = {}
        return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def testtest(request):
    api_key = 'Z8O8EWVEWLEFPD4X'
    if request.method == 'POST':
        nomAction = request.POST.get('nomAction', '')
        CSV_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=" + nomAction + "&interval=60min&slice=year1month1&apikey=" + api_key
        with requests.Session() as s:
            download = s.get(CSV_URL)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
        context = {
            'my_list': my_list,
            'nomAction': nomAction
        }
    else:
        context = {}
    return render(request, 'testtest.html', context)
