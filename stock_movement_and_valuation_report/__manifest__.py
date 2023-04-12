# code commented by jagadishmagesh1999@gmail.com
{
    'name': 'Stock Inventory Movement Report (On Excel)',
    'version': '1.2',
    'sequence': 1,
    'summary': 'Stock Inventory Movement And Valuation Report in Excel sheet',
    'description': """  This module helps to view product movement [IN/OUT] from selected warehouse by selecting date. """,
    'category': 'Stock',
    'author': 'JETZERP',
    'website': 'https://jetzerp.com/',
    'depends': ['account', 'stock', 'web'],
    'data': [
        'wizards/inventory_movemet_view.xml',
        # 'views/web_backend_css.xml',
        'reports/report.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    # 'icons': {
    #         '64': 'static/description/icon.png',
    #     },
    'images': [
        'static/description/banner.png',
        # 'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
