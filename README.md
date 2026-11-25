# Type Camp

Type Camp is a phone-friendly trainer for Pokémon GO players who want to recall type matchups during battles. Guided progression starts with Water, Fire, and Grass, then unlocks all 18 types and gradually introduces dual-type defenders. Each answer shows the GO multiplier. Water against Fire/Rock, for example, gets two advantages for a total of **1.6 × 1.6 = 2.56×**.

> **AI disclaimer**
>
> OpenAI’s ChatGPT Codex wrote all of this project’s code as an experiment to evaluate its capabilities. The code has not been reviewed by a human. Use it at your own risk.

The daily goal is ten questions. Keep practicing for as long as you like. Your browser remembers your profile automatically. To share progress with another device, open **Progress → Get recovery phrase** and enter the nine Pokémon names on the other device.

## How progression works

Every **10 correct answers** unlocks one more type, for both attacking moves and single-type defenders. All 18 single types are available after 150 correct answers; the first dual combination unlocks at 160. Each following set of 10 correct answers adds one dual combination, while keeping the single types and earlier dual combinations in practice. Missed and due reviews retain priority; other new questions favor the latest unlock.

The practice menu also offers **All 18 types** and **All dual types** immediately. Correct answers in every mode contribute to guided progression, including existing practice history. Returning to guided progression keeps your earned unlocks. Mistakes never remove unlocks, and progress carries across days and linked devices. The daily goal still counts all answers, independently of unlocks.

The bundled catalog covers **139 unique dual combinations** marked released in [PvPoke’s Pokémon GO roster](https://github.com/pvpoke/pvpoke/blob/a2dfcacab516ff0826ce7cfa2b4ac1cc10112587/src/data/gamemaster/pokemon.json), checked on November 25, 2026, including regional forms and Mega Evolutions. Type order does not create a second combination. The app needs no live data service. To include future GO releases, update `trainer/dual_types.py` from released entries in that roster and append new combinations without reordering existing ones. Keep the seven legacy examples and their type order to preserve saved review keys.

## Why the lessons work this way

Answering from memory practices retrieval. Immediate feedback corrects mistakes, and returning to a matchup on a later day builds longer-term recall. Type Camp schedules missed matchups for tomorrow and extends the interval when you remember them on a later review. [Retrieval practice](https://doi.org/10.1111/j.1467-9280.2006.01693.x) · [Corrective feedback](https://pubmed.ncbi.nlm.nih.gov/18491500/) · [Spaced practice](https://digitalcommons.usf.edu/psy_facpub/1766/)

## Deploy on an Ubuntu VPS

Type Camp uses Django, SQLite, and plain browser JavaScript. These steps assume Ubuntu 24.04 LTS, a user with `sudo`, and a domain pointed at the VPS. Allow incoming HTTP and HTTPS traffic on ports 80 and 443.

### 1. Install and clone

```sh
sudo apt update
sudo apt install git python3-venv nginx certbot python3-certbot-nginx openssl
sudo install -d -o "$(id -un)" -g "$(id -gn)" -m 755 /srv/typecamp
git clone https://github.com/jusasiiv/Type-Camp.git /srv/typecamp
cd /srv/typecamp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Configure the app

Run these once from the repo root. The first command creates a private `.env` from the tracked defaults. The second fills in a fresh secret key. Keep this file when updating.

```sh
install -m 600 .env.example .env
sed -i "s/^DJANGO_SECRET_KEY=$/DJANGO_SECRET_KEY=$(openssl rand -hex 32)/" .env
nano .env
```

Set `DJANGO_ALLOWED_HOSTS` to your domain (for example, `camp.example.com`, without `https://`). Adjust `TRAINER_TIME_ZONE` if you want the daily lesson to reset at a different local midnight. Git ignores `.env`.

### 3. Start the service

The supplied systemd unit reads `/srv/typecamp/.env`, creates the SQLite data directory at `/var/lib/typecamp`, and applies migrations before starting Gunicorn. Run static collection as the checkout owner.

```sh
sudo adduser --system --group --no-create-home typecamp
set -a
. ./.env
set +a
.venv/bin/python manage.py collectstatic --noinput
sudo install -m 644 deploy/typecamp.service /etc/systemd/system/typecamp.service
sudo systemctl daemon-reload
sudo systemctl enable --now typecamp
sudo systemctl status typecamp --no-pager
```

### 4. Connect your domain and enable HTTPS

In the same shell, use the domain from step 2 to install the Nginx site and request its certificate.

```sh
sed "s/camp.example.com/$DJANGO_ALLOWED_HOSTS/g" deploy/nginx.conf | sudo tee /etc/nginx/sites-available/typecamp >/dev/null
sudo ln -s /etc/nginx/sites-available/typecamp /etc/nginx/sites-enabled/typecamp
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx --redirect -d "$DJANGO_ALLOWED_HOSTS"
```

Open `https://your-domain/progress/` on your phone. If the app fails to start, inspect the service log with `sudo journalctl -u typecamp -n 50 --no-pager`.

### Update an installation

Back up the SQLite database and keep your existing `.env`. Run the following from `/srv/typecamp`.

```sh
git pull --ff-only origin trunk
.venv/bin/pip install -r requirements.txt
set -a
. ./.env
set +a
.venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart typecamp
```

## Credits

Type Camp is an unofficial fan project. Pokémon and character artwork belong to their respective owners. [Pokémon GO type chart](https://scopelyexplore.helpshift.com/hc/en/5-pokemon-go/faq/1157-type-effectiveness-in-battle/) · [PokéAPI sprites](https://github.com/PokeAPI/sprites)
