# -*- coding: utf-8 -*-

from random import randint
from trfi_def import *
import logging
import time


#################


def handle_exception(exc_type, exc_value, exc_traceback):
	if issubclass(exc_type, KeyboardInterrupt):
		sys.__excepthook__(exc_type, exc_value, exc_traceback)
		return

	logger_err.error("Loi khong xac dinh:", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

#################


is_running = True
first_run = True
old_item = []


def set_first_run(status):
	global first_run
	first_run = status


def set_running(status):
	global is_running
	is_running = status


def set_old_item(status):
	global old_item
	old_item = status


def write_phone_to_file(phone):
	try:
		if read_json_file('config.json')['setting']['export_phone']:
			with open(f'phone{counter}.txt', 'a') as f:
				f.write(phone + '\n')
	except Exception:
		logger.error('Loi write phone to file: %s', phone, exc_info=True)


def search_phone(desc):
	try:
		return re.search(
			r'((09|03|07|08|05)+([0-9]{8})\b)|((02)+([0-9]{9})\b)|((09|03|07|08|05|02)+([0-9]{0,4}(([. ])[0-9]{2,4}){1,2}([. ])[0-9]{2,4})\b)',
			desc).group(0).replace('\n', '').replace('.', '')
	except AttributeError:
		return None


# t = Thread(target=save_moigioi)
# t.start()

data = read_json_file('data.json')
distrId = list(data['distr']['id'].values())
distrTen = data['distr']['name']
distr = data['distr']['ten_kdau']
distr_hcm = data['distr_hcm']['name_full']
distr_hcm2 = data['distr_hcm']['name']


def get_price2(price, **kwargs):
	site = kwargs.get('site')
	url = kwargs.get('url')
	if site == 1:
		dtich = kwargs.get('dtich')
		try:
			if dtich == 'Không xác định' or price == 'Thỏa thuận':
				return '0'
			# cho thuê
			elif price.endswith('triệu/tháng'):
				res = price.replace(' triệu/tháng', '')
				return res
			elif price.endswith('nghìn/m2/tháng'):
				dtich = float(dtich.replace('m²', ''))
				price = float(price.replace(' nghìn/m2/tháng', ''))
				res = str((round((price * dtich) / 1000)))
				res = res.replace('.0', '')
				return res
			elif price.endswith('triệu/m2/tháng'):
				dtich = float(dtich.replace('m²', ''))
				price = float(price.replace(' triệu/m2/tháng', ''))
				res = str((round((price * dtich), 1)))
				res = res.replace('.0', '')
				return res
			# ban
			elif price.endswith('triệu/m²'):
				dtich = float(dtich.replace('m²', ''))
				price = float(price.replace(' triệu/m²', ''))
				res = round(price * dtich)
				return res
			elif price.endswith('nghìn/m²'):
				dtich = float(dtich.replace('m²', ''))
				price = float(price.replace(' nghìn/m²', ''))
				res = round(price * dtich / 1000)
				return res
			elif price.endswith('triệu'):
				res = round(float(price.replace(' triệu', '')))
				return res
			else:
				price = float(price.replace(' tỷ', ''))
				res = round(price * 1000)
				return res
		except Exception as e:
			logger.error('Loi: %s %s', e, url, exc_info=True)
			return '0'
	elif site == 2 or site == 4:
		try:
			pri = int(price.rstrip(' đ').replace('.', ''))
			if len(str(pri)) > 9:
				price_str = str(pri / 1000000000).replace('.0', '') + ' tỷ'
			else:
				price_str = str(round(pri / 1000000, 2)).replace('.0', '') + ' triệu'
			pri = str(pri / 1000000).replace('.0', '')
			return [price_str, pri]
		except Exception as e:
			logger.error('Loi: %s %s', e, exc_info=True)
			return [price, '0']
	elif site == 5:
		try:
			if price.endswith('tỷ'):
				price = price.replace('tỷ', '')
				rs = str(float(price.replace(',', '.')) * 1000).replace('.0', '')
			elif 'tỷ' in price and price.endswith('triệu'):
				rs = price.replace(' tỷ ', '').replace(' triệu', '')
			elif price.endswith('Triệu'):
				price = price.replace('Triệu', '')
				rs = float(price) / 1000
			elif price.endswith('Triệu/tháng'):
				rs = price.replace(' Triệu/tháng', '').replace(',', '.')
			elif price.endswith('đ/tháng'):
				rs = float(price.replace('đ/tháng', '')) / 1000
			else:
				rs = '0'
			return rs
		except Exception as e:
			logger.error('Loi: %s %s', e, url, exc_info=True)
			return '0'
	elif site == 6:
		try:
			if price.endswith('tỷ'):
				price = price.replace('tỷ', '')
				rs = str(float(price) * 1000).replace('.0', '')
			elif price.endswith('triệu'):
				rs = price.replace(' triệu', '')
			elif price.endswith('triệu/th'):
				rs = price.replace(' triệu/th', '')
			else:
				rs = '0'
			return rs
		except Exception as e:
			logger.error('Loi: %s %s', e, url, exc_info=True)
			return '0'
	elif site == 7:
		dtich = kwargs.get('dtich')
		try:
			if price.endswith('tỷ'):
				price = price.replace('tỷ', '')
				rs = str(float(price.replace(',', '.')) * 1000).replace('.0', '')
			elif 'tỷ' in price and price.endswith('triệu'):
				rs = price.replace(' tỷ ', '').replace(' triệu', '')
			elif price.endswith('triệu'):
				price = price.replace('triệu', '')
				rs = round(float(price) / 1000, 2)
			elif price.endswith('triệu/m²'):
				dtich = float(dtich.replace('m²', ''))
				price = float(price.replace(' triệu/m²', ''))
				res = str((round((price * dtich), 1)))
				rs = res.replace('.0', '')
			elif price.endswith('triệu/tháng'):
				rs = price.replace(' triệu/tháng', '')
			else:
				rs = '0'
			return rs
		except ValueError:
			pass
		except Exception as e:
			logger.error('Loi: %s %s', e, url, exc_info=True)
			return '0'


def get_price(price, **kwargs):
	def toFloat(string):
		return float(re.sub(f'm2|m²|[^0-9.]', '', string.replace(',', '.')))

	acreage = kwargs.get('acreage')
	try:
		price = price.lower().replace('m2', 'm²').replace(' ', '')
		if price.endswith('triệu'):
			price = toFloat(price) * 1000000
		elif price.endswith('triệu/m²'):
			price = (toFloat(price) * 1000000) * toFloat(acreage)
		elif price.endswith('tỷ'):
			price = toFloat(price) * 1000000000
		elif price.endswith('triệu/tháng'):
			price = toFloat(price)
		elif price.endswith('đ'):
			price = float(re.sub(f'[^0-9]', '', price))
		elif 'nghìn/m²' in price:
			price = (float(re.sub(f'[^0-9]', '', price)) * 1000) * toFloat(acreage)
		else:
			price = toFloat(price) * 1000
		return ('%.1f' % price).replace('.0', '')
	except ValueError:
		return 0


item_url_old = []


def set_item_url_old(item_url, site=None):
	global item_url_old
	length_max = 1000 if site == 2 else 400
	item_url_old += item_url
	dif_len = len(item_url_old) - length_max
	if dif_len > 100:
		del item_url_old[0:dif_len]
		if site == 2: item_url_old = list(set(item_url_old))


def get_area(provin, area, name_full=True):
	if name_full:
		if provin == 1:
			area = distrId[data['distr']['name_full'].index(area)]
		elif provin == 2:
			area = distr_hcm.index(area)
	else:
		if provin == 1:
			area = distrId[data['distr']['name'].index(area)]
		elif provin == 2:
			area = distr_hcm2.index(area)
	return area


class Bdscomvn(Base):
	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'vi,en;q=0.9,en-US;q=0.8',
		'Cache-Control': 'max-age=0',
		'Connection': 'keep-alive',
		'Cookie': '',
		'Host': 'm.batdongsan.com.vn',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
	}
	ttype = data['type']['bdscomvn']

	def get_detail(self, result, index, url):
		try:
			content = BeautifulSoup(result, 'lxml')
			phone = None
			try:
				phone = select(content, '.mobilecontact a').replace('O', '0').replace('o', '0').replace('.', '')
			except AttributeError:
				logger.error('Khong co so dien thoai %s - %s', phone, url)
			except Exception as e:
				logging.exception(e)

			title_url = url.split('/')[-1]
			desc = select(content, 'span.des-c')
			title = content.title.text.strip()
			if not phone: return
			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					# logger.info('Get detail: %s', title_url)
					price = select(content, '#ContentPlaceHolder_ProductDetail1_price> span:nth-of-type(2)')
					dtich = select(content, '#ContentPlaceHolder_ProductDetail1_Area > span:nth-of-type(2)')
					giass = get_price(price, acreage=dtich)
					type_ = 1
					cate = select(content, '.o-i-field:contains("Loại tin rao") > span:nth-of-type(2)').split(' (')[0]
					if cate == 'Cho thuê nhà trọ, phòng trọ': return
					cate = self.ttype[cate]
					area = select(content, '.diadiem-title').split(' - ')[-2]
					area = get_area(self.provin, area)
				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price, dtich,
					                       phone, type_, cate, area, giass, 1)
					write_phone_to_file(phone)
		except Exception as e:
			logger.error('Loi get detail: %s. %s', url, e, exc_info=True)

	def crawl(self):
		start = time.time()

		if self.type_ == 1: types_ = ['nha-dat-ban']
		elif self.type_ == 2: types_ = ['nha-dat-cho-thue']
		else: types_ = ['nha-dat-ban', 'nha-dat-cho-thue']
		_provin = 'ha-noi'
		if self.provin == 2: _provin = 'tp-hcm'

		urls = 'https://m.batdongsan.com.vn/{}-{}/p{}'

		if self.start_page:
			page = self.start_page
		else:
			page = 1

		while is_running:
			self.mess_cb.emit(' Trang %d' % page)
			items = []
			item_url = []
			self.item_url_for_compare.clear()
			for id_type, type_ in enumerate(types_):
				if page == 1:
					url = f'https://m.batdongsan.com.vn/{type_}-{_provin}'
				else:
					url = urls.format(type_, _provin, page)
				logger.warning('Page %d: %s - %ss' % (page, url, (time.time() - start)))
				if self.provin == 1:
					if self.type_ == 0:
						if id_type == 0:
							self.headers['Cookie'] = 'psortfilter=1$all$PsAs9iPYViWM8VzRR2hJ8A=='
						else:
							self.headers['Cookie'] = 'psortfilter=1$all$aL2/k6bZotEQ9VvXPsCE2g=='
					elif self.type_ == 1:
						self.headers['Cookie'] = 'psortfilter=1$all$PsAs9iPYViWM8VzRR2hJ8A=='
					elif self.type_ == 2:
						self.headers['Cookie'] = 'psortfilter=1$all$aL2/k6bZotEQ9VvXPsCE2g=='
				elif self.provin == 2:
					if self.type_ == 0:
						if id_type == 0:
							self.headers['Cookie'] = 'psortfilter=1$all$vAnyoJDh59EEOUF8Pi5T/A=='
						else:
							self.headers['Cookie'] = 'psortfilter=1$all$NSJV6b9vujjVp0lMyafQig=='
					elif self.type_ == 1:
						self.headers['Cookie'] = 'psortfilter=1$all$vAnyoJDh59EEOUF8Pi5T/A=='
					elif self.type_ == 2:
						self.headers['Cookie'] = 'psortfilter=1$all$NSJV6b9vujjVp0lMyafQig=='
				html = request_get(url, headers=self.headers)
				if not html: break
				# with open(f'nhadat{page}.html', 'w', encoding='utf8') as file:
				# 	file.write(html.text)
				soup = BeautifulSoup(html.text, "lxml")
				items += selects(soup, '.s-list > li > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				new_url = 'https://m.batdongsan.com.vn{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			# logger.info('%d %s', index, href)
			# Nếu break ở đây thì sẽ break cả vòng lặp while 1 ở ngoài
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				# Nếu k break vòng lặp for ở trên thì tiếp tục chạy
				logger.warning('So luong tin: %d', len(item_url))
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(page, item_url, 1)
				if task1 == 'not_detail':
					logger_err.error('not_detail')
					self.row_was_insert = 0
				self.mess_cb.emit(f'Trang {page}: Lấy được {self.row_was_insert} tin')
				task2 = self.start_task2(page, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				page += 1
				continue

			break

	# logger.info("Elapsed Time: %ss" % (time.time() - start))


class Chotot(Base):
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'DNT': '1',
		'Referer': 'https://nha.chotot.com/ha-noi/thue-bat-dong-san',
		'Sec-Fetch-Mode': 'cors',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
	}
	type_ban = data['type']['chotot_ban']
	type_thue = data['type']['chotot_thue']
	distr_id = data['distr']['id_chotot']
	distr_id2 = data['distr_hcm']['id_chotot']
	details = {}
	number = 50

	def get_detail(self, lid, index):
		provin = 12000
		if self.provin == 2: provin = 13000
		try:
			r = request_get('https://gateway.chotot.com/v1/public/ad-listing/{}'.format(lid), headers=self.headers)
			if not r: return
			rs = r.json()
			ad = rs['ad']
			ad_id = ad['ad_id']
			try:
				price = ad['price']
			except KeyError:
				price = '0'
				price_str = '0'
				logger.info("Giá không xác định - %s", ad_id)
			else:
				if len(str(price)) > 9:
					price_str = str(price / 1000000000) + ' tỷ'
				else:
					price_str = str(price / 1000000).replace('.0', '') + ' triệu'
				price = str(round(price / 1000000))
			try:
				size = str(ad['size']) + 'm²'
			except KeyError:
				size = '0'
			title = ad['subject']
			title_url = sl(title) + '-' + str(ad_id)
			desc = ad['body']
			phone = ad['phone']
			if not phone: return
			phone = self.validate_phone(phone, desc, title, title_url)
			if not phone:
				return
			else:
				try:
					type_ = ad['type']
					cate = str(ad['category'])
					if type_ == 's':
						cate = self.type_ban[cate]
					else:
						if cate == '1050': return
						cate = self.type_thue[cate]
					type_ = 1
					area = provin + ad['area']
					if self.provin == 1:
						area = distrId[self.distr_id.index(area)]
					elif self.provin == 2:
						area = self.distr_id2.index(area)

				except Exception as e:
					logger.error(e, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, size, phone, type_, cate, area, price, 3)
					write_phone_to_file(phone)
					return title_url
		except Exception:
			logger.error('Loi get detail', exc_info=True)

	def crawl(self):
		provin = 12000
		if self.provin == 2: provin = 13000
		if self.type_ == 1:
			type_ = 's,k'
		else:
			type_ = 'h,u'
		urls = 'https://gateway.chotot.com/v1/public/ad-listing?region_v2={}&cg=1000&limit={}&o={}&st={}&sp=0'

		if self.start_page:
			i = (self.start_page * self.number) - self.number
		else:
			i = 0

		count_tin = 0
		while is_running:
			page = round(i / self.number) + 1
			url = urls.format(provin, self.number, i, type_)
			self.mess_cb.emit(' Trang %d' % page)
			logger.warning('Page %d: %s' % (page, url))
			html = request_get(url, headers=self.headers)
			list_items = html.json()
			list_id = []
			self.item_url_for_compare.clear()
			if not html: continue
			# threads = []
			for index, ads in enumerate(list_items['ads']):
				self.progress_cb.emit((index + 1) * 100 / len(list_items['ads']))
				lid = ads['list_id']
				self.item_url_for_compare.append(lid)
				if lid in item_url_old:
					continue
				else:
					list_id.append(lid)
					self.get_detail(lid, index)
			else:
				if not list_id:
					return f'Chưa có tin mới'
				set_item_url_old(list_id)
				logger.warning('Continue')
				logger.warning('So luong tin: %d', len(list_id))
				logger.info('Insert to db')
				detail = []
				try:
					sorted_detail = dict(sorted(self.details.items()))
					detail = list(sorted_detail.values())
				except Exception:
					logger.error('Loi sort detail', exc_info=True)

				if not detail:
					logger.warning('not detail')
					self.mess_cb.emit(f'Trang {page}: Lấy được 0 tin')
					task2 = self.start_task2(page, list_id, is_running, first_run, site=3)
					if task2 == 'stop':
						break
					elif task2 == 'found_old_item':
						return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
					elif task2 == 'finish':
						return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				else:
					row = self.inserts_to_db(detail)
					if not row:
						logger_err.error('not row')
						continue
					row_was_insert = row[0]
					row_duplicate = row[1]
					count_tin += row_was_insert
					self.mess_cb.emit(f'Trang {page}: Lấy được {row_was_insert} tin')

					detail.clear()

					task2 = self.start_task2(page, list_id, is_running, first_run)
					if task2 == 'stop':
						break
					elif task2 == 'found_old_item':
						return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {count_tin}'
					elif task2 == 'finish':
						return f'Finish. Tổng số tin lấy được: {count_tin}'
				i += self.number
				continue

			break


class Muaban(Base):
	headers = {
		'DNT': '1',
		'Referer': 'https://muaban.net/',
		'Sec-Fetch-Mode': 'no-cors',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	list_cate = data['type']['muaban']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1]
			title = select(soup, 'h1.title')
			desc = select(soup, 'div.body-container')
			phone = None
			try:
				phone = select(soup, 'div.mobile-container__value > span', get='mobile')
			except AttributeError:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: phone = search_phone(desc)
			if not phone: return

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, 'div.price-container__value')
					price = get_price(price_str)
				except Exception:
					price_str = 'KXĐ'
					price = 0
				try:
					dtich = select(soup, '.tech-item:contains("Diện tích đất:") > .tech-item__value')
					if dtich == '-':
						dtich = 'KXĐ'
					elif not dtich.endswith('m²'):
						dtich += 'm²'
				except AttributeError:
					dtich = 'KXĐ'
				try:
					area = select(soup, '.location-clock__location').split(' - ')[0].replace('Thị Xã Sơn Tây',
					                                                                         'Thị xã Sơn Tây')
					area = get_area(self.provin, area)
				except Exception as e:
					area = 'KXĐ'
					logger.error(e)
				try:
					# desc = str(content.select_one('.pm-desc')) \
					#     .lstrip('<div class="pm-desc">').rstrip('</div>').replace('<br/>', '\n')
					cate = url.split('/')[3].rsplit('-', 1)[1].replace('c', '')
					if cate.startswith('33'):
						cate = '33'
					cate = self.list_cate[cate]
					type_ = 1
				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, dtich,
					                       phone, type_, cate, area, price, 2)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()

		if self.provin == 1: provin = 'ha-noi-l24'
		else: provin = 'ho-chi-minh-l59'

		if self.type_ == 1:
			type_ = [f'ban-nha-{provin}-c32', f'ban-can-ho-chung-cu-tap-the-{provin}-c38',
			         f'ban-dat-{provin}-c31']
		elif self.type_ == 2:
			type_ = [f'cho-thue-nha-dat-{provin}-c34', f'sang-nhuong-cua-hang-{provin}-c33']
		elif self.type_ == 3:
			type_ = [f'ban-nha-{provin}-c32']
		elif self.type_ == 4:
			type_ = [f'ban-dat-{provin}-c31', f'ban-can-ho-chung-cu-tap-the-{provin}-c38']
		else:
			type_ = [f'mua-ban-nha-dat-cho-thue-{provin}-c3']

		urls = ['https://muaban.net/{}?sort=1&display=simple&cp={}',
		        'https://muaban.net/{}?sort=1&display=simple&cp={}']

		if self.start_page:
			i = self.start_page
			start_i = (self.start_page * 2) - 1
		else:
			i = 1
			start_i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			items = []
			item_url = []
			self.item_url_for_compare.clear()
			for t in type_:
				for ui, u in enumerate(urls, start=start_i):
					url = u.format(t, ui)
					logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
					html = request_get(url, headers=self.headers)
					if not html:
						continue
					soup = BeautifulSoup(html.text, "lxml")
					items += selects(soup, '.list-item__link', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				time.sleep(1)
				continue
			cate = {'can-mua-nha-dat', 'can-ban-nha-dat', 'dich-vu-nha-dat'}
			for index, href in enumerate(items, start=0):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				if not self.check_url(href, cate):
					self.item_url_for_compare.append(href)
					if href in item_url_old:
						continue
					else:
						item_url.append(href)
			else:
				if not item_url:
					self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, 0))
					task2 = self.start_task2(i, item_url, is_running, first_run, site=2)
					if task2 == 'stop':
						break
					elif task2 == 'found_old_item':
						return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
					elif task2 == 'finish':
						return f'Finish. Tổng số tin lấy được: {self.count_tin}'
					i += 1
					start_i += 2
					continue
				set_item_url_old(item_url)
				logger.warning('So luong tin: %d', len(item_url))
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1, site=2)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run, site=2)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				start_i += 2
				continue

			break


