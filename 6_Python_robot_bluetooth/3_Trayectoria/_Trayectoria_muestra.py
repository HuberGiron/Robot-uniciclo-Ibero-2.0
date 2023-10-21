#LIBRERIAS 
import cv2
import numpy as np
import datetime
 
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

# print("Conectando Robot 2.....")
# robot2=Bt.connect("98:D3:71:F6:63:9C")
# print("Robot 2 OK")

print("Conectando Robot 3.....")
robot3=Bt.connect("98:D3:21:F7:B4:86")
print("Robot 3 OK")

robot_bt=robot3
robot=[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]


#INICIALIZACION DE VALORES ROBOT FISICO 1
wd=0
wi=0
wmax=150 #Velocidad angular robot maxima
l=25 #distancia del centro del robot al centro de las llantas
r=58 #radio llanta (pixeles)
L=120 #distancia entre centros de llantas (pixeles)


#ITERACIONES DE SIMULACION
tfin=500
i=0

#INICIALIZACION DE VARIABLES DE CONTROL
x,y,th,t,ex,ey,ux,uy,mx,my =aux.inicializar_arreglos2(tfin)

#------VALORES de ley de CONTROL------
k=130 #ganancia del control

#------VALORES TRAYECTORIA-------
T=500
w=(2*3.1416)/T
cx=0
cy=0
rad=300

while (True):

    #------Tiempo i --------
    t[i]=i
    print("t="+str(t[i]))

    #------TRAYECTORIA CIRCULAR------
    mx[i]=cx+rad*np.cos(w*t[i])
    my[i]=cy+rad*np.sin(w*t[i])
    mxp=-rad*w*np.sin(w*t[i])
    myp=rad*w*np.cos(w*t[i])

    #-------BUSQUEDA DE QR´s------
    #print("Buscamos aruco")
    frame, points, ids =cam.buscar_Aruco(camara, resolucionx, resoluciony)
    #print(ids)

    if len(points)>0:
        robot=cam.buscar_robots(points, ids, robot)
        #print("robot0(x="+str(robot[0][0])+",y="+str(robot[0][1])+",th="+str(robot[0][2])+")")

        #------LEY DE CONTROL CONVERGENCIA------
        x[i]=robot[3][0]-(resolucionx/2) #Obtenemos valor X de QR robot 
        y[i]=robot[3][1]-(resoluciony/2) #Obtenemos valor Y de QR robot 
        th[i]=robot[3][2] #Obtenemos valor Th de robot 

        x[i]=x[i]+(l*np.cos(th[i]))
        y[i]=y[i]+(l*np.sin(th[i]))

        A=np.array([[np.cos(th[i]), -l*np.sin(th[i])],
                    [np.sin(th[i]), l*np.cos(th[i])]])

        ex[i]=x[i]-mx[i]
        ey[i]=y[i]-my[i]

        ux[i]=-k*ex[i]+mxp
        uy[i]=-k*ey[i]+myp

        B=np.array([ux[i],uy[i]]) #Arreglo de Vector velocidad

        U=np.linalg.solve(A,B)
        #U=np.linalg.inv(A)*B  No sirve

        V=U[0] #Velocidad Lineal
        W=U[1]  #Velocidad Angular
         #print("v="+str(V)+"w="+str(W))


        #-------MODELO CINEMATICO ROBOT-------- 
        wd= (V/r)+((L*W)/(2*r))
        wi= (V/r)-((L*W)/(2*r))

        if(wd>wmax):
            wd=wmax
        elif(wd<-wmax):
            wd=-wmax

        if(wi>wmax):
            wi=wmax
        elif(wi<-wmax):
            wi=-wmax

        #print("wd="+str(wd)+"wi="+str(wi))
        #print("robot0(x="+str("%.0f" % x[i])+"y="+str("%.0f" % y[i])+"th="+str("%.2f" % th[i])+", ux="+str("%.0f" % ux[i])+", uy="+str("%.0f" % uy[i])+", V="+str("%.0f" % V)+", W="+str("%.0f" % W)+", wd="+str("%.0f" % wd)+"wi="+str("%.0f" % wi))

        Bt.move(robot_bt,wd, wi)

    i=i+1  

    if (i>tfin):
        break


    #-------VENTANA DE CAMARA-------- 
    texto_titulo="TRAYECTORIA (auto)"
    color=(0, 0, 255)
    cam.dibujar_aruco(frame, points, ids, resolucionx,resoluciony)
    cam.draw_texto_titulo(frame, texto_titulo, color)
    cam.draw_punto(frame,"XS,YS",(0,0,255), int(mx[i-1])+(int(resolucionx/2)), int(my[i-1])+(int(resoluciony/2)),resolucionx,resoluciony)
    cv2.imshow('Camara detector qr', frame) #Despliega la ventana 

    if cv2.waitKey(1) & 0xFF == 27: #Presiona esc para salir 
        break

#-------RUTINA DE CIERRE-------- 
Bt.move(robot_bt,0,0)  #Apagamos motores en Robot
Bt.disconnect(robot_bt) #Desconectamos Bluetooth
camara.release() #Liberamos Camara
cv2.destroyAllWindows() #Cerramos ventanas

e = datetime.datetime.now()
pg.plot_xy_x0y0_trayectoria(e,x, y,mx,my)
pg.plot_error_x_(e,ex,t)
pg.plot_error_y_(e,ey,t)
pg.plot_x_(e,x,t)
pg.plot_y_(e,y,t)