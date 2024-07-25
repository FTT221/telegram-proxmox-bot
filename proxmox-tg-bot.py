import requests
import telebot
from telebot import types
import os
import platform
import time
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ////////////////////////////////////////////////////////////////////////////////////////////////
# bot settings
telegram_token = "token"
ids = [telegram_id1, telegram_id2, telegram_id3]  # авторизация по white list
teleram_id_admin = "id-tg-admin"
# /bot settings
bot = telebot.TeleBot(telegram_token)
# proxmox settings
proxmox_url = "https://1.0.0.1:8006"
proxmox_node_name = "node-name"
proxmox_user = "user-pve-on-proxmox"
proxmox_password = "pass"
proxmox_realm = "pve"  #pve or pam
id_vm_mashine_1 = 100
id_vm_mashine_2 = 101
id_vm_mashine_3 = 102
# /proxmox settings
# #////////////////////////////////////////////////////////////////////////////////////////////////


def authenticat():
    session = requests.Session()
    session.verify = False
    login_payload = {  # формируем логин и пассворд для отправки
        "username": proxmox_user,
        "password": proxmox_password,
        "realm": proxmox_realm,
    }
    login_url = f"{proxmox_url}/api2/json/access/ticket"  # url для логинки делаем
    response = session.post(login_url, data=login_payload)  # запрос POST логинемся
    response.raise_for_status()  # получаем json резулятата

    ticket = response.json()["data"]["ticket"] #выбрать данные из json response data in ticket)
    csrf_token = response.json()["data"]["CSRFPreventionToken"]  # кукисы
    session.headers.update(
        {"CSRFPreventionToken": csrf_token, "Cookie": f"PVEAuthCookie={ticket}"}
    )
    return session


def status_vm(session, vm_id):
    status_vm_url = f"{proxmox_url}/api2/json/nodes/{proxmox_node_name}/qemu/{vm_id}/status/current"  # запрос гет на статус вм
    response = session.get(status_vm_url) # создаем сессию и делаем GET запрос
    status_vm_proxmox = response.json()["data"]["status"] # берем информацию data в ней берем status
    return status_vm_proxmox


def start_vm(session, vm_id):
    start_vm_url = f"{proxmox_url}/api2/json/nodes/{proxmox_node_name}/qemu/{vm_id}/status/start"  # запрос гет на старт вм
    response = session.post(start_vm_url)  # создаем сессию и делаем POST запрос
    response.raise_for_status()  # чекаем ошибки



def stop_vm(session, vm_id):
    # stop_vm_url = f"{proxmox_url}/api2/json/nodes/{proxmox_node_name}/qemu/{vm_id}/status/stop"  # запрос гет на стоп (экстеренный) вм
    stop_vm_url = f"{proxmox_url}/api2/json/nodes/{proxmox_node_name}/qemu/{vm_id}/status/shutdown"  # запрос гет на выкл vm
    response = session.post(stop_vm_url)  # создаем сессию и делаем POST запрос
    response.raise_for_status()  # чекаем ошибки



@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    global ids  # массив с айди пользователей которые допущены
    if message.from_user.id not in ids:
        bot.send_message(teleram_id_admin, "ПОПЫТКА ВХОДА ID:" + str(message.chat.id) + " Время:" + str(
            datetime.now()))  # отправка главному админу

    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("👋")
        btn2 = types.KeyboardButton("VMs")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, text="Привет!")
        time.sleep(2)  # костыль 2 сек
        bot.send_message(message.chat.id, text="Я бот для on/off VM".format(message.from_user),
                         reply_markup=markup)  # шлем привет на старт и даем кнопки
        time.sleep(1)  # костыль 1 сек
        bot.send_message(message.chat.id, text="All rights reserved " + str(datetime.now().year))

