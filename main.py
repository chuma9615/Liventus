import base64
import shutil
import struct
import binascii
from Crypto.Cipher import AES
import matplotlib.pyplot as plt
import utils
import datetime
import matplotlib.dates as mdates
import db
import sys

"""
El programa inicial debe ser ejecutado con 3 parametros de entrada

1. Data: Los datos de contenedores y controladores para hacer las consultas respectivas
2. Timestamp: String con el que se le asignará un nombre a la carpeta y archivo .zip

"""
timestamp = sys.argv[2]
#input = 
input = sys.argv[1].split(",")[:-1]  #Se hace split de los datos y se borra la ultima entrada del array ya que es vacía
input = [x if x is not '' else 'NOVALUE' for x in input] #Se rellenan los datos vacios
input = [input[i:i+5] for i in range(0,len(input),5)]
inputData = { fila[0]:fila[1:] for fila in input  } #Diccionario donde la llave es el Nº de Contenedor y el atributo es una lista con la información respectiva



for item in inputData.keys():
    print(item)
    controller_esn = inputData[item][0]
    if inputData[item][1] == ':00.000': #Si los datos vienen sin un dia especifico se termina la ejecucion de esa consulta
        break
    fechahora =datetime.datetime.strptime( inputData[item][1] ,'%d-%m-%Y %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S.%f")
    query = db.GET_HISTORY_SERVICE.format(CONTROLLER=controller_esn)
    rows = db.curTecnica.execute(query)
    if rows == 0: #Si no encuentra nada la primera consulta termina la ejecucion de ese ciclo
        inputData[item].append(str(None))
        break
    data = db.curTecnica.fetchall()
    hs_id = tuple(str(datos[0]) for datos in data)
    hl_id = tuple(str(datos[1]) for datos in data)
    #print(hs_id)
    #print(hl_id)
    query2 = db.GET_SERVICE_DATA.format(HS_ID=hs_id,HL_ID=hl_id,FECHAHORA=fechahora)
    db.curTecnica.execute(query2)
    data = db.curTecnica.fetchone()
    try:
        inputData[item].append(str(data[0]))
    except TypeError:
        inputData[item].append(str(None))


for item in inputData.keys():
    string = inputData[item][-1] #EL string es el serviceData del controlador
    if len(string) > 15: #esta sentencia es para asegurar que no sea none o vacío
        string = string.replace('*','')
        string = string.replace('#','')
        array = string.split('|')

        co2final = []
        o2final = []
        fechas_finales = []
        tempfinal = []
        diferencialfinal = 0
        identificador = []

        # print(utils.decrypt(array[0],tipo='raw_data'))
        if len(array)<16: #Si el array tiene menos de 16 items es que está corrupto
            break
        fecha_inicio = utils.decrypt(array[2],tipo='raw_data')
        fecha_inicio = utils.parse_date(fecha_inicio)


        for string in array[3:]: #Se va desencriptando cada datapoint y agregando al array correspondiente
            if len(string) == 24:
                result = utils.decrypt(string)

                co2 = result[6]*256 + result[5]
                o2 = result[8]*256 + result[7]
                temp = result[13]*256 + result[12]
                diferencial = (result[4] * 65536) + (result[3] * 256) + result[2]

                if temp > 32767:
                    temp = temp - 65536

                diferencialfinal += diferencial
                fechas_finales.append(fecha_inicio + datetime.timedelta(seconds = diferencialfinal))
                o2final.append(o2/100)
                co2final.append(co2/100)
                tempfinal.append(temp/100)

            if len(string) == 48:
                result = utils.decrypt(string[0:24])

                co2 = result[6]*256 + result[5]
                o2 = result[8]*256 + result[7]
                temp = result[13]*256 + result[12]
                diferencial = (result[4] * 65536) + (result[3] * 256) + result[2]
                if temp > 32767:
                    temp = temp - 65536

                diferencialfinal += diferencial
                fechas_finales.append(fecha_inicio + datetime.timedelta(seconds = diferencialfinal))
                o2final.append(o2/100)
                co2final.append(co2/100)
                tempfinal.append(temp/100)

                result = utils.decrypt(string[24:])

                co2 = result[6]*256 + result[5]
                o2 = result[8]*256 + result[7]
                temp = result[13]*256 + result[12]
                diferencial = (result[4] * 65536) + (result[3] * 256) + result[2]
                if temp > 32767:
                    temp = temp - 65536

                diferencialfinal += diferencial
                fechas_finales.append(fecha_inicio + datetime.timedelta(seconds = diferencialfinal))
                o2final.append(o2/100)
                co2final.append(co2/100)
                tempfinal.append(temp/100)


        utils.plot_O2_CO2(o2final,co2final,fechas_finales,item,inputData[item][2],inputData[item][3],timestamp)
        #utils.plot_temp(tempfinal,fechas_finales,item,timestamp)

try:
    shutil.make_archive("E:/ScriptGraficosPython/Graficos" + "/" + timestamp, 'zip',"E:/ScriptGraficosPython/Graficos" + "/" + timestamp)
except FileNotFoundError:
    pass
