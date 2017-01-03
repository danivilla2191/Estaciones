import Adafruit_BBIO.GPIO as GPIO
import time
from datetime import datetime, timedelta

alarm_file = './alarm_conf/alarm.conf.save'
int_a = 300 #duracion del encendido del led en segundos

GPIO.setup("P9_21", GPIO.OUT)
GPIO.setup("P9_24", GPIO.OUT)
#GPIO.setup("P9_14", GPIO.IN)
#GPIO.add_event_detect("P9_14", GPIO.FALLING)

#pin_anemometro = "P9_14"

def Anemometro(duracion,pin):
   '''Parametros: duracion es el tiempo en segundos, en el cual se desea medir la rapidez del viento.
      pin es un string con el pin utilizado'''

   Inicio = datetime.now()
   Fin = Inicio + timedelta(seconds=duracion)
   hora = Inicio
   vueltas = 0
   while (hora<=Fin):
      if GPIO.event_detected(pin): vueltas +=1
      hora = datetime.now()
      time.sleep(0.001)
   tiempo = hora - Inicio
   tiempo = tiempo.seconds    #segundos que se utilizaron para medir
   rev = vueltas/tiempo       #vueltas por segundo
   rapidez = 2.4/rev          #rapidez del viento en Km/h
   return rapidez

def reader():
   #Funcion para revisar los estados de alarma
   #se abre el archivo en donde se chequean las alarmas
   check =[]
   for line in open(alarm_file):
      if line[0] != "#":
        line = line.rstrip("\n")
        line = line.split("=")
        try:check.append(int(line[1]))
        except ValueError:pass
   return sum(check)
  
while True:
     a = reader()
     fin = datetime.now() + timedelta(seconds=int_a)
     if a == 0:
       while (datetime.now() <= fin):
            GPIO.output("P9_21", GPIO.HIGH)
            time.sleep(1)
            GPIO.output("P9_21", GPIO.LOW)
            time.sleep(1)
     else:
       while (datetime.now() <= fin):
            GPIO.output("P9_24", GPIO.HIGH)
            time.sleep(1)
            GPIO.output("P9_24", GPIO.LOW)
            time.sleep(1)

     time.sleep(0.01) 

  #GPIO.output("P9_24", GPIO.HIGH)
  #time.sleep(1)
  #GPIO.output("P9_21", GPIO.LOW)
  #GPIO.output("P9_24", GPIO.LOW)
  #viento = Anemometro(10,pin_anemometro)
  #print viento
  #time.sleep(1)


