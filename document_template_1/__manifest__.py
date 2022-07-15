{
    'name': 'Document Templates 1',
    'summary': 'First template set.',
    'description': '''
    Module for overwriting base Odoo templates (standard)
    for documents in sale and account.invoice. Set 1 of 3.
    ''',
    'author': 'myOdoo.pl',
    'website': 'https://myodoo.pl',
    'category': 'Templates',
    'version': '[V14]_3.16',
    'depends': [
        'account',
        'sale',
        'sale_management',
        'account_invoice_templates',
        'stabiframe_downpayment_modification'
    ],
    'data': [
        'report/external_layout_template.xml',
        'report/invoice_report_template.xml',
        'report/sale_report_template.xml',
        'views/sale_view.xml',
        'views/payment_method.xml'
    ],
    'installable': True,
    'auto_install': False,
}
