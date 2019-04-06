# Generated by Django 2.1.4 on 2019-03-16 19:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('name', models.CharField(max_length=60, unique=True)),
                ('departure_time', models.DateTimeField(null=True)),
                ('arrival_time', models.DateTimeField(null=True)),
                ('gate', models.CharField(blank=True, max_length=60, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='flights', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('class_group', models.CharField(default='Economy', max_length=60)),
                ('letter', models.CharField(max_length=1)),
                ('row', models.IntegerField()),
                ('booked', models.BooleanField(default=False)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flights.Flight')),
            ],
            options={
                'abstract': False,
            },
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
    ]
