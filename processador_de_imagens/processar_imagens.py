import cv2
import base64
import json
import pickle
import os
import threading
import requests
import time
import psutil
from filaimagens import imagens as filaimagens
from filaimagens import imagensfaasd as imagensfaasd
from datetime import datetime

def mover(imgpath):
    global path                       #Mudar para local de seu diretório de imagens processadas   
    comando = "mv " + imgpath + " " + path + "/imagens_processadas"  # Move a imagem para o diretório de imagens
    # processadas
    os.system(comando)
    f = open("log.txt", "a")
    f.write(f"moveu {imgpath}\n") #Escreve no log a imagem que foi movida
    f.close()


def faasd(json_data):
    date_time=str(datetime.now())
    global openfaas_url
    with open("log.txt", "a") as log_file:
        while True:
            try:
                # Envia a requisição POST, com a string da imagem em formato JSON para processamento
                response = requests.post(openfaas_url, data=json_data, timeout=20)
                # Verifica o status da resposta
                if response.status_code == 200:
                    log_file.write(f"requisição openfaas feita em {date_time}\n")
                    log_file.flush()  # Força a gravação imediata
                    return int(response.text)  # Retorna a resposta em caso de sucesso
                else:
                    log_file.write(f"erro: {response.status_code}\n")
                    log_file.flush()
                    return None  # Retorna a resposta mesmo com erro
            except requests.RequestException as e:
                # Trata exceções de requisição
                log_file.write(f"erro de conexão: {str(e)}, tentando novamente...\n")
                log_file.flush()  
                openfaas_url = atualizar_url()


def combine_to_json(imstr):
    #Transforma a string da imagem em json
    combined_dict = {
        "image_data": imstr
    }
    json_data = json.dumps(combined_dict)
    return json_data


def img2json(imgpath):
    # Carrega a imagem
    print(imgpath)
    img = cv2.imread(imgpath)
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Serializa a imagem usando pickle
    except cv2.error as e:
        return None
    imdata = pickle.dumps(gray)

    # Codifica em Base64 e converte para string
    imstr = {"image": base64.b64encode(imdata).decode('ascii')}
    return imstr


def adicionar_a_fila():
    global path
    while True:
        files = os.listdir(path)
        for file in files:
            filepath = (path + '/' + file) #Imagem com path
            if filepath.endswith(".jpg") and filepath not in filaimagens:
                sem.acquire() #Semaforo para a fila não ser alterada enquanto uma imagem é processada
                filaimagens.append(filepath)
                sem.release()


def processar_imagem():
    global cpu_usage
    while True:
        if filaimagens:
            sem.acquire() #Para não termos imagens novas enquanto uma imagem é processada
            imgpath = filaimagens[0]
            if cpu_usage < 70: #Caso o uso de cpu seja menor que 70%, processamos localmente 
               dado = face_detect(imgpath)
            else:
               dado = usar_faasd(imgpath) #caso contrario, utilizamos FaasD
            mover(imgpath)
            del filaimagens[0]
            sem.release()
#            if dado != None:
#                atualizar_thingspeak(dado)


def atualizar_url():
    f = open("/var/lib/motion/IC_processador-de-imagens/IP_raspberry/IP_raspberry.txt","r")
    IP_raspberry = f.readline() #Le a linha contendo o IP da raspberry pi
    while IP_raspberry == "":
        IP_raspberry = f.readline()
    IP_raspberry = IP_raspberry.strip() #Remove espaços no fim e começo da linha
    IP_raspberry = IP_raspberry + ":8080" #Adiciona a porta 8080 para a URL
    openfaas_url = "http://"+IP_raspberry+"/function/face-detect-thing" #Completa a URL
    f.close()
    return openfaas_url

def monitor():
    #Thread para monitorar o uso médio de CPU do sistema
    global cpu_usage

    while True:
        # Calcula o uso de CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        time.sleep(1)


def face_detect(img_path):
    #Função para processamento local de imagem
    global path_haarcascade
    #Cv2 lê a imagem
    img = cv2.imread(img_path)
    try:
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    except cv2.error as e:
        return None
    #Efetua a detecção utilizando o haarcascade frontalface default
    face_cascade = cv2.CascadeClassifier(path_haarcascade)
    faces = face_cascade.detectMultiScale(gray,1.1,3)
    #Retorna o numero de faces
    dado = len(faces)
    return dado


def usar_faasd(imgpath):
    #Função para utilizar o faasd
    #Transforma a imagem em string
    imstr = img2json(imgpath)
    if imstr != None:
        #Adiciona a string ao JSON
        json_data = combine_to_json(imstr)
        #Envia o JSON para o faasd 
        dado = faasd(json_data)
        return dado
    else:
        return None

#def atualizar_thingspeak(dado):
#    #Função utilizada para atualizar o thingspeak 
#    dado = str(dado)
    #Utiliza a API
#    thingspeak_post="https://api.thingspeak.com/update?api_key=<Chave API>" + dado
#    response = requests.post(thingspeak_post)
    #Caso a seção de texto da resposta seja igual a 0, houve algum problema e o thingspeak não foi atualizado
#    with open("log.txt", "a") as log_file:
#        if response.text != 0:
#            log_file.write("thingspeak atualizado com sucesso\n")
#            log_file.flush() 
#        else:
#            log_file.write(f"thingspeak: erro: {response.status_code}\n")
#            log_file.flush() 
#    time.sleep(60)



cpu_usage = 0 #Inicializa variável de uso de CPU
openfaas_url = atualizar_url() #Inicializa URL do openfaas
path = "/var/lib/motion" #Local onde as imagens estão salvas
path_haarcascade = path + "/IC_processador-de-imagens/haarcascade.xml" #Local onde o Haarcascade está salvo
sem = threading.Semaphore()
sem1 = threading.Semaphore()
t0 = threading.Thread(target=adicionar_a_fila)
t1 = threading.Thread(target=processar_imagem)
t2 = threading.Thread(target=monitor)
t2.start()
t0.start()
t1.start()
