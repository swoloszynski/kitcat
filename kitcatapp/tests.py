from django.test import TestCase
from kitcatapp.models import Contact, Connection
from django.utils import timezone
import datetime
from django.core.management import call_command
from django.utils.six import StringIO
from test.test_support import EnvironmentVarGuard
import os
from kitcatapp.src._twilio import Twilio

# Models
class ContactTest(TestCase):

    def test_str(self):
        contact = Contact(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180')
        self.assertTrue(isinstance(contact, Contact))
        self.assertEqual(contact.__str__(), 'Marilyn Monroe')

    def test_get_full_name(self):
        contact = Contact(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180')
        self.assertTrue(isinstance(contact, Contact))
        self.assertEqual(contact.full_name, 'Marilyn Monroe')

class ConnectionTest(TestCase):

    def test_str(self):
        contact = Contact.objects.create(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180')

        connection = Connection(contact=contact, \
                                is_complete=False,
                                due_date=datetime.date(2016, 3, 26))

        self.assertTrue(isinstance(connection, Connection))
        self.assertEqual(connection.__str__(), 'Marilyn Monroe 2016-03-26')

    def test_get_status_scheduled(self):
        contact = Contact.objects.create(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180')
        today = datetime.datetime.now().date()
        connection = Connection(contact=contact, \
                                is_complete=False,
                                due_date=today + datetime.timedelta(days=1))
        self.assertEqual(connection._get_status(), 'Scheduled')

    def test_get_status_due(self):
        contact = Contact.objects.create(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180')
        today = datetime.datetime.now().date()
        connection = Connection(contact=contact, \
                                is_complete=False,
                                due_date=today)
        self.assertEqual(connection._get_status(), 'Due')

    def test_get_status_overdue(self):
        contact = Contact.objects.create(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180')
        today = datetime.datetime.now().date()
        connection = Connection(contact=contact, \
                                is_complete=False,
                                due_date=today - datetime.timedelta(days=1))
        self.assertEqual(connection._get_status(), 'Overdue')

    def test_get_status_complete(self):
        contact = Contact.objects.create(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180')
        connection = Connection(contact=contact, \
                                is_complete=True,
                                due_date=datetime.date(2016, 3, 26))
        self.assertEqual(connection._get_status(), 'Complete')

# Commands
class CommandTest(TestCase):
    fixtures = ['contacts', 'connections']
    def test_command_output(self):
        # --test flag sets test date to 2016-03-29
        out = StringIO()
        call_command('get_reminders', '--test', stdout=out)
        expected = [
            'Amy Schumer 2016-03-29 False',
            'Tina Fey 2016-03-28 False',
            'Amy Schumer 2016-03-19 False',
            'Tina Fey 2016-02-29 False',
        ]
        self.assertIn('\n'.join(expected), out.getvalue())

# Supporting src
class TwilioTest(TestCase):
    def setUp(self):
        test_accout_sid = os.environ.get('TEST_TWILIO_SID')
        test_auth_token = os.environ.get('TEST_TWILIO_AUTH')

        self.env = EnvironmentVarGuard()
        self.env.set('KITCAT_TWILIO_SID', test_accout_sid)
        self.env.set('KITACT_TWILIO_AUTH', test_auth_token)
        self.env.set('KITCAT_TWILIO_FROM_PHONE', '+15005550006')

    def test_send_sms(self):
        with self.env:
            account_sid = os.environ.get('KITCAT_TWILIO_SID')
            auth_token = os.environ.get('KITACT_TWILIO_AUTH')
            from_phone = os.environ.get('KITCAT_TWILIO_FROM_PHONE')
            twilio = Twilio(account_sid, auth_token, from_phone)
            to_phone = '+17036257310'
            test_message = 'Call yo momma!'
            sms = twilio.send_sms(to_phone, test_message)
            assert sms.sid is not None
            assert sms.error_code is None
            assert sms.error_message is None
