# muxy

[![Django CI](https://github.com/munshkr/muxy/actions/workflows/django.yml/badge.svg)](https://github.com/munshkr/muxy/actions/workflows/django.yml)

RTMP-based streaming muxer for online events

Allows user to organize online self-streaming events, where each user can
stream herself to public channels or other streaming services.

## Requirements

* Postgres
* Python
* nginx-rtmp

## Install

### Docker

The easiest way to get everything running quickly is by using Docker Compose.

Run:

```bash
docker compose up 
```

This will build Muxy and start the server, while also serving Postgres database
service and nginx-rtmp.

### Manual

Clone repository or download zipfile and extract somewhere.

Create virtual environment and activate:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Initial configuration

Copy `env.sample` to `.env` and update if necessary. You should set at least:

- `SECRET_KEY`: Use a unique random string.
- `ALLOWED_HOSTS`: Add your hostname.
- `CORS_ALLOWED_ORIGINS`: Add your request origin.
- `LANGUAGE_CODE`: Set default language code.
- `TIME_ZONE`: Set server time zone if different than UTC.
- `PG*`: Set to corresponding Postgres database server

Now, run migrations to create and prepare database:

```bash
./manage.py migrate
```

Then, create a super user to enter admin panel:

```bash
./manage.py createsuperuser
```

Finally, collect static files for admin panel:

```bash
./manage.py collectstatic
```

## Usage

If you are using Docker, just use `docker compose up`

Otherwise, to run server locally, use:

```bash
./manage.py runserver
```

## Deploy

Read the [deployment](https://github.com/munshkr/muxy/wiki/Deploy) wiki page.

## License

This project is licensed under the GNU Affero General Public License v3.0.
See the [LICENSE](LICENSE) file for details.
