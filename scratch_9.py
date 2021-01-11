# import simplejson as json
#
# a = ['https://muaban.net/nha-hem-ngo-quan-ba-dinh-l2406-c3202/chu-rat-can-ban-nha-kim-ma-thuong-78m2-x-8-6-ty-id49963244', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/cho-thue-sa-n-van-pho-ng-mbkd-khu-nga-tu-so-125m2-22-trie-u-id56292507', 'https://muaban.net/nha-mat-tien-quan-cau-giay-l2407-c3401/cho-thue-nha-ma-t-pho-tra-n-duy-hung-150m2-3-ta-ng-mt-7m-id56292432', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-van-phong-chuyen-nghiep-130m2-mat-pho-tue-tinh-id43404297', 'https://muaban.net/mat-bang-cua-hang-shop-quan-cau-giay-l2407-c3403/cho-thue-nha-ma-t-pho-nguye-n-van-huyen-150m2-2-ta-ng-mt-7m-id56259716', 'https://muaban.net/nha-mat-tien-quan-dong-da-l2408-c3401/cho-thue-nha-pho-tha-i-thi-nh-125m2-6-ta-ng-mt-7-5m--id56259687', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/san-van-phong-showroom-cho-thue-tai-pho-chua-lang-130m2-32tr-th-id43593768', 'https://muaban.net/van-phong-quan-hoan-kiem-l2410-c3408/cho-thue-van-pho-ng-chuyen-nghie-p-pho-quang-trung-hoa-n-kie-m-id47564672', 'https://muaban.net/nha-mat-tien-quan-dong-da-l2408-c3401/cho-thue-nha-mat-pho-chua-boc-dong-da-120m2-mt-7m-id46056472', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/cho-thue-van-phong-dep-nhat-mat-pho-le-trong-tan-truong-chinh-id42314797', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-san-van-phong-showroom-dao-tao-40m2x3-mat-pho-le-thanh-nghi-id43758616', 'https://muaban.net/nha-mat-tien-quan-tay-ho-l2413-c3201/ban-nha-mat-pho-nguyen-dinh-thi-dt-70m2-x-5-tang-mt-6-2m-he-rong-3m--id55160533', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-san-van-phong-pho-ton-duc-thang-quan-dong-da-id44002513', 'https://muaban.net/nha-mat-tien-quan-hai-ba-trung-l2409-c3401/cho-thue-nha-mat-pho-ba-trieu-200m2x7t-mt-7m-de-kinh-doanh-vp-id45399160', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-san-van-phong-chuyen-nghiep-40m2-mat-pho-le-thanh-nghi-id44601651', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/van-phong-cao-cap-dien-tich-linh-hoat-10-200m2-tai-62-nguyen-huy-tuong-id46370133', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-van-phong-mat-pho-chua-lang-view-ho-3-mat-thoang-id45120689', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/van-phong-dep-thoang-40m2-60m2-100m2-tai-89b-nguyen-khuyen-dong-da-id44928109', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-san-van-phong-tien-ich-60m2-tai-tue-tinh-ba-trieu-id44952346', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-van-phong-25-m2-tai-14-nam-dong-quan-dong-da-id45131997', 'https://muaban.net/van-phong-quan-hoan-kiem-l2410-c3408/cho-thue-van-phong-40-100m2-mat-pho-yet-kieu-hoan-kiem-id48107170', 'https://muaban.net/khach-san-can-ho-dich-vu-quan-hai-ba-trung-l2409-c3404/cho-thue-can-ho-dich-vu-dep-day-du-tien-nghi-pho-tue-tinh-dt-120m2-id42889252', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-san-van-phong-showroom-phong-kham-view-dep-quan-dong-da-id44550704', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/cho-thue-van-phong-tien-ich-dep-mat-pho-le-trong-tan-110m2-30tr-th-id43173180', 'https://muaban.net/mat-bang-cua-hang-shop-quan-dong-da-l2408-c3403/cho-thue-mbkd-spa-dao-tao-phong-kham-pho-nguyen-khuyen-dong-da-id45421268', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/cho-thue-van-phong-tien-ich-mat-pho-le-trong-tan-thanh-xuan-id42101093', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-van-phong-spa-showroom-30m2-mat-pho-hue-id43527146', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/san-van-phong-cao-cap-25m2-tai-86-le-trong-tan-thanh-xuan-id46860226', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-van-phong-tai-so-4-le-thanh-nghi-phuong-cau-den-hai-ba-trung-id45126035', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-van-phong-spa-showroom-40-150m2-mat-pho-nguyen-khuyen-id43550327']
# b = ['https://muaban.net/nha-hem-ngo-quan-ba-dinh-l2406-c3202/chu-rat-can-ban-nha-kim-ma-thuong-78m2-x-8-6-ty-id49963244', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/cho-thue-sa-n-van-pho-ng-mbkd-khu-nga-tu-so-125m2-22-trie-u-id56292507', 'https://muaban.net/nha-mat-tien-quan-cau-giay-l2407-c3401/cho-thue-nha-ma-t-pho-tra-n-duy-hung-150m2-3-ta-ng-mt-7m-id56292432', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-van-phong-chuyen-nghiep-130m2-mat-pho-tue-tinh-id43404297', 'https://muaban.net/mat-bang-cua-hang-shop-quan-cau-giay-l2407-c3403/cho-thue-nha-ma-t-pho-nguye-n-van-huyen-150m2-2-ta-ng-mt-7m-id56259716', 'https://muaban.net/nha-mat-tien-quan-dong-da-l2408-c3401/cho-thue-nha-pho-tha-i-thi-nh-125m2-6-ta-ng-mt-7-5m--id56259687', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/san-van-phong-showroom-cho-thue-tai-pho-chua-lang-130m2-32tr-th-id43593768', 'https://muaban.net/van-phong-quan-hoan-kiem-l2410-c3408/cho-thue-van-pho-ng-chuyen-nghie-p-pho-quang-trung-hoa-n-kie-m-id47564672', 'https://muaban.net/nha-mat-tien-quan-dong-da-l2408-c3401/cho-thue-nha-mat-pho-chua-boc-dong-da-120m2-mt-7m-id46056472', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/cho-thue-van-phong-dep-nhat-mat-pho-le-trong-tan-truong-chinh-id42314797', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-san-van-phong-showroom-dao-tao-40m2x3-mat-pho-le-thanh-nghi-id43758616', 'https://muaban.net/nha-mat-tien-quan-tay-ho-l2413-c3201/ban-nha-mat-pho-nguyen-dinh-thi-dt-70m2-x-5-tang-mt-6-2m-he-rong-3m--id55160533', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-san-van-phong-pho-ton-duc-thang-quan-dong-da-id44002513', 'https://muaban.net/nha-mat-tien-quan-hai-ba-trung-l2409-c3401/cho-thue-nha-mat-pho-ba-trieu-200m2x7t-mt-7m-de-kinh-doanh-vp-id45399160', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-san-van-phong-chuyen-nghiep-40m2-mat-pho-le-thanh-nghi-id44601651', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/van-phong-cao-cap-dien-tich-linh-hoat-10-200m2-tai-62-nguyen-huy-tuong-id46370133', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-van-phong-mat-pho-chua-lang-view-ho-3-mat-thoang-id45120689', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/van-phong-dep-thoang-40m2-60m2-100m2-tai-89b-nguyen-khuyen-dong-da-id44928109', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-san-van-phong-tien-ich-60m2-tai-tue-tinh-ba-trieu-id44952346', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-van-phong-25-m2-tai-14-nam-dong-quan-dong-da-id45131997', 'https://muaban.net/van-phong-quan-hoan-kiem-l2410-c3408/cho-thue-van-phong-40-100m2-mat-pho-yet-kieu-hoan-kiem-id48107170', 'https://muaban.net/khach-san-can-ho-dich-vu-quan-hai-ba-trung-l2409-c3404/cho-thue-can-ho-dich-vu-dep-day-du-tien-nghi-pho-tue-tinh-dt-120m2-id42889252', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-san-van-phong-showroom-phong-kham-view-dep-quan-dong-da-id44550704', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/cho-thue-van-phong-tien-ich-dep-mat-pho-le-trong-tan-110m2-30tr-th-id43173180', 'https://muaban.net/mat-bang-cua-hang-shop-quan-dong-da-l2408-c3403/cho-thue-mbkd-spa-dao-tao-phong-kham-pho-nguyen-khuyen-dong-da-id45421268', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/cho-thue-van-phong-tien-ich-mat-pho-le-trong-tan-thanh-xuan-id42101093', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-van-phong-spa-showroom-30m2-mat-pho-hue-id43527146', 'https://muaban.net/van-phong-quan-thanh-xuan-l2414-c3408/san-van-phong-cao-cap-25m2-tai-86-le-trong-tan-thanh-xuan-id46860226', 'https://muaban.net/van-phong-quan-hai-ba-trung-l2409-c3408/cho-thue-van-phong-tai-so-4-le-thanh-nghi-phuong-cau-den-hai-ba-trung-id45126035', 'https://muaban.net/van-phong-quan-dong-da-l2408-c3408/cho-thue-van-phong-spa-showroom-40-150m2-mat-pho-nguyen-khuyen-id43550327']
# rs = set(a) & set(b)
# print(len(rs))
# # with open(f'old_item.txt', 'w', encoding='utf8') as f:
# #     f.write(str(a))
#
# with open('old_item.txt', 'w') as f:
#     json.dump(a, f)
# with open('old_item.txt', 'r') as f:
#     basicList = json.load(f)
#     print(type(basicList))
# import re
#
# s = """0913443982.0986588377.312312""".replace(' ', '')
# rs = re.split('[^[0-9]+', s)
# rs = '\n'.join(rs)
# print(rs)
import subprocess