class Vnexpress(Base):
	headers = {
		'DNT': '1',
		'Referer': 'https://raovat.vnexpress.net/',
		'Sec-Fetch-Mode': 'no-cors',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	cate_ban = data['type']['vnexpress_ban']
	cate_thue = data['type']['vnexpress_thue']

	def get_detail(self, result, index, url):
		type_ = self.type_
		try:
			content = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1].replace('.html', '')
			title = select(content, 'h1.page-title')
			desc = select(content, 'div.col > div:nth-child(2)')
			phone = None
			try:
				phone = select(content, '#profile-phone', get='phone').replace('.', '')
			except AttributeError:
				pass
			if not phone: phone = search_phone(desc)
			if not phone:
				logger.warning('Khong co so dien thoai: %s', url)
				return
			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price = select(content, 'span.price').split(' - ')[0].split('/')[0].strip()
					if price != 'Thương lượng':
						price = get_price(price, site=4)
						price_str = price[0]
						price = price[1]
					else:
						price_str = 'KXĐ'
						price = 0
				except Exception:
					logging.exception(url)
					price_str = 'KXĐ'
					price = 0
				try:
					area = select(content, '.breadcrumb-item:nth-of-type(2) a:nth-child(2)')
					area = get_area(self.provin, area)
				except Exception as e:
					logger.error(e)
					return False
				try:
					dtich = select(content, '.expand-item>span:contains("Diện tích căn hộ(m²)")+.pull-right')
					if dtich == '---':
						dtich = 'KXĐ'
					else:
						dtich += 'm²'
				except AttributeError:
					dtich = 'KXĐ'
				try:
					cate = select(content, '.breadcrumb-item:nth-of-type(3) a:nth-child(2)')
					if cate == 'Phòng trọ': return
					# if self.type_ == 0:
					#     if self.types[index] == 1:
					#         cate = self.cate_ban[cate]
					#     else:
					#         cate = self.cate_thue[cate]
					if type_ == 0:
						type_ = select(content, '.breadcrumb-item:nth-of-type(3) a:nth-child(1)')
					if type_ == 1 or type_ == 'Mua bán nhà đất':
						cate = self.cate_ban[cate]
					elif type_ == 2 or type_ == 'Thuê nhà đất':
						cate = self.cate_thue[cate]
					ltd = 1

				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, dtich,
					                       phone, ltd, cate, area, price, 4)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()

		provin = 'ha-noi'
		if self.provin == 2: provin = 'tp-ho-chi-minh'

		if self.type_ == 1:
			type_ = ['mua-ban-nha-dat']
		elif self.type_ == 2:
			type_ = ['thue-nha-dat']
		else:
			type_ = ['mua-ban-nha-dat', 'thue-nha-dat']

		urls = 'https://raovat.vnexpress.net/{}/{}?&page={}'

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			items = []
			item_url = []
			self.item_url_for_compare.clear()
			for index, t in enumerate(type_):
				if i == 1:
					url = f'https://raovat.vnexpress.net/{t}/{provin}'
				else:
					url = urls.format(t, provin, i)

				logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))

				html = request_get(url, headers=self.headers)
				if not html: break

				soup = BeautifulSoup(html.text, "lxml")
				item = selects(soup, 'a.product:has(.create-at)', get='href')
				items += item

			# if self.type_ == 0:
			#     if index == 0: self.types += [1 for i in range(len(item))]
			#     else: self.types += [2 for i in range(len(item))]

			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				if not href.startswith(('/' + provin)):
					continue
				new_url = 'https://raovat.vnexpress.net{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				continue

			break


