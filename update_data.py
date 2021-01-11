from trfi_def import ConnectDb
import simplejson as json


def get_data(type, site):
    global sql
    if site == 1:
        if type == 'quanhuyen':
            sql = "SELECT * FROM quanhuyen"
        if type == 'loaitin':
            sql = "SELECT idLoaiTin, Ten, TenKhongDau FROM loaitin WHERE Site LIKE '%{}%'".format(site)
    elif site == 3:
        if type == 'ltinban':
            sql = f"SELECT idLoaiTin, idChotot FROM loaitin WHERE Site LIKE '%{site}%' AND idLoaiTin LIKE '1%'"
        elif type == 'ltinthue':
            sql = f"SELECT idLoaiTin, idChotot FROM loaitin WHERE Site LIKE '%{site}%' AND idLoaiTin LIKE '2%'"

    db = ConnectDb()
    return db.fetchall(sql)


def update_data(data_ltin, data_distr, data_ltin_ban_chotot, data_ltin_thue_chotot):
    data = {
        'distr': {},
        'ttype': {},
        'muaban': {
            'name': [
                'Biệt thự, villa, Penthouse',
                'Căn hộ chung cư, tập thể',
                'Nhà hẻm/ngõ',
                'Nhà mặt tiền/phố',
                'Đất dự án, Khu dân cư'
            ]
        },
        'chotot': {}
    }
    data['distr']['id'] = [n['idQuanHuyen'] for n in data_distr]
    data['distr']['ten'] = [n['Ten2'] for n in data_distr]
    data['distr']['ten_kdau'] = [n['TenKhongDau2'] for n in data_distr]

    data['ttype']['id'] = [n['idLoaiTin'] for n in data_ltin]
    data['ttype']['ten'] = [n['Ten'] for n in data_ltin]
    data['ttype']['ban'] = [n['TenKhongDau'] for n in data_ltin if str(n['idLoaiTin']).startswith('1')]
    data['ttype']['thue'] = [n['TenKhongDau'] for n in data_ltin if str(n['idLoaiTin']).startswith('2')]

    data['chotot']['id_ban'] = [n['idLoaiTin'] for n in data_ltin_ban_chotot]
    data['chotot']['id_thue'] = [n['idLoaiTin'] for n in data_ltin_thue_chotot]
    data['chotot']['id_ban_ct'] = [n['idChotot'] for n in data_ltin_ban_chotot if str(n['idLoaiTin']).startswith('1')
                             if str(n['idLoaiTin']).startswith('1')]
    data['chotot']['id_thue_ct'] = [n['idChotot'] for n in data_ltin_thue_chotot if str(n['idLoaiTin']).startswith('2')
                              if str(n['idLoaiTin']).startswith('2')]
    return data


def start():
    print('update data start on def')
    data_ltin = get_data('loaitin', 1)
    data_distr = get_data('quanhuyen', 1)
    data_ltin_ban_chotot = get_data('ltinban', 3)
    data_ltin_thue_chotot = get_data('ltinthue', 3)
    mydata = update_data(data_ltin, data_distr, data_ltin_ban_chotot, data_ltin_thue_chotot)
    with open('data.json', 'w', encoding="utf8") as file:
        json.dump(mydata, file, indent=4, ensure_ascii=False)
    print('Done')


if __name__ == "__main__":
    print('update data start')
    start()
