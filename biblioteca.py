
def crear_biblioteca():
    return {"libros": [], "contador": 0}

def agregar_libro(bib, titulo, autor, año, genero):
    bib["contador"] += 1
    libro = {
        "id": bib["contador"],
        "titulo": titulo,
        "autor": autor,
        "año": año,
        "genero": genero,
        "leido": False
    }
    bib["libros"].append(libro)
    return f"'{titulo}' agregado (ID: {bib['contador']})"

def marcar_leido(bib, id_libro):
    for libro in bib["libros"]:
        if libro["id"] == id_libro:
            libro["leido"] = True
            return f"'{libro['titulo']}' marcado como leído"
    return "Libro no encontrado"

def mostrar_libros(bib):
    if not bib["libros"]:
        return "No hay libros"
    
    resultado = "LIBROS:\n"
    for libro in bib["libros"]:
        estado = "✓" if libro["leido"] else "✗"
        resultado += f"{libro['id']}. {libro['titulo']} - {libro['autor']} ({estado})\n"
    return resultado