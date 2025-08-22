
def mostrar_resultado(promedio):
    print(f"\n Promedio final: {promedio:.2f}")
    if promedio >= 8:
        print(" Excelente trabajo")
    elif promedio >= 6:
        print(" Aprobado")
    else:
        print("Reprobado")