import requests
from bs4 import BeautifulSoup
import sys

login = 'admin'
password = '1eec6p12'
ip = '192.168.51.254'
lic_chet = '70169'


def main(login, password,ip,lic_chet):
#Открываем сессию
	s = requests.Session()
#Передаем headers данные для входа
	login_pass = {'username':login,'password':password,'enter':' Enter '}
#POST запрос
	r = s.post("http://" + ip + "/login",data=login_pass)
	print('Информация по ЛК ' + str(lic_chet))
#headers для поиска ONT по ID
	LC = {'sort_id':'','sort_up':'','act':'find','desc_find':lic_chet}
#POST запрос
	r_login = s.post('http://' + ip + '/goform/onu_list_find',data=LC)
#Парсим html
	soup = BeautifulSoup(r_login.text, 'html.parser')
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
	r3= s.post('http://' + ip + '/goform/onu_state',data=MAC)
#Парсим и сохраняем важные данные в словарь
	soup2 = BeautifulSoup(r3.text, 'html.parser')
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
	print(dict1)
#Выводим статистику по pon порту
	r_stat=s.get('http://' + ip + '/goform/ont_statistics?nport=PON&ont='+ str(dict1.get('MAC')) + '&olt=0&olt_view=0' +'&list_view=1')
	soup3=BeautifulSoup(r_stat.text, 'html.parser')
	stats = soup3.find_all('table', class_='data')
#	print(stats)
	stats_dict=[]
#	for stat in stats:
#		stats_dict.append({
#			"TX/RX":stat.find('th').get_text(),
#			stat.find('td').get_text():"num"
#		}
#		)
#	print(stats_dict)
#тащим логи
#	r_log=s.get('http://' + ip + '/goform/log_handler')
#	soup4=BeautifulSoup(r_log.text, 'html.parser')
#	print(soup4.text)
#Close connection
	rclose=s.get('http://' + ip + '/logout')
	s.close()
r = main(login,password,ip,lic_chet)
