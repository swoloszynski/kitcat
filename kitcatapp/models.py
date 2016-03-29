from django.db import models
import datetime
from django.utils import timezone

class Contact(models.Model):
    DAILY      = '1'
    WEEKLY     = '7'
    BIWEEKLY   = '14'
    MONTHLY    = '28'
    QUARTERLY  = '90'
    BIANNUALLY = '180'
    YEARLY     = '365'

    FREQUENCY_CHOICES = (
        (DAILY,      'Daily'),
        (WEEKLY,     'Weekly'),
        (BIWEEKLY,   'Bi-Weekly'),
        (MONTHLY,    'Monthly'),
        (QUARTERLY,  'Every Three Months'),
        (BIANNUALLY, 'Every Six Months'),
        (YEARLY,     'Yearly'),
    )

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    date_met = models.DateField(blank=True, null=True)
    how_met = models.CharField(max_length=400, blank=True)
    about = models.TextField(blank=True)
    frequency = models.CharField(max_length=200, choices=FREQUENCY_CHOICES)

    def _get_full_name(self):
        "Returns first and last name."
        return '%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

class Connection(models.Model):

    contact = models.ForeignKey(Contact)
    is_complete = models.BooleanField(default=False)
    due_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    def _get_status(self):
        "Returns the status of the connection based on today's date."
        SCHEDULED = 'Scheduled'
        DUE       = 'Due'
        OVERDUE   = 'Overdue'
        COMPLETE  = 'Complete'

        if self.is_complete is True:
            return COMPLETE

        today = datetime.datetime.now().date()
        delta = (today - self.due_date).days

        if delta < 0:
            return SCHEDULED
        elif delta is 0:
            return DUE
        else:
            return OVERDUE
    status = property(_get_status)

    def __str__(self):
        return '%s %s %s' % (self.contact.first_name, self.contact.last_name, self.due_date)
