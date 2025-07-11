from odoo import models, fields, api
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import requests
import json


class LandingPage(models.Model):
    _name = 'landing.page'
    _description = 'Landing Page kiểm duyệt'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _logger = logging.getLogger(__name__)

    name = fields.Char(string='Tên landing page')
    url = fields.Char(string='URL trang web', required=True)
    status = fields.Selection([
        ('draft', 'Nháp'),
        ('pending', 'Chờ kiểm duyệt'),
        ('approved', 'Đã phê duyệt'),
        ('rejected', 'Từ chối'),
    ], string='Trạng thái', default='draft', readonly=True)

    feedback = fields.Text(string='Phản hồi kiểm duyệt')

    # Thông tin người thực hiện
    designer_id = fields.Many2one('res.users', string='Người thực hiện', tracking=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Số điện thoại')

    # Thông tin chi tiết
    topic = fields.Char(string='Chủ đề landing page')
    main_color = fields.Char(string='Màu sắc chủ đạo')
    launch_date = fields.Date(string='Ngày khởi chạy')
    target_audience = fields.Char(string='Đối tượng hướng đến')

    #Các trường đánh giá nội dung
    is_design_ok = fields.Boolean(string="Thiết kế hợp lý?")
    is_text_clear = fields.Boolean(string="Nội dung rõ ràng")
    is_mobile_friendly = fields.Boolean(string="Thân thiện di động")
    is_links_working = fields.Boolean(string="Liên kết hoạt động đúng")
    is_form_functional = fields.Boolean(string="Biểu mẫu hoạt động")
    is_browser_compatible = fields.Boolean(string="Tương thích trình duyệt")
    is_legit_content = fields.Boolean(string="Nội dung hợp pháp")
    is_clear_contact = fields.Boolean(string="Thông tin liên hệ rõ ràng")
    is_no_prohibited_content = fields.Boolean(string="Không có nội dung bị cấm")


    link_list = fields.Text(string="Danh sách liên kết")
    image_list = fields.Text(string="Danh sách hình ảnh")
    dangerous_links = fields.Text(string="Các liên kết nguy hiểm")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            url = vals.get('url')
            if url:
                links, images = self.extract_links_images(url)
                dangerous = self.check_urls_google_safebrowsing(links)
                vals['link_list'] = '\n'.join(links)
                vals['image_list'] = '\n'.join(images)
                vals['dangerous_links'] = '\n'.join(dangerous)
        return super().create(vals_list)           

    def write(self, vals):
        res = super().write(vals)
        if 'url' in vals:
            for record in self:
                links, images = record.extract_links_images(vals['url'])
                dangerous = record.check_urls_google_safebrowsing(links)
                record.link_list = '\n'.join(links)
                record.image_list = '\n'.join(images)
                record.dangerous_links = '\n'.join(dangerous)
        return res

    def extract_links_images(self, url):
        try:
            if not url.startswith('http'):
                url = 'http://' + url
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, timeout=10, headers=headers)
            print(response.text)
            soup = BeautifulSoup(response.text, 'html.parser')

            links = [urljoin(url, a.get('href')) for a in soup.find_all('a', href=True)]
            images = [urljoin(url, img.get('src')) for img in soup.find_all('img', src=True)]

            self._logger.info(f"Crawled {len(links)} links và {len(images)} images từ {url}")
            return links, images
        except Exception as e:
            self._logger.warning(f"Lỗi khi crawl {url}: {str(e)}")
            return [], []

    def check_urls_google_safebrowsing(self, urls):
        api_key = 'AIzaSyAg5fQ8dKDHlMeMpx91nlWGKu2G1yd-iYo'
        endpoint = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}'
        
        headers = {'Content-Type': 'application/json'}
        body = {
            "client": {
                "clientId": "odoo-system",
                "clientVersion": "1.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url} for url in urls]
            }
        }

        try:
            response = requests.post(endpoint, headers=headers, json=body, timeout=10)
            print(response.text)
            result = response.json()

            dangerous = set()
            if "matches" in result:
                for match in result["matches"]:
                    dangerous.add(match["threat"]["url"])
            return list(dangerous)

        except Exception as e:
            self._logger.warning(f"Lỗi khi gọi Google Safe Browsing: {e}")
            return []

    def action_open_iframe_review(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/landing/page/review/{self.id}',
            'target': 'current',
        }