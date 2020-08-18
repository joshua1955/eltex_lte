import eltex_lte_lib

login = 'admin'
password = '1eec6p12'
ip = '192.168.51.251'
lic_chet = '70033'

cookies=eltex_lte_lib.LteLoginCookies(login,password,ip)
dict=eltex_lte_lib.Data(lic_chet,cookies)
print(eltex_lte_lib.DataPonStats(dict[2].get('MAC'),'UNI0',cookies)[1])
eltex_lte_lib.LteLogout(cookies)
