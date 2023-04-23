from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage
from operator import truediv
from pickle import TRUE
import ssl #potrzebne do wyslania maila
import smtplib #serwer smtp do wyslania maila
import requests #odpalanie strony internetowej
from bs4 import BeautifulSoup #webscrapping
from pathlib import Path #sciezka
from datetime import datetime #data
import http.client as httplib #ustawienie limitu requestow?
import urllib.request #otwirzenie obrazu z linku
import time #czas

httplib._MAXHEADERS = 1000 #ustawienie limitu
 
with open('Pasy.txt','r') as f:
    lines=f.readlines()
    email_sender = lines[0].split('Login=')[1] #nadawca maila
    email_password = lines[1].split('Haslo=')[1] #haslo do maila stworzone dla pythona

with open('odbiorcy.txt','r') as f:
    email_receivers=f.read().splitlines() #adresaci

with open('Urls.txt','r') as f:
    Urls=f.read().splitlines() #adresaci

def read_txt(): #funkcja do odczytu pliku z przegladnietymi juz autami
    if not Path("widziane.txt").is_file(): #sprawdzanie czy plik istnieje
        f=open("widziane.txt","x")
        print("creating new file")
    
    with open("widziane.txt", "r") as f:
        widziane = f.read().splitlines()
    
    return widziane


def Car_spec(link): #funkcja do znalezienia podstawowych informacji o aucie (marka, model, cena, rok produkcji i zdjecie)
    page=requests.get(link) #otworzenie strony 
    soup=BeautifulSoup(page.content, "html.parser") #kod zrodlowy strony
    
    img = soup.find('div',class_="photo-item")
    src=img.find('img').get("data-lazy").split(";")[0] #zdjecie
    
    price=soup.find('div',"offer-price").get("data-price")+" PLN" #cena 
    
    params=soup.find('ul', class_="offer-params__list")
    marka, model,rok="","",""
    for el in params.find_all('li'): #lista podstawowych parametrow na stronie 
        if el.find('span') is not None:
            if el.find('span').get_text()=="Marka pojazdu":
                marka=el.find('a').get_text().strip() #marka pojazdu
            
            if el.find('span').get_text()=="Model pojazdu":
                model=el.find('a').get_text().strip() #model pojazdu

            if el.find('span').get_text()=="Rok produkcji":
                rok=el.find('div').get_text().strip() #rok produkcji
    print(marka)
    print(model)
    print(price)
    
    return [marka, model, rok, price, src]


def Sendemail(cars): #funkcja do wyslania maila
    for email_receiver in email_receivers:
        em = MIMEMultipart() #tworzenie pustej wiadomosci
        em['From'] = email_sender #nadawca
        em["To"] = email_receiver #odbiorca
        em['Subject'] = 'Otomoto' #tytul wiadomosci
        if cars: #sprawdzanie czy lista nie jest pusta zeby nie wysylac pustego maila
            for car in cars:
                body=car[5]+"\n"+car[0]+" "+car[1]+"\n"+car[3]+"\n"+car[2] #tworzenie tresci maila
                with urllib.request.urlopen(car[4]) as url: #otworzenie zdjecie z linku
                    image_data = url.read()
                img = MIMEImage(image_data,"png") 

                em.attach(MIMEText(body)) #dolaczenie tresci
                em.attach(img) #dolaczenie zdjecia

            context = ssl.create_default_context() #kontekst ssl z domyslnymi ustawieniami ssl dla bezpiecznego polaczenia

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp: #otworzenie serwera smtp
                smtp.login(email_sender,email_password) #zalogowanie sie na maila
                smtp.sendmail(email_sender, email_receiver, em.as_string()) #wyslanie wiadomosci
    

def Func_otomoto(message=True):
    for url in Urls:
        page=requests.get(url) #otworzenie strony internetowej
        soup = BeautifulSoup(page.content, "html.parser") #kod zrodlowy

        widziane=read_txt()

        cars=[]

        for el in soup.find_all('article',class_="ooa-1rudse5 eayvfn60"): #przegladanie kazdego ogloszenia
            link=el.find('a').get('href') #link do ogloszenia
            txt=link.split('/')[-1]

            if txt not in widziane: #sprawdzanie czy to nowe ogloszenie
                print(link)
                car=Car_spec(link)
                car.append(link)
                cars.append(car) 

                with open('widziane.txt', 'a') as f: #dopisywanie ogloszenia do juz przegladnietych
                    f.write(txt + '\n')
        if message:
            Sendemail(cars)


while(True): #petla zeby program dzialal caly czas do momentu recznego wylaczenia go
    now = datetime.now()
    current_time = now.strftime("%H:%M") #wyswietlanie godziny zeby widziec ze program dziala
    print(current_time)

    try:
        Func_otomoto(True) #uruchamianie funkci w try, zeby na wypadek np braku sieci program sie nie wylaczyl
    except Exception as e:
        print(e)
    
    time.sleep(60) #minuta odstepu miedzy kazdym wywolaniem funkcji co by serwerow nie spalic