class Rongbay(Base):
	headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
		'cache-control': 'no-cache',
		'dnt': '1',
		'pragma': 'no-cache',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-site': 'none',
		'sec-fetch-user': '?1',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
	}
	cate_ban = data['type']['rongbay_ban']
	cate_thue = data['type']['rongbay_thue']

	def get_detail(self, result, index, url):
		type_ = self.type_
		try:
			soup = BeautifulSoup(result, 'lxml')
			phone = None
			try:
				phone = select(soup, '#mobile_show > span')
			except AttributeError:
				logger.error('Khong co so dien thoai %s - %s', phone, url)
			except Exception as e:
				logging.exception(e)
			if not phone: return

			title = select(soup, '.title.font_28')
			title_url = url.split('/')[-1].rstrip('.html')
			try:
				desc = str(soup.select_one('.info_text')).replace('<br/>', '\n')
				desc = select(BeautifulSoup(desc, 'lxml'), '.info_text')
			except AttributeError:
				return False
			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price = select(soup, '.icon_bds:contains("Giá") > span')
				except AttributeError:
					price = 'KXĐ'
				try:
					dtich = select(soup, '.icon_bds:contains("Diện tích") > span')
				except AttributeError:
					dtich = 'KXĐ'
				try:
					giass = get_price(price, url=url, site=5)

					area = select(soup, 'p.cl_666')
					if '(' in area: area = area.split('(')[0]
					area = area.split(',')[-2].strip()
					if '.' in area: area = area.split('.')[1].strip()
					area = get_area(self.provin, area, name_full=False)
					cate = select(soup, '.nameScate > a')
					if cate == 'Nhà trọ/ Phòng trọ': return
					if type_ == 0:
						type_ = select(soup, '.nameCate > a')
					if type_ in (1, 'Mua bán nhà đất'):
						cate = self.cate_ban[cate]
					elif type_ in (2, 'Cho thuê'):
						cate = self.cate_thue[cate]
					ltd = 1
				except KeyError as e:
					logger.warning(e)
				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price, dtich,
					                       phone, ltd, cate, area, giass, 5)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'Ha-Noi'
		if self.provin == 2: provin = 'TP-HCM'
		if self.type_ == 1:
			type_ = ['Mua-Ban-nha-dat-c15']
		elif self.type_ == 2:
			type_ = ['Thue-va-cho-thue-nha-c272', 'Cho-thue-van-phong-c296']
		else:
			type_ = ['Mua-Ban-nha-dat-c15', 'Thue-va-cho-thue-nha-c272', 'Cho-thue-van-phong-c296']

		urls = 'https://rongbay.com/{}/{}-trang{}.html?ft=1'

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			items = []
			item_url = []
			self.item_url_for_compare.clear()
			for t in type_:
				url = urls.format(provin, t, i)
				logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
				html = request_get(url, headers=self.headers, timeout=30)
				if not html: continue
				soup = BeautifulSoup(html.text, "lxml")
				items += selects(soup, '.subCateBDS a.fa-external-link', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				if provin in href:
					self.item_url_for_compare.append(href)
					if href in item_url_old:
						continue
					else:
						item_url.append(href)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()
				i += 1
				continue

			break


class Dichvubds(Base):
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
	}
	list_cate = data['type']['dichvubds']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			phone = None
			try:
				phone = select(soup, '#colbds > p:contains("Điện thoại:")').split(': ')[-1]
			except AttributeError:
				logger.error('Khong co so dien thoai %s - %s', phone, url)
			except Exception as e:
				logging.exception(e)
			if not phone: return

			title_url = url.split('/')[-1].rstrip('.html')
			desc = select(soup, '#colbds > p')
			title = select(soup, '#colbds > h1')

			phone = self.validate_phone(phone, desc, title, title_url)
			if not phone:
				return
			else:
				try:
					price = select(soup, '.col-sm-4 > span')
				except Exception:
					price = 'KXĐ'
				try:
					dtich = selects(soup, '.col-sm-4 > span')[1]
				except IndexError:
					dtich = 'KXĐ'
				try:
					giass = get_price(price, url=url, site=6)
					area = select(soup, '#colbds > ol > li:nth-of-type(4)')
					area = get_area(self.provin, area)
					cate = select(soup, '#colbds > ol > li:nth-of-type(2)')
					if self.type_ == 1:
						cate = self.list_cate[cate]
					else:
						cate = self.list_cate[cate]
					ltd = 1
				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price, dtich,
					                       phone, ltd, cate, area, giass, 6)
					write_phone_to_file(phone)
		except Exception:
			logger.error('Loi get detail %s', url)

	def crawl(self):
		start = time.time()
		provin = 'ha-noi'
		if self.provin == 2: provin = 'ho-chi-minh'
		if self.type_ == 1:
			type_ = ['nha-dat-ban', 'can-ho-ban']
		elif self.type_ == 2:
			type_ = ['nha-cho-thue', 'can-ho-cho-thue', 'mat-bang-cho-thue', 'sang-nhuong-cua-hang']
		else:
			type_ = ['nha-dat-ban', 'can-ho-ban', 'nha-cho-thue', 'can-ho-cho-thue', 'mat-bang-cho-thue',
			         'sang-nhuong-cua-hang']

		urls = 'https://dichvubds.vn/{}-{}/page/{}'

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			item_url = []
			self.item_url_for_compare.clear()
			items = []
			self.mess_cb.emit(' Trang %d' % i)
			for t in type_:
				url = urls.format(t, provin, i)
				logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
				html = request_get(url, headers=self.headers)
				if not html: continue
				soup = BeautifulSoup(html.text, "lxml")
				items += selects(soup, '.col-xs-9.col-sm-10 >h3 > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				self.item_url_for_compare.append(href)
				if href in item_url_old:
					continue
				else:
					item_url.append(href)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url, site=2)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()
				i += 1
				continue

			break


