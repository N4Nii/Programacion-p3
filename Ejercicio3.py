estudiantes = {
    "A001": {"nombre": "Maria", "edad": 23, "calificaciones": [90, 85, 78]},
    "A002": {"nombre": "Lucero", "edad": 22, "calificaciones": [88, 91, 79]}
}

def agregar():
    id_est = input("ID: ").upper()
    if id_est in estudiantes:
        print("ID ya existe"); return
    nombre = input("Nombre: ")
    edad = int(input("Edad: "))
    notas = list(map(float, input("Calificaciones (coma): ").split(",")))
    estudiantes[id_est] = {"nombre": nombre, "edad": edad, "calificaciones": notas}

def mostrar():
    for id_est, info in estudiantes.items():
        prom = sum(info["calificaciones"]) / len(info["calificaciones"]) if info["calificaciones"] else 0
        print(f"{id_est} - {info['nombre']} - Promedio: {prom:.1f}")

def promedio():
    id_est = input("ID: ").upper()
    if id_est in estudiantes:
        info = estudiantes[id_est]
        prom = sum(info["calificaciones"]) / len(info["calificaciones"])
        print(f"{info['nombre']} - Promedio: {prom:.1f}")
    else: print("No encontrado")

def eliminar():
    id_est = input("ID: ").upper()
    if id_est in estudiantes: del estudiantes[id_est]; print("Eliminado")
    else: print("No encontrado")

while True:
    op = input("\n1.Agregar 2.Mostrar 3.Promedio 4.Eliminar 5.Salir: ")
    if op=="1": agregar()
    elif op=="2": mostrar()
    elif op=="3": promedio()
    elif op=="4": eliminar()
    elif op=="5": break
    else: print("Opción inválida")