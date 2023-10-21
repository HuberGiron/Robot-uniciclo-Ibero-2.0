#LIBRERIAS
import cv2
import numpy as np

from _py_librerias import Bluetooth as Bt
from _py_librerias import Camera as cam
from _py_librerias import xbox as xb

from _py_librerias import funciones_auxiliares as aux
from _py_librerias import control_robot as robotx
from _py_librerias import plot_graficas as pg

#------INICIALIZACION CAMARA------
#HD
resolucionx=1280
resoluciony=720
#Full HD
#resolucionx=1920
#resoluciony=1080
camara=cam.initialize(0,resolucionx,resoluciony)
texto_titulo=""

#------INICIALIZACION ROBOT------
# print("Conectando Robot 0.....")
# robot0=Bt.connect("98:D3:21:F7:B5:70")
# print("Robot 0 OK")

# print("Conectando Robot 1.....")
# robot1=Bt.connect("98:D3:31:FA:17:5B")
# print("Robot 1 OK")

print("Conectando Robot 2.....")
robot2=Bt.connect("98:D3:71:F6:63:9C")
print("Robot 2 OK")

print("Conectando Robot 3.....")
robot3=Bt.connect("98:D3:21:F7:B4:86")
print("Robot 3 OK")

robot_bt1=robot2
id_robot_bt1=2

robot_bt2=robot3
id_robot_bt2=3

