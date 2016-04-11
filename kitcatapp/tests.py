from django.test import TestCase
from kitcatapp.models import Contact, Connection, Profile
from django.contrib.auth.models import User
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
        user1 = User.objects.create(username='user1')
        contact = Contact(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180', \
                            user=user1)
        self.assertTrue(isinstance(contact, Contact))
        self.assertEqual(contact.__str__(), 'Marilyn Monroe')

    def test_get_full_name(self):
        user1 = User.objects.create(username='user1')
        contact = Contact(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180', \
                            user=user1)
        self.assertTrue(isinstance(contact, Contact))
        self.assertEqual(contact.full_name, 'Marilyn Monroe')

class ConnectionTest(TestCase):
    fixtures = ['users', 'contacts']

    def test_str(self):
        contact = Contact.objects.get(first_name='Amy')
        connection = Connection(contact=contact, \
                                is_complete=False,
                                due_date=datetime.date(2016, 3, 26))

        self.assertTrue(isinstance(connection, Connection))
        self.assertEqual(connection.__str__(), 'Amy Schumer 2016-03-26')

    def test_get_status_scheduled(self):
        contact = Contact.objects.get(first_name='Amy')
        today = datetime.datetime.now().date()
        connection = Connection(contact=contact, \
                                is_complete=False,
                                due_date=today + datetime.timedelta(days=1))
        self.assertEqual(connection._get_status(), 'Scheduled')

    def test_get_status_due(self):
        contact = Contact.objects.get(first_name='Amy')
        today = datetime.datetime.now().date()
        connection = Connection(contact=contact, \
                                is_complete=False,
                                due_date=today)
        self.assertEqual(connection._get_status(), 'Due')

    def test_get_status_overdue(self):
        contact = Contact.objects.get(first_name='Amy')
        today = datetime.datetime.now().date()
        connection = Connection(contact=contact, \
                                is_complete=False,
                                due_date=today - datetime.timedelta(days=1))
        self.assertEqual(connection._get_status(), 'Overdue')

    def test_get_status_complete(self):
        contact = Contact.objects.get(first_name='Amy')
        connection = Connection(contact=contact, \
                                is_complete=True,
                                due_date=datetime.date(2016, 3, 26))
        self.assertEqual(connection._get_status(), 'Complete')

class ProfileTest(TestCase):
    def test_str_username_only(self):
        user1 = User.objects.create(username='user1', first_name='', last_name='')
        profile = Profile.objects.create(user=user1)
        self.assertTrue(isinstance(profile, Profile))
        self.assertEqual(profile.__str__(), 'user1')

    def test_str_first_name_only(self):
        user1 = User.objects.create(username='user1', first_name='First', last_name='')
        profile = Profile.objects.create(user=user1)
        self.assertTrue(isinstance(profile, Profile))
        self.assertEqual(profile.__str__(), 'First (user1)')

    def test_str_last_name_only(self):
        user1 = User.objects.create(username='user1', first_name='', last_name='Last')
        profile = Profile.objects.create(user=user1)
        self.assertTrue(isinstance(profile, Profile))
        self.assertEqual(profile.__str__(), 'Last (user1)')

    def test_str_full_name_only(self):
        user1 = User.objects.create(username='user1', first_name='First', last_name='Last')
        profile = Profile.objects.create(user=user1)
        self.assertTrue(isinstance(profile, Profile))
        self.assertEqual(profile.__str__(), 'First Last (user1)')

# Commands
class BasicGetRemindersTest(TestCase):
    fixtures = ['users', 'profiles', 'contacts', 'connections']
    def test_date_ok_send_sms_reminder_for_due_connections(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders', '-y 2016', '-d 19', '-m 03')
            self.assertTrue(Command._send_sms_reminder.called, "Failed to send SMS.")
            expected_to_phone = '+17036257100'
            expected_reminder_text = 'Call Amy Schumer!\n'
            Command._send_sms_reminder.assert_called_with(expected_to_phone, expected_reminder_text)

    def test_date_ok_send_sms_reminder_for_overdue_connections(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders', '-y 2016', '-d 20', '-m 03')
            self.assertTrue(Command._send_sms_reminder.called, "Failed to send SMS.")
            expected_to_phone = '+17036257100'
            expected_reminder_text = 'Really, call Amy Schumer!\n'
            Command._send_sms_reminder.assert_called_once_with(expected_to_phone, expected_reminder_text)

    def test_date_ok_send_sms_reminder_for_due_and_overdue_connections(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders', '-y 2016', '-d 21', '-m 03')
            self.assertTrue(Command._send_sms_reminder.called, "Failed to send SMS.")
            expected_to_phone = '+17036257100'
            expected_reminder_text = 'Call Tina Fey!\nReally, call Amy Schumer!\n'
            Command._send_sms_reminder.assert_called_once_with(expected_to_phone, expected_reminder_text)

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

class MultiUserGetRemindersTest(TestCase):
    fixtures = ['users', 'profiles', 'contacts', 'connections_multiple_users']
    def test_send_sms_reminder_to_multiple_users(self):
        with mock.patch.object(Command, '_send_sms_reminder'):
            call_command('get_reminders', '-y 2016', '-d 17', '-m 04')
            self.assertTrue(Command._send_sms_reminder.called, "Failed to send SMS.")
            self.assertEqual(Command._send_sms_reminder.call_count, 2)

            expected_to_phone_1 = '+17036257100'
            expected_reminder_text_1 = 'Call Tina Fey!\n'
            first_call = mock.call(expected_to_phone_1, expected_reminder_text_1)

            expected_to_phone_2 = '+1234568790'
            expected_reminder_text_2 = 'Call Stephen Colbert!\n'
            second_call = mock.call(expected_to_phone_2, expected_reminder_text_2)

            calls = [first_call, second_call]
            Command._send_sms_reminder.assert_has_calls(calls)
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
