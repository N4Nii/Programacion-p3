
import numpy as np

def ingresar_matriz(nombre):
    """Función simplificada para ingresar matrices"""
    print(f"\nIngrese la matriz {nombre} (filas separadas por ';' y elementos por espacios):")
    print("Ejemplo: '1 2 3; 4 5 6' para una matriz 2x3")
    while True:
        try:
            datos = input(f"Matriz {nombre}: ").split(';')
            matriz = [list(map(float, fila.split())) for fila in datos]
            return np.array(matriz)
        except ValueError:
            print("Error: Formato incorrecto. Intente nuevamente.")

def main():
    print("Calculadora Matricial Simplificada")
    ops = {
        '1': ('Suma', lambda a, b: a + b, True),
        '2': ('Resta ', lambda a, b: a - b, True),
        '3': ('Multiplicación ', lambda a, b: a @ b, True),
        '4': ('Transposición ', lambda a, _: a.T, False),
    
        '5': ('Salir', None, False)
    }
    
    while True:
        print("\nOperaciones disponibles:")
        for i, j in ops.items():
            print(f"{i}. {j[0]}")
        
        op = input("Seleccione (1-5): ")
        
        if op == '5':
            print("¡Hasta luego!")
            break
            
        if op not in ops:
            print("Opción no válida")
            continue
            
        try:
            if ops[op][2]: 
                A = ingresar_matriz("A")
                B = ingresar_matriz("B")
                resultado = ops[op][1](A, B)
            else:  
                A = ingresar_matriz("A")
                resultado = ops[op][1](A, None)
                
            print("\nResultado:")
            print(resultado)
            
        except ValueError as e:
            print(f"Error en dimensiones: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()