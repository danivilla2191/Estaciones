#! /usr/bin/python2.7

import subprocess
import os

conf_dict = {}   #diccionario para  guardar los campos  de configuracion
alarm_file = '../alarm_conf/alarm.conf.save'

#funciones
def checker(file,message):
   #Esta funcion se encarga de escribir en el archivo de configuracion
   # de alarma
   #file = archivo de configuracion de alarma
   #message is what you want to write to alarm_file
   idx = 0
   for line in open(file): #identificando las linea que corresponde
      idx+=1
      if line[:3] == "date":break 
   #reemplazando y reescribiendo el archivo
   #print(line,idx)
   f = open(file,"r+")
   lines = f.readlines()
   lines[idx-1] = "date={}\n".format(message)
   f.close()
   #borrando el archivo anterior y creando uno nuevo
   os.remove(file)
   f = open(file,"a")
   #print(lines)
   for i in lines: f.write(i)
   f.close()
 
#abrir el archivo de configuracion
for line in open("date_checker.conf"):
   if line[0] != "#" and len(line) != 9:    #nine,taking year line as reference
     line = line.rstrip("\n")
     line = line.split("=")
     conf_dict[line[0]] = line[1]

#time since the epoch in seconds, it is taken from ref_date field in
#conf_file
date = subprocess.check_output(["date","-d","{}".format(conf_dict['ref_date']),
                                "+%s"],shell=False)
date = int(date.rstrip("\n")) 

#time since the epoch now
date_now =  subprocess.check_output(["date","+%s"],shell=False)

#Now is time to set the alarm
if date_now < date: checker(alarm_file,"1")
if date_now > date: checker(alarm_file,"0")
