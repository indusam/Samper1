{
    'name': "MX EDI - Fix BaseP Precision (CRPER654)",
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': "Fix BaseP decimal precision in payment complement (CFDI Pagos 2.0) to satisfy SAT validation CRPER654",
    'description': """
Overrides the ``payment20`` QWeb template from ``l10n_mx_edi`` so that the
``BaseP`` attribute is rounded to the payment currency's decimal places
instead of being hardcoded to 6 decimals, which the SAT rejects with
error CRPER654 for currencies such as MXN (max 2 decimals).
""",
    'author': "Samper",
    'license': 'LGPL-3',
    'depends': ['account', 'l10n_mx_edi'],
    'data': [
        'data/payment20_basep_fix.xml',
    ],
    'installable': True,
    'auto_install': False,
}
