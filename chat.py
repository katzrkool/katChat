import socket
from threading import Thread
import os
import time
import argparse
import sys

global close
close = False

parser = argparse.ArgumentParser()
parser.add_argument("-m", type=str, default=False, help="Manually override auto ip finding")
args = parser.parse_args()

def getIp():
    try:
        ifconfig = os.popen(
            "ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'").read()
        return ifconfig.split("\n")[0]
    except OSError:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if str(ip).startswith("127."):
            return False
        return ip

global ip
if args.m is False:
    ip = getIp()
else:
    ip = args.m

def init():
    global ip
    global close
    if ip is not False:
        print("Hi! Welcome to KatChat. Your secret number is {}".format(ip))
    else:
        ip = input("Hi! Welcome to KatChat. We couldn't determine your secret number :(.Please enter your local ip.")

    print("If your secret number doesn't work, find your local ip, and submit it manually with the -m flag\nEx: -m 192.168.0.2\n")
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
                close = True
                sys.exit(0)
    else:
        wait()


def isInt(i):
    try:
        int(i)
        return True
    except ValueError:
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
    global close
    if accept is False:
        c, addr = s.accept()
    else:
        c = accept
    while close is False:
        msg = c.recv(1024).decode()
        if msg == "Disconnect from Chat. #$52j":
            s.close()
            print("Disconnected from chat")
            close = True
            sys.exit(1)
        else:
            print(msg)


def send():
    global close
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, 16892))
    s.connect((secretNumber, 16891))
    while close is False:
        msg = input("")
        if msg == "exit()":
            try:
                s.send(str.encode("Disconnect from Chat. #$52j"))
            except BrokenPipeError:
                s.connect((secretNumber, 16891))
                s.send(str.encode("Disconnect from Chat. #$52j"))
            finally:
                s.close()
                close = True
                sys.exit(1)
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
