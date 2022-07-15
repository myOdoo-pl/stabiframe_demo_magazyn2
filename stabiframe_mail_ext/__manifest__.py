{
    'name': 'StabiFrame mail ext',
    'summary': 'StabiFrame mail ext',
    'description': '''
    Mail extension module for StabiFrame.
    ''',
    'author': 'myOdoo.pl',
    'website': 'https://myodoo.pl',
    'category': 'Tools',
    'version': '[V14]_0.4',
    'depends': [
        'account',
        'mail',
        'sale'
    ],
    'data': [
        'data/mail_data.xml',
        'data/mail_template_data.xml'
    ],
    'installable': True,
    'auto_install': False,
}
