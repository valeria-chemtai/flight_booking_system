from django.db import models, transaction
from common.models import BaseModel, SoftDeleteModel


class Location(BaseModel):
    country = models.CharField(max_length=60, null=False, blank=False)
    city = models.CharField(max_length=60, null=False, blank=False)
    airport = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        unique_together = (('country', 'city', 'airport'),)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # capitalize country and city.
        self.country = self.country.capitalize()
        self.city = self.city.capitalize()
        self.airport = self.airport.capitalize()
        return super(Location, self).save(force_insert=force_insert, force_update=force_update,
                                          using=using, update_fields=update_fields)

    def __str__(self):
        return '%s, %s, %s' % (self.airport, self.city, self.country)


class Flight(SoftDeleteModel):
    name = models.CharField(max_length=60, null=False, blank=False, unique=True)
    origin = models.ForeignKey(
        'Location', null=True, related_name='flight_origin', on_delete=models.DO_NOTHING)
    destination = models.ForeignKey(
        'Location', related_name='flight_destination', null=True, on_delete=models.DO_NOTHING)
    departure_time = models.DateTimeField(null=True)
    arrival_time = models.DateTimeField(null=True)
    gate = models.CharField(max_length=60, null=True, blank=True)
    created_by = models.ForeignKey(
        'authentication.user', null=False, blank=False, related_name='flights',
        on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=25, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'departure_time')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # uppercase name and gate.
        self.name = self.name.upper()
        if self.gate:
            self.gate = self.gate.upper()
        return super(Flight, self).save(force_insert=force_insert, force_update=force_update,
                                        using=using, update_fields=update_fields)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        super().delete()
        # soft_delete related objects
        if self._meta.related_objects:
            relations = [rel.get_accessor_name() for rel in self._meta.related_objects]
            for relation in relations:
                getattr(self, relation).all().delete()


class Seat(SoftDeleteModel):
    class_group = models.CharField(max_length=60, default='Economy')
    letter = models.CharField(max_length=1, null=False, blank=False)
    row = models.IntegerField(null=False, blank=False)
    booked = models.BooleanField(null=False, default=False)
    flight = models.ForeignKey('Flight', null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('letter', 'row', 'flight')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # uppercase letter.
        self.letter = self.letter.upper()
        return super(Seat, self).save(force_insert=force_insert, force_update=force_update,
                                      using=using, update_fields=update_fields)

    @property
    def seat(self):
        return str(self.row) + self.letter
