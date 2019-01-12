import base64
import struct
import binascii
from Crypto.Cipher import AES
import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import os
import datetime

def decrypt(data,tipo=None):
    """ Funcion que desencripta los datos de el controlador

        Input:
                data: str de los datos encriptados
                tipo: tipo de dato a desencriptar y retornar, si es 'raw_data' se devuelve el dato solicitado solamente desencriptado,
                      de no ser asi, se transforma de byte a un arreglo con los datapoints

        Output: arreglo con la informacion desencriptada"""


    data = base64.b64decode(data)
    data = str(binascii.hexlify(data),'utf-8').upper()
    data += '34AF336C9F031B3556738C63E61EA2F6'
    data = binascii.unhexlify(data)
    iv = "\0"*16
    aes = AES.new('0123456789ABCDEF', AES.MODE_ECB, iv)
    decd = aes.decrypt(data)
    if tipo == 'raw_data':
        return str(decd[:12],'utf-8')
    result = struct.unpack('32B', decd)

    return result

def parse_date(data):
    """
    Funcion que parsea un string como datetime

    Input: str representando una fecha
    Output: objeto tipo DateTime
    """
    fecha = datetime.datetime.strptime(data,'%y%m%d%H%M%S')
    return fecha

def plot_O2_CO2(o2,co2,fechas,esn,origen,destino,timestamp):

    """ Funcion encargarda de graficar los datos del controlador

        input:

            o2: arreglo con datos de O2
            co2: arreglo con datos de CO2
            fechas: arreglo con datos de las fechas de los datapoints

        output: """

    """Las 2 lineas de codigo siguientes se usan para poder cortar el grafico a la apertura de puertas y
    evitar que el algoritmo corte el grafico antes de comenzar el servicio """

    fecha_tracking = [x for x in fechas if x> fechas[0] + datetime.timedelta(days=1)  ]
    fecha_tracking = fechas.index(fecha_tracking[0])

    """ En este for se itera sobre los items de el arreglo 02 y co2 hasta que ambos superan el umbral que indica una apertura de puertas

        Se utilizo un umbral rudimentario pero efectivo, oportunidad de mejora
        """
    for item in range(fecha_tracking,len(o2)):
        if o2[item]>18.3 and co2[item]<1:
            break

    o2 = o2[:item+5]
    co2 = co2[:item+5]
    fechas = fechas[:item+5]

    path = "E:/ScriptGraficosPython/Graficos" + "/" + timestamp
    if not os.path.exists(path+'/'+esn):
        os.makedirs(path+'/'+esn)
        os.makedirs(path+'/'+esn+"/CO2_O2")




    font = {'family': 'serif',
        'color':  'black',
        'weight': 'bold',
        'size': 14,
        }
    fig, ax1 = plt.subplots()  #Se crean 2 subgraficos para manejar los ejes
    plt.subplots_adjust(top=0.7,bottom = 0.25)
    fig.set_size_inches(14.5 ,2)
    ax1.plot(fechas,co2,color = '#FF0000',linewidth=2)

    ax2 = ax1.twiny() #Se crea el subgrafico que comparte el eje y con ax1
    ax2.plot(fechas,o2, color = '#0088cc',linewidth=2)

    #Se crean los estilos para la informacion del eje x superior
    ax2.xaxis.set_major_locator(mdates.DayLocator(bymonthday=1))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax2.xaxis.set_tick_params(which = 'major',labelsize='medium')
    ax2.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(5,9,13,17,21,25)))
    ax2.xaxis.set_minor_formatter(mdates.DateFormatter("%b %d"))

    #Se inicializa la grilla con el estilo correspondiente
    ax2.grid(b=None, which='both', color='k', linestyle='-.',linewidth=0.3)
    ax1.grid(b=None, axis='y', color='k', linestyle='-.',linewidth=0.3)

    #Se ajustan los tamaños de los ejes
    ax1.axes.set_xlim( (fechas[0],fechas[-1]) )
    ax2.axes.set_xlim( (fechas[0],fechas[-1]) )
    ax1.axes.set_ylabel('CO2/O2 (%)',fontdict=font)
    ax1.set_xticklabels([])
    ax1.set_xticks([])
    plt.ylim((0, 30))
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=9)
    #Formato de la leyenda del grafico
    red_line = mlines.Line2D([],[],color='#FF0000', label='CO2',marker= 'o')
    blue_line = mlines.Line2D([],[],color='#0088cc', label=' O2',marker= 'o')
    plt.legend(handles = [red_line,blue_line],loc = 2,bbox_to_anchor=[0,-0.09],ncol=2)

    ax1.annotate(origen + ' - ' + destino,
            xy=(0.5, -0.03), xytext=(0, 10),
            xycoords=('axes fraction', 'figure fraction'),
            textcoords='offset points',
            size=12, ha='center', va='bottom')

    ax1.annotate('Contenedor: '+esn,
            xy=(0.5, 0.85), xytext=(0, 10),
            xycoords=('axes fraction', 'figure fraction'),
            textcoords='offset points',
            size=12, ha='center', va='top')

    # plt.title('Contenedor: '+esn)
    plt.savefig(path+'/'+esn+"/CO2_O2/"+esn+'.png',quality=50,dpi=70)
    plt.close('all')

def plot_temp(temp,fechas,esn,timestamp):
    path = "E:/ScriptGraficosPython/Graficos"+ "/" + timestamp
    if not os.path.exists(path+'/'+esn):
        os.makedirs(path+'/'+esn)
        os.makedirs(path+'/'+esn+"/Temperatura")

    """ Funcion encargarda de graficar los datos de temperatura del controlador

        input:

            temp: arreglo de datos de tempertatura
            fechas: arreglo con datos de las fechas de los datapoints

        output: """

    font = {'family': 'serif',
        'color':  'black',
        'weight': 'bold',
        'size': 16,
        }

    #Se crean los graficos y estilos para la informacion de los ejes
    fig, ax1 = plt.subplots()
    fig.set_size_inches(9,3)
    ax1.plot(fechas,temp,color = '#0088cc',linewidth=2)
    ax1.xaxis.set_major_locator(mdates.DayLocator(bymonthday=5))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax1.xaxis.set_tick_params(which = 'major',labelsize='x-large')
    ax1.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=(10,15,20,25,30)))
    ax1.xaxis.set_minor_formatter(mdates.DateFormatter("%b %d"))
    ax1.xaxis.tick_top()

    ax1.grid(b=None, which='both', axis='both', color='k', linestyle='-.',linewidth=0.3)
    ax1.axes.set_xlim( (fechas[0],fechas[-1]) )
    ax1.axes.set_ylabel('TEMP (Cº)',fontdict=font)

    #Formato de la leyenda del grafico
    blue_line = mlines.Line2D([],[],color='#0088cc', label=' O2',marker= 'o')
    plt.legend(handles = [blue_line],loc = 2)
    plt.ylim((-10, 40))


    plt.savefig(path+'/'+esn+'/Temperatura/'+esn+'.png',quality=100,dpi=400)
    plt.close('all')
