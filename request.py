import eltex_lte_lib

login = 'admin'
password = 'password'
ip = '192.168.1.1'
lic_chet = '70033'

cookies=eltex_lte_lib.LteLoginCookies(login,password,ip)
dict=eltex_lte_lib.Data(lic_chet,cookies)
print("Main inf about ont terminal:")
print('\nUNI0')
print(dict[0])
print('\nUNI1')
print(dict[1])
print('\nMain data')
print(dict[2])

print('\nUNI0 received stats')
print(eltex_lte_lib.DataPonStats(dict[2].get('MAC'),'UNI0',cookies)[0])

print('\nUNI0 transmited stats')
print(eltex_lte_lib.DataPonStats(dict[2].get('MAC'),'UNI0',cookies)[1])

print('\nPON received stats')
print(eltex_lte_lib.DataPonStats(dict[2].get('MAC'),'PON',cookies)[0])

print('\nPON transmited stats')
print(eltex_lte_lib.DataPonStats(dict[2].get('MAC'),'PON',cookies)[1])

print('\nLTE logs')
print(eltex_lte_lib.LteLogs(cookies))

eltex_lte_lib.LteLogout(cookies)
