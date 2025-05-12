# Asistente para la limpieza de usuarios antiguos del sistema.

Cometido: Este script asiste interactivamente para borrar usuarios del sistema cuya fecha de último acceso sea anterior a una dada.
Compara el último acceso a el sistema del usuario y si es anterior a él  año indicado por la variable **"anio_ultimo_acceso"**
va a considerar que este usuario es un candidato a ser eliminado, dándonos la opción de poder eliminarlo.
Si decidimos eliminar el usuario, lo eliminará tanto de la base de datos ldap como su directorio del /home del servidor.

* !El script no borra datos sin confirmar!
* Tenemos 2 scripts uno para profesores y otro para alumnos.

 ![A sample image](cleanUsers.png)

## Puesta en marcha.
1. Cambiar variables: "mi_servidor_ldap, contra_ldap, servidor, contra_servidor"
2. En un equipo con Xubuntu 22 (no ejecutar en el servidor): 
```bash 
    apt-get install python3-pip
    pip3 install ldap3
    pip3 install paramiko
```
3. Ejecutar script: 
```bash
    python3 clean_students.py
```
