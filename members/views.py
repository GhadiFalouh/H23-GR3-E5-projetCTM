import csv
import requests
import random
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template import loader
from .models import Member, Action, PorteFeuille
from django.http import HttpResponse
from .forms import CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def accueil(request):
    return render(request, 'accueil.html')


@login_required(login_url='login')  # pour interdire l acees sans si tu nes pas connecte
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

    # print(mymember.firstname) sa marche
    if request.user.is_authenticated and request.user.username == mymember.username:  # on verifie si l utilsateur va dans son profil
        return redirect('moncompte', id=mymember.id)
    context = {
        'mymember': mymember,
    }
    return render(request, 'details.html', context)


# Seul le membre associé a cette portefeuille a le droit d'accéder à cela
@login_required(login_url='login')
def moncompte(request, id):
    firstname = request.user.first_name
    if request.method == 'POST':
        action = request.POST.get('action')
        mymember = Member.objects.get(id=id)
        print('mymember ', mymember)
        portefeuille = mymember.portefeuille
        if portefeuille is None:
            # create a new PorteFeuille object for the member
            portefeuille = PorteFeuille.objects.create()
            portefeuille.id =random.randint(10000000, 99999999)
            mymember.portefeuille = portefeuille
            portefeuille.save()
            mymember.save()
        actions_dict = portefeuille.actions
        #print("ac ", actions_dict)
        if len(actions_dict) == 0:
            actions_dict = {'AAPL': 0, 'MSFT': 0, 'GOOGL': 0, 'AMZN': 0, 'Meta': 0, 'TSLA': 0, 'V': 0, 'DIS': 0,
                        'KO': 0, 'WMT': 0, 'MCD': 0, 'BA': 0, 'IBM': 0}
            mymember.portefeuille.actions = actions_dict
        actions_dict[action] += 1
        portefeuille.save()
        mymember.portefeuille = portefeuille
        mymember.save()
        print("dict",mymember.portefeuille.actions)
        # portefeuille['a'] = 1
        return HttpResponse(f"Action choisie : {action}")
    else:
        context = {'firstname': firstname, 'member_id': id}
        return render(request, 'moncompte.html', context)


@login_required(login_url='login')  # on met cela avant chaque methode acessible avec un login
def main(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render())


def testing(request):
    ''''
    member = Member(firstname= 'firstname', lastname = 'lastname')
    member.save()
    '''
    mymember = Member.objects.values_list('firstname')
    if request.user.is_authenticated:
        a = request.user.email
        print(a)
        print(mymember[0])
        if ('Ghadi',) in mymember:
            print(True)
    template = loader.get_template('template.html')
    context = {
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))


def registerPage(request):
    if request.user.is_authenticated:  # ces deux lignes interdit l acces a la page de registration si on est deja connecte
        return redirect('main')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                # Cette partie associe chaque user a un member qui peut participer a la simulation
                creationPortefeuille(form)
                #
                user = form.cleaned_data.get('username')
                messages.success(request,
                                 'Votre compte est crée ' + user)  # source : django documentation
                return redirect('login')

        context = {'form': form}
        return render(request, 'accounts/register.html', context)


def creationPortefeuille(form):
    first_name = form.cleaned_data.get('first_name')
    last_name = form.cleaned_data.get('last_name')
    username = form.cleaned_data.get('username')

    member = Member(firstname=first_name, lastname=last_name, username=username)
    member.save()


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
