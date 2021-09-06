from hashlib import new
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import requests
from bs4 import BeautifulSoup
import base64
import json
import random


w_host = '192.168.1.1'
w_ssid = 'LAB_ROUTER'
w_admin_login = 'admin'
w_admin_password = 'password'
w_pass_file = 'mini_rockyou.txt'
b_path = os.environ.get('BASH_PATH')

auth_key = base64.b64encode(('%s:%s' % (w_admin_login, w_admin_password)).encode()).decode()


def send_email(m: str, to: str, s: str):
    msg = MIMEMultipart()

    password = os.environ.get('EMAIL_PASSWORD')
    msg['From'] = os.environ.get('EMAIL_LOGIN')
    msg['To'] = to
    msg['Subject'] = s

    msg.attach(MIMEText(m, 'plain'))

    server = smtplib.SMTP('smtp.yandex.ru', 587)
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


def get_pass():
    response = requests.get('http://%s/WLG_wireless_guest1.htm' % w_host, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.102 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Basic %s' % auth_key,
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://%s" % w_host,
        "Connection": "keep-alive"})
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text)
    try:
        e = soup.findAll('script')[3].string.split('\n')[46].split('"')[1]
    except Exception:
        return json.dumps({'status': 'error', 'error': 'Не удалось получить пароль'})

    return json.dumps({'status': 'ok', 'response': {'password': e}})


def get_rand_pass():
    lines = open(w_pass_file, encoding='utf-8', errors="ignore").read().splitlines()
    myline = random.choice(lines)
    return myline


def change_pass(passwd=None):
    if passwd is None:
        passwd = get_rand_pass()

    data = {
        "submit_flag": "wlan_guest",
        "sec_wpaphrase_len": len(passwd),
        "old_length": "",
        "generate_flag": "",
        "hidden_wpa_psk": passwd,
        "hidden_sec_type": 4,
        "wep_press_flag": "",
        "wpa1_press_flag": 0,
        "wpa2_press_flag": 1,
        "wpas_press_flag": 0,
        "wps_change_flag": 5,
        "hidden_enable_guestNet": 1,
        "hidden_enable_ssidbro": 1,
        "hidden_allow_guest": 0,
        "endis_wlan_isolation": 0,
        "radiusServerIP": "",
        "s_gssid": w_ssid,
        "hidden_WpaeRadiusSecret": "",
        "guestID": 1,
        "enable_guestNet": 1,
        "enable_ssidbro": 1,
        "gssid": w_ssid,
        "security_type": "WPA2 - PSK",
        "passphrase": passwd
    }

    response = requests.get('http://%s/WLG_wireless_guest1.htm' % w_host, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.102 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Basic %s' % auth_key,
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://%s" % w_host,
        "Connection": "keep-alive"})
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text).find('form')
    try:
        timestamp = soup.get('action').split()[1].split('=')[1]
    except Exception:
        return json.dumps({'status': 'error', 'error': 'Не удалось сменить пароль'})

    response = requests.post('http://%s/apply.cgi?/WLG_wireless_guest1.htm%%20timestamp=%s' % (w_host, timestamp), headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.102 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Basic %s' % auth_key,
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://%s" % w_host,
        "Referer": "http://%s/WLG_wireless_guest1.htm" % w_host,
        "Connection": "keep-alive"}, data=data)
    response.encoding = 'utf-8'

    return json.dumps({'status': 'ok', 'response': {'password': passwd}})


def get_count():
    return len(os.listdir(b_path))

def clear():
    filelist = [f for f in os.listdir(b_path)]
    for f in filelist:
        os.remove(os.path.join(b_path, f))
    alph = 'qwertyuiopasdfghjklzxcvbnm1234567890'
    new_pass = ''.join([random.choice(alph) for _ in range(16)])
    rand_token = '-'.join([''.join([random.choice(alph) for _ in range(4)]) for _ in range(4)])
    with open(b_path+'/'+rand_token, 'w') as file:
        file.write('Excellent, you got that! Your flag: ' + new_pass)
    return new_pass
