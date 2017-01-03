#python 2.7

#Modulos que se necesitan importar en los scripts principales
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
import numpy as np
import subprocess
from datetime import datetime,timedelta
import pickle
import os
import time

#Definiciones de los pines
GPIO.setup("P9_14", GPIO.IN)
GPIO.add_event_detect("P9_14", GPIO.FALLING)
 
#El ADC se establece en el script principal

def f_pickle(funcion,archivo,objeto):
   #funcion puede ser un string: abrir o guardar
   #Esta funcion guarda o retornas objetos en formato pickle
   #El archivo preferiblemente debe ser el path completo sin escribir
   #pickle como extension, no el local
   if funcion == "abrir":
     with open("{}.pickle".format(archivo),'rb') as fl: 
         return pickle.load(fl)        
   elif funcion == "guardar":
     with open("{}.pickle".format(archivo),'wb') as fl: pickle.dump(objeto,fl)
   else: print "Error en la funcion para {0} el archivo pickle {1}".format(
                funcion,archivo)    
     
def dicc_veleta():
   #creando el diccionario con los datos para las direcciones de la veleta
   dir_veleta = "/root/scripts/pruebas/calibraciones/veleta/calibraciones_veleta.txt" #archivo con las calibraciones
   lista = []  #contenedor para formar el diccionario

   with open(dir_veleta,"r") as f:
       try:
          for line in f:
             line = line.split(",")
             line = (float(line[1]),line[0])    #(key,item)
             lista.append(line)
       except ValueError, IOError: 
             print "Revisar archivo de calibracion, se ha detectado un problema"
             return 1

   return dict(lista)

def median_filter(lista):
   #from numpy import array, median
   lista = np.array(lista)
   return np.median(lista)

def veleta(volt,direccion):
  #Esta funcion retorna la direccion que se mide en el pin indicado
  #Se utiliza para calibrar la veleta,se especifica la direccion como un string
  dir = "/root/scripts/pruebas/calibraciones/veleta/{}".format(direccion)
  R = [23000,10009]                        #Agregar valores de la resistencias
  vel = (R[0]/R[1] + 1)*volt
  f = open(dir,"a")
  f.write(str(vel)+"\n")
  f.close()
  return vel

def direccion_del_viento(dicc,pin):
   '''Esta funcion busca en el direccionario de direcciones cual 
      direccion es la mas probable'''
   #Obteniendo el voltaje en la veleta
      
   R = [23000,10009]                 #Agregar valores de la resistencias
   volt = []
   for i in range(100):  
      vol = 1.8*ADC.read(pin)
      volt.append(vol)
   volt = median_filter(volt) 
   volt = (R[0]/R[1] + 1)*volt

   keys = []
   dif  = []
   #buscando la direccion
   for i in dicc.keys():
      if round(volt,3) == i: return dicc[i]
      keys.append(i)
      dif.append(abs(i-round(volt,3)))
   #sino funciona la busqueda de la direccion
   min_value = dif.index(min(dif))
   key = keys[min_value]
   return dicc[key]
   
def Alarma_Visual(sensores):
   '''Esta funcion controla el encendido de los leds''' 
   #Parametros:sensores es una lista con los sensores
   #from datetime import datetime,timedelta
   #import pickle
   #import os
   time = datetime.now()
   Intv = timedelta(minutes=30)
   path ="/root/scripts//old_time.pickle" #direccion al archivo de tiempo
   #with open("time.pickle",'wb') as fl: pickle.dump(time,fl)
   f_pickle("guardar","time", time)
   for i in sensores:
      if i == "veleta": pass
      elif i == "i2c":  pass
      elif i == "gases": pass
      elif i == "digitales":pass
      elif i == "tiempo":
          if os.path.isfile(path): 
            #with open("time.pickle",'wb') as fl
            t = f_pickle("abrir",path,time)
               #continuar con las funciones para comparacion de tiempo
   f_pickle("guardar","old_time", time)            
   #with open("old_time.pickle",'wb') as fl: pickle.dump(time,fl)
        
