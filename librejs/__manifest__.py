{
    'name': 'LibreJS tagging',
    'version': '1.0',
    'summary': 'Tag all served JavaScript as free software for GNU LibreJS',
    'description': """
Odoo port of the wp-librejs approach (https://wordpress.org/plugins/wp-librejs/):

* Inline @licstart/@licend blanket license notice on every page (LGPL-3-or-later).
* Hidden rel="jslicense" link pointing at /web/jslicense.
* /web/jslicense serves the JavaScript License Web Labels table (id="jslicense-labels1").
* Minified JS bundles are prefixed with the license banner before being sent to the browser.
""",
    'category': 'Hidden',
    'depends': ['web'],
    'data': [
        'views/templates.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'license': 'LGPL-3',
}
