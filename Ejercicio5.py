
def leer_estudiantes():

    try:
        with open("estudiantes.txt", "r") as archivo:
            lineas = archivo.readlines()
        
        estudiantes = []
        for linea in lineas:
            linea = linea.strip()
            if linea and ',' in linea:
                nombre, calificacion = linea.split(',', 1)
                try:
                    calificacion = float(calificacion)
                    estudiantes.append((nombre, calificacion))
                except ValueError:
                    print(f"Error: Calificación no válida para {nombre}")
        
        return estudiantes
    
    except FileNotFoundError:
        print("Error: El archivo estudiantes.txt no existe")
        return []
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []

def calcular_promedio(estudiantes):

    if not estudiantes:
        return 0
    
    total = sum(calificacion for _, calificacion in estudiantes)
    return total / len(estudiantes)

def generar_reporte(estudiantes):
   
    try:
        with open("reporte.txt", "w") as archivo:
            
            for nombre, calificacion in estudiantes:
                archivo.write(f"{nombre},{calificacion}\n")
            
            
            promedio = calcular_promedio(estudiantes)
            archivo.write(f"Promedio general: {promedio:.1f}")
        
        print("Reporte generado en reporte.txt")
    
    except Exception as e:
        print(f"Error al generar el reporte: {e}")

def agregar_estudiante():
   
    try:
        nombre = input("Nombre del estudiante: ").strip()
        if not nombre:
            print("El nombre no puede estar vacío")
            return
        
        calificacion = float(input("Calificación: "))
        if calificacion < 0 or calificacion > 100:
            print("La calificación debe estar entre 0 y 100")
            return
        
        
        with open("estudiantes.txt", "a") as archivo:
            archivo.write(f"{nombre},{calificacion}\n")
        
        print(f"Estudiante {nombre} agregado correctamente")
    
    except ValueError:
        print("Error: La calificación debe ser un número")
    except Exception as e:
        print(f"Error al agregar estudiante: {e}")

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*40)
    print("     GESTIÓN DE ESTUDIANTES")
    print("="*40)
    print("1. Ver promedio actual")
    print("2. Generar reporte completo")
    print("3. Agregar nuevo estudiante")
    print("4. Ver todos los estudiantes")
    print("5. Salir")
    print("="*40)

def main():
    
    
    try:
        open("estudiantes.txt", "a").close()
    except:
        pass
    
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            estudiantes = leer_estudiantes()
            if estudiantes:
                promedio = calcular_promedio(estudiantes)
                print(f"Promedio actual: {promedio:.1f}")
            else:
                print("No hay estudiantes registrados")
        
        elif opcion == "2":
            estudiantes = leer_estudiantes()
            if estudiantes:
                generar_reporte(estudiantes)
            else:
                print("No hay estudiantes para generar reporte")
        
        elif opcion == "3":
            agregar_estudiante()
        
        elif opcion == "4":
            estudiantes = leer_estudiantes()
            if estudiantes:
                print("\nLISTA DE ESTUDIANTES:")
                for nombre, calificacion in estudiantes:
                    print(f"{nombre}: {calificacion}")
            else:
                print("No hay estudiantes registrados")
        
        elif opcion == "5":
            print("¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()