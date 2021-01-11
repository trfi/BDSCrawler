# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from trfi_def import select, selects


html = """
<div class="dv-cont-dt"><div><a class="swipebox" href="/Upload/User/Avatar/2020/9ac6ded7-2c4e-4105-94d5-3c040f7c6d22.jpg" rel="nofollow" title="Xem ảnh cỡ lớn"><img alt="" src="/Upload/User/Avatar/2020/Thumbnai/9ac6ded7-2c4e-4105-94d5-3c040f7c6d22.jpg" id="imgAvataDetail" class="w3-circle"></a><label id="lbHoTen"><a title="Click để xem trang cá nhân của chinh nt" href="/tv/417753">chinh nt</a></label><a data-toggle="tooltip" id="btnclickpopchattopic" data-placement="bottom" rel="nofollow" target="_blank" title="" href="https://nhadat24h.net/chatroom-chattinrao-ida417753-subtopic3728669?#" data-original-title="Chat công khai hỏi về bất động sản này"><i class="fa fa-comments-o"></i></a><a data-toggle="tooltip" href="javascript:binTopicChat('417753');" data-placement="bottom" title="" data-original-title="Chat riêng tư với tôi"><i class="fa fa-comment-o"></i></a></div><p><label><i class="fa fa-user"></i>Công Ty Nhà Đất - Môi Giới BĐS</label><label><i class="fa fa-map-marker"></i><a rel="nofollow" title="Xem vị trí trên Gmap" href="/gmap.aspx?idu=417753" class="popup-gmaps">tố hữu hà đông hà nội</a></label><label><i class="fa fa-phone"></i><a title="Mobile" id="viewmobinumber" href="tel:0585198604">0585198604</a>-<a title="Mobile" href="tel:"></a></label><label><a id="yeucaugoilai" title="Bạn quan tâm đến bất động sản này và bạn muốn CHINH NT gọi điện tư vấn ngay cho bạn!" class="buttonNhacGoilai"><i class="fa fa-bell-o"></i><span id="numgoilai" class="begTest">0</span>Yêu cầu chinh nt gọi điện tư vấn.</a></label></p><input type="hidden" id="IDAChat" value="417753"></div>
"""
# with open('html_page.html', 'w', encoding='utf8') as f:
#     f.write(html)
soup = BeautifulSoup(html, 'lxml')

res = selects(soup, 'a[title=Mobile]')
print('\n'.join(filter(None, res)))
print('cc')