# Kitcat App

## Dev Set Up

#### DB - Postgres
* Install and start Postgres.
* Create database

```
$ createdb kitcat_db
$ psql
CREATE ROLE kitcat_user WITH LOGIN PASSWORD '<password>';
GRANT ALL PRIVILEGES ON DATABASE kitcat_db TO kitcat_user;
ALTER USER kitcat_user CREATEDB;
```

* Create environment variables with configs

```
export KITCAT_DB_NAME=kitcat_db
export KITCAT_DB_USER=kitcat_user
export KITCAT_DB_PASSWORD=<password>

export KITCAT_TWILIO_SID=<sid>
export KITCAT_TWILIO_AUTH=<auth token>
export KITCAT_TWILIO_TO_PHONE=<Twilio-registered test phone number>
export KITCAT_TWILIO_FROM_PHONE=<Twilio-registered test phone number>

export TEST_TWILIO_SID=<test sid>
export TEST_TWILIO_AUTH=<test auth token>
export TEST_TWILIO_TO_PHONE=<Twilio-registered test phone number>
export TEST_TWILIO_FROM_PHONE=+15005550006
```

#### Initializing Dev Environment

* Install virtualenv
* Create new virtualenv: `virtualenv env`
* Install dependencies: `pip install -r requirements.txt`

#### Run App Locally

* Bring migrations up to date: `python manage.py migrate`
* Start server: `python manage.py runserver`
* [View in your browser](http://127.0.0.1:8000/)

#### Staging
* Install [Heroku Toolbelt CLI](https://toolbelt.heroku.com/) and login.
* Follow [Heroku Getting Started guide](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)

## Testing

#### Code coverage

* Generate code coverage report:
```
coverage run manage.py test kitcatapp -v 2
coverage html
```
* View results at `htmlcov/index.html`

#### Run unit tests
* Run `python manage.py test kitcatapp`

## Staging
* To push changes:
```
git push heroku master
heroku run python manage.py migrate --list # Check for unapplied migrations
heroku run python manage.py migrate kitcatapp # Apply migrations
```

## Custom Commands

#### Get connections due on or before date (default to today)
* Run `python manage.py get_reminders -y 2016 -d 30 -m 03`
