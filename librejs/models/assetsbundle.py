"""Tag minified JS bundles with a LibreJS-recognizable license banner.

Odoo's own JS (and the free-software libraries bundled with it) is LGPL-3.
The banner is prepended after minification, before the bundle ir.attachment
is written, so every JS file sent to the browser carries its license.
"""
from odoo import models
from odoo.addons.base.models.assetsbundle import AssetsBundle

LICENSE_JS = """\
/* @licstart  The following is the entire license notice for the
 * JavaScript code in this page.
 *
 * Copyright (C) Odoo S.A. and contributors
 *
 * The JavaScript code in this page is free software: you can
 * redistribute it and/or modify it under the terms of the GNU
 * Lesser General Public License (GNU LGPL) as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.  The code is distributed
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU LGPL for more details.
 *
 * As additional permission under GNU LGPL version 3 section 7, you
 * may distribute non-source (e.g., minimized or compacted) forms of
 * that code without the copy of the GNU LGPL normally required by
 * section 4, provided you include this license notice and a URL
 * through which recipients can access the Corresponding Source.
 *
 * @licend  The above is the entire license notice
 * for the JavaScript code in this page.
 */
"""


class LibreJSAssetsBundle(AssetsBundle):
    def save_attachment(self, extension, content):
        # ponytail: tag min.js only — debug bundles keep their sourcemap
        # line offsets intact and are covered by the page-level notice.
        if extension == 'min.js':
            content = LICENSE_JS + content
        return super().save_attachment(extension, content)


class IrQweb(models.AbstractModel):
    _inherit = 'ir.qweb'

    # Mirrors odoo.addons.base.models.ir_qweb.IrQweb._get_asset_bundle,
    # returning our subclass so every bundle gets the banner.
    # ponytail: *args/**kwargs forward — signature differs between Odoo
    # versions (20 adds binary/autoprefix); forwarding keeps us compatible.
    def _get_asset_bundle(self, bundle_name, *args, **kwargs):
        if kwargs.get('assets_params') is None:
            kwargs['assets_params'] = self.env['ir.asset']._get_asset_params()
        files, external_assets = self._get_asset_content(bundle_name, kwargs['assets_params'])
        return LibreJSAssetsBundle(bundle_name, files, external_assets,
                                   env=self.env, *args, **kwargs)


def post_init_hook(env):
    # Bundles generated before this module existed have no banner; drop them
    # so they are rebuilt on the next request.
    env['ir.attachment'].sudo().search([
        ('url', 'like', '/web/assets/%'),
        ('url', 'like', '%.js'),
    ]).unlink()
