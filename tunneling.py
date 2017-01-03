import subprocess
from datetime import datetime 
import time
import linecache

while True:
 
 host = [] 
 with open("ip_server.txt") as f:
    try:
        for line in f:
           line = line.rstrip("\n") 
           line = line.split(",") 
           host.append(line)
           break #para que solo lea la primera linea
    except ValueError, IOError: 
        fecha = datetime.now().isoformat()
        z = open("Error.txt","a")
        z.write("Revisar el Archivo ip_server.txt,{} \n".format(fecha))
        z.close()

 #probando conexion a internet
 c = subprocess.call("ping -c 1 8.8.8.8 > /dev/null 2>&1&",shell=True)
 if (c == 0):pass
 elif (c!=0):
     fecha = datetime.now().isoformat()
     z = open("Error.txt","a")
     z.write("No hay conexion a internet,{} \n",format(fecha))
     z.close()
 
 linecache.checkcache("ip_server.txt")   
 activar = linecache.getline("ip_server.txt",2)
 activar = activar.split(",")
 activar = activar[1].rstrip("\n")
 #flag = False
 if activar == "si": flag = True
 elif activar == "no":flag = False
 print activar
 linecache.clearcache()

 c = 0 
 while flag:
     #intenta conectarse durante 5 minutos luego se cierra
     c += 1
     a = subprocess.check_output(["vtund",host[0][0],host[0][1]],shell=False)
     if (c == 30): break   #si se cumplen 5 min y el tunel no funciona
     if (a == 0): break    #si se abre correctamente el tunel
     elif (a!=0): continue #tratando de establecer el tunel 
     time.sleep(10)

 time.sleep(10)  
