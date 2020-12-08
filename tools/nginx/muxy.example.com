server {
    listen 4567;
    server_name muxy.example.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/sammy/muxy/static;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/muxy_gunicorn.sock;
    }
}
