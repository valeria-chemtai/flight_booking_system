from django_rq import job

from django.utils import timezone

from bookings.emails import send_booking_reminder_email
from bookings.models import Booking


@job('default')
def travel_date_reminder_job(bookings):
    for booking in bookings:
        # send user's reminders of their travel
        send_booking_reminder_email(booking)


def travel_date_reminder():
    """Remind users a day before about their flight."""
    next_days_date = timezone.now().date() + timezone.timedelta(days=1)
    # get all bookings for the next day
    bookings = Booking.objects.filter(travel_date=next_days_date)
    travel_date_reminder_job.delay(bookings)
