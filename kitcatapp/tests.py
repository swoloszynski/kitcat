from django.test import TestCase
from kitcatapp.models import Contact, Connection
from django.utils import timezone
import datetime
from django.core.management import call_command
from test.test_support import EnvironmentVarGuard
import os
from kitcatapp.src._twilio import Twilio
from kitcatapp.management.commands.get_reminders import Command
import mock
import unittest

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
    def test_date_ok_send_sms_reminder_for_due_connections(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders', '-y 2016', '-d 19', '-m 03')
            self.assertTrue(Command._send_sms_reminder.called, "Failed to send SMS.")
            expected_reminder_text = 'Call Amy Schumer!\n'
            Command._send_sms_reminder.assert_called_once_with(expected_reminder_text)

    def test_date_ok_send_sms_reminder_for_overdue_connections(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders', '-y 2016', '-d 20', '-m 03')
            self.assertTrue(Command._send_sms_reminder.called, "Failed to send SMS.")
            expected_reminder_text = 'Really, call Amy Schumer!\n'
            Command._send_sms_reminder.assert_called_once_with(expected_reminder_text)

    def test_date_ok_dont_send_sms_reminder_if_no_connections(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders', '-y 2015', '-d 19', '-m 03')
            self.assertFalse(Command._send_sms_reminder.called, "Tried to send empty SMS.")

    def test_date_ok_dont_send_sms_reminder_if_only_complete_due_connections(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders', '-y 2016', '-d 27', '-m 02')
            self.assertFalse(Command._send_sms_reminder.called, "Tried to send empty SMS.")

    def test_date_ok_dont_send_sms_reminder_if_only_complete_overdue_connections(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders', '-y 2016', '-d 28', '-m 02')
            self.assertFalse(Command._send_sms_reminder.called, "Tried to send empty SMS.")

    def test_bad_date_dont_send_sms_reminder(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders')
            self.assertTrue(Command._send_sms_reminder.called, "Failed to send SMS.")

# Src
class TwilioTest(TestCase):
    def setUp(self):
        test_accout_sid = os.environ.get('TEST_TWILIO_SID')
        test_auth_token = os.environ.get('TEST_TWILIO_AUTH')
        test_to_phone = os.environ.get('TEST_TWILIO_TO_PHONE')
        twilio_test_from_number = '+15005550006'

        self.env = EnvironmentVarGuard()
        self.env.set('KITCAT_TWILIO_SID', test_accout_sid)
        self.env.set('KITACT_TWILIO_AUTH', test_auth_token)
        self.env.set('KITCAT_TWILIO_TO_PHONE', test_to_phone)
        self.env.set('KITCAT_TWILIO_FROM_PHONE', twilio_test_from_number)

    def test_send_sms(self):
        with self.env:
            account_sid = os.environ.get('KITCAT_TWILIO_SID')
            auth_token = os.environ.get('KITACT_TWILIO_AUTH')
            to_phone = os.environ.get('KITCAT_TWILIO_TO_PHONE')
            from_phone = os.environ.get('KITCAT_TWILIO_FROM_PHONE')
            twilio = Twilio(account_sid, auth_token, from_phone)
            test_message = 'Call yo momma!'
            sms = twilio.send_sms(to_phone, test_message)
            assert sms.sid is not None
            assert sms.error_code is None
            assert sms.error_message is None
