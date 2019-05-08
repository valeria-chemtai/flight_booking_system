from django.db import models
from common.models import SoftDeleteModel


class Booking(SoftDeleteModel):
    origin = models.ForeignKey(
        'flights.Location', null=True, related_name='origin', on_delete=models.DO_NOTHING)
    destination = models.ForeignKey(
        'flights.Location', related_name='destination',
        null=True, on_delete=models.DO_NOTHING)
    travel_date = models.DateField(null=True, blank=True)
    booked_by = models.ForeignKey(
        'authentication.user', null=False, blank=False, related_name='bookings',
        on_delete=models.DO_NOTHING)
    flight = models.ForeignKey(
        'flights.Flight', null=False, blank=False,
        related_name='booking', on_delete=models.DO_NOTHING)
    seat = models.ForeignKey(
        'flights.Seat', null=False, blank=False,
        related_name='booking', on_delete=models.DO_NOTHING)
