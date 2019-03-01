from django.db import models, transaction
from common.models import BaseModel, SoftDeleteModel


class Location(BaseModel):
    country = models.CharField(max_length=60, null=False, blank=False)
    city = models.CharField(max_length=60, null=False, blank=False)
    airport = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        unique_together = (('country', 'city', 'airport'),)


class Flight(SoftDeleteModel):
    name = models.CharField(max_length=60, null=False, blank=False, unique=True)
    origin = models.ForeignKey(
        'Location', null=True, related_name='flight_origin', on_delete=models.DO_NOTHING)
    destination = models.ForeignKey(
        'Location', related_name='flight_destination', null=True, on_delete=models.DO_NOTHING)
    departure_time = models.DateTimeField(null=True)
    arrival_time = models.DateTimeField(null=True)
    gate = models.CharField(max_length=60, null=False, blank=False)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        super().delete()
        # soft_delete related objects
        if self._meta.related_objects:
            relations = [rel.get_accessor_name() for rel in self._meta.related_objects]
            for relation in relations:
                getattr(self, relation).all().delete()


class Seat(SoftDeleteModel):
    letter = models.CharField(max_length=1, null=False, blank=False)
    row = models.IntegerField(null=False, blank=False)
    booked = models.BooleanField(null=False, default=False)
    flight = models.ForeignKey('Flight', null=False, blank=False, on_delete=models.CASCADE)
