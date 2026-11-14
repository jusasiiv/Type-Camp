# Type Camp

A mobile-first Pokémon GO type trainer built with Django 5.2, SQLite, HTML, CSS, and plain browser JavaScript. JavaScript updates the lesson card in place. Standard forms also support the entire practice flow.

## Run locally

Use Python 3.10–3.14. From the project directory on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Run the tests with `.\.venv\Scripts\python manage.py test`.

## Practice and persistence

- Start with Water, Fire, and Grass. Use the deck selector to practice all 18 single types or a set of real dual-type defenders.
- A lesson targets ten answers per calendar day. Continue indefinitely, or finish and return later. Each submitted answer is saved in SQLite.
- Missed matchups are eligible for another try after two intervening answers and are due the next day. Correct recall on a due day increases the interval. Same-day repetitions cannot promote a matchup.
- The progress screen counts matchups successfully recalled on a later review day. A signed, long-lived browser cookie identifies each anonymous trainer.
- For cross-device access, choose **Progress → Get recovery phrase** and save the nine Pokémon names in order. On another device open the same site and choose **Progress → Restore progress with a phrase**. Capitalization, extra spaces, and hyphen separators are accepted. Both devices then share the same questions, attempts, and review schedule. A browser with existing answers shows both lifetime totals before changing profiles.
- The server stores a hash of the phrase. Save the phrase when it appears or replace it from a connected browser. Clearing cookies starts a new profile until you restore the original.
- The Python chart calculates type effectiveness by adding exponents for the defending types, then applying the Pokémon GO base of 1.6. Other battle damage factors are outside the scope of this trainer.

## Host on Ubuntu

Copy the source to the VPS, e.g. `/srv/typecamp`. Create a Python virtual environment there and install the dependencies:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Create an environment file at `/etc/typecamp.env` readable by the service. Set `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS=your.domain`, `DJANGO_SECRET_KEY` to a stable random secret, and `TRAINER_DB=/var/lib/typecamp/db.sqlite3`. Generate a secret with `.venv/bin/python -c "import secrets; print(secrets.token_urlsafe(64))"`. Optionally set `TRAINER_TIME_ZONE` to the IANA time zone for daily lessons. The default is Europe/Helsinki.

Create a system user named `typecamp` and give it write access to `/var/lib/typecamp`. With the environment variables above exported, run `.venv/bin/python manage.py migrate` as that user, then `.venv/bin/python manage.py collectstatic --noinput` as the project owner and `.venv/bin/python manage.py check --deploy`.

Example systemd unit at `/etc/systemd/system/typecamp.service`:

```ini
[Unit]
Description=Type Camp Django application
After=network.target

[Service]
User=typecamp
WorkingDirectory=/srv/typecamp
EnvironmentFile=/etc/typecamp.env
ExecStart=/srv/typecamp/.venv/bin/gunicorn --bind 127.0.0.1:8100 --workers 2 config.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Run `sudo systemctl daemon-reload` and `sudo systemctl enable --now typecamp`. Point your domain at the VPS and configure its HTTPS reverse proxy. For Nginx, put these locations inside your domain’s TLS server block:

```nginx
location /static/ {
    alias /srv/typecamp/staticfiles/;
}
location / {
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_pass http://127.0.0.1:8100;
}
```

Open the HTTPS domain on your phone. Keep the secret key when updating the app and back up the database using SQLite’s backup facility.

## References

[Pokémon GO type chart](https://scopelyexplore.helpshift.com/hc/en/5-pokemon-go/faq/1157-type-effectiveness-in-battle/) · [GO Stadium battle handbook](https://www.stadiumgaming.gg/pdfs/handbook.pdf)

Pokémon sprites are distributed via the [PokéAPI sprite collection](https://github.com/PokeAPI/sprites). Pokémon and character artwork belong to their respective owners. Type Camp is an unofficial fan project.