import requests
from text_unidecode import unidecode
import re


#
#
# string = "\n👉🏻 Tầng 5 : -Ô n'hỏ d\iện/ tích sử."
#
# string = re.sub(r'[^\w.,:"\'/\\()@\-!%*\n]', ' ', string)
#
# print(string)

# moigioi = {'012', '123', '015'}
# val = [('012', 'cc'), ('015', 'cl'), ('123', 'cdcm'), ('123', 'okcc'), ('015', 'clcxz')]
#
# for i in range(len(val) - 1, -1, -1):
#     if val[i][0] in moigioi:
#         val.pop(i)
# print(val)


# def f():
#     yield 'y0'
#     yield 'x * 3'
#     yield 'y0 ** 4'
#
#
# a = f()
#
# for i in a:
#     print(i)

# server = 'http://104.199.238.174'
# data = {"update": True}
# res = requests.put(f'{server}/api/tools/update_all', json=data)
# print(res.json())

process_name = 'BDSCrawler.exe'
cmd = 'TASKLIST /FI "STATUS eq running"  /FI "IMAGENAME eq BDSCrawler.exe"'
output = subprocess.run(cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE).stdout
print(len(output.split('\n'))-4)
print(output.split('\n'))

# mylist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# mylist += [11, 12, 13, 14]
# dif_len = len(mylist) - 10
# print(dif_len)
# if dif_len > 1:
#     del mylist[0:dif_len]
# mylist = list(set(mylist))
# print(mylist)
# print(len(mylist))
