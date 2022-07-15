
{
    'name': 'Account Rate Alternative',
    'version': '1.0 (14.0)',
    'category': 'Currency',
    'description': """Zmiana kursu waluty dla poszczególnych faktur, z pominięciem aktualnych kursów dostępnych w bazie danych.""",
    'author': "Jan Dziurzyński, Maciej Wichowski - OpenGlobe",
    'website': 'http://www.openglobe.pl',
    'depends': [
                # 'account',
                'account_invoice_pl_og',
                ],
    'data': [
        'views/account_invoice_view.xml',
        'views/account_view.xml',
        # 'views/account_move_view.xml',
    ],
    'demo': [],
    'test':[],
    'installable': True,
    'images': [],
}
