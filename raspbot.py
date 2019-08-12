import os
import time
import telepot
import subprocess
import configparser
import urllib.request
import RPi.GPIO as gpio
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

config = configparser.ConfigParser()
location = '{}/config.ini'.format(os.getcwd())
config.read(location)

BOT_API = config['BOT_API']['api']

admin_id = int(config['ADMIN']['id'])

autho_1 = int(config['AUTHORIZED']['id_1'])

autho_2 =int( config['AUTHORIZED']['id_2'])


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/pins'), KeyboardButton(text='/temp'), KeyboardButton(text='/process')],
        [KeyboardButton(text='/memory'), KeyboardButton(text='/uptime'), KeyboardButton(text='/sduse')],
        [KeyboardButton(text='/datetime'), KeyboardButton(text='/lan_wan'), KeyboardButton(text='/ip')],
    ])


keyboard_pins = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='4'), KeyboardButton(text='5'), KeyboardButton(text='6'), KeyboardButton(text='12'), KeyboardButton(text='13'), KeyboardButton(text='16'), KeyboardButton(text='17'), KeyboardButton(text='18')],
        [KeyboardButton(text='20'), KeyboardButton(text='21'), KeyboardButton(text='22'), KeyboardButton(text='23'), KeyboardButton(text='24'), KeyboardButton(text='25'), KeyboardButton(text='26'), KeyboardButton(text='27')],
        [KeyboardButton(text='/voltar')],
    ])


def start(chat_id, comando):
    bot.sendMessage(chat_id, '''Bem Vindo!!
Iniciando o Bot...
Use os comandos do teclado abaixo:''', reply_markup=keyboard)


def temperature(chat_id, comando):
    temp = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3
    bot.sendMessage(chat_id, 'Temperatura atual da CPU: {:.2f}°C'.format(temp))


def process(chat_id, comando):
    quantProc = subprocess.getstatusoutput('ps -aux | wc -l')[1]
    bot.sendMessage(chat_id, 'Quantidade de processos ativos: {}'.format(quantProc))


def memory(chat_id, comando):
    mem_total = int(subprocess.getoutput("awk '/MemTotal/ { print $2 }' /proc/meminfo"))/1024
    mem_used = int(subprocess.getoutput("awk '/MemFree/ { print $2 }' /proc/meminfo"))/1024
    mem_free = int(subprocess.getoutput("awk '/MemAvailable/ { print $2 }' /proc/meminfo"))/1024
    bot.sendMessage(chat_id, '''Total: {:.2f} MB
Em uso: {:.2f} MB
Livre: {:.2f} MB'''.format(mem_total, mem_used, mem_free))


def upTime(chat_id, comando):
    uptime = subprocess.getstatusoutput('uptime -p')[1]
    bot.sendMessage(chat_id, 'Up Time do sistema: {}'.format(uptime))


def sdCard(chat_id, comando):
    sd_size = subprocess.getoutput("df -h | grep /dev/root | awk '{print $2}'")
    sd_used = subprocess.getoutput("df -h | grep /dev/root | awk '{print $3}'")
    sd_available = subprocess.getoutput("df -h | grep /dev/root | awk '{print $4}'")
    sd_percent_use = subprocess.getoutput("df -h | grep /dev/root | awk '{print $5}'")
    bot.sendMessage(chat_id, '''Tamanho do MicroSD: {}
Espaço usado: {}
Espaço disponível: {}
Porcentagem: {}'''.format(sd_size, sd_used, sd_available, sd_percent_use))


def date(chat_id, comando):
    date = subprocess.getstatusoutput('date')[1]
    bot.sendMessage(chat_id, 'Data e hora do Sistema: {}'.format(date))


def network(chat_id, comando):
    rx_wifi = subprocess.getstatusoutput('cat /sys/class/net/wlan0/statistics/rx_bytes')[1]
    rx_text = 'Quantidade de banda recebida pela rede Wifi:'
    rx_float = float(rx_wifi)
    rx_float_mb = rx_float / 1024 / 1024
    if rx_float_mb > 1024:
        rx_float_gb = rx_float_mb / 1024
        bot.sendMessage(chat_id, '{} {:.2f} Gbs'.format(rx_text, rx_float_gb))
    else:
        bot.sendMessage(chat_id, '{} {:.2f} Mbs'.format(rx_text, rx_float_mb))
        tx_wifi = subprocess.getstatusoutput('cat /sys/class/net/wlan0/statistics/tx_bytes')[1]
        tx_text = 'Quantidade de banda enviada pela rede Wifi:'
        tx_float = float(tx_wifi)
        tx_float_mb = tx_float / 1024 / 1024
    if tx_float_mb > 1024:
        tx_float_gb = tx_float_mb / 1024
        bot.sendMessage(chat_id, '{} {:.2f} Gbs'.format(tx_text, tx_float_gb))
    else:
        bot.sendMessage(chat_id, '{} {:.2f} Mbs'.format(tx_text, tx_float_mb))