robot=[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
wmax=150 #Velocidad angular robot maxima
l=25 #distancia del centro del robot al centro de las llantas
r=58 #radio llanta (pixeles)
L=120 #distancia entre centros de llantas (pixeles)

#INICIALIZACION DE VALORES ROBOT FISICO 1
wd1=0
wi1=0
x1s=0
y1s=0

#INICIALIZACION DE VALORES ROBOT FISICO 2
wd2=0
wi2=0
xs2=0
ys2=0
C21x=250
C21y=0

#INICIALIZACION DE VARIABLES DE CONTROL ROBOT 1
x1=0
y1=0
th1=0
ex1=0
ey1=0
ux1=0
uy1=0

#INICIALIZACION DE VARIABLES DE CONTROL ROBOT 2
x2=0
y2=0
th2=0
ex2=0
ey2=0
ux2=0
uy2=0

#INICIALIZACION DE VARIABLES DE CONTROL GENERAL
i=0
t=0 #Tiempo

#------VALORES CONTROL------
k=130 #ganancia del control


while (True):

    #-------BUSQUEDA DE QR´s------
    #print("Buscamos aruco")
    frame, points, ids =cam.buscar_Aruco(camara, resolucionx, resoluciony)
    #print(ids)

    if len(points)>0:
        robot=cam.buscar_robots(points, ids, robot)
        #print("robot0(x="+str(robot[0][0])+",y="+str(robot[0][1])+",th="+str(robot[0][2])+")")

        #------LEY DE CONTROL TRAYECTORIA------

        #ROBOT LIDER 1
        x1=robot[id_robot_bt1][0]-(resolucionx/2) #Obtenemos valor X de QR robot 
        y1=robot[id_robot_bt1][1]-(resoluciony/2) #Obtenemos valor Y de QR robot 
        th1=robot[id_robot_bt1][2] #Obtenemos valor Th de robot 
        x1=x1+(l*np.cos(th1))
        y1=y1+(l*np.sin(th1))

        A1=np.array([[np.cos(th1), -l*np.sin(th1)],
            [np.sin(th1), l*np.cos(th1)]])
        
        ex1=x1-x1s
        ey1=y1-y1s
        ux1=-k*ex1
        uy1=-k*ey1

        B1=np.array([ux1,uy1]) #Arreglo de Vector velocidad

        U1=np.linalg.solve(A1,B1)
        #U=np.linalg.inv(A)*B  No sirve

        V1=U1[0] #Velocidad Lineal
        W1=U1[1]  #Velocidad Angular


        #ROBOT SEGUIDOR 2
        x2=robot[id_robot_bt2][0]-(resolucionx/2) #Obtenemos valor X de QR robot 
        y2=robot[id_robot_bt2][1]-(resoluciony/2) #Obtenemos valor Y de QR robot 
        th2=robot[id_robot_bt2][2] #Obtenemos valor Th de robot 
        x2=x2+(l*np.cos(th2))
        y2=y2+(l*np.sin(th2))

        A2=np.array([[np.cos(th2), -l*np.sin(th2)],
            [np.sin(th2), l*np.cos(th2)]])
        
        xs2=x1+C21x
        ys2=y1+C21y

        ex2=x2-xs2
        ey2=y2-ys2
        ux2=-k*ex2
        uy2=-k*ey2

        B2=np.array([ux2,uy2]) #Arreglo de Vector velocidad

        U2=np.linalg.solve(A2,B2)
        #U=np.linalg.inv(A)*B  No sirve

        V2=U2[0] #Velocidad Lineal
        W2=U2[1]  #Velocidad Angular
   
        
        #-------MODELO CINEMATICO ROBOT 1-------- 
        wd1= (V1/r)+((L*W1)/(2*r)) #Calulo de wd robot unicilo
        wi1= (V1/r)-((L*W1)/(2*r)) #Calulo de wi robot unicilo

        if(wd1>wmax):
            wd1=wmax
        elif(wd1<-wmax):
            wd1=-wmax

        if(wi1>wmax):
            wi1=wmax
        elif(wi1<-wmax):
            wi1=-wmax

        #print("wd="+str(wd)+"wi="+str(wi))
        #print("robot0(x="+str("%.0f" % x[i])+"y="+str("%.0f" % y[i])+"th="+str("%.2f" % th[i])+", ux="+str("%.0f" % ux[i])+", uy="+str("%.0f" % uy[i])+", V="+str("%.0f" % V)+", W="+str("%.0f" % W)+", wd="+str("%.0f" % wd)+"wi="+str("%.0f" % wi))
        Bt.move(robot_bt1,wd1, wi1)

        #-------MODELO CINEMATICO ROBOT 2-------- 
        wd2= (V2/r)+((L*W2)/(2*r)) #Calulo de wd robot unicilo
        wi2= (V2/r)-((L*W2)/(2*r)) #Calulo de wi robot unicilo

        if(wd2>wmax):
            wd2=wmax
        elif(wd2<-wmax):
            wd2=-wmax

        if(wi2>wmax):
            wi2=wmax
        elif(wi2<-wmax):
            wi2=-wmax

        #print("wd="+str(wd)+"wi="+str(wi))
        #print("robot0(x="+str("%.0f" % x[i])+"y="+str("%.0f" % y[i])+"th="+str("%.2f" % th[i])+", ux="+str("%.0f" % ux[i])+", uy="+str("%.0f" % uy[i])+", V="+str("%.0f" % V)+", W="+str("%.0f" % W)+", wd="+str("%.0f" % wd)+"wi="+str("%.0f" % wi))
        Bt.move(robot_bt2,wd2, wi2)

    #-------VENTANA DE CAMARA-------- 
    texto_titulo="FORMACION 2-robots (auto)"
    color=(0, 0, 255)
    cam.dibujar_aruco(frame, points, ids, resolucionx,resoluciony)
    cam.draw_texto_titulo(frame, texto_titulo,color)
    cam.draw_punto(frame,"X1s,Y1s",(0,0,255), int(x1s)+(int(resolucionx/2)), int(y1s)+(int(resoluciony/2)),resolucionx,resoluciony)
    cam.draw_punto(frame,"X2s,Y2s",(0,0,255), int(xs2)+(int(resolucionx/2)), int(ys2)+(int(resoluciony/2)),resolucionx,resoluciony)
    cv2.imshow('Camara detector qr', frame) #Despliega la ventana 

    if cv2.waitKey(1) & 0xFF == 27: #Presiona esc para salir 
        break

#-------RUTINA DE CIERRE-------- 
Bt.move(robot_bt1,0,0)  #Apagamos motores en Robot
Bt.disconnect(robot_bt1) #Desconectamos Bluetooth
Bt.move(robot_bt2,0,0)  #Apagamos motores en Robot
Bt.disconnect(robot_bt2) #Desconectamos Bluetooth
camara.release() #Liberamos Camara
cv2.destroyAllWindows() #Cerramos ventanas
