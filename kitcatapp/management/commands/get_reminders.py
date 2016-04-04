from django.core.management.base import BaseCommand, CommandError
from kitcatapp.models import Contact, Connection
from django.utils import timezone
import datetime
import os
from kitcatapp.src._twilio import Twilio

class Command(BaseCommand):
    help = 'Finds due and overdue connections'

    def add_arguments(self, parser):
        parser.add_argument('--test',
            action='store_true',
            dest='test',
            default=False,
            help='Run command in test environment')

    def _send_sms_reminder(self, reminder_text):
        account_sid = os.environ.get('KITCAT_TWILIO_SID')
        auth_token = os.environ.get('KITCAT_TWILIO_AUTH')
        from_phone = os.environ.get('KITCAT_TWILIO_FROM_PHONE')
        twilio = Twilio(account_sid, auth_token, from_phone)

        to_phone = os.environ.get('KITCAT_TWILIO_TO_PHONE')
        twilio.send_sms(to_phone, reminder_text)

    def _get_due_connections(self, due_date):
        due_connections = Connection.objects.filter(due_date=due_date)
        message = ''
        for connection in due_connections:
            message += "Call %s %s!\n" % (connection.contact.first_name,
                connection.contact.last_name)
        return message

    def _get_overdue_connections(self, due_date):
        yesterday = due_date - datetime.timedelta(days=1)
        start_date = datetime.date(1000, 1, 1)
        overdue_connections = Connection.objects.filter(due_date__range=(
            start_date, yesterday)).order_by('-due_date')
        message = ''
        for connection in overdue_connections:
            message += "Really, call %s %s!\n" % (connection.contact.first_name,
                connection.contact.last_name)
        return message

    def handle(self, *args, **options):
        if options['test']:
            due_date = datetime.date(2016,03,19)
        else:
            due_date = datetime.datetime.now().date()

        due_message = self._get_due_connections(due_date)
        overdue_message = self._get_overdue_connections(due_date)
        self._send_sms_reminder(due_message + overdue_message)
