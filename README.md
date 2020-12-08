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

To run server locally, use:

```
./manage.py runserver
```


## Deploy

### Configure Muxy server

Copy service files for gunicorn:

```bash
sudo cp tools/systemd/muxy_gunicorn.* /etc/systemd/system/
```

Edit `/etc/systemd/system/muxy_gunicorn.service` to replace path to muxy on
`ExecStart`, and correctly set `User` and `Group`.

Copy nginx site config:

```bash
sudo cp tools/nginx/muxy.example.com /etc/nginx/conf.d/sites-available/
```

Rename file to correct server name and edit file to fix server name.

### Configure nginx-rtmp to set validation

The following is an `nginx-rtmp` sample configuration, that configures an RTMP
application to use Muxy allow/deny mechanism.

```
rtmp {
    application live {
        ...

        notify_update_timeout 10s;

        # HTTP callback when a stream starts publishing.
        # Returns 2xx only if publisher is allowed to publish now.
        on_publish http://localhost:4567/events/rtmp/on-publish/;

        # Called when a stream stops publishing.  Response is ignored.
        on_publish_done http://localhost:4567/events/rtmp/on-publish-done/;

        # Called with a period of notify_update_timeout,
        # to force disconnect publisher when her allotted time ends.
        on_update http://localhost:4567/events/rtmp/on-update/;
    }
}
```
