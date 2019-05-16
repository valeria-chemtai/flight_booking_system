# Generated by Django 2.1.4 on 2019-05-15 18:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('name', models.CharField(max_length=60)),
                ('departure_time', models.DateTimeField(blank=True, null=True)),
                ('arrival_time', models.DateTimeField(blank=True, null=True)),
                ('gate', models.CharField(blank=True, max_length=60, null=True)),
                ('status', models.CharField(blank=True, max_length=25, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='flights', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('country', models.CharField(max_length=60)),
                ('city', models.CharField(max_length=60)),
                ('airport', models.CharField(blank=True, max_length=60, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('class_group', models.CharField(default='Economy', max_length=60)),
                ('letter', models.CharField(max_length=1)),
                ('row', models.IntegerField()),
                ('booked', models.BooleanField(default=False)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flights.Flight')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together={('country', 'city', 'airport')},
        ),
        migrations.AddField(
            model_name='flight',
            name='destination',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='flight_destination', to='flights.Location'),
        ),
        migrations.AddField(
            model_name='flight',
            name='origin',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='flight_origin', to='flights.Location'),
        ),
        migrations.AlterUniqueTogether(
            name='seat',
            unique_together={('letter', 'row', 'flight')},
        ),
        migrations.AlterUniqueTogether(
            name='flight',
            unique_together={('name', 'departure_time')},
        ),
    ]
