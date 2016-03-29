from django.test import TestCase
from kitcatapp.models import Contact, Connection
from django.utils import timezone
import datetime

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
                                due_date=today - datetime.timedelta(days=1))
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
                                due_date=today + datetime.timedelta(days=1))
        self.assertEqual(connection._get_status(), 'Overdue')

    def test_get_status_complete(self):
        contact = Contact.objects.create(first_name='Marilyn', \
                            last_name='Monroe', \
                            frequency = '180')
        connection = Connection(contact=contact, \
                                is_complete=True,
                                due_date=datetime.date(2016, 3, 26))
        self.assertEqual(connection._get_status(), 'Complete')
