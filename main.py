import random
from tkinter import *
import tkinter as tk
import threading
import RPi.GPIO as GPIO
# from pad4pi import rpi_gpio
import time
import library
import serial
import requests
# from fastapi import FastAPI, Request
# from flask import Flask, redirect, url_for, request
import math


def get_ser():
    try:
        return serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    except:
        return serial.Serial('/dev/ttyACM1', 9600, timeout=1)


lettertype = "Poppins"
backgroundColor = "#1B1B1E"
forgroundColor = "#FBFFFE"

root = Tk()
root.title("EXIT")
root.state("iconic")
# root.attributes('-fullscreen',True)

root.config(bg=backgroundColor)

win = Frame(root)
win.config(bg=backgroundColor)
win.pack(fill=BOTH, expand=True, padx=50, pady=50)

global objecten
objecten = []


def RFIDPage():
    global IBAN
    done = False
    IBAN = ""

    global objecten
    for obj in objecten:
        obj.destroy()

    titel = tk.Label(win, text="EXIT", font=(lettertype, 45, 'bold'))
    welkomLabel = tk.Label(win, text="welkom bij EXIT", font=(lettertype, 30))
    pasLabel = tk.Label(win, text="plaats uw pas op de kaartlezer")

    objecten = [titel, welkomLabel, pasLabel]

    for obj in objecten:
        obj.config(fg=forgroundColor, bg=backgroundColor)
        obj.pack()

    def scannen():
        global reading
        reading = True
        while reading:
            global IBAN
            IBAN = library.readCard()
            print(IBAN)
            if library.validateIban(IBAN):
                reading = False
                loginPage(IBAN)

    scanner = threading.Thread(target=scannen)
    scanner.start()


