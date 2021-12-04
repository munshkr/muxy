# muxy

[![Django CI](https://github.com/munshkr/muxy/actions/workflows/django.yml/badge.svg)](https://github.com/munshkr/muxy/actions/workflows/django.yml)

RTMP-based streaming muxer for online events

Allows user to organize online self-streaming events, where each user can
stream herself to public channels or other streaming services.

## Install

Clone repository or download zipfile and extract somewhere.

Create virtual environment and activate:

```
virtualenv -p python3.7 .venv
source .venv/bin/activate
```

Install the dependencies:

```
pip3 install -r requirements.txt
```

Copy `env.sample` to `.env` and update if necessary. You should set at least:

- `SECRET_KEY`: Use a unique random string.
- `ALLOWED_HOSTS`: Add your hostname.
- `CORS_ALLOWED_ORIGINS`: Add your request origin.
- `LANGUAGE_CODE`: Set default language code.
- `TIME_ZONE`: Set server time zone if different than UTC.
- `DB_PATH`: Set to a valid sqlite3 database file

Now, run migrations to create and prepare database:

```
./manage.py migrate
```

Then, create a super user to enter admin panel:

```
./manage.py createsuperuser
```

Finally, collect static files for admin panel:

```
./manage.py collectstatic
```

To run server locally, use:

```
./manage.py runserver
```


## Deploy

Read the [deployment](https://github.com/munshkr/muxy/wiki/Deploy) wiki page.
