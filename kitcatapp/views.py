from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from .models import Contact, Connection, Profile
import datetime

@login_required
def index(request):
    user = request.user
    profile = Profile.objects.get(user=request.user)
    today = datetime.date.today()
    start_date = datetime.date(1000, 1, 1)
    connections = Connection.objects \
        .filter(contact__user=user) \
        .filter(due_date__range=(start_date, today)) \
        .filter(is_complete=False) \
        .order_by('-due_date')


    context = {
        'profile': profile,
        'connections': connections
    }
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))