def ip(chat_id, comando):
    if chat_id == admin_id or chat_id == autho_1 or chat_id == autho_2:
        ip_lan = subprocess.getstatusoutput('ifconfig wlan0 |  grep inet | cut -c 14-26 | head -1')[1]
        ip_ex = urllib.request.urlopen('http://bot.whatismyipaddress.com/').read()
        bot.sendMessage(chat_id, 'Ip local: {} \nIp externo: {}'.format(ip_lan, ip_ex.decode('utf-8')))
    else:
        bot.sendMessage(chat_id, 'No chat_id admin.')


def voltar(chat_id, comando):
    bot.sendMessage(chat_id, 'Iniciando novamente...', reply_markup=keyboard)


def help(chat_id, comando):
    bot.sendMessage(chat_id, 'Utilize os comandos abaixo para interagir com o bot! :>', reply_markup=keyboard)


def controlPins(chat_id, comando, pino):
    gpio.setmode(gpio.BCM)
    gpio.setwarnings(False)
    gpio.setup(pino, gpio.OUT)
    estado = gpio.input(pino)
    if estado == 0:
        gpio.output(pino, True)
        bot.sendMessage(chat_id, 'Pino {} ligado'.format(pino), reply_markup=keyboard_pins)
    elif estado == 1:
        gpio.output(pino, False)
        bot.sendMessage(chat_id, 'Pino {} desligado'.format(pino), reply_markup=keyboard_pins)
    else:
        print('Ops! Falha ao identificar a msg recebida.')


def getStatus(chat_id, comando, pino):
    listapinos = ['4', '5', '6', '12', '13', '16', '17', '18',
		  '20', '21', '22', '23', '24', '25', '26', '27']
    for i in range(len(listapinos)):
        pinos = int(listapinos[i])
        gpio.setup(pinos, gpio.OUT)
        estado_apos = gpio.input(pinos)
        bot.sendMessage(chat_id, 'Pino {} em estado {}'.format(pinos, estado_apos))


def getinfo(chat_id, comando, m, content_type):
    if chat_id < 0:
        print('Comando usado -->', comando)
        print('---------------------------')
        print('Menssage do tipo %s. Comando: %s \n' % (content_type, comando))
        print('Chat ID do Grupo : %s' % m.chat[0])
        print('Tipo de chat : %s' % m.chat[1])
        print('Nome do Grupo: %s' % m.chat[2])
        print('Chat Id User: %s' % m.from_[0])
        print('Username: %s' % m.from_[3])
        print('First Name : %s' % m.from_[1])
        print('Last Name: %s' % m.from_[2])
        print(time.strftime('%Y-%m-%d %H:%M:%S'))
        print('--------------------------------------')
    else:
        print('Comando usado -->', comando)
        print('---------------------------')
        print('Menssage do tipo %s. Comando: %s \n' % (content_type, comando))
        print('Chat ID : %s' % m.chat[0])
        print('Tipo de chat : %s' % m.chat[1])
        print('Username : %s' % m.chat[3])
        print('First Name: %s' % m.chat[4])
        print('Last Name: %s' % m.chat[5])
        print(time.strftime('%Y-%m-%d %H:%M:%S'))
        print('--------------------------------------')


def handle(msg):
    comando = msg['text']
    content_type, chat_type, chat_id = telepot.glance(msg)
    m = telepot.namedtuple.Message(**msg)

    if comando.isdigit():
        pino = int(comando)
        controlPins(chat_id, comando, pino)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/start':
        start(chat_id, keyboard)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/temp':
        temperature(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/process':
        process(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/memory':
        memory(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/uptime':
        upTime(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/sduse':
        sdCard(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/datetime':
        date(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/lan_wan':
        network(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/ip':
        ip(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/help':
        help(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/voltar':
        voltar(chat_id, comando)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/pins':
        bot.sendMessage(chat_id, 'Selecione o pino no teclado abaixo:', reply_markup=keyboard_pins)
        getinfo(chat_id, comando, m, content_type)

    elif comando == '/estado':
        getStatus(chat_id, comando, pino)
        getinfo(chat_id, comando, m, content_type)

    else:
        bot.sendMessage(chat_id, 'Tente usar os comandos no teclado :>', reply_markup=keyboard)
        getinfo(chat_id, comando, m, content_type)


bot = telepot.Bot(BOT_API)
bot.message_loop(handle)

print('Aguardando comandos ...')

while 1:
    time.sleep(5)
