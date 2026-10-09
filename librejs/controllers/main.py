"""Web-labels controller: the LibreJS 'JavaScript License Web Labels' table."""
from odoo import http
from odoo.http import request
from odoo.release import series

# ponytail: static bundle list — Odoo emits a fixed set of bundles per page;
# try/except keeps this working across 18/19/20 where names differ.
BUNDLES = [
    'web.assets_frontend_minimal',
    'web.assets_frontend_lazy',
    'web.assets_frontend',
    'web.assets_web',
    'web.assets_backend',
]

LICENSE_URL = 'http://www.gnu.org/licenses/lgpl-3.0.html'
LICENSE_NAME = 'GNU-LGPL-3.0-or-later'
SOURCE_URL = f'https://github.com/odoo/odoo/tree/{series}'


class LibreJSController(http.Controller):

    @http.route('/web/jslicense', type='http', auth='public')
    def jslicense(self, **kwargs):
        qweb = request.env['ir.qweb']
        scripts = []
        for bundle in BUNDLES:
            try:
                nodes = qweb._get_asset_nodes(bundle, css=False, js=True)
            except Exception:
                continue  # bundle doesn't exist in this version
            for node in nodes:
                src = node[1].get('src')
                if src and src not in scripts:
                    scripts.append(src)
        return request.render('librejs.weblabels', {
            'scripts': scripts,
            'license_url': LICENSE_URL,
            'license_name': LICENSE_NAME,
            'source_url': SOURCE_URL,
        })
