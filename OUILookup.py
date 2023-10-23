import subprocess
import getopt
import sys
import urllib.request

# Función para obtener los datos de fabricación de una tarjeta de red por IP
def obtener_datos_por_ip(ip, ipusuario, macusuario, mac1, nombre):
    if ip in ipusuario:
        indice = ipusuario.index(ip)
        print("Mac: ", macusuario[indice])
        macu = macusuario[indice].split("-")[:3]
        macs = macu[0].upper() + "-" + macu[1].upper() + "-" + macu[2].upper()
        if macs in mac1:
            indice = mac1.index(macs)
            print("fabricante: ",nombre[indice])
        else:
            print("no se encuentra el fabricante.")
    else:
        print("Error: ip is outside the host network")
    pass

# Función para obtener los datos de fabricación de una tarjeta de red por MAC
def obtener_datos_por_mac(mac,macusuario,mac1,nombre):
    if mac in macusuario:
        print("Mac address: ",mac)
        if "-" in mac:
            macu = mac.split("-")[:3]
            macs = macu[0].upper() + "-" + macu[1].upper() + "-" + macu[2].upper()
            if macs in mac1:
                indice = mac1.index(macs)
                print("Fabricante: ",nombre[indice])
            else:
                print("No se encuentra fabricante.")
        else:
            macu = mac.split(":")[:3]
            macs = macu[0].upper() + ":" + macu[1].upper() + ":" + macu[2].upper()
            if macs in mac1:
                indice = mac1.index(macs)
                print("Fabricante: ",nombre[indice])
            else:
                print("No se encuentra fabricante.")
    else:
        print("Mac address: ",mac)
        print("Fabricante : Not found")
    pass

# Función para obtener la tabla ARP
def obtener_tabla_arp(ipusuario, macusuario, mac1, nombre):
    print("Datos del usuario:")
    for i in range(len(ipusuario)):
        macusuarioo = macusuario[i].split("-")[:3]
        macusuarioa = macusuarioo[0].upper() + "-" + macusuarioo[1].upper() + "-" + macusuarioo[2].upper()
        if macusuarioa in mac1:
            indice = mac1.index(macusuarioa)
            print("IP:", ipusuario[i], "MAC:", macusuario[i], "Fabricante:", nombre[indice])
        else:
            print("IP:", ipusuario[i], "MAC:", macusuario[i])

def save_arp_table_to_file():
    filename = "a.txt"
    try:
        arp_output = subprocess.check_output(["arp", "-a"], text=True)
        with open(filename, "w") as f:
            f.write(arp_output)
    except subprocess.CalledProcessError as e:
        print("Error al obtener la tabla ARP:", e)

# Leer la tabla ARP desde un archivo en el mismo directorio que el script y almacenarla en un arreglo
def read_arp_table_from_file():
    filename = "a.txt"
    arp_table = []
    try:
        with open(filename, "r") as f:
            arp_lines = f.read().strip().split('\n')[2:]
            for line in arp_lines:
                parts = line.split()
                if len(parts) == 4:
                    ip_address, physical_address, _, a = parts
                    arp_table.append((ip_address, physical_address))

    except FileNotFoundError:
        print(f"El archivo {filename} no se encontró.")
    return arp_table

def main(argv):
    save_arp_table_to_file()
    arp_table = read_arp_table_from_file()
    ipusuario = []
    macusuario = []
    if arp_table:
        for ip2, mac2 in arp_table:
            ipusuario.append(ip2)
            macusuario.append(mac2)

    url = "https://raw.githubusercontent.com/boundary/wireshark/master/manuf"

    with urllib.request.urlopen(url) as response:
        content = response.read().decode("utf-8").split('\n')

    datos_no_comentados = []
    mac1 = []
    nombre = []

    for linea in content:
        linea = linea.strip()
        linea = linea.split("#")[0]
        linea = linea.split("	")
        if len(linea) == 2:
            if ":" in linea[0]:
                maccontrol = linea[0].split(":")
                macfinal = maccontrol[0].upper() + ":" + maccontrol[1].upper() + ":" + maccontrol[2].upper()
                mac1.append(macfinal)
            else:
                maccontrol = linea[0].split("-")[:3]
                macfinal = maccontrol[0].upper() + "-" + maccontrol[1].upper() + "-" + maccontrol[2].upper()
                mac1.append(macfinal)
            nombre.append(linea[1])

    ip = None
    mac = None
    arp = None

    try:
        opts, args = getopt.getopt(argv, "i:m:a", ["ip=", "mac=", "arp"])

    except getopt.GetoptError:
        print("Use: ./OUILookup --ip <IP> | --mac <IP> | --arp | [--help] ")
        print("--ip : IP del host a consultar.\n--mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.\n--arp: muestra los fabricantes de los host disponibles en la tabla arp.\n--help: muestra este mensaje y termina.")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--ip"):
            ip = arg
            obtener_datos_por_ip(ip, ipusuario, macusuario, mac1, nombre)
        if opt in ("-m", "--mac"):
            mac = arg
            obtener_datos_por_mac(mac,macusuario,mac1,nombre)
        if opt in ("-a", "--arp"):
            obtener_tabla_arp(ipusuario, macusuario, mac1, nombre)
            arp = arg

    # Solo mostrar el mensaje si no se proporcionó ninguna opción válida
    if ip is None and mac is None and arp is None :
        print("Debe proporcionar una opción válida (-i, -m o -a).")

if __name__ == "__main__":
    main(sys.argv[1:])