def loginPage(IBAN):
    global objecten
    for obj in objecten:
        obj.destroy()
    iban = IBAN
    print(iban)
    global balans
    balans = ""
    naam = ""
    snelPin = 70

    pinText = tk.Label(win, text="voer uw pincode in", font=(lettertype, 30))
    entryfield = tk.Label(win, text="", font=(lettertype, 40))
    melding = tk.Label(win, text="", font=(lettertype, 30))
    knopA = tk.Label(win, text="(A) Oke", font=(lettertype, 20), relief='sunken')
    knopB = tk.Label(win, text="(B) £" + str(snelPin) + ",- opnemen", font=(lettertype, 20), relief='sunken')
    knopC = tk.Label(win, text=("(C) " + "backspace"), font=(lettertype, 20), relief='sunken')
    knopD = tk.Label(win, text=("(D) " + "afbreken"), font=(lettertype, 20), relief='sunken')

    objecten = [pinText, melding, entryfield, knopA, knopB, knopC, knopD]

    for obj in objecten:
        obj.config(fg=forgroundColor, bg=backgroundColor)
        obj.pack()
    L1 = 6
    L2 = 13
    L3 = 26
    L4 = 19

    C1 = 12
    C2 = 16
    C3 = 20
    C4 = 21

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(L1, GPIO.OUT)
    GPIO.setup(L2, GPIO.OUT)
    GPIO.setup(L3, GPIO.OUT)
    GPIO.setup(L4, GPIO.OUT)

    GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def pinInvoer(IBAN):
        try:
            req = requests.get("http://145.24.222.173:8080/api/v1/fetch/iban/==/" + iban).json()
            # stat = req.status_code
            pin = req[0]["pin"]
            global naam
            naam = req[0]["first_name"]
            # balans = res["data"]["balance"]
            # strBalance = str(balance)
            return str(pin)
        except:
            print("something went horribly wrong")

    def balance(IBAN):
        iban = IBAN
        try:
            req = requests.get("http://145.24.222.173:8080/api/v1/fetch/iban/==/" + iban).json()
            # stat = req.status_code
            balans = req[0]["balance"]
            strBalance = str(balance)
            return int(balans)
        except:
            print("something went horribly wrong")

    def newBalance(iban, balance, bedrag):
        balans = balance
        bedr = bedrag
        global Iban
        Iban = iban
        object = {"name": "data",
                  "id": iban,
                  "body": {
                      "balance": (balans - bedr)
                  }
                  }

        requests.post("http://145.24.222.173:8080/api/v1/insert", json=object)

    def pogingCheck(iban):
        req = requests.get("http://145.24.222.173:8080/api/v1/fetch/iban/==/" + iban).json()
        poging = req[0]["attempts"]
        return poging

    def pogingUpdate(iban, poging):
        Iban = iban
        poging1 = poging
        object = {"name": "data",
                  "id": iban,
                  "body": {
                      "attempts": (poging1 + 1)
                  }
                  }
        requests.post("http://145.24.222.173:8080/api/v1/insert", json=object)

    def readLine(line, characters):
        GPIO.output(line, GPIO.HIGH)
        if (GPIO.input(C1) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[0]
        elif (GPIO.input(C2) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[1]
        elif (GPIO.input(C3) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[2]
        elif (GPIO.input(C4) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[3]
        else:
            GPIO.output(line, GPIO.LOW)
            return "-1"

    def checkKeypad():
        value = "-1"
        if (value == "-1"):
            value = readLine(L1, ["1", "2", "3", "A"])
        if (value == "-1"):
            value = readLine(L2, ["4", "5", "6", "B"])
        if (value == "-1"):
            value = readLine(L3, ["7", "8", "9", "C"])
        if (value == "-1"):
            value = readLine(L4, ["*", "0", "#", "D"])
        return value

    def slaOp():
        ser = get_ser()
        invoer = ""
        ster = ""
        status = True
        global pin
        pin = ""
        # print(iban)
        while status:
            if (checkKeypad() != "-1"):
                if (checkKeypad() == "A"):
                    # pin = balance(iban)
                    if pogingCheck(iban) < 3:
                        if invoer == pinInvoer(iban):
                            status = False
                            beginScherm(iban)
                        else:
                            melding.config(text="verkeerde pin, poging " + str(pogingCheck(iban) + 1)+ " van 3")
                            invoer = ""
                            ster = ""
                            entryfield.config(text=ster)
                            pogingUpdate(iban, pogingCheck(iban))
                            time.sleep(0.5)
                    else:
                        melding.config(text="pas geblokkeerd")
                        status = False
                        time.sleep(5)
                        RFIDPage()

                elif (checkKeypad() == "B"):
                    if invoer == pinInvoer(iban):
                        if pogingCheck(iban) < 3:
                            if balance(iban) < snelPin:
                                status = False
                                melding.config(text="onvoldoende balans")
                                time.sleep(5)
                                RFIDPage()
                            else:
                                status = False
                                try:
                                    newBalance(iban, balance(iban), snelPin)
                                    ser.write(b"!" + b"3" + b"\n")
                                    ser.write(b"%" + b"1" + b"\n")
                                    bonOptie(70, iban)
                                except:
                                    melding.config(text="fout")
                                    time.sleep(3)
                                    RFIDPage()
                        else:
                            status = False
                            melding.config(text="pas geblokkeerd")
                            time.sleep(5)
                            RFIDPage()
                    elif invoer == "":
                        melding.config(text="voer een pincode in")
                    else:
                        melding.config(text="verkeerde pin nog " + str(pogingCheck(iban)) + " pogingen")
                        pogingUpdate(iban, pogingCheck(iban))
                elif (checkKeypad() == "C"):
                    invoer = ""
                    ster = ""
                    entryfield.config(text=ster)
                elif (checkKeypad() == "D"):
                    status = False
                    RFIDPage()
                else:
                    if (checkKeypad() == "-1"):
                        pass
                    else:
                        invoer = invoer + checkKeypad()
                        ster = ster + "*"
                        entryfield.config(text=ster)
                        print(invoer)
                        time.sleep(0.5)

    login = threading.Thread(target=slaOp)
    login.start()


def beginScherm(iban):
    # naam = name
    global objecten
    for obj in objecten:
        obj.destroy()

    welcomeLabel = tk.Label(win, text="welcome " + naam, font=(lettertype, 30), relief='sunken')
    balanceLabel = tk.Label(win, text="(A) saldo bekijken", font=(lettertype, 30), relief='sunken')
    moneyLabel = tk.Label(win, text="(B) geld opnemen", font=(lettertype, 30), relief='sunken')
    knopD = tk.Label(win, text=("(D) " + "afbreken"), font=(lettertype, 30), relief='sunken')

    objecten = [welcomeLabel, balanceLabel, moneyLabel, knopD]

    for obj in objecten:
        obj.config(fg=forgroundColor, bg=backgroundColor)
        obj.pack()

    L1 = 6
    L2 = 13
    L3 = 26
    L4 = 19

    C1 = 12
    C2 = 16
    C3 = 20
    C4 = 21

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(L1, GPIO.OUT)
    GPIO.setup(L2, GPIO.OUT)
    GPIO.setup(L3, GPIO.OUT)
    GPIO.setup(L4, GPIO.OUT)

    GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def readLine(line, characters):
        GPIO.output(line, GPIO.HIGH)
        if (GPIO.input(C1) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[0]
        elif (GPIO.input(C2) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[1]
        elif (GPIO.input(C3) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[2]
        elif (GPIO.input(C4) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[3]
        else:
            GPIO.output(line, GPIO.LOW)
            return "-1"

    def checkKeypad():
        value = "-1"
        if (value == "-1"):
            value = readLine(L1, ["1", "2", "3", "A"])
        if (value == "-1"):
            value = readLine(L2, ["4", "5", "6", "B"])
        if (value == "-1"):
            value = readLine(L3, ["7", "8", "9", "C"])
        if (value == "-1"):
            value = readLine(L4, ["*", "0", "#", "D"])
        return value

    def buttons():
        status = True
        while status:
            time.sleep(0.5)
            if checkKeypad() != -1:
                if checkKeypad() == "A":
                    status = False
                    checkSaldo(iban)
                elif checkKeypad() == "B":
                    status = False
                    geldOpnemen(iban)
                elif checkKeypad() == "D":
                    status = False
                    RFIDPage()

    beginscherm = threading.Thread(target=buttons)
    beginscherm.start()


def checkSaldo(iban):
    global objecten
    for obj in objecten:
        obj.destroy()
    y = requests.get("http://145.24.222.173:8080/api/v1/fetch/iban/==/" + iban).json()
    global balance
    balance = y[0]["balance"]
    strBalance = str(balance)

    saldoLabel = tk.Label(win, text="saldo: " + strBalance, font=(lettertype, 30), relief='sunken')
    moneyLabel = tk.Label(win, text="(A) geld opnemen", font=(lettertype, 30), relief='sunken')
    knopD = tk.Label(win, text=("(D) " + "beginscherm"), font=(lettertype, 30), relief='sunken')

    objecten = [saldoLabel, moneyLabel, knopD]

    for obj in objecten:
        obj.config(fg=forgroundColor, bg=backgroundColor)
        obj.pack()

    L1 = 6
    L2 = 13
    L3 = 26
    L4 = 19

    C1 = 12
    C2 = 16
    C3 = 20
    C4 = 21

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(L1, GPIO.OUT)
    GPIO.setup(L2, GPIO.OUT)
    GPIO.setup(L3, GPIO.OUT)
    GPIO.setup(L4, GPIO.OUT)

    GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def readLine(line, characters):
        GPIO.output(line, GPIO.HIGH)
        if (GPIO.input(C1) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[0]
        elif (GPIO.input(C2) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[1]
        elif (GPIO.input(C3) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[2]
        elif (GPIO.input(C4) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[3]
        else:
            GPIO.output(line, GPIO.LOW)
            return "-1"

    def checkKeypad():
        value = "-1"
        if (value == "-1"):
            value = readLine(L1, ["1", "2", "3", "A"])
        if (value == "-1"):
            value = readLine(L2, ["4", "5", "6", "B"])
        if (value == "-1"):
            value = readLine(L3, ["7", "8", "9", "C"])
        if (value == "-1"):
            value = readLine(L4, ["*", "0", "#", "D"])
        return value

    def buttons():
        status = True
        while status:
            time.sleep(0.5)
            if checkKeypad() != -1:
                if checkKeypad() == "A":
                    status = False
                    geldOpnemen(iban)
                elif checkKeypad() == "D":
                    status = False
                    beginScherm(iban)

    checksaldo = threading.Thread(target=buttons())
    checksaldo.start()


def geldOpnemen(IBAN):
    global objecten
    for obj in objecten:
        obj.destroy()
    iban = IBAN
    y = requests.get("http://145.24.222.173:8080/api/v1/fetch/iban/==/" + iban).json()
    global balans
    balans = y[0]["balance"]
    message = tk.Label(win, text="", font=(lettertype, 30))
    vijfEuro = tk.Label(win, text="(A) £5,-", font=(lettertype, 20), relief='sunken')
    tienEuro = tk.Label(win, text="(B) £10,-", font=(lettertype, 20), relief='sunken')
    twintigEuro = tk.Label(win, text="(C) £20,-", font=(lettertype, 20), relief='sunken')
    anderBedragLabel = tk.Label(win, text="(#) ander bedrag", font=(lettertype, 20), relief='sunken')
    knopD = tk.Label(win, text=("(D) " + "terug"), font=(lettertype, 20), relief='sunken')

    objecten = [message, vijfEuro, tienEuro, twintigEuro, anderBedragLabel, knopD]

    for obj in objecten:
        obj.config(fg=forgroundColor, bg=backgroundColor)
        obj.pack()
    L1 = 6
    L2 = 13
    L3 = 26
    L4 = 19

    C1 = 12
    C2 = 16
    C3 = 20
    C4 = 21

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(L1, GPIO.OUT)
    GPIO.setup(L2, GPIO.OUT)
    GPIO.setup(L3, GPIO.OUT)
    GPIO.setup(L4, GPIO.OUT)

    GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def newBalance(iban, balance, bedrag):
        balans = balance
        bedr = bedrag
        global Iban
        Iban = iban
        object = {"name": "data",
                  "id": iban,
                  "body": {
                      "balance": (balans - bedr)
                  }
                  }

        requests.post("http://145.24.222.173:8080/api/v1/insert", json=object)

    def readLine(line, characters):
        GPIO.output(line, GPIO.HIGH)
        if (GPIO.input(C1) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[0]
        elif (GPIO.input(C2) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[1]
        elif (GPIO.input(C3) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[2]
        elif (GPIO.input(C4) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[3]
        else:
            GPIO.output(line, GPIO.LOW)
            return "-1"

    def checkKeypad():
        value = "-1"
        if (value == "-1"):
            value = readLine(L1, ["1", "2", "3", "A"])
        if (value == "-1"):
            value = readLine(L2, ["4", "5", "6", "B"])
        if (value == "-1"):
            value = readLine(L3, ["7", "8", "9", "C"])
        if (value == "-1"):
            value = readLine(L4, ["*", "0", "#", "D"])
        return value

    def buttons():
        ser = get_ser()
        status = True
        while status:
            time.sleep(1)
            if checkKeypad() != -1:
                if checkKeypad() == "A":
                    if balans >= 5:
                        status = False
                        ser.write(b"$" + b"1" + b"\n")
                        newBalance(iban, balans, 5)
                        bonOptie(5, iban)
                    else:
                        status = False
                        message.config(text="onvoldoende saldo")
                        print("te weinig saldo")
                        time.sleep(5)
                        RFIDPage()
                elif checkKeypad() == "B":
                    if balans >= 10:
                        status = False
                        ser.write(b"%" + b"1" + b"\n")
                        newBalance(iban, balans, 10)
                        bonOptie(10, iban)
                    else:
                        status = False
                        print("te weinig saldo")
                        message.config(text="onvoldoende saldo")
                        time.sleep(5)
                        RFIDPage()
                elif checkKeypad() == "C":
                    if balans >= 10:
                        status = False
                        ser.write(b"!" + b"1" + b"\n")
                        newBalance(iban, balans, 20)
                        bonOptie(20, iban)
                    else:
                        status = False
                        print("te weinig saldo")
                        message.config(text="onvoeldoende saldo")
                        time.sleep(5)
                        RFIDPage()
                elif checkKeypad() == "D":
                    status = False
                    beginScherm(iban)
                elif checkKeypad() == "#":
                    status = False
                    anderBedrag(balans, iban)

    geldopnemen = threading.Thread(target=buttons())
    geldopnemen.start()


def anderBedrag(balans, IBAN):
    global objecten
    for obj in objecten:
        obj.destroy()
    iban = IBAN
    global keuzeBedrag
    bedragLabel = tk.Label(win, text="voer het bedrag in: ", font=(lettertype, 20))
    keuzeBedrag = tk.Label(win, text="", font=(lettertype, 20))
    message = tk.Label(win, text="", font=(lettertype, 30))
    knopA = tk.Label(win, text="(A) oke", font=(lettertype, 20), relief='sunken')
    knopD = tk.Label(win, text=("(D) " + "beginscherm"), font=(lettertype, 20), relief='sunken')

    objecten = [bedragLabel, keuzeBedrag, knopA, knopD, message]

    for obj in objecten:
        obj.config(fg=forgroundColor, bg=backgroundColor)
        obj.pack()
    L1 = 6
    L2 = 13
    L3 = 26
    L4 = 19

    C1 = 12
    C2 = 16
    C3 = 20
    C4 = 21

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(L1, GPIO.OUT)
    GPIO.setup(L2, GPIO.OUT)
    GPIO.setup(L3, GPIO.OUT)
    GPIO.setup(L4, GPIO.OUT)

    GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def readLine(line, characters):
        GPIO.output(line, GPIO.HIGH)
        if (GPIO.input(C1) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[0]
        elif (GPIO.input(C2) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[1]
        elif (GPIO.input(C3) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[2]
        elif (GPIO.input(C4) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[3]
        else:
            GPIO.output(line, GPIO.LOW)
            return "-1"

    def checkKeypad():
        value = "-1"
        if (value == "-1"):
            value = readLine(L1, ["1", "2", "3", "A"])
        if (value == "-1"):
            value = readLine(L2, ["4", "5", "6", "B"])
        if (value == "-1"):
            value = readLine(L3, ["7", "8", "9", "C"])
        if (value == "-1"):
            value = readLine(L4, ["*", "0", "#", "D"])
        return value

    def buttons():
        status = True
        invoer = ""
        while status:
            time.sleep(0.5)
            if checkKeypad() != -1:
                if checkKeypad() == "A":
                    if balans >= int(invoer):
                        status = False
                        biljetKeuze(invoer, iban, balans)
                    else:
                        message.config(text="onvoldoende saldo")
                        status = False
                        time.sleep(5)
                        RFIDPage()
                elif checkKeypad() == "#":
                    pass
                elif checkKeypad() == "*":
                    pass
                elif checkKeypad() == "B":
                    pass
                elif checkKeypad() == "C":
                    pass
                elif checkKeypad() == "D":
                    status = False
                    beginScherm(iban)
                else:
                    if checkKeypad() == "-1":
                        pass
                    else:
                        invoer = invoer + checkKeypad()
                        keuzeBedrag.config(text=invoer)
                        time.sleep(0.5)

    anderbedrag = threading.Thread(target=buttons)
    anderbedrag.start()


def biljetKeuze(invoer, IBAN, balance):
    global objecten
    for obj in objecten:
        obj.destroy()
    global iban
    iban = IBAN
    global balans
    balans = balance
    bedragKeuze = invoer

    def knopA(a, b, c):
        global knopa5
        global knopa10
        global knopa20
        knopa5 = c
        knopa10 = b
        knopa20 = a

    def knopB(a, b, c):
        global knopb5
        global knopb10
        global knopb20
        knopb5 = c
        knopb10 = b
        knopb20 = a

    def knopC(a, b, c):
        global knopc5
        global knopc10
        global knopc20
        knopc5 = c
        knopc10 = b
        knopc20 = a

    def round_to_nearest_5(amount):
        return math.floor(amount / 5) * 5

    def calculate_cash(amount):
        cash_options = [20, 10, 5]
        cash_combinations = []

        rounded_amount = round_to_nearest_5(amount)

        for i in range(math.floor(rounded_amount / cash_options[0]) + 1):
            for j in range(math.floor((rounded_amount - i * cash_options[0]) / cash_options[1]) + 1):
                remaining_amount = rounded_amount - i * cash_options[0] - j * cash_options[1]
                if remaining_amount % cash_options[2] == 0:
                    k = remaining_amount // cash_options[2]
                    cash_combinations.append((i, j, k))

        # Sort combinations by the total number of bills used
        cash_combinations.sort(key=lambda x: sum(x))

        # Return the top 3 viable options, if available
        return cash_combinations[:3]

    amount = int(bedragKeuze)
    cash_combinations = calculate_cash(amount)

    if len(cash_combinations) == 0:
        print("No valid combinations of cash.")
    else:
        if len(cash_combinations) < 3:
            cash_combinations += [(0, 0, 0)] * (3 - len(cash_combinations))
        combination1, combination2, combination3 = cash_combinations[:3]

        cashOption1_20, cashOption1_10, cashOption1_5 = combination1
        cashOption2_20, cashOption2_10, cashOption2_5 = combination2
        cashOption3_20, cashOption3_10, cashOption3_5 = combination3

        knopA(cashOption1_20, cashOption1_10, cashOption1_5)
        knopB(cashOption2_20, cashOption2_10, cashOption2_5)
        knopC(cashOption3_20, cashOption3_10, cashOption3_5)
        global knopa5
        global knopa10
        global knopa20
        global knopb5
        global knopb10
        global knopb20
        global knopc5
        global knopc10
        global knopc20

    biljetVijf = tk.Label(win,
                          text="(A) " + str(knopa20) + " x €20, " + str(knopa10) + "x €10, " + str(knopa5) + "x €5",
                          font=(lettertype, 30), relief='sunken')
    biljetTien = tk.Label(win,
                          text="(B) " + str(knopb20) + " x €20, " + str(knopb10) + "x €10, " + str(knopb5) + "x €5",
                          font=(lettertype, 30), relief='sunken')
    biljetTwintig = tk.Label(win,
                             text="(C) " + str(knopc20) + " x €20, " + str(knopc10) + "x €10, " + str(knopc5) + "x €5",
                             font=(lettertype, 30), relief='sunken')
    knopD = tk.Label(win, text=("(D) " + "beginscherm"), font=(lettertype, 30), relief='sunken')

    objecten = [biljetVijf, biljetTien, biljetTwintig, knopD]

    for obj in objecten:
        obj.config(fg=forgroundColor, bg=backgroundColor)
        obj.pack()

    L1 = 6
    L2 = 13
    L3 = 26
    L4 = 19

    C1 = 12
    C2 = 16
    C3 = 20
    C4 = 21

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(L1, GPIO.OUT)
    GPIO.setup(L2, GPIO.OUT)
    GPIO.setup(L3, GPIO.OUT)
    GPIO.setup(L4, GPIO.OUT)

    GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def newBalance(iban, balance, bedrag):
        # balans = int(balance)
        bedr = int(bedrag)
        object = {"name": "data",
                  "id": iban,
                  "body": {
                      "balance": (int(balance) - int(bedr))
                  }
                  }

        requests.post("http://145.24.222.173:8080/api/v1/insert", json=object)

    def readLine(line, characters):
        GPIO.output(line, GPIO.HIGH)
        if (GPIO.input(C1) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[0]
        elif (GPIO.input(C2) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[1]
        elif (GPIO.input(C3) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[2]
        elif (GPIO.input(C4) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[3]
        else:
            GPIO.output(line, GPIO.LOW)
            return "-1"

    def checkKeypad():
        value = "-1"
        if (value == "-1"):
            value = readLine(L1, ["1", "2", "3", "A"])
        if (value == "-1"):
            value = readLine(L2, ["4", "5", "6", "B"])
        if (value == "-1"):
            value = readLine(L3, ["7", "8", "9", "C"])
        if (value == "-1"):
            value = readLine(L4, ["*", "0", "#", "D"])
        return value

    def buttons():
        status = True
        ser = get_ser()
        ser.reset_input_buffer()
        while status:
            time.sleep(1)
            if checkKeypad() != -1:
                if checkKeypad() == "A":
                    status = False
                    # print(times5 + " x 5")
                    new = str.encode(str(knopa5))
                    new1 = str.encode(str(knopa10))
                    new2 = str.encode(str(knopa20))
                    ser.write(b"$" + new + b"\n")
                    ser.write(b"%" + new1 + b"\n")
                    ser.write(b"!" + new2 + b"\n")
                    newBalance(iban, balans, invoer)
                    newi = str.encode(iban)
                    inv = str.encode(invoer)
                    ser.write(b"&" + newi + inv + b"\n")
                    bonOptie(invoer, iban)
                elif checkKeypad() == "B":
                    status = False
                    # print(times10 + " x 10")
                    new = str.encode(str(knopb5))
                    new1 = str.encode(str(knopb10))
                    new2 = str.encode(str(knopb20))
                    ser.write(b"$" + new + b"\n")
                    ser.write(b"%" + new1 + b"\n")
                    ser.write(b"!" + new2 + b"\n")
                    newBalance(iban, balans, invoer)
                    newi = str.encode(iban)
                    inv = str.encode(invoer)
                    ser.write(b"&" + newi + inv + b"\n")
                    bonOptie(invoer, iban)
                elif checkKeypad() == "C":
                    status = False
                    # print(times20 + " x 20")
                    # new = str.encode(times20)
                    new = str.encode(str(knopb5))
                    new1 = str.encode(str(knopb10))
                    new2 = str.encode(str(knopb20))
                    ser.write(b"$" + new + b"\n")
                    ser.write(b"%" + new1 + b"\n")
                    ser.write(b"!" + new2 + b"\n")
                    newBalance(iban, balans, invoer)
                    bonOptie(invoer, iban)
                elif checkKeypad() == "D":
                    status = False
                    beginScherm(iban)

    biljetkeuze = threading.Thread(target=buttons())
    biljetkeuze.start()


def succesScreen():
    global objecten
    for obj in objecten:
        obj.destroy()

    succesLabel = tk.Label(win, text="transactie wordt verwerkt...", font=(lettertype, 30))
    wachtLabel = tk.Label(win, text="even geduld a.u.b")

    objecten = [succesLabel, wachtLabel]

    for obj in objecten:
        obj.config(fg=forgroundColor, bg=backgroundColor)
        obj.pack()

    def goto():
        time.sleep(random.randint(5, 8))
        RFIDPage()

    next = threading.Thread(target=goto)
    next.start()


def bonOptie(bedrag, iban):
    amount = bedrag
    i = iban
    global objecten
    for obj in objecten:
        obj.destroy()

    vraagLabel = tk.Label(win, text="wilt u de bon?", font=(lettertype, 30), relief='sunken')
    jaLabel = tk.Label(win, text="(A) ja", font=(lettertype, 30), relief='sunken')
    neeLabel = tk.Label(win, text="(B) nee", font=(lettertype, 30), relief='sunken')

    objecten = [vraagLabel, jaLabel, neeLabel]

    for obj in objecten:
        obj.config(fg=forgroundColor, bg=backgroundColor)
        obj.pack()

    L1 = 6
    L2 = 13
    L3 = 26
    L4 = 19

    C1 = 12
    C2 = 16
    C3 = 20
    C4 = 21

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(L1, GPIO.OUT)
    GPIO.setup(L2, GPIO.OUT)
    GPIO.setup(L3, GPIO.OUT)
    GPIO.setup(L4, GPIO.OUT)

    GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def readLine(line, characters):
        GPIO.output(line, GPIO.HIGH)
        if (GPIO.input(C1) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[0]
        elif (GPIO.input(C2) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[1]
        elif (GPIO.input(C3) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[2]
        elif (GPIO.input(C4) == 1):
            GPIO.output(line, GPIO.LOW)
            return characters[3]
        else:
            GPIO.output(line, GPIO.LOW)
            return "-1"

    def checkKeypad():
        value = "-1"
        if (value == "-1"):
            value = readLine(L1, ["1", "2", "3", "A"])
        if (value == "-1"):
            value = readLine(L2, ["4", "5", "6", "B"])
        if (value == "-1"):
            value = readLine(L3, ["7", "8", "9", "C"])
        if (value == "-1"):
            value = readLine(L4, ["*", "0", "#", "D"])
        return value

    def buttons():
        status = True
        ser = get_ser()
        ser.reset_input_buffer()
        while status:
            time.sleep(0.5)
            if checkKeypad() != -1:
                if checkKeypad() == "A":
                    status = False
                    newi = str.encode(i)
                    inv = str.encode(str(amount))
                    ser.write(b"&" + newi + inv + b"\n")
                    succesScreen()
                elif checkKeypad() == "B":
                    status = False
                    succesScreen()

    next = threading.Thread(target=buttons)
    next.start()


def scherm():
    RFIDPage()


scherm = threading.Thread(target=scherm)
scherm.start()

root.mainloop()
