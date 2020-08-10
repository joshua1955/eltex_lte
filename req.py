import requests
from bs4 import BeautifulSoup
import sys

login = 'admin'
password = '1eec6p12'
ip = '192.168.51.253'
lic_chet = '82029'

def login_cookies(login, password,ip,lic_chet):
#Открываем сессию
	s = requests.Session()
#Передаем headers данные для входа
	login_pass = {'username':login,'password':password,'enter':' Enter '}
#POST запрос авторизации
	r = s.post("http://" + ip + "/login",data=login_pass)
#Сохраняем куки, чтобы можно было заходить без авторизации
	cookies=s.cookies
	return cookies

def find_PONMAC(lic_chet,cookies):
#headers для поиска ONT по ID
	LC = {'sort_id':'','sort_up':'','act':'find','desc_find':lic_chet}
#Вытащим IP из куки
	ip=cookies.list_domains()[0]
#POST запрос
	r_find = requests.post('http://' + ip + '/goform/onu_list_find',data=LC,cookies=cookies)
#Парсим html
	soup = BeautifulSoup(r_find.text, 'html.parser')
#Куда подключен
	print('Подключаемся к ' + soup.title.string)
#Если не будет ONT по ID, то завершаем программу
	if 'No available ONT.' in soup.text:
		print('Нет такого ЛК на этом станционном терминале\n')
		sys.exit()
#Умело парсим данные и сохраняем важные данные в словарь
	a = soup.thead.find_all('td')
	res_a = []
	for i in a:
		res_a.extend(i)
	b = soup.tbody.find_all('td')
	res_b = []
	for i in b:
		res_b.extend(i)
	dict1 = {}
	for i in range(len(res_a) - 2):
		dict1.update({res_a[i]:res_b[i]})
#headers для поиска ONT по MAC
	MAC = {'mode':'view','type':'olt','from': 'list','olt':dict1.get('Channel'),'onu_count': '1','mac': dict1.get('MAC')}
#Post запрос
	r= requests.post('http://' + ip + '/goform/onu_state',data=MAC)
#Парсим и сохраняем важные данные в словарь
	soup2 = BeautifulSoup(r.text, 'html.parser')
	q=soup2.find_all(attrs={'name':"olt"})
	row_1=[]
	row_2=[]
	row1=soup2.find_all("th","edit-ins")
	for i in row1:
                row_1.extend(i)
	row2=soup2.find_all("td","edit-ins",limit=7)
	for i in row2:
		row_2.extend(i)
	for i in range(len(row_2)):
		dict1.update({row_1[i]:row_2[i]})
	return dict1

#Выводим статистику по pon порту
def lte_pon_stats(MAC,cookies):
	ip=cookies.list_domains()[0]
	#str(dict1.get('MAC'))
	r_stat=s.get('http://' + ip + '/goform/ont_statistics?nport=PON&ont='+ str(MAC) + '&olt=0&olt_view=0' +'&list_view=1',cookies=cookies)
	soup=BeautifulSoup(r_stat.text, 'html.parser')
	stats = soup.find_all('table', class_='data')
	print(stats)
	stats_dict=[]
	for stat in stats:
		stats_dict.append({
			"TX/RX":stat.find('th').get_text(),
			stat.find('td').get_text():"num"
		}
		)
	return stats_dict


#Close connection
def lte_logout(cookies):
	ip=cookies.list_domains()[0]
	rclose=s.get('http://' + ip + '/logout',cookies=cookies)
	s.close()


#Тащим логи
def lte_logs(cookies):
	ip=cookies.list_domains()[0]
	r_log=requests.get('http://' + ip + '/goform/log_handler',cookies=cookies)
	soup=BeautifulSoup(r_log.text, 'html.parser')
	logs_str=str(soup.find_all('textarea'))
	logs=logs_str.lstrip('[<textarea cols="105" id="log" name="log" nowrap="" readonly="" rows="25">').rstrip('</textarea>]')
	return logs



cookies=login_cookies(login,password,ip,lic_chet)
print(lte_logs(cookies))
