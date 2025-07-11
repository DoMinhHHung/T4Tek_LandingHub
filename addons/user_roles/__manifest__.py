{
    'name': 'User Roles',
    'version': '1.0',
    'summary': 'Module phân quyền người dùng cho hệ thống landing hub',
    'description': 'Quản lý các nhóm quyền Admin, CTV, CTV SEO, Kiểm duyệt viên và User',   
    'category': 'Tools',
    'depends': ['base'],
    'license': 'LGPL-3',
    'sequence': 5,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/roles_views.xml',
        'views/roles_menu.xml',

    ],
    'installable': True,
    'application': True,
}
