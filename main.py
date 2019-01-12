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
#input = "TRIU8919671,886B0F74F7BE,13-09-2018 00:00:00.000,SAN ANTONIO,PHILADELPHIA,CXRU1466663,886B0F7CAC2F,14-09-2018 00:00:00.000,SAN ANTONIO,PHILADELPHIA,SEGU9284611,886B0F7CAAEF,14-09-2018 00:00:00.000,SAN ANTONIO,PHILADELPHIA,TEMU9337410,886B0F7E3391,14-09-2018 00:00:00.000,SAN ANTONIO,PHILADELPHIA,TEMU9266363,886B0F7CAAAB,10-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,CGMU5078935,886B0F7CA87C,10-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,CGMU5328295,886B0F54A761,10-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,CGMU5302393,886B0F7CA839,10-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,CXRU1620613,886B0F003BD6,11-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,SEGU9158887,886B0F7CA796,12-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8571637,886B0F7E33F1,10-09-2018 00:00:00.000,VALPARAISO,LONDON,TEMU9296671,000780A3508C,10-09-2018 00:00:00.000,VALPARAISO,LONDON,TTNU8672606,886B0F003B56,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8672740,886B0F7CAA94,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8574359,886B0F003C33,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8672376,886B0F7E35FC,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8672458,886B0F02C7FD,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8673747,886B0F54ACC5,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8673768,886B0F02C711,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8677017,886B0F003B9A,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8679616,886B0F02C7C8,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8679832,886B0F7CA76C,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8670732,886B0F2DBEE8,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8672139,886B0F7CA96E,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8673789,886B0F54AC85,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8672437,886B0F02C7B7,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8673243,000780A3746A,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,TTNU8673480,886B0F003D04,22-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM,CXRU1492235,886B0F02CA4B,29-09-2018 00:00:00.000,VALPARAISO,ROTTERDAM, ".split(",")[:-1]
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
