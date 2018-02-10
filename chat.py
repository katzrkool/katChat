import socket
from threading import Thread, Lock
import os
import time


def getIp():
    ifconfig = os.popen(
        "ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'").read()
    ip = ifconfig.split("\n")[0]
    return ip


global ip
try:
    ip = getIp()
except:
    ip = False


def init():
    global ip
    if ip is not False:
        print("Hi! Welcome to KatChat. Your secret number is {}\n".format(ip))
    else:
        ip = input("Hi! Welcome to KatChat. We couldn't determine your secret number :(.Please enter your local ip.\n")
    choice = input(
        "If you would like to connect to someone else, type c,\nIf you would like to wait for a connection, press w.\t")
    while choice is not "c" and choice is not "w":
        choice = input("Invalid selection, please try again.\t")
    if choice is "c":
        try:
            connect()
        except Exception as e:
            print(e)
            if input("Sorry, connection failed. Would you like to wait for a connection? (y/n)") is "y":
                wait()
            else:
                exit(0)
    else:
        wait()


def isInt(i):
    try:
        int(i)
        return True
    except:
        return False


def validIp(ip):
    if ip.count(".") is not 3:
        return False
    ipParts = ip.split(".")
    for i in ipParts:
        if not isInt(i):
            return False
        if int(i) > 255 or int(i) < 0:
            return False
    return True


def connect():
    global secretNumber
    secretNumber = input("Please enter the secret number you would like to connect to.\t")
    while not validIp(secretNumber):
        secretNumber = input("Sorry, invalid number, please try again.\t")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, 16891))
    s.listen(5)
    Thread(target=listen, args=(s, False)).start()
    Thread(target=send).start()


def listen(s, accept):
    if accept is False:
        c, addr = s.accept()
    else:
        c = accept
    while True:
        print(c.recv(1024).decode())


def send():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, 16892))
    s.connect((secretNumber, 16891))
    while True:
        msg = input("")
        if msg is "exit()":
            exit(0)
        else:
            try:
                s.send(str.encode(msg))
            except BrokenPipeError:
                s.connect((secretNumber, 16891))
                s.send(str.encode(msg))


def wait():
    global secretNumber
    secretNumber = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, 16891))
    s.listen(5)

    c, addr = s.accept()
    print("Got connection from ", addr)
    secretNumber = addr[0]

    Thread(target=listen, args=(s, c)).start()
    while secretNumber is 0:
        time.sleep(0.5)
    Thread(target=send).start()


init()
'''
global s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((ip, 16891))
'''
