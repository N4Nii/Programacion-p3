
import Bibliotecas as gestor
import Buscador as buscador
import Estadisticas as stats

def main():
    
    mi_biblioteca = gestor.crear_biblioteca()
    
  
    print(gestor.agregar_libro(mi_biblioteca, "Don Quijote de la Mancha", "Miguel de Cervantes", 1605, "Novela"))
    print(gestor.agregar_libro(mi_biblioteca, "La Odisea", "Homero", -800, "Épica"))
    print(gestor.agregar_libro(mi_biblioteca, "Orgullo y prejuicio", "Jane Austen", 1813, "Novela romántica"))
    print(gestor.agregar_libro(mi_biblioteca, "El señor de los anillos", "J.R.R. Tolkien", 1954, "Fantasía"))
    
   
    print(gestor.marcar_leido(mi_biblioteca, 1))
    print(gestor.marcar_leido(mi_biblioteca, 3))
    

    print("\n" + gestor.mostrar_libros(mi_biblioteca))
    
    
    print(buscador.mostrar_resultados(buscador.buscar_por_autor(mi_biblioteca, "Tolkien")))
    
   
    print(stats.mostrar_Estadisticas(mi_biblioteca))
    
  
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
            print(stats.mostrar_Estadisticas(mi_biblioteca))
        
        elif opcion == "7":
            print("¡Hasta pronto!")
            break
        
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()