import Adafruit_BBIO.GPIO as GPIO
import time
from datetime import datetime

GPIO.setup("P9_11", GPIO.IN)
GPIO.add_event_detect("P9_11", GPIO.FALLING) 

lluvia = 0.0 

#Intervalo de Medicion en minutos
Int = 5
dir = "/root/datos/prec_pluvial/{}" 

c = 0 #variable para controlar que no se guarden muchos datos a los 5 min 

while True:
  hora = datetime.now()
  minute = hora.minute
  if GPIO.event_detected("P9_11"): lluvia += 0.2794
  if (c==1) and (minute%5!=0): c = 0 
  if (minute%Int == 0) and (c == 0):
    f = open(dir.format(str(hora.date())),"a")
    f.write("{0},{1} \n".format(hora.isoformat(),lluvia))
    f.close()
    lluvia = 0
    c = 1   
  time.sleep(0.01)
