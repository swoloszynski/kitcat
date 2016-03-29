from django.core.management.base import BaseCommand, CommandError
from kitcatapp.models import Contact, Connection
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Finds due and overdue connections'

    def add_arguments(self, parser):
        parser.add_argument('--test',
            action='store_true',
            dest='test',
            default=False,
            help='Run command in test environment')

    def _get_due_connections(self, due_date):
        due_connections = Connection.objects.filter(due_date=due_date)
        for connection in due_connections:
            self.stdout.write("%s %s" % (connection, connection.is_complete))

    def _get_overdue_connections(self, due_date):
        yesterday = due_date - datetime.timedelta(days=1)
        start_date = datetime.date(1000, 1, 1)
        overdue_connections = Connection.objects.filter(due_date__range=(
            start_date, yesterday)).order_by('-due_date')
        for connection in overdue_connections:
            self.stdout.write("%s %s" % (connection, connection.is_complete))

    def handle(self, *args, **options):
        if options['test']:
            due_date = datetime.date(2016,03,29)
        else:
            due_date = datetime.datetime.now().date()

        self._get_due_connections(due_date)
        self._get_overdue_connections(due_date)
