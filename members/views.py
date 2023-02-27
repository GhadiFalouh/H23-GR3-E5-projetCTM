import csv

import requests
from django.shortcuts import render
from django.template import loader
from .models import Member
from django.http import HttpResponse, HttpResponseRedirect



def members(request):
    mymembers = Member.objects.all().values()
    template = loader.get_template('all_members.html')
    context = {
        'mymembers': mymembers,
    }
    return HttpResponse(template.render(context, request))


def details(request, id):
    mymember = Member.objects.get(id=id)
    template = loader.get_template('details.html')
    context = {
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))


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


def testtest(request):
    api_key = ('Z8O8EWVEWLEFPD4X')
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
