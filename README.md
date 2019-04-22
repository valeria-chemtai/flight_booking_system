[![Build Status](https://travis-ci.org/valeria-chemtai/flight_booking_system.svg?branch=develop)](https://travis-ci.org/valeria-chemtai/flight_booking_system)
# Flight Booking System
Online flight booking system API for Company Airtech.

This API is built using Django/DRF

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
export POSTGRES_DB_NAME = 'flight_system'
export POSTGRES_DB_USER = 'postgres'
export POSTGRES_DB_PASSWORD = ''
export POSTGRES_DB_HOST = 'localhost'
export POSTGRES_DB_PORT = 5432
export APP_SETTINGS="development"
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
| `/v1/flights/` | `POST`| Add a flight to the system| Staff |
| `/v1/flights/` | `GET`| List all flights available in system| Registered users |
| `/v1/flights/<pk>/` | `GET`| Retrieve a flight by id| Registered users |
| `/v1/flights/<pk>/` | `PUT`| Edit a flight by id| Staff |
| `/v1/flights/<pk>/` | `DELETE`| DELETE a flight by id| Superuser |
| `flights/<flight_pk>/seats/`| `POST`| Add flight seat | Staff |
| `flights/<flight_pk>/seats/`| `GET`| List all flight seats | Registered users |
| `flights/<flight_pk>/seats/<pk>/`| `GET`| Retrieve a seat by id | Registered users |
| `flights/<flight_pk>/seats/<pk>/`| `PUT`| Edit a seat by id | Staff |
| `flights/<flight_pk>/seats/<pk>/`| `DELETE`| Edit a seat by id | Superuser |

## Testing
You can run the tests ```python manage.py test```
