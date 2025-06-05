#Version 1.0
#Fecha 
#Autor: Julio de Sande. IES Santa Lucía del Trampal
#Cometido: Este script asiste interactivamente para borrar usuarios del sistema cuya fecha de último acceso sea anterior a una dada.
#
# Ejecución:
#   1) Cambiar variables: "mi_servidor_ldap, contra_ldap, servidor, contra_servidor"
#   2) En un equipo con Xubuntu 22 (no ejecutar en el servidor): 
#       apt-get install python3-pip
#       pip3 install ldap3
#       pip3 install paramiko
#   3) Ejecutar script: python3 clean_users_server_client.py
#
# Notas: 
# -Probado con Python 3.10.12 (Xubuntu 22.04)  
# -Se imprime el directorio que se va a borrar para para mayor control, no obstante hacer copias de seguridad.


import subprocess
import ldap3
import os
import ipaddress
import sys
import time
import socket
import paramiko

#Variable del año ultimo acceso candidatos a ser borrados.
anio_ultimo_acceso=2023

#Datos ldap de tu centro
servidor_ldap='ldap://172.23.96.2:389'
contra_ldap="xxxx"
#Datos servidor principal
servidor="172.23.96.2"
contra_servidor="xxxx"


def print_slow(str):
    for char in str:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.03)

def pintar_cabecera():

    os.system('clear')
    
    print ("""\033[34m    
       
******************************************************
*  ____ _                    _   _                   *
* / ___| | ___  __ _ _ __   | | | |___  ___ _ __ ___ *
*| |   | |/ _ \/ _` | '_ \  | | | / __|/ _ \ '__/ __|*
*| |___| |  __/ (_| | | | | | |_| \__ \  __/ |  \__ \*
* \____|_|\___|\__,_|_| |_|  \___/|___/\___|_|  |___/*
*            / ___|  ___ _ ____   _____ _ __         *
*            \___ \ / _ \ '__\ \ / / _ \ '__|        *
*             ___) |  __/ |   \ V /  __/ |           *
*            |____/ \___|_|    \_/ \___|_|           *
******************************************************

            \033[0m""")                                       
    print("=" * 54)
    print("Limpiar Usuarios Profesores Antiguos - By J. de Sande".center(54))
    print("=" * 54)
    print("\n[!] REALIZAR COPIA DE SEGURIDAD DEL SERVIDOR     [!]")
    print("    +--------------------------------------------+")                                           
    print("    |  > Copia seguridad ldap                    |")
    print("    |  > Copia seguridad /home/profesor          |")
    print("    +--------------------------------------------+")
    print("\n[!] Es un asistente, \033[31mno borra datos\033[0m si no hay una confirmación  ")
    print("[!] Ten abierto Rayuela con el profesorado activo, para decidir\n")
    print (f"[!] Año último acceso de candidatos a ser eliminados:\033[31m {anio_ultimo_acceso} \033[0m \n")


# Funcion que nos da la posibilidad de borrar un usuario
def borrar_opcional(client, conn, home, usuario):
    respuesta = input(f"\n[?] Borrar?: Si(s), No(n) \033[31m[ rm -R {home} ]\033[0m: ")
    if respuesta != "s" and respuesta != "n":
        print_slow("\n[X] Error: Pulse 's' o 'n'. Abortando operación.\n")
        sys.exit (1)
    elif (respuesta=="s"):
        dn = f'uid={usuario},ou=People,dc=instituto,dc=extremadura,dc=es'
        result = conn.delete(dn)
        if (result):
            print (f"[*] Se ha borrado el profesor {usuario} del ldap con éxito")
        stdin, stdout, stderr = client.exec_command("rm -R "+home)
        exit_status = stdout.channel.recv_exit_status()
        if (exit_status) == 0:
            print (f"[*] Se ha borrado el directorio: {home} con éxito\n")    
        else:
            print (stdout.read().decode())
            print (stderr.read().decode())
 

def pide_contras():
    global contra_ldap
    global contra_servidor

    #print (f"\n[*] Iniciando conexión con: {mi_servidor_ldap}")
    contra_ldap = input("[?] Introduce la clave de la base de datos Ldap: ")
    if len(contra_ldap) == 0:
        print_slow("\n[X] Error: Clave vacía detectada.\n")
        print("Saliendo del programa...\n")
        sys.exit(0)       

    contra_servidor = input("[?] Introduce la clave de tu servidor: ")
    if len(contra_ldap) == 0:
        print_slow("\n[X] Error: Clave vacía detectada.\n")
        print("Saliendo del programa...\n")
        sys.exit(0)       
   

    return True


