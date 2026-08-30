# Deploying StrictDoc (strictdoc.navtopilote.dev)

## Commands

```sh
cd ~/vps_infrastructure_2/services/strictdoc

# status / logs / restart
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f strictdoc_web
docker compose -f docker-compose.prod.yml restart

# redeploy (git pull first for new eurobot/ content)
git pull
docker compose -f docker-compose.prod.yml up -d --build

# health check
curl -s -o /dev/null -w '%{http_code}\n' https://strictdoc.navtopilote.dev/
```

This app is a fork of the open-source StrictDoc requirements-management tool,
repurposed for the Eurobot robotics course (see `AGENTS.md`/`README.md`). It's
deployed behind this VPS's shared `core/` edge nginx, protected by Authelia
(`core/authelia/`) since StrictDoc's own web server has no auth or read-only
mode of its own — anyone who reaches it unauthenticated is bounced to
`https://auth.navtopilote.dev/`.

Unlike `chat`, there's no CI, no dedicated nginx/certbot, and no database —
StrictDoc is purely file-based. TLS/proxying is entirely the shared edge's job
(`core/edge/conf.d/strictdoc.conf`); auth is entirely Authelia's job.

## Redeploy loop

```sh
cd ~/vps_infrastructure_2/services/strictdoc
git pull                      # picks up new eurobot/ content or a Dockerfile bump
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs -f strictdoc_web
```

No edge reload needed — `strictdoc.conf` uses the `resolver 127.0.0.11 +
set $upstream_strictdoc` trick, so nginx re-resolves the container's IP on
every request instead of caching it from container start.

A plain `docker compose restart strictdoc_web` (no `--build`) is enough for a
content-only change, since `eurobot/` is bind-mounted into the container, not
baked into the image — `--build` only matters if the Dockerfile or the
installed StrictDoc version needs to change.

## Status / logs / restart

```sh
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f strictdoc_web
docker compose -f docker-compose.prod.yml restart
```

## Health checks

```sh
curl -s -o /dev/null -w '%{http_code}\n' https://strictdoc.navtopilote.dev/   # 302 unauthenticated, 200 once logged in
docker compose -f docker-compose.prod.yml exec strictdoc_web wget -qO- http://127.0.0.1:5111/ | head
```

## Direction of truth — the web-edit caveat

The container mounts `./eurobot` read-write, and StrictDoc's web UI can save
node edits, grammar changes, and document config changes directly to those
files. **Any edit made through the authenticated web UI lands in this git
working tree, not in a commit.** If you (or anyone with an Authelia login)
edits a document in the browser and then a later `git pull` brings in
upstream changes, you can lose that edit or hit a merge conflict. Treat live
web edits the same as any other local change: `git status` / commit / push
them yourself before the next `git pull` — nothing here does that
automatically.

## Why `working_dir: /data/eurobot`, not `/data`

`strictdoc server` writes its cache/output dir relative to the process's CWD.
Only `./eurobot` is bind-mounted (deliberately narrower than the whole
fork — `eurobot/` is self-contained, so the running container never sees the
rest of the source tree). The image's `WORKDIR` (`/data`) itself is
root-owned and nothing is mounted there, so running with CWD `/data` and
`strictdoc server eurobot` fails with `Permission denied: 'output'`. Fix:
`working_dir: /data/eurobot` + `command: strictdoc server . ...` — CWD is the
writable bind mount itself.

## Adding a second Authelia-protected service later

No new Authelia container needed:
1. Add an `access_control` rule for the new domain in
   `core/authelia/configuration.yml`.
2. In that service's own edge vhost, add `resolver 127.0.0.11 valid=10s;`,
   `error_page 401 =302 https://auth.navtopilote.dev/?rd=$scheme://$http_host$request_uri;`,
   and inside its `location /`: `include /etc/nginx/snippets/authelia.conf;`
   is actually the internal verify location (add it once per server block,
   see `strictdoc.conf` for the exact shape) plus `auth_request
   /authelia-verify;`.
3. `docker compose -f core/docker-compose.yml restart authelia` only if you
   changed `configuration.yml` (it doesn't hot-reload); `nginx -t && nginx -s
   reload` on `edge` for the vhost change.

## Admin account / password reset

One user is seeded in `core/authelia/users.yml` (argon2id hash — generate a
new one with `docker run --rm authelia/authelia:latest authelia crypto hash
generate argon2 --password '<pw>'`, the CLI subcommand is `crypto hash
generate argon2`, not the older `hash-password`). Password reset emails go
through the same AWS SES SMTP account `chat` uses
(`services/chat/.env`'s `SMTP_*`/`EMAIL_FROM`) — port 587/STARTTLS was
assumed since chat's `.env` doesn't pin an explicit port; if reset emails
don't arrive, check that assumption first (`core/authelia/configuration.yml`'s
`notifier.smtp.address`).

## Secrets

`core/authelia/secrets/*.txt` (chmod 600, gitignored via
`core/authelia/secrets/` in the outer `.gitignore`): `jwt_secret`,
`session_secret`, `storage_encryption_key` (each a fresh `openssl rand -hex
64`), and `smtp_password` (copied verbatim from `services/chat/.env`). None of
these live in `configuration.yml` itself — they're injected via Authelia's
`AUTHELIA_*_FILE` environment-variable convention in `core/docker-compose.yml`.
