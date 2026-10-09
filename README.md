# odoo-librejs

A small Odoo module that makes an Odoo site pass GNU LibreJS. It is a port of
the approach used by [wp-librejs, a WordPress plugin](https://wordpress.org/plugins/wp-librejs/): instead of touching any
JavaScript, the site declares that the JS it serves is free software.

Odoo Community's own JavaScript is LGPL-3 and the libraries bundled with it are
free too (MIT, BSD, Apache). The module says so in the three places LibreJS
looks, plus one extra:

1. An inline `@licstart`/`@licend` license notice on every page. Frontend and
   backend both render through `web.layout`, so one inherited template covers
   both.
2. A hidden `<a rel="jslicense">` link pointing at `/web/jslicense`.
3. A "JavaScript License Web Labels" table at `/web/jslicense`
   (`<table id="jslicense-labels1">`), one row per script the site serves, each
   with a license link and a source link.
4. Every minified JS bundle gets the same license banner prepended before it is
   stored and served, so the tag travels with the file itself and not just the
   page that references it.

Tested on Odoo 18 LTS and 20. The asset API these hooks use is the same on 19,
so it works there too. Nothing to configure.

## Installing into an Odoo Community instance

1. Put the `librejs` folder somewhere on the server and make sure it is on the
   addons path, either by copying it into an existing addons directory or by
   extending the path at startup:

   ```
   cp -r librejs /opt/odoo/extra-addons/

   odoo --addons-path=/opt/odoo/extra-addons,<your usual paths>
   ```

2. Install it. Either from the backend: activate developer mode (Settings,
   General Settings, Developer Tools), go to Apps, click Update Apps List,
   search for "LibreJS tagging" and hit Install. Or from the command line:

   ```
   odoo -d yourdb -i librejs --stop-after-init
   ```

3. Restart Odoo. JS bundles that were cached before the module existed are
   dropped by its post-init hook and rebuilt with the banner on the next
   request, so no manual cache clearing is needed.

Uninstalling the module removes the notice, the link and the labels page.
Bundles cached while it was active stay tagged until they are regenerated, so
uninstall and then bump the assets if you want them gone immediately (or just
restart with `-u base`).

## Trying it with podman

Postgres and Odoo on one network, module mounted in:

```bash
podman network create odoo

podman run -d --name odoo-db --network odoo \
  -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres \
  -v odoo-db-data:/var/lib/postgresql/data \
  docker.io/library/postgres:16

podman run -d --name odoo --network odoo -p 8069:8069 \
  -e HOST=odoo-db -e USER=odoo -e PASSWORD=odoo \
  -v odoo-data:/var/lib/odoo \
  -v "$(pwd)/librejs:/mnt/extra-addons/librejs" \
  -t docker.io/library/odoo:20 \
  -d odoo -i librejs --http-interface=0.0.0.0
```

First start takes a minute or two while the database is created, then open
http://localhost:8069 and log in with admin/admin. Swap the image tag to
`odoo:18` for the LTS. Two podman quirks worth knowing: recent Odoo images bind
127.0.0.1 inside the container, which is what the `--http-interface` flag
fixes, and podman 6 removed `--link`, hence the explicit network.

## Testing

Without LibreJS involved, check that everything is tagged before it is sent:

```
python3 check_librejs.py http://localhost:8069
```

The script fetches the login page, confirms the inline notice and the
rel=jslicense link are present, downloads every script tag it finds and checks
that each one starts with the license banner, checks all of them are listed in
the web labels table, and finally parses the bundle to make sure the banner did
not break the JavaScript.

Then with LibreJS: install the
[LibreJS extension](https://addons.mozilla.org/firefox/addon/librejs/) in
Firefox, open the site, and the icon should report no non-free JavaScript.
Loading the same site in a profile without the extension should behave exactly
like a stock Odoo.
