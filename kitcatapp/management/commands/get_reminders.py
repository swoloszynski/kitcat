from django.core.management.base import BaseCommand, CommandError
from kitcatapp.models import Contact, Connection, Profile
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import os
from kitcatapp.src._twilio import Twilio

class Command(BaseCommand):
    help = 'Finds due and overdue connections'

    def _send_sms_reminder(self, to_phone, reminder_text):  # pragma: no cover
        account_sid = os.environ.get('KITCAT_TWILIO_SID')
        auth_token = os.environ.get('KITCAT_TWILIO_AUTH')
        from_phone = os.environ.get('KITCAT_TWILIO_FROM_PHONE')
        twilio = Twilio(account_sid, auth_token, from_phone)

        twilio.send_sms(to_phone, reminder_text)

    def _get_due_connections(self, user, due_date):
        due_connections = Connection.objects.filter(due_date=due_date) \
            .filter(contact__user=user) \
            .filter(is_complete=False)
        message = ''
        for connection in due_connections:
            message += "Call %s %s!\n" % (connection.contact.first_name,
                connection.contact.last_name)
        return message

    def _get_overdue_connections(self, user, due_date):
        yesterday = due_date - datetime.timedelta(days=1)
        start_date = datetime.date(1000, 1, 1)
        overdue_connections = Connection.objects \
            .filter(due_date__range=(start_date, yesterday)) \
            .filter(contact__user=user) \
            .order_by('-due_date').filter(is_complete=False)
        message = ''
        for connection in overdue_connections:
            message += "Really, call %s %s!\n" % (connection.contact.first_name,
                connection.contact.last_name)
        return message

    def add_arguments(self, parser):
        today = datetime.datetime.now().date()
        parser.add_argument('-y', '--year', default=today.year, type=int, choices=range(2015, 2100))
        parser.add_argument('-m', '--month', default=today.month, type=int, choices=range(1, 13))
        parser.add_argument('-d', '--day', default=today.day, type=int, choices=range(1, 32))

    def handle(self, *args, **options):
        try:
            year = options['year']
            month = options['month']
            day = options['day']

            due_date = datetime.date(year,month,day)

            users = User.objects.all()
            for user in users:
                user_profile = Profile.objects.get(user=user.id)
                if user_profile:
                    to_phone = user_profile.phone_number
                    if to_phone:
                        message = ''
                        due_message = self._get_due_connections(user, due_date)
                        overdue_message = self._get_overdue_connections(user, due_date)
                        message = due_message + overdue_message

                    if message:
                        self._send_sms_reminder(to_phone, message)

        except ValueError:  # pragma: no cover
            print('No valid date option.')
