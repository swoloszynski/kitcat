from django.test import TestCase
from kitcatapp.models import Contact, Connection
from django.utils import timezone
from datetime import datetime

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
                                due_date=datetime(2016, 3, 26))

        self.assertTrue(isinstance(connection, Connection))
        self.assertEqual(connection.__str__(), 'Marilyn Monroe 2016-03-26')
