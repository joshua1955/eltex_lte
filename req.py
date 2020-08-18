import requests
from bs4 import BeautifulSoup

def LteLoginCookies(login:str, password:str,ip:str):
#Открываем сессию
    session = requests.session()
#Проверим доступен ли станционный терминал
    try:
        if requests.get('http://'+ ip, timeout=5).url != ("http://" + ip +  "/login"):
            print('Check server\'s IP. Looks like it\'s not ELTEX LTE')
    except requests.exceptions.ConnectTimeout:
        print('Check server\'s IP. Server doesn\'t response')
#Передаем headers данные для входа
    login_pass = {'username':login,'password':password,'enter':' Enter '}
#POST запрос авторизации и проверка удалось ли авторизоваться
    r = session.post("http://" + ip + "/login",data=login_pass)
    if r.url != ("http://" + ip +  "/home"):
        print('Не удалось авторизоваться')
        exit()
#Сохраняем куки, чтобы можно было заходить без авторизации
    cookies=session.cookies
    return cookies

def Data(lic_chet:str,cookies):
	main_list=[]
#headers для поиска ONT по ID
	LC = {'sort_id':'','sort_up':'','act':'find','desc_find':lic_chet}
#Вытащим IP из куки
	ip=cookies.list_domains()[0]
#POST запрос
	r_find = requests.post('http://' + ip + '/goform/onu_list_find',data=LC,cookies=cookies)
#Парсим html
	soup = BeautifulSoup(r_find.text, 'html.parser')
#Куда подключен
#	print('Подключаемся к ' + soup.title.string)
#Если не будет ONT по ID, то завершаем программу
	if 'No available ONT.' in soup.text: 
		print('Нет такого ЛК на этом станционном терминале')
		exit()
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
	MAC_dict = {'mode':'view','type':'olt','from': 'list','olt':dict1.get('Channel'),'onu_count': '1','mac': dict1.get('MAC')}
#Post запрос
	r= requests.post('http://' + ip + '/goform/onu_state',data=MAC_dict,cookies=cookies)
#Парсим и сохраняем важные данные в словарь
	soup2 = BeautifulSoup(r.text, 'html.parser')
	q=soup2.find_all(attrs={'name':"olt"})
	row_1=[]
	row_2=[]
	row1=soup2.find_all("th","edit-ins")
	for i in row1:
                row_1.extend(i)
#['Type:', 'MAC address:', 'Channel:', 'State:', 'Firmware revision:', 'Laser power:', 'Video laser power:', 
#'PON Counters', 'MAC', 'LLID', 'State', 'Port', 'State', 'Linked', 'Speed', 'Duplex', 'Flow control', 'Auto-negotiation', 'Counters']
	row2=soup2.find_all("td","edit-ins",limit=7)
	for i in row2:
		row_2.extend(i)
#['NTE-2', '02:00:22:02:16:D8', '0', 'OK', '2.60', '2.6 uW (-25.9 dBm)', 'n/a']
#Добавляем новые данные в словарь, исключая повторяющиеся данные
	for i in range(len(row_2)):
		if row_1[i] == "MAC address:" or row_1[i] == "Channel:" or row_1[i] == "State:" :
			pass
		else:
			dict1.update({row_1[i].rstrip(':'):row_2[i]})

	lan0_dict={}
	for i in range(11,len(row_1)-1,1):
		lan0_dict.update({row_1[i]:''})
#{'Port': '', 'State': '', 'Linked': '', 'Speed': '', 'Duplex': '', 'Flow control': '', 'Auto-negotiation': ''}
#Добавим значения
	row=soup2.find_all('tr')
	port0=row[14]
	port0_d=[]
	lan1_dict={}
	for i in port0:
                port0_d.extend(i)

	lan0_dict.update({'Port':port0_d[1],'State':port0_d[2],'Linked':port0_d[3],'Speed':port0_d[5],'Duplex':port0_d[6],'Flow control':port0_d[7],'Auto-negotiation':port0_d[9]})
	main_list.append(lan0_dict)

	if dict1['Type'] == 'NTE-2' or dict1['Type'] == 'NTE-2C':
		port1_d=[]
		port1=row[15]
		for i in port1:
	                port1_d.extend(i)
		lan1_dict.update({'Port':port1_d[1],'State':port1_d[2],'Linked':port1_d[3],'Speed':port1_d[5],'Duplex':port1_d[6],'Flow control':port1_d[7],'Auto-negotiation':port1_d[9]})
		main_list.append(lan1_dict)

#Добавляем номер olt - OLT0
	olt=soup2.find("tr").text
	dict1.update({"OLT":olt[25:29]})
	main_list.append(dict1)
	return main_list

#Выводим статистику по pon порту
def DataPonStats(MAC:str,PORT:str,cookies):
#PORT:
#UNI0 - Lan NTE-2
#PON - for everybody
	main_list=[]
	ip=cookies.list_domains()[0]
	r_stat=requests.get('http://' + ip + '/goform/ont_statistics?nport=' + PORT + '&ont='+ MAC + '&olt=0&olt_view=0' +'&list_view=1',cookies=cookies)
	soup=BeautifulSoup(r_stat.text, 'html.parser')
	stats = soup.find('table', class_='data').find_all('td')
	stats_list=[]
	for stat in stats:
		stats_list.extend(stat)
	stats_dict_received={}
	stats_dict_transmited={}

	for i in range(len(stats_list)):
		if PORT =='PON':
			if i%2 == 0 and i<28:
				stats_dict_received.update({stats_list[i].rstrip('.'):stats_list[i+1]})
			elif i%2 == 0 and i>27:
				stats_dict_transmited.update({stats_list[i].rstrip('.'):stats_list[i+1]})
		else:
			if i%2 == 0 and i<36:
				stats_dict_received.update({stats_list[i].rstrip('.'):stats_list[i+1]})
			elif i%2 == 0 and i>35:
				stats_dict_transmited.update({stats_list[i].rstrip('.'):stats_list[i+1]})

	main_list.append(stats_dict_received)
	main_list.append(stats_dict_transmited)
# main_list[0] - received
# main_list[1] - transmited
	return main_list


#Close connection
def LteLogout(cookies):
	ip=cookies.list_domains()[0]
	rclose=requests.get('http://' + ip + '/logout',cookies=cookies)

#Тащим логи
def LteLogs(cookies):
	ip=cookies.list_domains()[0]
	r_log=requests.get('http://' + ip + '/goform/log_handler',cookies=cookies)
	soup=BeautifulSoup(r_log.text, 'html.parser')
	logs=soup.find('textarea').text.lstrip('\n').rstrip('\n')
	return logs


login = 'admin'
password = '1eec6p12'
ip = '192.168.51.251'
lic_chet = '70033'

cookies=LteLoginCookies(login,password,ip)
dict=Data(lic_chet,cookies)
print(DataPonStats(dict[2].get('MAC'),'UNI0',cookies)[1])
#LteLogout(cookies)
