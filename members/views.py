from django.shortcuts import render
from django.template import loader
from .models import Member
from django.http import HttpResponse, HttpResponseRedirect

api_key =('Z8O8EWVEWLEFPD4X')

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
    mymembers = Member.objects.all().values()
    template = loader.get_template('testtest.html')
    context = {
        'mymembers': mymembers,
    }
    return HttpResponse(template.render(context, request))