# Flujo principal.
if __name__ == "__main__":

    conn=None #conexion con ldap
    client=None #conexion ssh con el servidor
    pintar_cabecera()
    pide_contras ()

    # Comprobación de que no estamos en el servidor principal.
    '''result = subprocess.run(["hostname"], capture_output=True, text=True)
    if result.stdout == "servidor\n":
        print (result.stdout)
        print(f"\n[X] No debemos ejecutar el script en el servidor principal\n")
        sys.exit(1)'''

    # Conexión ssh con el servidor principal
    try:
    
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=servidor, username="root", password=contra_servidor)
        stdin, stdout, stderr = client.exec_command("hostname")
    
    except paramiko.AuthenticationException:
        print(f"\n[X] Fallo en la autenticación ssh con el servidor\n")
        sys.exit(1)
    except paramiko.SSHException as ssh_exception:
        print(f"\n[X] Error de SSH: {ssh_exception}\n")
        sys.exit(1)
    except paramiko.socket.error as socket_error:
        print(f"\n[X] Error de socket: {socket_error}\n")
        sys.exit(1)
    except paramiko.TimeoutError:
        print(f"\n[X] La conexión ha excedido el tiempo de espera\n")
        sys.exit(1)


    if ("servidor" in stdout.read().decode()):
        print_slow ("[*] Conexión ssh establecida con el servidor \033[32m.........Ok \033[0m \n")
    else:
        print_slow ("[X] Error al establecer conexión ssh con el servidor\n")
        sys.exit(1)

    try:

        server = ldap3.Server(servidor_ldap, get_info=ldap3.ALL)
        conn = ldap3.Connection(server, 'cn=admin,ou=people,dc=instituto,dc=extremadura,dc=es' ,contra_ldap, auto_bind=True)
        # Realizar una búsqueda
        base_dn = 'ou=People,dc=instituto,dc=extremadura,dc=es'
        search_filter = '(objectClass=*)'
        conn.search(base_dn, search_filter, attributes=['uid','cn','homeDirectory','userPassword'])

        if (conn):
            print_slow ("[*] Conexión establecida con la base de datos ldap \033[32m...Ok \033[0m \n")
        else:
            print_slow ("[X] Se ha producido un error, abortando ... ")
            sys.exit(0)
 
        x = input("\n[*] Pulse cualquier tecla para continuar: ")
        
        for entry in conn.entries:
            usuario = entry['uid'].value
            home = str(entry['homeDirectory'].value)
            nombre_completo = str(entry['cn'].value)

            if len (home) <= 16: #control para evitar borrar el directorio raiz. /home/profesor
                print (f"[!] El directorio {home} , es un directorio no válido, seguimos con el siguiente elemento\n")
                continue       

            if ("profesor" in home): #Sólo procesamos los profesores.

                stdin, stdout, stderr = client.exec_command("ls -la "+home+"/.Xauthority")
                error = stderr.read().decode()
                if ("no se puede acceder" in error):
                    print (f"[*] Usuario: '{usuario}' no tiene fichero '.Xauthority'")
                    print ("    Nombre completo: "+ nombre_completo)
                    borrar_opcional(client, conn, home, usuario)
                    continue

                campos = stdout.read().decode().split() 
                
                if len (campos)>= 1:
                    print (f"[*] Usuario: '{usuario}' último acceso: {campos[5:8]}")
            
                    es_hora_anio = campos[7].split (":")
                    if (len(es_hora_anio)==1): # Con esta condición controlamos que el último acceso es un año, no una hora.
                        #print ( "Es un año")
                        if (int(es_hora_anio[0])<=anio_ultimo_acceso):
                            print (f"\n---> {usuario} , no entra en el sistema desde el año: { es_hora_anio[0] }")
                            #print (f"---> {usuario} , es un candidato a ser eliminado.")
                            print ("---> Nombre completo: "+ nombre_completo)
                            borrar_opcional(client, conn, home, usuario)
                            

    except ldap3.core.exceptions.LDAPException as e:
        print(f"[X] Error de conexión:{servidor_ldap} {str(e)}")
        print("Saliendo del programa...\n")
        sys.exit(0)
    except Exception as e:
        print(f"[X] Error inesperado: {str(e)}")
        print("Saliendo del programa...\n")
        sys.exit(0)

    print_slow ("[*] Cerrando conexiones y saliendo del programa\n")
    # Cerrar la conexiones
    if conn is not None:
        conn.unbind()
    
    if client is not None:
        client.close()