class Sosanhnha(Base):
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
	}
	list_cate = data['type']['sosanhnha']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			phone = None
			try:
				phone = select(soup, 'div.notices_h p:nth-of-type(2) span').strip('"').replace('.', '')
			except AttributeError:
				logger.error('Khong co so dien thoai %s - %s', phone, url)
			except Exception as e:
				logging.exception(e)
			if not phone: return

			title_url = url.split('/')[-1]
			desc = soup.select_one('div.description')
			try:
				soup.h2.decompose()
				soup.h4.decompose()
				soup.h3.decompose()
				soup.h3.decompose()
				soup.h3.decompose()
				soup.h3.decompose()
				soup.h3.decompose()
			except AttributeError:
				pass
			desc = BeautifulSoup(str(desc).replace('<br/>', '\n'), 'lxml').text.strip()
			title = select(soup, 'h1.title')

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price = select(soup, 'span.price').split(' - ')[0].split(',')[0]
				except Exception:
					price = 'KXĐ'
				try:
					dtich = select(soup, 'span.acreage')
				except Exception:
					dtich = 'KXĐ'
				try:
					giass = get_price(price, acreage=dtich)
					area = select(soup, 'div.open-group-chat > strong').split(' tại ')[1].split(',')[0]
					area = get_area(self.provin, area)
					cate = select(soup, 'div.box_breadcrumb > ol > li:nth-child(1) > a > span').replace(',', '')
					cate = self.list_cate[cate]
					type_ = 1
				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price, dtich,
					                       phone, type_, cate, area, giass, 7)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'hà-nội'
		if self.provin == 2: provin = 'hồ-chí-minh'
		if self.type_ == 1:
			type_ = ['nhà-đất-bán']
		elif self.type_ == 2:
			type_ = ['nhà-đất-cho-thuê']
		else:
			type_ = ['nhà-đất-bán', 'nhà-đất-cho-thuê']

		urls = 'https://sosanhnha.com/{}-tại-' + provin + '{}'

		if self.start_page:
			i = self.start_page
		else:
			i = 1

		next_page = ''
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			items = []
			item_url = []
			self.item_url_for_compare.clear()
			soup = None
			for t in type_:
				if i == 1:
					url = urls.format(t, '')
				else:
					url = urls.format(t, next_page)
				logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
				html = request_get(url, self.headers)
				if not html: break
				soup = BeautifulSoup(html.text, "lxml")
				items += selects(soup, 'a.title', get='href')
			next_page = '/' + select(soup, '.pagination > li:last-child > a', get='href').split('/')[-1]
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				new_url = 'https://sosanhnha.com{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('So luong tin: %d', len(item_url))
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))

				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				continue

			break


