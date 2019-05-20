[![Build Status](https://travis-ci.org/valeria-chemtai/flight_booking_system.svg?branch=develop)](https://travis-ci.org/valeria-chemtai/flight_booking_system)
# Flight Booking System
Online flight booking system API for Company Airtech.

This API is built using Django/DRF
## Prerequisites
[Postgres](https://www.postgresql.org/)

[Redis](https://redis.io/)

## Installation and Setup
Clone the repo
```
https://github.com/valeria-chemtai/flight_booking_system.git
```
Navigate to the root folder
```
cd flight_booking_system/backend_system/
```
create a virtualenv using virtualenvwrapper
```
mkvirtualenv flight_system
```
activate virtualenv by running the following
```
workon flight_system
```
Inside virtualenv open a postactivate file to store default configuration variables by running the command
```
subl $VIRTUAL_ENV/bin/postactivate
```
In the postactivate file add the defaults you would like configured.
```
export SECRET_KEY='akjshdkqiu3ye723y42i34'
export DEBUG = False
export POSTMARK_TOKEN='your postmark token'
export POSTMARK_SENDER_EMAIL='domain specific email registered on postmark'
```
For database settings; if you prefer configuring settings commented out, add the following settings.
```
export POSTGRES_DB_NAME = 'flight_system'
export POSTGRES_DB_USER = 'postgres'
export POSTGRES_DB_PASSWORD = ''
export POSTGRES_DB_HOST = 'localhost'
export POSTGRES_DB_PORT = 5432
```
If you prefer using [dj_database_url](https://pypi.org/project/dj-database-url/),as per the uncommented DATABASE in the settings file, only add the postgres database url to the postactivate file. i.e.
```
export DATABASE_URL="postgres://user@localhost:5432/flight_system"
```
Alternatively if you do not want to do all these, just replace the defaults in [config/settings](https://github.com/valeria-chemtai/flight_booking_system/blob/develop/backend_system/config/settings.py) file.

Install the requirements
```
pip install -r requirements.txt
```
Create a postgres database called flight_system using PgAdmin, why? its easy

Alternatively create the database from the command line by running the script:
```
$ createdb flight_system
```

Run migrations to create tables
```
python manage.py migrate
```
## Launch the progam
Start your redis server and make sure it is running throughout to be able to send travel date reminders
```
redis-server
```
Open another terminal and start [django_rq](https://github.com/rq/django-rq) worker
```
python manage.py rqworker default
```
Open another terminal to queue jobs with [rq-scheduler](https://github.com/rq/rq-scheduler)
```
python manage.py rqscheduler
```
Finally start the server

Run 
```
python manage.py runserver
```
Interact with the API, send http requests using Postman(json format)
## API Endpoints
| URL Endpoint | HTTP Methods | Summary | Permission_level |
| -------- | ------------- | --------- |------------------|
| `/v1/auth/signup/` | `POST`  | Register a new user| any |
| `/v1/auth/sign-in/` | `POST` | Login and retrieve token | Registered users |
|`/v1/auth/change-password/`| `POST` | Change password | Logged in registered users |
| `/v1/auth/users/` | `GET` | List all system users | staff |
| `/v1/auth/users/<pk>/` | `GET` |  Retrieve a user by ID| staff/user with id specified |
| `/v1/auth/users/<pk>/` | `PUT` | Update a user info by ID| superuser/user with id specified |
| `/v1/allowed-destinations/` | `POST` |  Add company allowed destinations | staff |
| `/v1/allowed-destinations/` | `GET` |  List company allowed destinations | registered users |
| `/v1/allowed-destinations/<pk>` | `GET` |  Retrieve a single location | registered users |
| `/v1/allowed-destinations/<pk>` | `PUT` |  Update a single location | staff |
| `/v1/allowed-destinations/<pk>` | `DELETE` |  Delete a single location | Superuser |
| `/v1/bookings/` | `POST`| Book a flight| Registered users |
| `/v1/bookings/` | `GET`| List all bookings available in system| Registered users(Normal users will only see their bookings while staff will see all bookings)|
| `/v1/bookings/<pk>/` | `GET`| Retrieve specific booking| Registered user who made booking or staff |
| `/v1/bookings/<pk>/` | `PUT`| Edit specific booking| Registered user who made booking or staff |
| `/v1/bookings/<pk>/` | `DELETE`| Edit specific booking| Registered user who made booking or staff |
| `/v1/bookings/?travel_date=YYYY-MM-DD` | `GET`| List all bookings available in system for a particular travel date| Registered users(Normal users will only see their bookings while staff will see all bookings)|
| `/v1/flights/` | `POST`| Add a flight to the system| Staff |
| `/v1/flights/` | `GET`| List all flights available in system| Registered users |
| `/v1/flights/<pk>/` | `GET`| Retrieve a flight by id| Registered users |
| `/v1/flights/<pk>/` | `PUT`| Edit a flight by id| Staff |
| `/v1/flights/<pk>/` | `DELETE`| DELETE a flight by id| Superuser |
| `/v1/flights/<flight_pk>/bookings/`| `POST`| Make booking for a specific flight| Staff |
| `/v1/flights/<flight_pk>/bookings/`| `GET`| Get bookings made for a specific flight| Staff |
| `/v1/flights/<flight_pk>/bookings/assign-flight-to-bookings/`| `POST`| Mass assign bookings to a particular flight| Staff |
| `/v1/flights/<flight_pk>/seats/`| `POST`| Add flight seat | Staff |
| `/v1/flights/<flight_pk>/seats/`| `GET`| List all flight seats | Registered users |
| `/v1/flights/<flight_pk>/seats/<pk>/`| `GET`| Retrieve a seat by id | Registered users |
| `/v1/flights/<flight_pk>/seats/<pk>/`| `PUT`| Edit a seat by id | Staff |
| `/v1/flights/<flight_pk>/seats/<pk>/`| `DELETE`| Edit a seat by id | Superuser |

## Testing
You can run the tests ```python manage.py test```

## Heroku app
[https://vc-flight-booking-system.herokuapp.com](https://vc-flight-booking-system.herokuapp.com)

sample request [here](https://github.com/valeria-chemtai/flight_booking_system/blob/develop/Docs/sample_requests.md)
