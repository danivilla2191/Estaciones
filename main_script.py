#python 2.7
import Adafruit_BBIO.ADC as ADC
import Adafruit_DHT
import Adafruit_BBIO.GPIO as GPIO
from datetime import datetime
import numpy as np
import time
import modulo_general
import subprocess

#Establecimiento de los pines, inicio sensores I2C
ADC.setup()
modulo_general.init_presion()
dicc_vel =  modulo_general.dicc_veleta()
#GPIO.setup("P9_14", GPIO.IN)
#GPIO.add_event_detect("P9_14", GPIO.FALLING)

#Contenedores para los datos
dir_base = "/root/datos/"
dir_bmp  =  dir_base + "presion/{}"     #bmp180
dir_AM2302 = dir_base + "humedad/{}"  #AM2302
dir_Anm = dir_base + "Anemometro/{}"  #Anemometro
dir_gas = dir_base + "gases/{}"       #gases
dir_veleta = dir_base + "veleta/{}"    #veleta

c = 0 # variable para controlar que no se guarden muchos datos a los 5 min
while True:
  #Contenedores para los datos
  pres_temp = []                       #bmp180 
  hum_temp = []                        #AM2302
  Anm = []                             #Anemometro
  gases = []                           #[MQ_135,TGS]
  #Ciclo de Medicion
  flag = True
  while flag:
    #Presion y Temperatura bmp180
    #print "Hola"
    pres_bmp,temp_bmp = round((modulo_general.presion_temp("pressure"))/100,1), round((modulo_general.presion_temp("temp"))/10,1)
    #pres_bmp,temp_bmp = modulo_general.check_alarma(pres_bmp,"presion")
    pres_temp.append([pres_bmp,temp_bmp])
    #humedad
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302,"P8_11")
    if humidity is not None and temperature is not None:
      hum_temp.append([humidity,temperature])
    if humidity is None and temperature is None: pass
    #Anemometro
    Anemometro = modulo_general.Anemometro(20,0.01,"P9_14")
    print Anemometro
    Anm.append(Anemometro)
    #Gases
    MQ_135 = modulo_general.gas(10,0.05,"P9_40")
    TGS = modulo_general.gas(10,0.05,"P9_37")
    print MQ_135,TGS
    gases.append([MQ_135,TGS])
    #veleta
    veleta = modulo_general.direccion_del_viento(dicc_vel,"P9_33")
    #print "Hola"    
    #Terminar ciclo de medidas
    minute = datetime.now().minute
    #enganar al beaglebone para que no registre medidas durante el resto de los
    #cinco minutos
    if (minute%5) == 0 and (c == 1): minute = 6 
    c = 0 
    #si el beaglebone no es enganado entonces procede a guardar las medidas
    if (minute%5) == 0 and (c == 0):
      c = 1 
      flag = False
      fecha = datetime.now()
      date  = str(fecha.date())
    time.sleep(1)
       
  #Guardando los datos
  #datos = []        #contenedor con los datos que se van a guardar
  if not flag:
    #presion
    pres_temp = np.array(pres_temp)
    pres_temp = modulo_general.prom_array(pres_temp,fecha.isoformat())
    modulo_general.salvar_datos([pres_temp,dir_bmp.format(date)])
    #presion humedad AM2302
    hum_temp = np.array(hum_temp)
    hum_temp = modulo_general.prom_array(hum_temp,fecha.isoformat())
    modulo_general.salvar_datos([hum_temp,dir_AM2302.format(date)])
    #Anemometro
    Anm = np.array(Anm)
    Anm = np.mean(Anm)
    Anm = [Anm,fecha.isoformat()]
    modulo_general.salvar_datos([Anm,dir_Anm.format(date)])
    #Gases
    gases = np.array(gases)
    gases = modulo_general.prom_array(gases,fecha.isoformat())
    modulo_general.salvar_datos([gases,dir_gas.format(date)])
    #veleta
    veleta = modulo_general.direccion_del_viento(dicc_vel,"P9_33")
    modulo_general.salvar_datos([[veleta,fecha.isoformat()],dir_veleta.format(date)])
    
  time.sleep(0.01)
