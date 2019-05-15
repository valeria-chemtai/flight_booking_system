# Generated by Django 2.1.4 on 2019-05-15 18:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('flights', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('travel_date', models.DateField(blank=True, null=True)),
                ('booked_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL)),
                ('destination', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='destination', to='flights.Location')),
                ('flight', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='booking', to='flights.Flight')),
                ('origin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='origin', to='flights.Location')),
                ('seat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='booking', to='flights.Seat')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
