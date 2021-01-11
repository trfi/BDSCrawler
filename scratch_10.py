import requests
from bs4 import  BeautifulSoup
from trfi_def import selects

r = requests.Session()

headers = {
    "accept": "*/*",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "content-type": "text/plain;charset=UTF-8",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
}
i = 1
provin = 5
idlink = 295776
idlink_thue = 295942
idlink_hcm = 409644
idlink_hcm_thue = 295819
type_ = 1

data2 = f'_GetIPAddress=\r\n_id_tt={provin}\r\n_id_q=0\r\n_id_kv=0\r\n_id_ln=0\r\n_id_hn=0\r\n_fromTD=\r\n_toDT=\r\n_dvDT=1\r\n_fromG=\r\n_dvGfrom=10\r\n_toG=\r\n_dvGto=10000\r\n_keyWord=\r\n_ID_LT={type_}\r\n_orderby=1\r\n_id_u=0\r\n_yesVIP=1\r\n_NguonTin=0\r\n_Matin=0\r\n_PageIndex={i}\r\n_offerYear=12\r\n_IDLink={idlink}\r\n_TotallRow=3928'
res = r.post('https://nhadat24h.net/ajax/XPRO._2014Index,XPRO.ashx?_method=search2019&_session=rw', headers=headers, data=data2)

print(res.status_code)
print(res.text)

soup = BeautifulSoup(res.text, 'lxml')
items = selects(soup, 'div.dv-item > a:nth-of-type(1)', get='href')

from pprint import  pprint
pprint(items)
print(len(items))
