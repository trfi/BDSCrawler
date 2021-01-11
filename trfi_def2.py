# -*- coding: utf-8 -*-
# import atexit
import concurrent.futures
import gc
import logging
import re
import sys
import time
import threading
from datetime import datetime, timedelta
import traceback
from logging import config
from threading import Thread
import MySQLdb
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import simplejson as json
from slugify import slugify as sl
from logging_config import LOGGING_CONFIG
from simplejson import loads, dumps
from text_unidecode import unidecode

###################

gc.enable()


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger_err.error("Loi khong xac dinh:", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


class ExcThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

    def run(self):
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception:
            logger_err.error(traceback.format_exc())


###################


counter_file = 'counter.json'


def read_counter():
    return loads(open("counter.json", "r").read())


counter = read_counter()
old_item_file = f'old_item{counter}.json'


def increase_counter():
    with open(counter_file, "w") as f:
        f.write(dumps(counter + 1))


def reduce_counter():
    rd_c = read_counter() - 1
    with open(counter_file, "w") as f:
        f.write(dumps(rd_c))


increase_counter()
# atexit.register(reduce_counter)

####################

rq = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adt_10 = HTTPAdapter(pool_connections=10, pool_maxsize=10, pool_block=True, max_retries=retry)
adt_20 = HTTPAdapter(pool_connections=20, pool_maxsize=20, pool_block=True, max_retries=retry)
adt_30 = HTTPAdapter(pool_connections=30, pool_maxsize=30, pool_block=True, max_retries=retry)
rq.mount('https://', adt_20)
rq.mount('http://', adt_20)
rq.mount('https://m.batdongsan.com.vn', adt_30)
rq.mount('https://muaban.net', adt_30)
rq.mount('https://alonhadat.com.vn', adt_10)
rq.mount('https://dithuenha.com', adt_10)
rq.mount('http://www.nhaban.vn', adt_10)


######################


def read_json_file(file):
    with open(file, "r", encoding="utf8") as read_file:
        return json.load(read_file)


def write_json_file(file, data):
    with open(file, 'w', encoding="utf8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def garbage_collect(text):
    def wrapped(func):
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            c = gc.collect()
            print(text, c)
            return result

        return inner

    return wrapped


######################


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger()


def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


logger_err = setup_logger('error_logger', 'error_log.log', level=logging.ERROR)


def prepare_data():
    with open(f'keywords.txt', 'r', encoding='utf-8') as f:
        global keywords
        keywords = set(l.rstrip('\n').lower() for l in f)

    # with open(f'phone.txt', 'w') as f:
    #     f.write('')


ExcThread(target=prepare_data).start()

num_recent_phone = read_json_file('config.json')['setting']['check_phone']
num_recent_phone_hcm = read_json_file('config.json')['setting']['check_phone_hcm']

moigioi, recent_phone = set(), set()

province = 1


def set_moigioi():
    global moigioi
    while True:
        db = ConnectDb(dict=False)
        moigioi.update(db.get_moigioi(province))
        if moigioi:
            db.conn.close()
            break
        else:
            logger_err.error('Khong lay duoc list moi gioi')
            db.conn.close()
            time.sleep(2)


def update_moigioi(time_moigioi):
    global moigioi
    time_moigioi = str(datetime.strptime(time_moigioi, '%Y-%m-%d %H:%M:%S') - timedelta(days=1))
    while True:
        db = ConnectDb(dict=False)
        moigioi_new = db.get_moigioi_by_time(time_moigioi, province)
        if moigioi_new is None:
            logger_err.error('Khong lay duoc list moi gioi va sdt gan day')
            db.conn.close()
            time.sleep(2)
            continue
        elif moigioi_new:
            moigioi.update(moigioi_new)
            logger_err.error(f'Length moigioi: {len(moigioi)}')
            db.conn.close()
            break
        else:
            break


def set_recent_phone():
    global recent_phone
    while True:
        db = ConnectDb(dict=False)
        recent_phone = db.get_recent_phone()
        if recent_phone:
            break
        else:
            logger_err.error('Khong lay duoc list sdt gan day')
            time.sleep(2)


time_moigioi = str()
moigioi_status = True


def get_data_to_check():
    global time_moigioi, moigioi_status
    if moigioi_status:
        set_moigioi()
        time_moigioi = current_time()
        moigioi_status = False
    else:
        update_moigioi(time_moigioi)
        time_moigioi = current_time()
    set_recent_phone()


phone_on_page = []


class Base:
    headers = {}
    details = {}
    count_moigioi = 0
    count_tin = 0
    row_was_insert = 0
    row_duplicate = 0
    threads = []
    item_url_for_compare = []
    compare_item = 0

    def __init__(self, provin, type_, progress, mess, **kwargs):
        self.provin = provin
        self.type_ = type_
        self._tpage = kwargs.get('page')
        self.start_page = kwargs.get('start_page')
        self.end_page = kwargs.get('end_page')
        self.progress_cb = progress
        self.mess_cb = mess
        global province
        province = provin

    def fetch(self, el):
        index, url = el
        # logger.info('%s - %ss' % (url, (time.time() - start)))
        html = request_get(url)
        if not html: return
        if html.status_code == 200:
            x = Thread(target=self.get_detail, args=(html.content, index, url))
            self.threads.append(x)
            x.start()
            html = None
        else:
            logger_err.error('Status code: %s - %s', html.status_code, url)

    def thread_with_message(self, target, message, *args, **kwargs):
        def target_with_msg(*args, **kwargs):
            try:
                row = target(*args, **kwargs)
                self.row_was_insert = row[0]
                self.count_tin += row[0]
                self.row_duplicate = row[1]
            except TypeError as e:
                logger.warning(e)
            logger.info(message)
            logger.info('Tong so tin lay duoc: %d', self.count_tin)

        thread = Thread(target=target_with_msg, args=args, kwargs=kwargs)
        thread.start()
        return thread

    def start_task(self, i, item_urls, end, site=None):
        if site == 2:
            workers = 90
        else:
            workers = 50
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            executor.map(self.fetch, enumerate(item_urls))
        for index, t in enumerate(self.threads):
            t.join()
            self.progress_cb.emit(((index + 1) * 85 / len(self.threads)) + 15)
        logger.info('Page %d: %d/%d tin moi gioi', i, self.count_moigioi, len(item_urls))
        self.count_moigioi = 0

        # Neu phone on page > 500 thi xoa bot so cu di de lai 400
        global phone_on_page
        dif_len = len(phone_on_page) - 400
        if dif_len > 100:
            del phone_on_page[0:dif_len]
            phone_on_page = list(set(phone_on_page))

        # Insert to db
        logger.info('Insert to db')
        try:
            if len(self.details.items()) > 0:
                sorted_detail = dict(sorted(self.details.items()))
                detail = list(sorted_detail.values())
                x = self.thread_with_message(self.inserts_to_db, 'Insert finished', detail)
                x.join()
            else:
                logger_err.error('return not detail')
                return 'not_detail'
        except Exception:
            logger_err.error('Loi insert to db ngoai', exc_info=True)
            return 'not_detail'
        # if end:
        #     x.join()

    @garbage_collect('task 2')
    def start_task2(self, i, item_url, is_running, first_run, site=None):
        if not is_running:
            self.mess_cb.emit(f'Stopped. Tổng số tin lấy được: {self.count_tin}')
            return 'stop'
        if self._tpage == 'custom' and i == self.end_page:
            logger.warning('End page: %s', self.end_page)
            return 'finish'
        elif self._tpage == 'auto':
            if first_run:
                write_old_item(i, self.item_url_for_compare, self.type_)
                if i == self.end_page:
                    logger.warning('End page first run: %s', self.end_page)
                    return 'finish'
            else:
                if site == 2 and i == 35:
                    return 'finish'
                elif site != 2 and i == 25:
                    return 'finish'
                old_item = read_json_file(old_item_file)
                write_old_item(i, self.item_url_for_compare, self.type_)
                self.compare_item = len(set(old_item) & set(self.item_url_for_compare))
                if self.compare_item > 0:
                    logger.warning(
                        f'Gap {self.compare_item} tin cu tren trang, dung. Tong so tin lay duoc: {self.count_tin}')
                    return f'found_old_item'

    def validate_phone(self, phones, title, desc, title_url):
        is_invalid = False
        try:
            phones = list(dict.fromkeys(re.split('[^[0-9]+', phones.replace(' ', ''))))
            for i, phone in enumerate(phones):
                if phone.startswith('84'):
                    phone = phone.replace('84', '0', 1)
                    phones[i] = phone
                if not phone.startswith('0'):
                    phone = '0' + phone
                    phones[i] = phone
                if phone in phone_on_page:
                    logger.info('Trung so dien thoai tren cung trang %s - %s', phone, title_url)
                    is_invalid = True
                    continue
                else:
                    phone_on_page.append(phone)
                    if is_invalid: return None
                if self.check_key(title, desc, title_url):
                    is_invalid = True
        except Exception as e:
            logger_err.error('Loi valid phone: %s', e, exc_info=True)
            return None
        else:
            if not phones or is_invalid:
                return None
            else:
                return '\n'.join(phones)

    def is_phone_invalid(self, phones):
        is_invalid = False
        try:
            phones = phones.split('\n')
            for i, phone in enumerate(phones):
                if num_recent_phone > 0 and phone in recent_phone:
                    logger.info('Trung so dien thoai gan day - %s', phone)
                    is_invalid = True
                    if len(phones) == 1: return is_invalid
                    continue
                elif phone in moigioi:
                    logger.info('Moi gioi check phone: %s', phone)
                    self.count_moigioi += 1
                    is_invalid = True
        except Exception as e:
            logger_err.error('Loi valid phone: %s', e, exc_info=True)
            return False
        else:
            return is_invalid

    def inserts_to_db(self, val):
        get_data_to_check()
        logger.warning('Check moi gioi va loai bo truoc khi insert')
        try:
            for i in range(len(val) - 1, -1, -1):
                if self.is_phone_invalid(val[i][5]):
                    #logger.warning('MOI GIOI - %s', val[i][5])
                    val.pop(i)
        except Exception as e:
            logger_err.error('Loi check moi gioi lan 2: %s', e, exc_info=True)

        if len(val) < 1:
            return [0, 0]

        table_tin = 'tinchinhchu'
        if self.provin == 2: table_tin = 'tinchinhchu_hcm'

        sql = f"INSERT INTO {table_tin} (TieuDe, TieuDeKhongDau, NoiDung, Gia, DienTich," \
              "Phone, LoaiTinDang, idLoaiTin, idQuanHuyen, GiaSS, id_site)" \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id"
        i = 1
        while True:
            try:
                db = ConnectDb()
                db.cursor.execute("SET time_zone = '+07:00';")
                db.cursor.execute("SET INNODB_LOCK_WAIT_TIMEOUT=120;")
                db.cursor.executemany(sql, val)
                db.conn.commit()
            except MySQLdb._exceptions.IntegrityError as e:
                logger.warning('Tin da co: %s', e)
            except Exception as e:
                if i > 5:
                    return [0, 0]
                    break
                logger_err.error('Khong insert duoc %s', e, exc_info=True)
                logger_err.error(str(val))
                i += 1
                time.sleep(3)
            else:
                logger.info("%s row was inserted to Database", db.cursor.rowcount)
                row_duplicate = len(val) - db.cursor.rowcount
                return [db.cursor.rowcount, row_duplicate]
                break

    def check_key(self, title, desc, title_url):
        string = title + ' ' + desc
        for key in keywords:
            k = unidecode(key.lower())
            s = unidecode(string.lower())
            if k in s:
                logger.info('Moi gioi check key: %s - %s', key, title_url)
                self.count_moigioi += 1
                return True
        return False

    def check_url(self, href, cate):
        for i in cate:
            if i in href:
                return True
        return False


class ConnectDb:
    def __init__(self, dict=True):
        f = read_json_file('config.json')
        host = f['database']['host']
        port = f['database']['port']
        user = f['database']['user']
        passwd = f['database']['passwd']
        dbname = f['database']['dbname']

        while True:
            try:
                self.conn = MySQLdb.connect(host=host, port=port, user=user,
                                            passwd=passwd, db=dbname, charset="utf8mb4")
                if dict:
                    self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
                else:
                    self.cursor = self.conn.cursor()
            except (MySQLdb.Error, MySQLdb.Warning) as e:
                logger_err.error('Db error. Loi ket noi database %s', e, exc_info=True)
                time.sleep(5)
                logger_err.error('---- Thu lai ----')
            except Exception as e:
                logger_err.error('Unknown error. Loi ket noi Database: %s', e, exc_info=True)
            else:
                break

    def fetchall(self, sql):
        try:
            self.cursor.execute(sql)
            rs = self.cursor.fetchall()
            return rs
        except Exception as e:
            logger_err.error("Fetch all error: khong lay duoc du lieu. %s", e)

    def fetchone(self, sql, *args):
        try:
            self.cursor.execute(sql)
            rs = self.cursor.fetchone()
            return rs
        except Exception as e:
            logging.debug('Khong insert duoc %s - %s', e, args[0])
            self.conn.rollback()

    def get_last_title_url(self, site):
        sql = f"SELECT TieuDeKhongDau FROM tinchinhchu WHERE id_site='{site}' ORDER BY id DESC LIMIT 1"
        self.cursor.execute(sql)
        rs = self.cursor.fetchall()
        return [row['TieuDeKhongDau'] for row in rs]

    def get_moigioi(self, province=1):
        table = 'moigioibds'
        if province == 2: table = 'moigioibds_hcm'
        sql = f"SELECT Phone FROM {table}"
        try:
            self.cursor.execute(sql)
            rs = self.cursor.fetchall()
            if not rs:
                logger_err.error('Khong lay duoc list moi gioi tu server')
                return None
                # raise Exception("Khong lay duoc list moi gioi tu server")
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            logger_err.error('Db error. Loi get moi gioi %s', e, exc_info=True)
            return None
        except Exception as e:
            logger_err.error('Unknown error. Loi get moi gioi %s', e, exc_info=True)
            return None
        else:
            return {row[0] for row in rs}

    def get_moigioi_by_time(self, time_moigioi, province=1):
        table = 'moigioibds'
        if province == 2: table = 'moigioibds_hcm'
        sql = f"SELECT Phone FROM {table} WHERE `updated_at` >= '{time_moigioi}'"
        try:
            self.cursor.execute(sql)
            rs = self.cursor.fetchall()
            if not rs:
                logger.info('Khong co moi gioi moi')
                return set()
                # raise Exception("Khong lay duoc list moi gioi tu server")
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            logger_err.error('Db error. Loi get moi gioi %s', e, exc_info=True)
            return None
        except Exception as e:
            logger_err.error('Unknown error. Loi get moi gioi %s', e, exc_info=True)
            return None
        else:
            return {row[0] for row in rs}

    def get_recent_phone(self):
        if province == 1:
            table_tin = 'tinchinhchu'
            num_recent = num_recent_phone
        else:
            table_tin = 'tinchinhchu_hcm'
            num_recent = num_recent_phone_hcm

        sql = f"SELECT Phone FROM {table_tin} ORDER BY updated_at DESC LIMIT {num_recent}"
        try:
            self.cursor.execute(sql)
            rs = self.cursor.fetchall()
            if not rs:
                logger_err.error('Khong lay duoc phone gan day-')
                return None
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            logger_err.error('Db error. Loi get phone gan day %s', e, exc_info=True)
            return None
        except Exception as e:
            logger_err.error('Unknown error. Loi get recent phone: %s', e, exc_info=True)
            return None
        else:
            return {row[0] for row in rs}

    def check_user(self, username, passwd):
        sql = "SELECT username, password FROM user_toolsbds"
        self.cursor.execute(sql)
        rs = self.cursor.fetchall()
        for r in rs:
            if username == r['username'] and passwd == r['password']:
                return True
        return False


# def sql_insert(title, title_url, desc, price, dtich, phone, ltin, quan, giass, site):
#     return f'INSERT INTO tinnhadat (TieuDe, TieuDeKhongDau, NoiDung, Gia, DienTich, Phone, idLoaiTin, idQuanHuyen, giass, id_site)' \
#         f'VALUES ("{title}","{title_url}","{desc}","{price}","{dtich}","{phone}","{ltin}","{quan}","{giass}",{site})'


def check_recent_phone(phone, recent_phone):
    for row in recent_phone:
        if phone == row['Phone']:
            return True
    return False


def write_old_item(i, item_url, type_, site=None):
    if i == 1:
        write_json_file(old_item_file, item_url)
    # if i in (2, 3) and type_ == 1:
    #     data = read_json_file(old_item_file) + item_url
    #     write_json_file(old_item_file, data)


def request_get(url, headers=None, timeout=30):
    if not headers:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
    for i in range(3):
        try:
            response = rq.get(url, headers=headers, timeout=timeout)
            if response.status_code != 200:
                logger_err.error(f'Lỗi request đến server: {response.status_code} - {url}')
                time.sleep(3)
        except requests.exceptions.ConnectTimeout:
            logger_err.error('Request timeout!')
            time.sleep(3)
        except Exception:
            logger_err.error('Request error')
            time.sleep(3)
        else:
            return response
    return None


def select(soup, selector, **kwargs):
    if kwargs.get('get'):
        return str(BeautifulSoup.select_one(soup, selector).get(kwargs.get('get')))
    else:
        return str(BeautifulSoup.select_one(soup, selector).text.strip())


def selects(soup, selector, **kwargs):
    if kwargs.get('get'):
        return [i.get(kwargs.get('get')) for i in BeautifulSoup.select(soup, selector)]
    else:
        return [i.text.strip() for i in BeautifulSoup.select(soup, selector)]


def checkUser(self, QtWidgets):
    db = ConnectDb()
    if db.check_user(self.txtUser.text(), self.txtPass.text()):
        self.accept()
        return True
    else:
        QtWidgets.QMessageBox.warning(
            self, 'Error', 'Sai tên đăng nhập hoặc mật khẩu')


def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


if __name__ == "__main__":
    pass
    import time

    db = ConnectDb(dict=False)
    start = time.time()
    """Xoa trung"""
    # db.cursor.execute("SET INNODB_LOCK_WAIT_TIMEOUT=2000;")
    # sql = 'DELETE FROM tinchinhchu WHERE id NOT IN (SELECT * FROM (SELECT MAX(n.id) FROM tinchinhchu n GROUP BY n.Phone) x)'
    # db.cursor.execute(sql)
    # db.conn.commit()

    # sql = 'SELECT Phone, COUNT(Phone) FROM tinchinhchu GROUP BY Phone HAVING COUNT(Phone) > 1'
    #sql = "SELECT Phone FROM `tinchinhchu_hcm` ORDER BY `id` DESC limit 2000"
    s = 'Cần Bán Gấp Căn Hộ Quận Hoàng Mai DT 76m2 3 Phòng Ngủ A'
    sql = f"DELETE FROM `tinfacebook` WHERE `TieuDe` LIKE '%{s}%'"
    #sql = f"UPDATE `tinfacebook` SET idLoaiTin = 4 WHERE `TieuDe` LIKE '%{s}%'"
    # sql = "SELECT TieuDeKhongDau, GiaSS, id_site, created_at FROM tinchinhchu WHERE GiaSS LIKE 'KXĐ%'"
    #sql = "SELECT * FROM `tinchinhchu` WHERE `id_site` = 3 ORDER BY `id` DESC LIMIT 10"
    # sql = "DESCRIBE `moigioibds`"
    
    db.cursor.execute(sql)
    rs = db.cursor.fetchall()
    print(rs)
    print(time.time() - start)
