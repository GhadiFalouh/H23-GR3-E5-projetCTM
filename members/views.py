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
    print(mymembers)
    template = loader.get_template('all_members.html')
    context = {
        'mymembers': mymembers,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login')
def details(request, id):
    mymember = Member.objects.get(id=id)
    if request.user.is_authenticated and request.user.username == mymember.username:  # on verifie si l utilsateur va dans son profil
        return redirect('moncompte', id=mymember.id)
    context = {
        'mymember': mymember,
    }
    return render(request, 'details.html', context)


''''
def graphique(request, action):
    listeDonnees = getPrix(action,0,True)
    context = {'listeDonnees': listeDonnees, 'action': action}
    return render(request, 'graph.html',context)
'''


def recherche(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        listeDonnees = getPrix(action, 0, True)
        liste_prix = []
        liste_date = []
        for i in range(len(listeDonnees[0][0][0])):
            liste_prix.append(listeDonnees[0][i][1])
            liste_date.append(listeDonnees[0][i][0])
        for i in range(len(liste_prix) // 2):
            liste_prix[i], liste_prix[-1 - i] = liste_prix[-1 - i], liste_prix[i]
            liste_date[i], liste_date[-1 - i] = liste_date[-1 - i], liste_date[i]

        context = {'action': action, 'liste_prix': liste_prix, 'liste_date': liste_date}
        return render(request, 'graph.html', context)
    else:
        return render(request, 'recherche.html')


# Seul le membre associé a cette portefeuille a le droit d'accéder à cela
@login_required(login_url='login')
def moncompte(request, id):
    firstname = request.user.first_name
    if request.method == 'POST':
        action = request.POST.get('action')
        mymember = Member.objects.get(id=id)
        portefeuille = mymember.portefeuille
        actions_dict = portefeuille.actions

        typeOperation = request.POST.get('type')

        if typeOperation == 'Acheter':
            montantDepense, etat = getPrix(action, portefeuille.montant, False)
            if etat:
                portefeuille.montant -= montantDepense
                actions_dict[action] += 1
        else:
            montantRecuperer, etat = getPrix(action, portefeuille.montant, False)
            portefeuille.montant += montantRecuperer
            actions_dict[action] -= 1
        portefeuille.save()
        mymember.portefeuille = portefeuille
        mymember.save()
        context = {'firstname': firstname, 'member_id': id}
        return render(request, 'moncompte.html', context)
    else:
        context = {'firstname': firstname, 'member_id': id}
        return render(request, 'moncompte.html', context)


def getPrix(nomAction, max,
            graph):  # si graphe on return tous les donnees, si nin on return le prix seulement(pour acheter ou vendre)
    api_key = 'Z8O8EWVEWLEFPD4X'
    CSV_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=" + nomAction + "&interval=60min&slice=year1month1&apikey=" + api_key
    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        if graph:
            listePrix = []
            for element in range(1, len(my_list)):
                temp_liste = []
                temp_liste.append(my_list[element][0])
                temp_liste.append(float(my_list[element][1]))
                listePrix.append(temp_liste)
            return listePrix, True
        else:
            prix = float(my_list[1][1])
            if max >= prix:
                return prix, True
            else:
                return prix, False


@login_required(login_url='login')  # on met cela avant chaque methode acessible avec un login
def main(request):
    mymember = None
    mymembers = Member.objects.all().values()
    for member in mymembers:
        if member['username'] == request.user.username:
            mymember = Member.objects.get(id=member['id'])
            #Member.objects.get(id=id)
    context = {
        'mymember': mymember,
        'id': mymember.id,
    }
    template = loader.get_template('accueil_v2.html')
    return HttpResponse(template.render(context, request))


def testing(request):
    ''''
    member = Member(firstname= 'firstname', lastname = 'lastname')
    member.save()
    '''
    mymember = Member.objects.values_list('firstname')
    if request.user.is_authenticated:
        a = request.user.email
    #        print(a)
    #        print(mymember[0])
    #       if ('Ghadi',) in mymember:
    #           print(True)
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
    portefeuille = PorteFeuille.objects.create()
    portefeuille.id = random.randint(10000000, 99999999)
    actions_dict = {'AAPL': 0, 'MSFT': 0, 'GOOGL': 0, 'AMZN': 0, 'Meta': 0, 'TSLA': 0, 'V': 0, 'DIS': 0,
                    'KO': 0, 'WMT': 0, 'MCD': 0, 'BA': 0, 'IBM': 0}
    portefeuille.actions = actions_dict
    member = Member(firstname=first_name, lastname=last_name, username=username, portefeuille=portefeuille)
    portefeuille.save()
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
        return render(request, 'accounts/connexion.html', context) # accounts/login.html


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
