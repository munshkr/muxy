# muxy

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

Copy `env.sample` to `.env` and update if necessary. You should set at least:

- `SECRET_KEY`: Use a unique random string.
- `ALLOWED_HOSTS`: Add your hostname.
- `LANGUAGE_CODE`: Set default language code.
- `TIME_ZONE`: Set server time zone if different than UTC.

To run server locally, use:

```
./manage.py runserver
```


## Deploy

### Configure Muxy server

Copy service files for gunicorn:

```bash
sudo cp tools/systemd/muxy-gunicorn.s* /etc/systemd/system/
```

Edit `/etc/systemd/system/muxy-gunicorn.service` to replace path to muxy on
`ExecStart`, and correctly set `User` and `Group`.

Start and enable service for gunicorn:

```bash
sudo systemctl start muxy-gunicorn
sudo systemctl enable muxy-gunicorn
```

Check if service is running correctly with:

```bash
sudo systemctl status muxy-gunicorn
```

Copy nginx site config:

```bash
sudo cp tools/nginx/muxy.example.com /etc/nginx/sites-available/
```

Rename file to correct server name and edit file to fix server name.

Then, enable site config on Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/muxy.example.com /etc/nginx/sites-enabled/
```

Check for syntax errors on config before restarting nginx:

```bash
sudo nginx -t
```

If everything went OK, restart Nginx:

```bash
sudo systemctl restart nginx
```

### Configure nginx-rtmp to set validation

The following is an `nginx-rtmp` sample configuration, that configures an RTMP
application to use Muxy allow/deny mechanism.  Remember to replace
`muxy.example.com` with your Muxy hostname.

```
rtmp {
    application live {
        ...

        notify_update_timeout 10s;

        # HTTP callback when a stream starts publishing.
        # Returns 2xx only if publisher is allowed to publish now.
        on_publish http://muxy.example.com/rtmp/on-publish/;

        # Called when a stream stops publishing.  Response is ignored.
        on_publish_done http://muxy.example.com/rtmp/on-publish-done/;

        # Called with a period of notify_update_timeout,
        # to force disconnect publisher when her allotted time ends.
        on_update http://muxy.example.com/rtmp/on-update/;
    }
}
```