def salvar_datos(archivos_datos):
   #Guarda los datos, se le pasan los archivos en una lista, de forma
   #tal que una tupla sea de la siguiente forma: (dato,archivo)
   #dato es una lista con los archivos con lo que se quiera pasar
   f = open(archivos_datos[1],'a')
   c = 0
   for i in archivos_datos[0]:      
      c+=1 
      if c == len(archivos_datos[0]): f.write(str(i)+"\n")
      elif c < len(archivos_datos[0]): f.write(str(i)+",")
   f.close()
 
def promedio(datos,cifras_decimales):
   #Retorna el promedio de los datos (lista),cifras_decimales es un int
   #que indica la cantidad de cifras decimales
   return round(sum(datos)/len(datos),cifras_decimales)

def ultravioleta(cifras):
   #Retorna el valor medido por el sensor ultravioleta
   #Necesita el ADC y GPIO.setup("P8_10", GPIO.OUT)
   #cifras indica la cantidad de cifras decimales con que se retorna el valor
   #import Adafruit_BBIO.GPIO as GPIO
   #import Adafruit_BBIO.ADC as ADC
   #import time

   GPIO.output("P8_10", GPIO.HIGH)
   time.sleep(0.1)
   ultra = 1.8*ADC.read("P9_36")
   R = [10016,22000]
   ultra = (R[0]/R[1] + 1)*ultra
   ultra = 8.51*ultra - 8.81   #funcion para estimar la Intensidad mW/cm2
   GPIO.output("P8_10", GPIO.LOW)
   time.sleep(0.1)
   return round(ultra,cifras)

def init_presion():
  #funcion para iniciar el sensor de presion
  dir = "/root/scripts/presion_init/presion_init.sh"  #script de Inicio
  try: x = subprocess.check_output(["sh",dir],shell=False)
  except subprocess.CalledProcessError: x = 1      
  return x

def presion_temp(variable):
  #Retorna la presion y la temperatura medidas por el bmp180,
  #Parametros pressure para la presion y temp para temperatura
  pres = subprocess.check_output("cat /sys/class/i2c-adapter/i2c-1/1-0077/{}0_input".format(variable),shell=True)
  pres = float(pres.rstrip("\n"))
  return pres

def check_alarma(actual,alarma):
   #Esta funcion se encarga de verificar sino hay error en los sensores
   #El 0, indica una mala medida, el 1 una buena
   #Parametros actual=valor actual de la variable,
   #alarma = lugar en donde se guarda el archivo pickle 
   x = ""
   archivo = "/root/datos/alarma/{}".format(alarma)
   if (actual == 0) or (actual == x): #mala lectura
     f_pickle("guardar",archivo,0)
     return -1
   if actual != 0 and actual != x : #buena lectura
     f_pickle("guardar",archivo,1)
     return actual

def prom_array(array,fecha):
   #Parametros array = array de cualquier dimension, fecha = string 
   #import numpy as np
   #retorna una lista con los datos, la hora a la que fueron tomados
   #el promedio se retorna en orden segun las columnas del array
   x = np.mean(array,axis=0)
   lista = [round(i,1) for i in x]
   lista.append(fecha)
   return lista

def Anemometro(tiempo,muestreo,pin):
   #Funcion para medir la velocidad del anemometro
   #Como parametro toma el tiempo que toma las muestras y el tiempo
   #entre cada muestra
   hora = datetime.now()   
   int =  timedelta(seconds=tiempo)
   fin = hora + int
   c  = 0
   while hora <= fin:
        if GPIO.event_detected(pin):c+=1
        hora = datetime.now()
        time.sleep(muestreo)
   if c == 0: return 0
   elif c is None: return -1
   elif c > 0:
       c = c/tiempo 
       return c*2.4

def gas(tiempo,muestreo,pin):
   hora = datetime.now()
   int =  timedelta(seconds=tiempo)
   fin = hora + int
   c = []
   while hora <= fin:       
        volt = 1.8*ADC.read(pin)
        c.append(volt) 
        hora = datetime.now()
        time.sleep(muestreo)
   return round(sum(c)/len(c),3)
   
if __name__== "__main__": pass
   
   
          
