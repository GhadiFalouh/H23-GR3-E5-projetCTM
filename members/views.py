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


# py manage.py runserver


def accueil(request):
    """responsable de la page d'accueil

        Parameters
        ----------
        Request :
            le type de rquete

        Returns
        -------
        renvoi vers la page d'accueil
        """
    return render(request, 'accueil.html')


@login_required(login_url='login')  # pour interdire l'acees sans si tu n'es pas connecté
def members(request):
    """Responsable de la liste des membres (cette partie ne peut être accèder que avec le url

        Parameters
        ----------
        request :
            le type de rquete
        Returns
        -------
        contexte
            la liste des membres
        template
            la page html corespondant
        """
    mymembers = Member.objects.all().values()
    template = loader.get_template('all_members.html')
    context = {
        'mymembers': mymembers,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login')
def details(request, id):
    """Pour trouver les données de chaque utiliateur (cette partie de code ne peut être accèder que avec un url)

           Parameters
           ----------
           request :
               le type de rquête

           Returns
           -------
           contexte
               les données de l'utilisateur qu'on cherche
           """
    mymember = Member.objects.get(id=id)
    if request.user.is_authenticated and request.user.username == mymember.username:  # on verifie si l utilsateur va dans son profil
        return redirect('moncompte', id=mymember.id)
    context = {
        'mymember': mymember,
    }
    return render(request, 'details.html', context)


@login_required(login_url='login')
def devise(request):
    """
        Pour afficher le graphique d'un action choisi
    """
    mymembers = Member.objects.all().values()
    if request.method == 'POST':
        action = request.POST.get('action')  # pour savoir le nom de l'action qu'on cherche
        listeDonnees = getPrix(action, 0, True)
        liste_prix = []
        liste_date = []
        # La partie suivant sert à filtrer les données reçues de l'api Alpha vantage pour acceder seulement aux infos qu'on a besoin
        for i in range(len(listeDonnees[0][0][0])):
            liste_prix.append(listeDonnees[0][i][1])
            liste_date.append(listeDonnees[0][i][0])
        for i in range(len(liste_prix) // 2):
            liste_prix[i], liste_prix[-1 - i] = liste_prix[-1 - i], liste_prix[i]
            liste_date[i], liste_date[-1 - i] = liste_date[-1 - i], liste_date[i]

        context = {'action': action, 'liste_prix': liste_prix, 'liste_date': liste_date}
        return render(request, 'devise.html', context)
    else:
        return render(request, 'devise.html')


def recherche(request):
    """Responsable de la recherche des données à l'aide de l'API

    """

    def filtrerInfo(action):
        listeDonnees = getPrix(action, 0, True)
        liste_prix = []
        liste_date = []
        # La partie suivant sert a filtrer les donnees recus par l'API Alpha Vantage pour récuperer ce qu'on cherche
        for i in range(len(listeDonnees[0][0][0])):
            liste_prix.append(listeDonnees[0][i][1])
            liste_date.append(listeDonnees[0][i][0])
        for i in range(len(liste_prix) // 2):
            liste_prix[i], liste_prix[-1 - i] = liste_prix[-1 - i], liste_prix[i]
            liste_date[i], liste_date[-1 - i] = liste_date[-1 - i], liste_date[i]
        return liste_prix, liste_date

    if request.method == 'POST':
        action = request.POST.get('action')
        liste_prix, liste_date = filtrerInfo(action)
        context = {'action': action, 'liste_prix': liste_prix, 'liste_date': liste_date}
        return render(request, 'devise.html', context)
    else:
        return render(request, 'recherche.html')


def panier(request):
    """
    Responsable de l'achat et la vente des actions
    """
    actions_dict = {}
    mymembers = Member.objects.all().values()
    mymember = None  # pour initialiser
    cout = 0
    portefeuille = None
    for member in mymembers:  # pour trouver le données de l'utilisateur actuel
        if member['username'] == request.user.username:
            mymember = Member.objects.get(id=member['id'])
            portefeuille = mymember.portefeuille
            actions_dict = portefeuille.actions

    if request.method == 'POST':  # si utilisateur veut acheter ou vendre
        action = request.POST.get('action')
        typeOperation = request.POST.get('type')
        if typeOperation == 'Acheter':
            montantDepense, etat = getPrix(action, mymember.portefeuille.montant, False)
            solde = mymember.portefeuille.montant - montantDepense
            cout = montantDepense
            if etat:
                portefeuille.montant -= montantDepense
                actions_dict[action] += 1
        else:  # si vente
            montantRecuperer, etat = getPrix(action, mymember.portefeuille.montant, False)
            solde = mymember.portefeuille.montant + montantRecuperer
            cout -= montantRecuperer
            portefeuille.montant += montantRecuperer
            actions_dict[action] -= 1
        portefeuille.save()
        mymember.portefeuille = portefeuille
        mymember.save()  # on souvgarde les nouvelles données de l'utilisateur dans la base de données
        context = {
            'mymember': mymember, 'solde': solde, 'montant_actuel': mymember.portefeuille.montant,
            'valeur': getValeur(actions_dict) + solde, 'cout': cout, 'action': action
        }

        return render(request, 'panier.html', context)
    context = {
        'mymember': mymember
    }

    return render(request, 'panier1.html', context)


# Seul le membre associé a cette portefeuille a le droit d'accéder à cela
@login_required(login_url='login')
def moncompte(request, id):
    """
    Responsable de l'affichage des données dans la page personnelle (cette partie n'est pas utiliser dans le projet, mais
            on a décidé de le garder, car elle peut être utile si on veut continuer le projet)
    """
    firstname = request.user.first_name
    email = request.user.email
    mymember = Member.objects.get(id=id)
    portefeuille = mymember.portefeuille
    actions_dict = portefeuille.actions
    valeur = getValeur(actions_dict) + portefeuille.montant
    if request.method == 'POST':
        action = request.POST.get('action')
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
        context = {'firstname': firstname, 'member_id': id, 'membre': mymember, 'email': email, 'valeur': valeur}
        return render(request, 'MonCompteV2.html', context)
    else:
        context = {'firstname': firstname, 'member_id': id, 'membre': mymember, 'email': email, 'valeur': valeur}
        return render(request, 'MonCompteV2.html', context)


def getValeur(dict_actions: PorteFeuille.actions) -> int:
    """
        Pour trouver la valeur du compte de l'utilisateur (montant dipo + valeur des actions qu'il possède)
    """
    valeur = 0
    for cle, val in dict_actions.items():
        if val > 0:
            prix, ignore = getPrix(cle, 10000, False)
            temp = int(val) * int(prix)  # le 10000 pour etre sure que le montant n est pas trop petit
            valeur += temp
    return valeur


def getPrix(nomAction, max, graph):
    """
       Responsable de trouver la prix d'un action sur le marché et vérifier si on a assez d'argent pour en acheter un
       Parameters
           ----------
           nomAction :
           max: le montant d'argent disponible
           graph: si graphe == True on return tous les donnees, si nin on return le prix seulement (pour acheter ou vendre)

           Returns
           -------
           prix : le prix de l'action selectioné
           etat : si il est possible d'acheter ou de vendre cette action

    """
    api_key = 'Z8O8EWVEWLEFPD4X'
    CSV_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=" + nomAction + "&interval=60min&slice=year1month1&apikey=" + api_key
    # Cette partie a été pris du site de l'api alphavantage : https://www.alphavantage.co/documentation/
    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        if graph:
            listePrix = []
            for element in range(1, len(my_list)):
                # Configuration des données pour faire un graphique avec
                temp_liste = []
                temp_liste.append(my_list[element][0])
                temp_liste.append(float(my_list[element][1]))
                listePrix.append(temp_liste)
            return listePrix, True
        else:  # vérification de la possibilité de faire l'operation
            prix = float(my_list[1][1])
            if max >= prix:
                return prix, True
            else:
                return prix, False


@login_required(login_url='login')  # on met cela avant chaque methode acessible avec un login
def main(request):
    """
       Responsable de l'affichage de la page main (accueil)
    """
    mymember = None
    mymembers = Member.objects.all().values()
    for member in mymembers:
        if member['username'] == request.user.username:
            mymember = Member.objects.get(id=member['id'])
            # Member.objects.get(id=id)
    context = {
        'mymember': mymember,
        'id': mymember.id,
    }
    template = loader.get_template('accueil_v2.html')
    return HttpResponse(template.render(context, request))


def testing(request):
    ''''
    C'est un teste, il ne fait pas partie du projet
    '''
    mymember = Member.objects.values_list('firstname')
    if request.user.is_authenticated:
        a = request.user.email
    template = loader.get_template('template.html')
    context = {
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))


def registerPage(request):
    ''''
        Responsable de la création d'un nouveau compte
    '''
    if request.user.is_authenticated:  # ces deux lignes interdit l acces a la page de registration si on est deja connecte
        return redirect('main')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                # Cette partie associe chaque user a un member qui peut participer à la jeu de simulation
                creationPortefeuille(form)
                user = form.cleaned_data.get('username')
                messages.success(request,
                                 'Votre compte est crée ' + user)  # source : django documentation
                return redirect('login')

        context = {'form': form}
        return render(request, 'accounts/register.html', context)


def creationPortefeuille(form):
    ''''
        Responsable de l'insiatlisation du portefeuille de l'utilisateur
    '''
    first_name = form.cleaned_data.get('first_name')
    last_name = form.cleaned_data.get('last_name')
    username = form.cleaned_data.get('username')
    portefeuille = PorteFeuille.objects.create()
    portefeuille.id = random.randint(10000000, 99999999)
    actions_dict = {'AAPL': 0, 'MSFT': 0, 'GOOGL': 0, 'AMZN': 0, 'Meta': 0, 'TSLA': 0, 'V': 0, 'DIS': 0,
                    'KO': 0, 'WMT': 0, 'MCD': 0, 'BA': 0, 'IBM': 0}  # forme initial d'une portefeuille (dict)
    portefeuille.actions = actions_dict
    # Création d'un nouveau membre:
    member = Member(firstname=first_name, lastname=last_name, username=username, portefeuille=portefeuille)
    portefeuille.save()
    member.save()


def loginPage(request):
    ''''
         Responsable de la connexion de l'utilisateur à son compte
    '''
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
        return render(request, 'accounts/connexion.html', context)  # accounts/login.html


def logoutUser(request):
    logout(request)
    return redirect('login')


def testtest(request):
    ''''
        Teste de la fonctionalité d'affichage de graphique (cela n'est pas utilisé dans le projet)
    '''
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
