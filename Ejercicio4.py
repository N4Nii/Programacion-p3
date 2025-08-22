import biblioteca as gestor
import buscador as buscador
import estadisticas as stats

def main():
    
    mi_biblioteca = gestor.crear_biblioteca()
    
    # Libros iniciales
    print(gestor.agregar_libro(mi_biblioteca, "Los miserables", "Victor Hugo", 1862, "Novela histórica"))
    print(gestor.agregar_libro(mi_biblioteca, "Fahrenheit 451", "Ray Bradbury", 1953, "Ciencia ficción"))
    print(gestor.agregar_libro(mi_biblioteca, "Hamlet", "William Shakespeare", 1603, "Tragedia"))
    print(gestor.agregar_libro(mi_biblioteca, "Matar a un ruiseñor", "Harper Lee", 1960, "Novela social"))
    
    # Marcar algunos como leídos
    print(gestor.marcar_leido(mi_biblioteca, 1))
    print(gestor.marcar_leido(mi_biblioteca, 3))
    
    # Mostrar lista de libros
    print("\n" + gestor.mostrar_libros(mi_biblioteca))
    
    # Buscar un autor (en minúsculas para que coincida con la lógica del buscador)
    print(buscador.mostrar_resultados(buscador.buscar_por_autor(mi_biblioteca, "bradbury")))
    
    # Mostrar estadísticas
    print(stats.mostrar_estadisticas(mi_biblioteca))
    
    # Menú interactivo
    while True:
        print("\n--- GESTIÓN DE BIBLIOTECA PERSONAL ---")
        print("1. Agregar libro")
        print("2. Marcar libro como leído")
        print("3. Buscar por título")
        print("4. Buscar por autor")
        print("5. Ver todos los libros")
        print("6. Ver estadísticas")
        print("7. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            titulo = input("Título: ")
            autor = input("Autor: ")
            año = input("Año: ")
            genero = input("Género: ")
            print(gestor.agregar_libro(mi_biblioteca, titulo, autor, año, genero))
        
        elif opcion == "2":
            print(gestor.mostrar_libros(mi_biblioteca))
            try:
                id_libro = int(input("ID del libro a marcar como leído: "))
                print(gestor.marcar_leido(mi_biblioteca, id_libro))
            except:
                print("ID inválido")
        
        elif opcion == "3":
            titulo = input("Título a buscar: ")
            resultados = buscador.buscar_por_titulo(mi_biblioteca, titulo)
            print(buscador.mostrar_resultados(resultados))
        
        elif opcion == "4":
            autor = input("Autor a buscar: ")
            resultados = buscador.buscar_por_autor(mi_biblioteca, autor)
            print(buscador.mostrar_resultados(resultados))
        
        elif opcion == "5":
            print(gestor.mostrar_libros(mi_biblioteca))
        
        elif opcion == "6":
            print(stats.mostrar_estadisticas(mi_biblioteca))
        
        elif opcion == "7":
            print("¡Hasta pronto!")
            break
        
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()