class Muabannha(Base):
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
	}
	list_cate = data['type']['muabannhachinhchu']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			desc = re.sub('http[s]?://.*', '', select(soup, '.desc-mota')).replace('(Nguồn:', '').strip()
			phone = None
			try:
				phone = search_phone(desc)
			except AttributeError:
				logger.error('Khong co so dien thoai %s - %s', phone, url)
			except Exception as e:
				logging.exception(e)
			if not phone: return

			title_url = url.split('/')[-2] + '-' + str(randint(1000000, 9999999))
			title = select(soup, '.entry-title')

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price = select(soup, '.col-ht-1:contains("Giá")+td')
				except Exception:
					price = 'KXĐ'
				try:
					acreage = select(soup, '.col-ht-1:contains("Diện tích:")+td')
				except IndexError:
					acreage = 'KXĐ'
				try:
					giass = get_price(price, acreage=acreage)
					area = select(soup, '.col-diachi > a:nth-of-type(2)').replace('TX ', '')
					area = get_area(self.provin, area, name_full=False)
					cate = select(soup, '.col-ht-1:contains("Hình thức:")+td > a')
					cate = self.list_cate[cate]
					type_ = 1
				except Exception as e:
					logger_err.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price, acreage,
					                       phone, type_, cate, area, giass, 8)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = '789'
		if self.provin == 2: provin = '788'
		if self.type_ == 1:
			type_ = ['5']
		elif self.type_ == 2:
			type_ = ['6', '7']
		else:
			type_ = ['5', '6', '7']

		urls = 'http://muabannhachinhchu.vn/page/{}/?s&taxonomy%5Bproject_danhmuc%5D={}&taxonomy%5Bproject_hinhthuc%5D&taxonomy%5Bproject_location%5D={}&taxonomy%5Bproject_location2%5D=0&taxonomy%5Bproject_khoanggia%5D&taxonomy%5Bproject_dientich%5D&submit=T%C3%ACm+ki%E1%BA%BFm'

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			items = []
			item_url = []
			self.item_url_for_compare.clear()
			for t in type_:
				url = urls.format(i, t, provin)
				logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
				html = request_get(url, self.headers)
				if not html: break
				soup = BeautifulSoup(html.text, "lxml")
				items += selects(soup, '.title > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				self.item_url_for_compare.append(href)
				if href in item_url_old:
					continue
				else:
					item_url.append(href)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					gc.collect()
					break
				elif task2 == 'found_old_item':
					gc.collect()
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					gc.collect()
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()
				i += 1
				continue

			break


class Homedy(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	cate_ban = data['type']['homedy_ban']
	cate_thue = data['type']['homedy_thue']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1].replace('?src=list_pc', '')
			title = soup.title.string
			desc = BeautifulSoup(str(soup.select('.readmore')).replace('</p><p>', '\n'), 'lxml').text.lstrip(
				'\n[').rstrip(']\n')
			phone = None
			try:
				phone = select(soup, 'span[data-mobile]', get='data-mobile')
				if phone.startswith('.'): phone = phone.replace('.', '0', 1)
			except Exception:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, '.product-detail > .row:contains("Giá:") > .cell:nth-of-type(2)').replace(
						'\n', ' ')
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup,
					                 '.product-detail > .row:contains("Diện tích:") > .cell:nth-of-type(2)').replace(
						'\n', '')
				except AttributeError:
					acreage = 'KXĐ'
				try:
					price = get_price(price_str, acreage=acreage)
					area = select(soup, '[itemprop=addressLocality]')
					area = get_area(self.provin, area)
					cate = select(soup, 'div.breadcrumb > ul > li:nth-child(3) > a > span')
					if cate == 'Bất động sản khác':
						cate = select(soup, 'div.col-sm-12.related-products > div:nth-child(2) > a').replace('Bán ', '',
						                                                                                     1)
					if self.type_ == 1:
						cate = self.cate_ban[cate]
					else:
						cate = self.cate_thue[cate]

					type_ = 1

				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 9)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'ha-noi'
		if self.provin == 2: provin = 'tp-ho-chi-minh'
		if self.type_ == 1:
			type_ = 'ban-nha-dat'
		else:
			type_ = 'cho-thue-nha-dat'

		urls = f'https://homedy.com/{type_}-{provin}?sort=new&p='

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			item_url = []
			self.item_url_for_compare.clear()
			url = urls + str(i)
			logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
			html = request_get(url, headers=self.headers, timeout=30)
			if not html: continue
			soup = BeautifulSoup(html.text, "lxml")
			items = selects(soup, '.product-item > a:nth-child(3)', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				new_url = 'https://homedy.com/{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				continue

			break


class Nhadattop1(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	list_cate = data['type']['nhadattop1']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1].replace('.htm', '')
			title = soup.title.string
			desc = select(soup, 'div.des')
			phone = None
			try:
				phone = select(soup, 'a.phone').replace('.', '')
			except AttributeError:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, '.pro_price').replace('Giá:', '').strip()
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup, '.pro_acreage').replace('Diện tích:', '').strip()
				except AttributeError:
					acreage = 'KXĐ'
				try:
					cate_area = select(soup, '.item_breadcrumbs:nth-of-type(3) > a > span').split(' tại ')
					area = cate_area[1]
					cate = cate_area[0].replace('Bán ', '')
				except AttributeError:
					cate = select(soup, '.item_breadcrumbs:nth-of-type(2) > a > span').split(' tại ')[0].replace('Bán ',
					                                                                                             '')
					try:
						area = select(soup, 'p.item_detail').split('-')[-2].strip()
					except IndexError:
						area = select(soup, 'p.item_detail').split(',')[-2].strip()
				try:
					price = get_price(price_str, acreage=acreage)
					area = get_area(self.provin, area = get_area(self.provin, area))
					if cate == 'Bất động sản khác': return
					cate = self.list_cate[cate]
					type_ = 1
				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 10)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = '3'
		if self.provin == 2: provin = '4'
		urls = f'https://nhadattop1.com/home/search.php?&city={provin}&price=0&page='

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			item_url = []
			self.item_url_for_compare.clear()
			url = urls + str(i)
			logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
			html = request_get(url, headers=self.headers)
			if not html: continue
			soup = BeautifulSoup(html.content, "lxml")
			items = selects(soup, '.title > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				new_url = 'https://nhadattop1.com{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run, site=10)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				continue

			break


class Dithuenha(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	list_cate = data['type']['dithuenha']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1].replace('.htm', '')
			title = soup.title.string
			desc = select(soup, 'div.des')
			phone = None
			try:
				phone = select(soup, 'a.phone').replace('.', '')
			except AttributeError:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return
			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, '.pro_price').replace('Giá:', '').strip()
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup, '.pro_acreage').replace('Diện tích:', '').strip()
				except AttributeError:
					acreage = 'KXĐ'
				try:
					price = get_price(price_str, acreage=acreage)
					cate = select(soup, 'div.search_form_item.search_form_item_2 > span')
					area = select(soup, 'div.search_form_item.search_form_item_3 > span')
					if area == 'Hà Nội':
						try:
							area = select(soup, 'p.item_detail').split(',')[-2].strip()
						except IndexError:
							area = select(soup, 'p.item_detail').split('-')[-2].strip()
					area = get_area(self.provin, area.replace('Huyện Từ Liêm', 'Quận Bắc Từ Liêm'))
					list_remove = ('Phòng trọ', 'Loại bất động sản khác', 'Ở ghép', 'Kho, nhà xưởng')
					if cate in list_remove: return
					cate = self.list_cate[cate]
					type_ = 1

				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 11)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = '3'
		if self.provin == 2: provin = '4'
		urls = f'https://dithuenha.com/home/search.php?&city={provin}&price=0&page='

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			item_url = []
			self.item_url_for_compare.clear()
			url = urls + str(i)
			logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
			html = request_get(url, headers=self.headers)
			if not html: continue
			soup = BeautifulSoup(html.content, "lxml")
			items = selects(soup, '.title > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				new_url = 'https://dithuenha.com{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				continue

			break


class Tinbatdongsan(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	list_cate = data['type']['tinbatdongsan']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1].replace('.htm', '')
			title = soup.title.string
			desc = select(soup, '#infoDetail')
			phone = None
			try:
				phone = select(soup, '#toPhone').split(' - ')[0]
			except AttributeError:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, 'div.pull-left > span.fsize-17.green-clr.fweight-700')
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup, 'div.pull-right > span.fsize-17.green-clr.fweight-700')
				except AttributeError:
					acreage = 'KXĐ'
				try:
					if price_str == '--':
						price_str = 'KXĐ'
					if acreage == '--':
						acreage = 'KXĐ'
					price = get_price(price_str, acreage=acreage)
					area_cate = select(soup, 'div.folder-title.clearfix > div > div').split(' - ')
					area = area_cate[2]
					cate = area_cate[0]
					cate = self.list_cate[cate]
					try:
						area = get_area(self.provin, area)
					except ValueError:
						area = area_cate[1]
						area = get_area(self.provin, area)

					type_ = 1

				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 12)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'ha-noi'
		if self.provin == 2: provin = 'tp-hcm'
		if self.type_ == 1:
			type_ = 'nha-dat-ban'
		else:
			type_ = 'nha-dat-cho-thue'

		urls = 'https://tinbatdongsan.com/{}-{}/p{}.htm'

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			item_url = []
			self.item_url_for_compare.clear()
			url = urls.format(type_, provin, i)
			logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
			html = request_get(url, headers=self.headers)
			if not html: continue
			soup = BeautifulSoup(html.content, "lxml")
			items = selects(soup, '#hplTitle', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				new_url = 'https://tinbatdongsan.com{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))

				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				continue

			break


class Nhaban(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	cate_ban = data['type']['nhaban_ban']
	cate_thue = data['type']['nhaban_thue']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1]
			title = select(soup, '.fr-title-detail > h1')
			desc = select(soup, '#detail_description')
			phone = None
			try:
				phone = select(soup, '.fone')
			except AttributeError:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return
			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, '.price').replace('Giá: ', '').replace(' VND', '').replace('  ', ' ')
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup, '.struct-one > tr > td')
					if not acreage:
						acreage = select(soup, '.struct-one > tr:nth-of-type(2) > td')
					if not acreage:
						acreage = 'KXĐ'
				except AttributeError:
					acreage = 'KXĐ'
				try:
					price = get_price(price_str, acreage=acreage)
					area = select(soup, '.fr-title-detail+div > a').split(', ')[0].replace('Từ Liêm', 'Nam Từ Liêm')
					cate = select(soup, 'div.breadcrumb > ul > li:nth-child(3) > a > span')
					list_remove = ('Nhà trọ', 'Đất nền nhà phố', 'Đất nền biệt thự')
					if cate in list_remove: return
					area = get_area(self.provin, area, name_full=False)
					if self.type_ == 1:
						cate = self.cate_ban[cate]
					else:
						cate = self.cate_thue[cate]
					type_ = 1

				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 13)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'ha-noi-c194'
		if self.provin == 2: provin = 'ho-chi-minh-c218'
		if self.type_ == 1:
			type_ = 'mua-ban-nha-dat'
		else:
			type_ = 'cho-thue-nha-dat'

		urls = f'http://www.nhaban.vn/{type_}/{provin}'
		para = '?view=1&sortk=start_date&sortb=desc'
		if self.start_page:
			i = self.start_page - 1
			page = self.start_page
		else:
			i = 0
			page = 1

		while is_running:
			self.mess_cb.emit(' Trang %d' % page)
			item_url = []
			self.item_url_for_compare.clear()
			url = ('%s/%d/%s' % (urls, i, para))
			logger.warning('Page %d: %s - %ss' % (page, url, (time.time() - start)))
			html = request_get(url, headers=self.headers)
			if not html: continue
			soup = BeautifulSoup(html.text, "lxml")
			items = selects(soup, '.content > h3 > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				self.item_url_for_compare.append(href)
				if href in item_url_old:
					continue
				else:
					item_url.append(href)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(page, self.row_was_insert))
				task2 = self.start_task2(page, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 21
				page += 1
				continue

			break


class Dothi(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
		'Cookie': ''
	}
	headers_mobile = {
		'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
		'Cookie': ''
	}
	list_cate = data['type']['dothi']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1].replace('.htm', '')
			title = soup.title.text.strip()
			desc = BeautifulSoup(str(soup.select_one('.pd-desc-content')).replace('<br/>', '\n'), 'lxml').text.strip()
			phone = None
			try:
				phone = select(soup, '#tbl2 > tr:contains("Di động") > td:nth-of-type(2)')
			except AttributeError:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, '.spanprice')
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup, '.spanprice+span')
				except AttributeError:
					acreage = 'KXĐ'
				try:
					price = get_price(price_str, acreage=acreage)
					area = select(soup, '.pd-location').split(' - ')[-2]
					cate = select(soup, '#tbl1 > tbody > tr:contains("Loại tin rao") > td:nth-of-type(2)').split(' (')[
						0]
					cate = self.list_cate[cate]
					area = get_area(self.provin, area)
					type_ = 1
				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 14)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'ha-noi'
		if self.provin == 2: provin = 'tp-hcm'
		if self.type_ == 1:
			type_ = 'nha-dat-ban'
			self.headers_mobile['Cookie'] = 'psortfilter=1$/nha-dat-ban.htm'
		else:
			type_ = 'nha-dat-cho-thue'
			self.headers_mobile['Cookie'] = 'psortfilter=1$/nha-dat-cho-thue.htm'

		urls = 'https://m.dothi.net/{}-{}/p{}.htm'

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			item_url = []
			self.item_url_for_compare.clear()
			url = urls.format(type_, provin, i)
			logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
			html = request_get(url, headers=self.headers_mobile)
			if not html: continue
			if i == 1:
				with open(f'html_page{i}.html', 'w', encoding='utf8') as f:
					f.write(html.text)
			soup = BeautifulSoup(html.content, "lxml")
			items = selects(soup, '.title-14 > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				new_url = 'https://dothi.net{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run, site=14)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				continue

			break


class Nhadatcanban(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	cate_ban = data['type']['nhadatcanban_ban']
	cate_thue = data['type']['nhadatcanban_thue']

	def get_cate_from_desc(self, desc_cate):
		if self.type_ == 1:
			list_cate = data['type']['nhadatcanban_ban'].keys()
		else:
			list_cate = data['type']['nhadatcanban_thue'].keys()
		for key in list_cate:
			if key.lower() in desc_cate.lower():
				if self.type_ == 1:
					return self.cate_ban[key]
				else:
					return self.cate_thue[key]

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result.decode('utf-8', 'ignore'), 'lxml')
			title_url = url.split('/')[-1].replace('.html', '')
			title = soup.title.string
			desc = BeautifulSoup(str(soup.select_one('.detail')).replace('<br/>', '\n'), 'lxml').text.strip()
			phone = None
			try:
				phone = select(soup, 'article > ul > li:contains("Điện thoại") > strong')
			except AttributeError:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, '.info > span')
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup, '.info > span:nth-of-type(2)')
				except AttributeError:
					acreage = 'KXĐ'
				try:
					price = get_price(price_str, acreage=acreage)
					area = select(soup, '#cbxDistricts')
					cate = select(soup, '#cbxTypes').replace(' cần bán', '').replace(' cho thuê', '')
					if cate == 'Nhà trọ cho thuê': return
					if self.type_ == 1:
						cate = self.cate_ban[cate]
					else:
						cate = self.cate_thue[cate]
					try:
						area = get_area(self.provin, area)
					except ValueError:
						area = 0
						if self.type_ == 1:
							cate = 10
						else:
							cate = 21
					type_ = 1
				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 15)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'ha-noi'
		if self.provin == 2: provin = 'ho-chi-minh'
		if self.type_ == 1:
			type_ = 'nha-dat-can-ban'
		else:
			type_ = 'nha-dat-cho-thue'

		urls = f'https://nhadatcanban.com.vn/{type_}-tai-{provin}'

		if self.start_page:
			i = self.start_page
		else:
			i = 1
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			item_url = []
			self.item_url_for_compare.clear()
			if i < 2:
				url = urls
			else:
				url = ('%s/page-%d' % (urls, i))
			logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
			html = request_get(url, headers=self.headers)
			if not html: continue
			soup = BeautifulSoup(html.text, "lxml")
			items = selects(soup, '.list > article h4 > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				new_url = 'https://nhadatcanban.com.vn/{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run, site=15)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				continue

			break


class Alonhadat(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	cate_ban = data['type']['alonhadat_ban']
	cate_thue = data['type']['alonhadat_thue']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1].replace('.html', '')
			aid = title_url.split('-')[-1]
			title = select(soup, '.title h1')
			desc = select(soup, 'div.detail')
			phone = None
			try:
				phone = request_get(
					f'https://alonhadat.com.vn/handler/Handler.ashx?command=35&propertyid={aid}&captcha=')
				phone = '/'.join(re.findall("tel:([0-9]{10,11})'", phone.text))
			except Exception:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, '.price > span.value')
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup, '.square > span.value')
				except AttributeError:
					acreage = 'KXĐ'
				try:
					price = get_price(price_str, acreage=acreage)
					area = select(soup, '.address > span.value').split(', ')[-2]
					cate = select(soup, 'table > tr:nth-child(3) > td:nth-child(2)')
					area = get_area(self.provin, area)
					if cate == 'Phòng trọ, nhà trọ': return
					if self.type_ == 1:
						cate = self.cate_ban[cate]
					else:
						cate = self.cate_thue[cate]

					type_ = 1

				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 16)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'ha-noi'
		if self.provin == 2: provin = '' # TODO
		if self.type_ == 1:
			type_ = 'can-ban'
		else:
			type_ = 'cho-thue'

		urls = f'https://alonhadat.com.vn/nha-dat/{type_}/nha-dat/1/{provin}'

		if self.start_page:
			i = self.start_page
		else:
			i = 1

		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			item_url = []
			self.item_url_for_compare.clear()
			if i < 2:
				url = urls + '.html'
			else:
				url = ('%s/trang--%d.html' % (urls, i))
			logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))

			html = request_get(url, headers=self.headers)
			if not html: continue
			soup = BeautifulSoup(html.text, "lxml")
			items = selects(soup, '.ct_title > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				new_url = 'https://alonhadat.com.vn{}'.format(href)
				self.item_url_for_compare.append(new_url)
				if new_url in item_url_old:
					continue
				else:
					item_url.append(new_url)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()
				i += 1
				continue

			break


class Bdstuanqua(Base):
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
	}
	list_cate = data['type']['bdstuanqua']
	details = {}
	number = 20

	def get_detail(self, _id, index):
		try:
			r = request_get(f'https://api.bdstuanqua.com/web/article/detail?id={_id}', self.headers)
			ad = r.json()
			title = ad['title']
			title_url = sl(title) + '-' + str(_id)
			desc = BeautifulSoup(ad['content'], 'lxml').text.strip()
			price_str = 'KXĐ'
			price = 0
			size = 'KXĐ'
			phone = search_phone(desc)
			if not phone: return

			phone = self.validate_phone(phone, desc, title, title_url)
			if not phone:
				return
			else:
				try:
					distr = ad['district']['name']
				except TypeError:
					distr = 1
				else:
					distr = distrId[data['distr']['name_full'].index(distr)]
				try:
					cate = ad['category']['name']
					cate = self.list_cate[cate]
					type_ = 1

				except Exception as e:
					logger.error(e, exc_info=True)
				else:
					self.details[index] = (
					title, title_url, desc, price_str, size, phone, type_, cate, distr, price, 17)
					write_phone_to_file(phone)
					return title_url
		except Exception:
			logger.error('Loi get detail', exc_info=True)

	def crawl(self):
		if self.type_ == 1:
			type_ = ['mua-ban-can-ho-chung-cu', 'mua-ban-nha-rieng-dat-tho-cu', 'mua-ban-biet-thu-nha-lien-ke',
			         'mua-ban-trang-trai-condotel']
		else:
			type_ = ['thue-va-cho-thue-can-ho-chung-cu', 'thue-va-cho-thue-nha-rieng', 'thue-van-phong',
			         'thue-cua-hang-ki-ot', 'thue-kho-nha-xuong-dat']

		urls = 'https://api.bdstuanqua.com/web/articles?category={}&local={}&perPage={}&page={}'

		if self.start_page:
			i = self.start_page
		else:
			i = 1

		count_tin = 0
		list_item = []
		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			for t in type_:
				url = urls.format(t, self.provin, self.number, i)
				logger.info('Page %d: %s' % (i, url))
				rs = request_get(url, self.headers)
				if rs:
					for articles in rs.json()['articles']:
						list_item.append(articles['_id'])

			if not list_item: continue

			for index, _id in enumerate(list_item):
				self.progress_cb.emit((index + 1) * 100 / len(list_item))
				self.get_detail(_id, index)
			else:
				# Insert to db
				logger.warning('Continue')
				logger.info('Insert to db')
				detail = []
				try:
					sorted_detail = dict(sorted(self.details.items()))
					detail = list(sorted_detail.values())
				except Exception:
					logger.error('Loi sort detail', exc_info=True)
				if not detail:
					continue
				row = self.inserts_to_db(detail)
				if not row:
					continue
				row_was_insert = row[0]
				row_duplicate = row[1]
				count_tin += row_was_insert
				self.mess_cb.emit(f'Trang {i}: Lấy được {row_was_insert} tin')
				detail.clear()

				task2 = self.start_task2(i, list_item, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()

				i += 1
				continue

			break


class Nhadathay(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	list_cate = data['type']['nhadathay']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-1]
			title = soup.title.string
			desc = BeautifulSoup(str(soup.select_one('.pm-desc')).replace('<br/>', '\n'), 'lxml').text.strip()
			phone = None
			try:
				phone = select(soup, '.table-detail > .row:contains("Số điện thoại") > .tb_des')
			except AttributeError:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone:
				return
			else:
				try:
					price_str = select(soup, '.price > span') + 'đ'
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup, '.acreage > span')
				except AttributeError:
					acreage = 'KXĐ'
				try:
					price = get_price(price_str, acreage=acreage)
					area = select(soup, '.product-location').split(' -\n')[-2]
					cate = select(soup, '.table-detail > .row:contains("Danh mục") > .tb_des').split(' tại ')[0]
					area = get_area(self.provin, area)
					if cate == 'Cho thuê nhà trọ, phòng trọ': return
					cate = self.list_cate[cate]

					type_ = 1

				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 18)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'ha-noi'
		if self.provin == 2: provin = 'ho-chi-minh'
		if self.type_ == 1:
			type_ = 'nha-dat-ban'
		else:
			type_ = 'nha-dat-cho-thue'

		urls = f'https://nhadathay.com/{type_}-{provin}?page='

		if self.start_page:
			i = self.start_page
		else:
			i = 1

		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			item_url = []
			self.item_url_for_compare.clear()
			url = ('%s%d' % (urls, i))
			logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
			html = request_get(url)
			if not html: continue
			soup = BeautifulSoup(html.text, "lxml")
			items = selects(soup, 'div.item-name > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				self.item_url_for_compare.append(href)
				if href in item_url_old:
					continue
				else:
					item_url.append(href)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				set_item_url_old(item_url)
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()
				i += 1
				continue

			break


class Muabanchinhchu(Base):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
	}
	list_cate = data['type']['muabanchinhchu']

	def get_cate_from_title(self, title):
		list_cate = self.list_cate.keys()
		for key in list_cate:
			if key.lower() in title.lower():
				return self.list_cate[key]

	@staticmethod
	def get_phone(post_id):
		data = {"action": "show_phone", "post_id": post_id}
		return requests.post('https://muabanchinhchu.net/wp-admin/admin-ajax.php', data=data).json()['phone']

	def get_detail(self, result, index, url):
		try:
			soup = BeautifulSoup(result, 'lxml')
			title_url = url.split('/')[-2]
			title = soup.title.string
			desc = select(soup, '.realty-infor > p')
			post_id = select(soup, '#main > article', get='id').split('-')[1]
			phone = None
			try:
				phone = self.get_phone(post_id)
			except AttributeError:
				logger.warning('Khong co so dien thoai: %s', url)
			if not phone: return

			phone = self.validate_phone(phone, title, desc, title_url)
			if not phone: return
			else:
				try:
					price_str = select(soup, '.price-area > .value:nth-of-type(1)')
				except Exception:
					price_str = 'KXĐ'
				try:
					acreage = select(soup, '.price-area > .value:nth-of-type(2)')
				except AttributeError:
					acreage = 'KXĐ'
				try:
					price = get_price(price_str, acreage=acreage)
					area = select(soup, '.location-realty > a:nth-of-type(3)')
					area = get_area(self.provin, area)
					cate = self.get_cate_from_title(title)
					if not cate: return

					type_ = 1

				except Exception as e:
					logger.error('Loi lay du lieu: %s - %s', e, url, exc_info=True)
				else:
					self.details[index] = (title, title_url, desc, price_str, acreage,
					                       phone, type_, cate, area, price, 19)
					write_phone_to_file(phone)
		except Exception:
			logger_err.error('Loi get detail: %s', url, exc_info=True)

	def crawl(self):
		start = time.time()
		provin = 'ha-noi'
		if self.provin == 2: provin = 'tp-ho-chi-minh'

		urls = f'https://muabanchinhchu.net/tinh-thanh/{provin}/'

		if self.start_page:
			i = self.start_page
		else:
			i = 1

		while is_running:
			self.mess_cb.emit(' Trang %d' % i)
			item_url = []
			self.item_url_for_compare.clear()
			if i == 1:
				url = urls
			else:
				url = ('%spage/%d/' % (urls, i))
			logger.warning('Page %d: %s - %ss' % (i, url, (time.time() - start)))
			html = request_get(url)
			if not html: continue
			soup = BeautifulSoup(html.text, "lxml")
			items = selects(soup, '.info-realty > h4 > a', get='href')
			if not items:
				logger.warning('Khong tim thay tin')
				continue
			for index, href in enumerate(items):
				self.progress_cb.emit((index + 1) * 15 / len(items))
				item_url.append(href)
			else:
				if not item_url:
					return 'Chưa có tin mới'
				logger.warning('Continue')
				logger.warning('Khoi tao thread get detail. Vui long doi...')
				task1 = self.start_task(i, item_url, 1)
				if task1 == 'not_detail':
					self.row_was_insert = 0
				self.mess_cb.emit('Trang {}: Lấy được {} tin'.format(i, self.row_was_insert))
				task2 = self.start_task2(i, item_url, is_running, first_run)
				if task2 == 'stop':
					break
				elif task2 == 'found_old_item':
					return f'Gặp {self.compare_item} tin cũ, dừng. Tổng số tin lấy được: {self.count_tin}'
				elif task2 == 'finish':
					return f'Finish. Tổng số tin lấy được: {self.count_tin}'
				gc.collect()
				i += 1
				continue

			break


if __name__ == "__main__":
	pass
