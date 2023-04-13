# code commented by jagadishmagesh1999@gmail.com
{
    'name': 'Stock Inventory Movement Report (On Excel)',
    'version': '1.2',
    'sequence': 1,
    'summary': 'Stock Inventory Movement And Valuation Report in Excel',
    'description': """  This module helps to view product movement [IN/OUT] from selected warehouse by selecting date. """,
    'category': 'Stock',
    'author': 'JETZERP',
    'website': 'https://jetzerp.com/',
    'depends': ['account', 'stock', 'web'],
    'data': [
        'wizards/inventory_movemet_view.xml',
        'reports/report.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
