from odoo import http
from odoo.http import request

class LandingPageController(http.Controller):

    @http.route('/landing/page/review/<int:landing_id>', type='http', auth='user', website=True)
    def review_landing_page(self, landing_id, **kwargs):
        landing = request.env['landing.page'].sudo().browse(landing_id)
        return request.render('website_censorship.template_landing_review', {
            'landing': landing
        })

    @http.route('/landing/page/review/save/<int:landing_id>', type='http', auth='user', methods=['POST'], csrf=False)
    def review_submit(self, landing_id, **post):
        record = request.env['landing.page'].sudo().browse(landing_id)
        # Danh sách các trường boolean kiểm duyệt
        checklist_fields = [
            'is_design_ok',
            'is_text_clear',
            'is_mobile_friendly',
            'is_links_working',
            'is_form_functional',
            'is_browser_compatible',
            'is_legit_content',
            'is_clear_contact',
            'is_no_prohibited_content',
        ]

        # Gán giá trị cho mỗi trường (True nếu có trong form post)
        values = {field: field in post for field in checklist_fields}

        # Thêm feedback
        values['feedback'] = post.get('feedback', '')

        # Cập nhật trạng thái: chỉ duyệt nếu tất cả đều True
        values['status'] = 'approved' if all(values[field] for field in checklist_fields) else 'rejected'

        record.write(values)

        return request.redirect('/web')
