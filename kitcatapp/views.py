from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from .models import Contact, Connection, Profile
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

@login_required
def index(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
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
    except ObjectDoesNotExist:
        raise Http404("User profile does not exist")
