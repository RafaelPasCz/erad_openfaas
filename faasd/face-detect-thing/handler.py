import cv2
import requests
import pickle
import json
import base64
def handle(req):

    
    data = json.loads(req)# Carregar o JSON

    # Recuperar a imagem codificada 
    img_data = base64.b64decode(data["image_data"]["image"])
    img = pickle.loads(img_data) #transforma imagem num array numpy

    face_cascade = cv2.CascadeClassifier('/home/app/function/haarcascade_frontalface_default.xml') #carrega haarcascade
    i = 0
    faces = face_cascade.detectMultiScale(img,1.1,3) #efetua a detecção
    for face in faces:
        i = i+1
    dado = str(i)
    return dado

