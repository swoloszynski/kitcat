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
        self.twilio.send_sms(to_phone, reminder_text)

    def _format_message(self, connections, due_date):
        due_before_text = 'Call '
        overdue_before_text = 'Really, call '
        after_text = '!\n'
        message = ''

        for connection in connections:
            full_name = "%s %s" % (connection.contact.first_name,
                connection.contact.last_name)
            full_name = full_name.strip()
            if connection.due_date == due_date:
                message += due_before_text
                message += full_name
                message += after_text
            elif connection.due_date < due_date:
                message += overdue_before_text
                message += full_name
                message += after_text

        return message.strip()

    def _get_connections(self, user, due_date):
        today = due_date
        start_date = datetime.date(1000, 1, 1)
        # Decreasing due_date means connections due today are first
        connections = Connection.objects \
            .filter(contact__user=user) \
            .filter(due_date__range=(start_date, today)) \
            .filter(is_complete=False) \
            .order_by('-due_date')
        return connections

    def _init_twilio_client(self):  # pragma: no cover
        account_sid = os.environ.get('KITCAT_TWILIO_SID')
        auth_token = os.environ.get('KITCAT_TWILIO_AUTH')
        from_phone = os.environ.get('KITCAT_TWILIO_FROM_PHONE')
        self.twilio = Twilio(account_sid, auth_token, from_phone)

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

            self._init_twilio_client()

            users = User.objects.all()
            for user in users:
                try:
                    user_profile = Profile.objects.get(user=user.id)
                    to_phone = user_profile.phone_number
                    if not to_phone:
                        pass

                    connections = self._get_connections(user, due_date)
                    if len(connections) < 1:
                        pass

                    message = self._format_message(connections, due_date)
                    if message:
                        self._send_sms_reminder(to_phone, message)
                except:
                    print('Missing profile for %s' % user)

        except ValueError:  # pragma: no cover
            print('No valid date option.')