@bot.message_handler(content_types=['text'])  # чекая текст
def func(message):
    if (message.text == "👋"):
        bot.send_sticker(message.chat.id, sticker='CAACAgIAAxkBAAEKR3xlAAEefpv72ZSxDjKLIK55JtLmYJsAAk8YAAK_gxBLPTcI6IN6YGIwBA')
        bot.send_message(message.chat.id, text="Я бот для включение VMs в proxmox")

    elif (message.text == "VMs"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(f"{id_vm_mashine_1}")
        btn2 = types.KeyboardButton(f"{id_vm_mashine_2}")
        btn3 = types.KeyboardButton(f"{id_vm_mashine_3}")
        back = types.KeyboardButton("Главное меню")
        markup.add(back, btn3, btn2, btn1)  # даем кнопки
        bot.send_message(message.chat.id, text="Выберете устройство:", reply_markup=markup)

    elif (message.text == f"{id_vm_mashine_1}"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(f"Power ON {id_vm_mashine_1}")  # далаем кнопки
        btn2 = types.KeyboardButton(f"Power OFF {id_vm_mashine_1}")
        btn3 = types.KeyboardButton(f"Status {id_vm_mashine_1}")
        back = types.KeyboardButton("Меню Выбора VMs")
        markup.add(back, btn3, btn2, btn1)  # даем кнопки
        bot.send_message(message.chat.id, text="Выберете действие:", reply_markup=markup)

    elif (message.text == f"Power ON {id_vm_mashine_1}"):
        session = authenticat()  # создаем сесию и логинимся там
        vm_id = id_vm_mashine_1  # переменная для айди машины из настроек
        response = start_vm(session, vm_id)  # запрос в сессию и стат вм
        bot.send_message(message.chat.id, text="ON")

    elif (message.text == f"Power OFF {id_vm_mashine_1}"):
        session = authenticat()  # создаем сесию и логинимся там
        vm_id = id_vm_mashine_1  # переменная для применниение айди машины из настроек
        response = stop_vm(session, vm_id)  # запрос в сессию и офф вм
        bot.send_message(message.chat.id, text="OFF")

    elif (message.text == f"Status {id_vm_mashine_1}"):
        # time.sleep(3)
        session = authenticat()  # создаем сесию и логинимся там
        vm_id = id_vm_mashine_1  # переменная для применниение айди машины из настроек
        response = status_vm(session, vm_id)  # запрос в сессию и статус вм
        if response == "running":
            bot.send_message(message.chat.id, text="ON")
        elif response == "stopped":
            bot.send_message(message.chat.id, text="OFF")
        else:
            bot.send_message(message.chat.id, text="Error Запрос выдал :" + str(response))

    elif (message.text == f"{id_vm_mashine_2}"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(f"Power ON {id_vm_mashine_2}")  # далаем кнопки
        btn2 = types.KeyboardButton(f"Power OFF {id_vm_mashine_2}")
        btn3 = types.KeyboardButton(f"Status {id_vm_mashine_2}")
        back = types.KeyboardButton("Меню Выбора VMs")
        markup.add(back, btn3, btn2, btn1)  # даем кнопки
        bot.send_message(message.chat.id, text="Выберете действие:", reply_markup=markup)

    elif (message.text == f"Power ON {id_vm_mashine_2}"):
        session = authenticat()  # создаем сесию и логинимся там
        vm_id = id_vm_mashine_2  # переменная для применниение айди машины из настроек
        response = start_vm(session, vm_id)  # запрос в сессию и стат вм
        bot.send_message(message.chat.id, text="ON")

    elif (message.text == f"Power OFF {id_vm_mashine_2}"):
        session = authenticat()  # создаем сесию и логинимся там
        vm_id = id_vm_mashine_2  # переменная для применниение айди машины из настроек
        response = stop_vm(session, vm_id)  # запрос в сессию и офф вм
        bot.send_message(message.chat.id, text="OFF")

    elif (message.text == f"Status {id_vm_mashine_2}"):
        # time.sleep(3)
        session = authenticat()  # создаем сесию и логинимся там
        vm_id = id_vm_mashine_2  # переменная для применниение айди машины из настроек
        response = status_vm(session, vm_id)  # запрос в сессию и статус вм
        if response == "running":
            bot.send_message(message.chat.id, text="ON")
        elif response == "stopped":
            bot.send_message(message.chat.id, text="OFF")
        else:
            bot.send_message(message.chat.id, text="❗Error Запрос выдал :" + str(response))


    elif (message.text == f"{id_vm_mashine_3}"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(f"Power ON {id_vm_mashine_3}")  # далаем кнопки
        btn2 = types.KeyboardButton(f"Power OFF {id_vm_mashine_3}")
        btn3 = types.KeyboardButton(f"Status {id_vm_mashine_3}")
        back = types.KeyboardButton("Меню Выбора VMs")
        markup.add(back, btn3, btn2, btn1)  # даем кнопки
        bot.send_message(message.chat.id, text="Выберете действие:", reply_markup=markup)

    elif (message.text == f"Power ON {id_vm_mashine_3}"):
        session = authenticat()  # создаем сесию и логинимся там
        vm_id = id_vm_mashine_3  # переменная для применниение айди машины из настроек
        response = start_vm(session, vm_id)  # запрос в сессию и стат вм
        bot.send_message(message.chat.id, text="ON")

    elif (message.text == f"Power OFF {id_vm_mashine_3}"):
        session = authenticat()  # создаем сесию и логинимся тут был bysg
        vm_id = id_vm_mashine_3  # переменная для применниение айди машины из настроек
        response = stop_vm(session, vm_id)  # запрос в сессию и офф вм
        bot.send_message(message.chat.id, text="OFF")

    elif (message.text == f"Status {id_vm_mashine_3}"):
        # time.sleep(3)
        session = authenticat()  # создаем сесию и логинимся там
        vm_id = id_vm_mashine_3  # переменная для применниение айди машины из настроек
        response = status_vm(session, vm_id)  # запрос в сессию и статус вм
        if response == "running":
            bot.send_message(message.chat.id, text="ON")
        elif response == "stopped":
            bot.send_message(message.chat.id, text="OFF")
        else:
            bot.send_message(message.chat.id, text="❗Error Запрос выдал :" + str(response))

    elif (message.text == "Меню Выбора VMs"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(f"{id_vm_mashine_1}")  # далаем кнопки
        btn2 = types.KeyboardButton(f"{id_vm_mashine_2}")
        back = types.KeyboardButton("Главное меню")
        btn3 = types.KeyboardButton(f"{id_vm_mashine_3}")
        markup.add(back, btn3, btn2, btn1)  # даем кнопки
        bot.send_message(message.chat.id, text="Вы вернулись в Меню Выбора VM")
        bot.send_message(message.chat.id, text="Выберете устройство:", reply_markup=markup)


    elif (message.text == "Главное меню"):  # кофиг кнопкок назад
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("👋")
        button2 = types.KeyboardButton("VMs")
        markup.add(button1, button2)  # конфиг кнопкок
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)  # даем мееню
    else:
        bot.send_message(message.chat.id, text="Unknown command") # 404

bot.polling(none_stop=True)
