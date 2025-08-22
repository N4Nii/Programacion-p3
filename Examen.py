#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPG de Consola (Aventura Larga con Combate de 3 Opciones)
---------------------------------------------------------
- Múltiples jugadores con nombre y rol (Gobierno, Narco, Puntero, Vecino)
- Guardia/carga en JSON
- Aventura de capítulos con narrativa variable por rol
- Combate consistente: 1) Atacar 2) Curarse 3) Usar objeto especial
- Inventario, botín, tienda opcional, descanso seguro
- XP, subida de nivel, logros

Ejecuta:
    python rpg_culiacan.py
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple

# =========================
# Colores ANSI (sin colorama)
# =========================
CLR_R = "\033[31m"   # Rojo
CLR_G = "\033[32m"   # Verde
CLR_Y = "\033[33m"   # Amarillo
CLR_B = "\033[34m"   # Azul
CLR_M = "\033[35m"   # Magenta
CLR_C = "\033[36m"   # Cian
CLR_W = "\033[37m"   # Blanco
CLR_RST = "\033[0m"  # Reset

# Desactiva colores si la terminal no los soporta (opcional)
def _supports_color() -> bool:
    try:
        # Windows 10+ y la mayoría de terminals modernas soportan ANSI
        return True
    except Exception:
        return False

if not _supports_color():
    CLR_R = CLR_G = CLR_Y = CLR_B = CLR_M = CLR_C = CLR_W = CLR_RST = ""

# =========================
# Config y Datos
# =========================
SAVE_FILE = "jugadores.json"
RNG = random.Random()

# Definiciones base por rol
ROLES = {
    "Gobierno": {
        "vida": 120, "ataque": (14, 22), "defensa": 3,
        "arsenal": ["Rifle de asalto", "Pistola"],
        "intro": "Eres parte de un operativo que intenta estabilizar la ciudad en medio de un día caótico."
    },
    "Narco": {
        "vida": 100, "ataque": (16, 24), "defensa": 1,
        "arsenal": ["Cuerno de chivo", "Pistola"],
        "intro": "Eres brazo armado de una facción que busca recuperar control y mercancía."
    },
    "Puntero": {
        "vida": 85, "ataque": (12, 18), "defensa": 0,
        "arsenal": ["Pistola", "Radio"],
        "intro": "Eres puntero: ojos y oídos en las entradas de la ciudad, sobreviviendo como puedes."
    },
    "Vecino": {
        "vida": 80, "ataque": (10, 16), "defensa": 0,
        "arsenal": ["Cuchillo", "Piedra"],
        "intro": "Eres un civil atrapado en el fuego cruzado; la prioridad es sobrevivir y ayudar si puedes."
    },
}

# Ítems y efectos
USABLES = {
    "botiquín": "Cura 30-45 HP.",
    "granada": "Daño fijo 35-45 al enemigo.",
    "molotov": "Daño 25-35 e incendio leve (sangrado leve del enemigo).",
    "chaleco": "Absorbe 6 de daño por 3 golpes enemigos.",
    "estimulante": "Aumenta ataque por 3 turnos (+5 al mínimo y máximo).",
    "cuchillo": "Golpe rápido (daño 12-18, no gasta munición).",
}

# Logros (se agregan al cumplir condiciones)
ACHIEVEMENTS = {
    "primer_combo": "Tu primera victoria en combate.",
    "nivel_3": "Has alcanzado el nivel 3.",
    "coleccionista": "Has acumulado 6+ objetos en el inventario.",
    "tres_capitulos": "Has superado 3 capítulos de la campaña.",
    "jefe_derrotado": "Venciste a un comandante enemigo."
}

# =========================
# Utilidades de E/S
# =========================
def clear():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

def pause(msg: str = "Pulsa ENTER para continuar..."):
    try:
        input(CLR_C + msg + CLR_RST)
    except EOFError:
        pass

def ask_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            n = int(raw)
            if lo <= n <= hi:
                return n
        print(CLR_Y + f"Ingresa un número válido [{lo}-{hi}]." + CLR_RST)

def ask_choice(prompt: str, options: List[str]) -> int:
    print(CLR_B + prompt + CLR_RST)
    for i, op in enumerate(options, 1):
        print(f"  {i}. {op}")
    return ask_int("> ", 1, len(options)) - 1

# =========================
# Modelo Jugador
# =========================
class Jugador:
    def __init__(
        self,
        nombre: str,
        rol: str,
        nivel: int = 1,
        xp: int = 0,
        vida: Optional[int] = None,
        inventario: Optional[Dict[str, int]] = None,
        arsenal: Optional[List[str]] = None,
        defensa: int = 0,
        buff_turnos: int = 0,
        chaleco_cargas: int = 0,
        capitulo: int = 0,
        logros: Optional[List[str]] = None,
    ):
        base = ROLES.get(rol, ROLES["Vecino"])
        self.nombre = nombre
        self.rol = rol
        self.nivel = nivel
        self.xp = xp
        self.vida_max = base["vida"] + (nivel - 1) * 20
        self.vida = vida if vida is not None else self.vida_max
        self.ataque_min, self.ataque_max = base["ataque"]
        self.defensa_base = base["defensa"]
        self.defensa_bono = defensa
        self.arsenal = arsenal[:] if arsenal else base["arsenal"][:]
        self.inventario = inventario.copy() if inventario else {
            "botiquín": 2, "granada": 1, "molotov": 0, "chaleco": 0,
            "estimulante": 0, "cuchillo": 1
        }
        self.buff_turnos = buff_turnos
        self.chaleco_cargas = chaleco_cargas
        self.capitulo = capitulo  # progreso de campaña
        self.logros = logros[:] if logros else []
        self._check_achievements_inventory()

    # --------- Cálculos de combate ----------
    def tirada_ataque(self) -> int:
        lo, hi = self.ataque_min, self.ataque_max
        if self.buff_turnos > 0:
            lo += 5
            hi += 5
        return RNG.randint(lo, hi)

    def recibir_daño(self, dmg: int) -> int:
        # Defensa pasiva
        dmg = max(0, dmg - self.defensa_base - self.defensa_bono)
        # Chaleco absorbe parte
        if self.chaleco_cargas > 0:
            absorb = min(6, dmg)
            dmg -= absorb
            self.chaleco_cargas -= 1
            print(CLR_Y + f"Chaleco absorbe {absorb}. Cargas restantes: {self.chaleco_cargas}." + CLR_RST)
        self.vida -= dmg
        return dmg

    def curarse(self, lo: int = 30, hi: int = 45) -> int:
        cur = RNG.randint(lo, hi)
        self.vida = min(self.vida_max, self.vida + cur)
        return cur

    def ganar_xp(self, cantidad: int):
        self.xp += cantidad
        while self.xp >= 100:
            self.xp -= 100
            self.nivel += 1
            self.vida_max += 20
            self.vida = self.vida_max
            self.ataque_min += 1
            self.ataque_max += 2
            print(CLR_G + f"🔼 {self.nombre} sube a nivel {self.nivel}! Vida restaurada." + CLR_RST)
            if self.nivel >= 3 and "nivel_3" not in self.logros:
                self.logros.append("nivel_3")
                print(CLR_G + f"🏅 Logro: {ACHIEVEMENTS['nivel_3']}" + CLR_RST)

    def add_item(self, clave: str, n: int = 1):
        self.inventario[clave] = self.inventario.get(clave, 0) + n
        self._check_achievements_inventory()

    def remove_item(self, clave: str, n: int = 1) -> bool:
        if self.inventario.get(clave, 0) >= n:
            self.inventario[clave] -= n
            if self.inventario[clave] <= 0:
                del self.inventario[clave]
            return True
        return False

    def _check_achievements_inventory(self):
        total = sum(self.inventario.values())
        if total >= 6 and "coleccionista" not in self.logros:
            self.logros.append("coleccionista")
            print(CLR_G + f"🏅 Logro: {ACHIEVEMENTS['coleccionista']}" + CLR_RST)

    # --------- Serialización ----------
    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "rol": self.rol,
            "nivel": self.nivel,
            "xp": self.xp,
            "vida": self.vida,
            "vida_max": self.vida_max,
            "ataque_min": self.ataque_min,
            "ataque_max": self.ataque_max,
            "defensa_base": self.defensa_base,
            "defensa_bono": self.defensa_bono,
            "arsenal": self.arsenal,
            "inventario": self.inventario,
            "buff_turnos": self.buff_turnos,
            "chaleco_cargas": self.chaleco_cargas,
            "capitulo": self.capitulo,
            "logros": self.logros,
        }

    @staticmethod
    def from_dict(d: dict) -> "Jugador":
        j = Jugador(
            nombre=d["nombre"],
            rol=d["rol"],
            nivel=d.get("nivel", 1),
            xp=d.get("xp", 0),
            vida=d.get("vida"),
            inventario=d.get("inventario", {}),
            arsenal=d.get("arsenal", []),
            defensa=d.get("defensa_bono", 0),
            buff_turnos=d.get("buff_turnos", 0),
            chaleco_cargas=d.get("chaleco_cargas", 0),
            capitulo=d.get("capitulo", 0),
            logros=d.get("logros", []),
        )
        # Reasignar valores si existen para compatibilidad
        j.vida_max = d.get("vida_max", j.vida_max)
        j.ataque_min = d.get("ataque_min", j.ataque_min)
        j.ataque_max = d.get("ataque_max", j.ataque_max)
        j.defensa_base = d.get("defensa_base", j.defensa_base)
        return j

# =========================
# Persistencia
# =========================
def guardar_jugadores(jugadores: List[Jugador], archivo: str = SAVE_FILE):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump([j.to_dict() for j in jugadores], f, ensure_ascii=False, indent=2)
    print(CLR_B + "💾 Progreso guardado." + CLR_RST)

def cargar_jugadores(archivo: str = SAVE_FILE) -> List[Jugador]:
    if not os.path.exists(archivo):
        return []
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Jugador.from_dict(d) for d in data]
    except Exception:
        return []

# =========================
# Enemigos y eventos
# =========================
def make_enemy(name: str, hp: int, atk: Tuple[int, int], xp: int, bleed: int = 0) -> Dict:
    return {"nombre": name, "vida": hp, "ataque": atk, "xp": xp, "sangrado": bleed}

def chapter_enemies_for_role(rol: str) -> List[Dict]:
    # Secuencia larga de la campaña (12+ encuentros potenciales)
    # Ajustes ligeros por rol a los nombres/HP
    mult = {"Gobierno": 1.0, "Narco": 1.05, "Puntero": 0.95, "Vecino": 0.9}.get(rol, 1.0)
    hp = lambda base: int(base * mult)

    return [
        make_enemy("Punteros rivales", hp(60), (8, 12), 30),
        make_enemy("Convoy ligero", hp(85), (10, 15), 45),
        make_enemy("Sicario en moto", hp(70), (12, 16), 40),
        make_enemy("Bloqueo callejero", hp(95), (12, 18), 55),
        make_enemy("Célula armada", hp(110), (14, 20), 70),
        make_enemy("Emboscada en barrio", hp(120), (15, 22), 80),
        make_enemy("Francotirador oculto", hp(90), (18, 26), 90),
        make_enemy("Blindada improvisada", hp(140), (16, 24), 110),
        make_enemy("Civiles armados", hp(130), (14, 22), 95),
        make_enemy("Patrulla agresiva", hp(135), (16, 25), 110),
        make_enemy("Jefe local", hp(160), (18, 28), 140),
        make_enemy("Comandante enemigo", hp(190), (20, 30), 180),
    ]

def role_line(rol: str, base: str) -> str:
    # Personaliza una línea según el rol para dar sabor narrativo
    if rol == "Gobierno":
        extra = "Te coordinarás por radio con tu unidad y solicitarás apoyo cuando sea posible."
    elif rol == "Narco":
        extra = "Tus jefes quieren resultados y poca atención; la discreción no siempre es opción."
    elif rol == "Puntero":
        extra = "Tienes ojos en la ciudad, pero pocos recursos si la cosa se complica."
    else:
        extra = "Tu prioridad es sobrevivir y ayudar sin llamar la atención."
    return f"{base} {extra}"

CHAPTER_TEXT = [
    "El cielo gris y el murmullo de sirenas anuncian que hoy nada será normal.",
    "A la altura de la avenida principal, un convoy bloquea el paso y el bullicio crece.",
    "Te internas por calles secundarias; una moto ronda con actitud sospechosa.",
    "Un camión atraviesa la calle y varios encapuchados bajan con prisa.",
    "En una esquina, ves a una célula moviéndose entre puestos y autos varados.",
    "Las fachadas esconden miradas; algo no cuadra y te preparas para lo peor.",
    "De un edificio cercano, un disparo preciso rompe el silencio por un segundo.",
    "Un vehículo improvisado con placas de metal ruge por la avenida adyacente.",
    "El rumor de pasos y voces tensas te alcanza en un callejón sin salida.",
    "Una patrulla recorre en zigzag como buscando provocar reacción.",
    "Al final del corredor urbano, alguien da órdenes con voz de mando.",
    "Todo desemboca en un patio improvisado convertido en cuartel enemigo.",
]

# =========================
# Combate (3 opciones constantes)
# =========================
def usar_objeto_especial(j: Jugador, enemigo: Dict) -> str:
    """
    Devuelve un mensaje de resultado. No cambia el turno del enemigo.
    """
    # Mostrar objetos usables disponibles
    disponibles = [k for k in USABLES.keys() if j.inventario.get(k, 0) > 0]
    if not disponibles:
        return CLR_Y + "No tienes objetos especiales disponibles." + CLR_RST

    idx = ask_choice(
        f"Elige objeto especial a usar (inventario {j.inventario}):",
        [f"{k} — {USABLES[k]}" for k in disponibles] + ["Cancelar"]
    )
    if idx == len(disponibles):  
        return CLR_Y + "Acción cancelada." + CLR_RST

    item = disponibles[idx]

   
    if item == "granada":
        if j.remove_item("granada", 1):
            daño = RNG.randint(35, 45)
            enemigo["vida"] -= daño
            return CLR_Y + f"💣 Lanzas una granada e infliges {daño} de daño." + CLR_RST

    if item == "molotov":
        if j.remove_item("molotov", 1):
            daño = RNG.randint(25, 35)
            enemigo["vida"] -= daño
            enemigo["sangrado"] = enemigo.get("sangrado", 0) + 2
            return CLR_Y + f"🔥 Lanzas un molotov: {daño} de daño e incendio leve (sangrado 2/turno)." + CLR_RST

    if item == "botiquín":
        if j.remove_item("botiquín", 1):
            cur = j.curarse(30, 45)
            return CLR_G + f"🩹 Usas un botiquín y recuperas {cur} de vida." + CLR_RST

    if item == "chaleco":
        if j.remove_item("chaleco", 1):
            j.chaleco_cargas += 3
            return CLR_C + "🧥 Te equipas un chaleco: absorberá 6 de daño por 3 golpes." + CLR_RST

    if item == "estimulante":
        if j.remove_item("estimulante", 1):
            j.buff_turnos += 3
            return CLR_M + "⚡ Te inyectas un estimulante: +5 de ataque por 3 turnos." + CLR_RST

    if item == "cuchillo":
       
        daño = RNG.randint(12, 18)
        enemigo["vida"] -= daño
        return CLR_Y + f"🔪 Golpe rápido con cuchillo: {daño} de daño." + CLR_RST

    return CLR_Y + "Nada sucede..." + CLR_RST

def combate(j: Jugador, enemigo: Dict) -> bool:
    """
    Combate por turnos. Devuelve True si el jugador gana, False si pierde/huye.
    Reglas:
      - Mismas 3 opciones en cada turno: Atacar / Curarte / Usar objeto especial
      - Efectos de sangrado se aplican al enemigo cada turno si existen
      - Estimulante dura 3 turnos (ataque aumentado)
      - Chaleco absorbe hasta 6 de daño en 3 golpes
    """
    print(CLR_R + f"\n💥 Enfrentamiento contra {enemigo['nombre']}!" + CLR_RST)
    turno = 1
    while j.vida > 0 and enemigo["vida"] > 0:
        print(CLR_W + f"\n— Turno {turno} —" + CLR_RST)
        print(f"{CLR_C}Tu vida: {j.vida}/{j.vida_max} | Enemigo: {enemigo['vida']} HP{CLR_RST}")

        
        print("1) Atacar    2) Curarte    3) Usar objeto especial")
        elec = ask_int("> ", 1, 3)

        if elec == 1:
            base = j.tirada_ataque()
            crit = 1.5 if RNG.random() < 0.15 else 1.0
            daño = int(base * crit)
            enemigo["vida"] -= daño
            nota = " (CRÍTICO)" if crit > 1.0 else ""
            print(CLR_G + f"Disparas con {random.choice(j.arsenal)} e infliges {daño} de daño{nota}." + CLR_RST)

        elif elec == 2:
            if j.inventario.get("botiquín", 0) > 0:
                j.remove_item("botiquín", 1)
                cur = j.curarse(30, 45)
                print(CLR_G + f"🩹 Te curas {cur} de vida. {j.vida}/{j.vida_max} HP." + CLR_RST)
            else:
                print(CLR_Y + "No tienes botiquines. Pierdes el turno intentando improvisar." + CLR_RST)

        else:
            msg = usar_objeto_especial(j, enemigo)
            print(msg)

       
        bleed = enemigo.get("sangrado", 0)
        if bleed > 0 and enemigo["vida"] > 0:
            enemigo["vida"] -= bleed
            print(CLR_R + f"Enemigo sufre {bleed} de daño por incendio/sangrado." + CLR_RST)

        
        if enemigo["vida"] <= 0:
            print(CLR_G + f"✅ {enemigo['nombre']} ha caído." + CLR_RST)
            j.ganar_xp(enemigo["xp"])
            if enemigo["nombre"].lower().startswith("comandante") and "jefe_derrotado" not in j.logros:
                j.logros.append("jefe_derrotado")
                print(CLR_G + f"🏅 Logro: {ACHIEVEMENTS['jefe_derrotado']}" + CLR_RST)
           
            loot_roll = RNG.random()
            if loot_roll < 0.35:
                j.add_item("botiquín", 1)
                print(CLR_C + "Encuentras un botiquín en el área." + CLR_RST)
            elif loot_roll < 0.55:
                j.add_item("granada", 1)
                print(CLR_C + "Encuentras una granada en una mochila." + CLR_RST)
            elif loot_roll < 0.70:
                j.add_item("molotov", 1)
                print(CLR_C + "Improvisas un molotov con lo que hay a mano." + CLR_RST)
            return True

        
        if j.vida > 0:
            e_lo, e_hi = enemigo["ataque"]
            daño_e = RNG.randint(e_lo, e_hi)
            recibido = j.recibir_daño(daño_e)
            print(CLR_R + f"{enemigo['nombre']} contraataca y te hace {recibido} de daño." + CLR_RST)

        
        if j.buff_turnos > 0:
            j.buff_turnos -= 1
            if j.buff_turnos == 0:
                print(CLR_M + "El efecto del estimulante se ha desvanecido." + CLR_RST)

        turno += 1

    
    if j.vida <= 0:
        print(CLR_R + f"\n💀 {j.nombre} ha sido derrotado... PERDISTE." + CLR_RST)
        
        j.vida = max(1, j.vida_max // 2)
        return False

    return True


def tienda(j: Jugador):
    print(CLR_M + "\n🛒 Puesto clandestino / Tienda improvisada" + CLR_RST)
    stock = [
        ("botiquín", 30), ("granada", 40), ("molotov", 35),
        ("chaleco", 50), ("estimulante", 45)
    ]
    print("Puedes intercambiar XP por suministros (1 XP = 1 crédito).")
    print(f"Tienes {j.xp} créditos (XP actuales).")
    while True:
        opts = [f"{k} ({c} cr) — {USABLES[k]}" for (k, c) in stock] + ["Salir"]
        idx = ask_choice("¿Qué deseas comprar?", opts)
        if idx == len(stock):
            break
        item, cost = stock[idx]
        if j.xp >= cost:
            j.xp -= cost
            j.add_item(item, 1)
            print(CLR_G + f"Compraste {item}. Créditos restantes: {j.xp}" + CLR_RST)
        else:
            print(CLR_Y + "No tienes suficientes créditos." + CLR_RST)

def descanso(j: Jugador):
    print(CLR_C + "\n🛏️ Zona segura improvisada. Decides descansar un momento." + CLR_RST)
    cur = RNG.randint(20, 35)
    j.vida = min(j.vida_max, j.vida + cur)
    print(CLR_G + f"Recuperas {cur} de vida. {j.vida}/{j.vida_max} HP." + CLR_RST)
    # Pequeña posibilidad de encontrar algo
    if RNG.random() < 0.25:
        j.add_item("botiquín", 1)
        print(CLR_C + "Mientras descansas, consigues un botiquín." + CLR_RST)

# =========================
# Campaña/Aventura
# =========================
def intro_rol(j: Jugador):
    print(CLR_M + f"\n=== {j.nombre} — {j.rol} (Nivel {j.nivel}) ===" + CLR_RST)
    base = ROLES.get(j.rol, ROLES["Vecino"])["intro"]
    print(role_line(j.rol, base))

def jugar_capitulo(j: Jugador, cap_idx: int) -> bool:
    # Mostrar narrativa del capítulo
    texto = CHAPTER_TEXT[cap_idx]
    print(CLR_Y + "\n" + texto + CLR_RST)

    # Opcional: cada 3 capítulos, ofrecer descanso o tienda
    if cap_idx in (2, 5, 8, 10):
        aux = ask_choice(
            "Antes de avanzar, ¿quieres hacer algo?",
            ["Seguir de inmediato", "Descansar (curarte)", "Tienda (intercambiar XP por objetos)"]
        )
        if aux == 1:
            descanso(j)
        elif aux == 2:
            tienda(j)

    enemigos = chapter_enemies_for_role(j.rol)
    enemigo = enemigos[cap_idx]
    return combate(j, enemigo)

def aventura_larga(j: Jugador):
    """
    Aventura de 12 capítulos. A cada jugador se le guarda el capítulo alcanzado
    para continuar en la próxima sesión. Las opciones de combate son siempre
    las mismas (Atacar / Curarte / Objeto especial).
    """
    intro_rol(j)

    total_caps = len(CHAPTER_TEXT)
    cap = j.capitulo  # desde dónde continua
    if cap == 0:
        print(CLR_C + "Comienzas el recorrido desde el inicio de la jornada..." + CLR_RST)
    else:
        print(CLR_C + f"Retomas la campaña desde el capítulo {cap+1}/{total_caps}." + CLR_RST)

    superados_en_esta_sesion = 0

    while cap < total_caps and j.vida > 0:
        exito = jugar_capitulo(j, cap)
        if exito:
            cap += 1
            superados_en_esta_sesion += 1
            j.capitulo = cap
            if superados_en_esta_sesion == 3 and "tres_capitulos" not in j.logros:
                j.logros.append("tres_capitulos")
                print(CLR_G + f"🏅 Logro: {ACHIEVEMENTS['tres_capitulos']}" + CLR_RST)
        else:
            # Derrota: no avanza capítulo, pero puede seguir intentando
            print(CLR_Y + "Te replegaste a un punto seguro. Podrás intentarlo otra vez." + CLR_RST)
            break

    if cap >= total_caps:
        print(CLR_G + f"\n🎉 ¡{j.nombre} completó la campaña! Nivel {j.nivel}, XP {j.xp}, Vida {j.vida}/{j.vida_max}" + CLR_RST)
        if "primer_combo" not in j.logros:
            j.logros.append("primer_combo")  # usar como 'campaña completa' si no se logró antes
    else:
        print(CLR_C + f"\nProgreso: Capítulo {cap}/{total_caps}. Puedes continuar más tarde." + CLR_RST)

# =========================
# Gestión de jugadores (menús)
# =========================
def crear_jugador() -> Jugador:
    clear()
    print(CLR_M + "=== Registrar Jugador ===" + CLR_RST)
    while True:
        nombre = input("Nombre: ").strip()
        if nombre:
            break
        print(CLR_Y + "El nombre no puede estar vacío." + CLR_RST)

    roles = list(ROLES.keys())
    idx = ask_choice("Elige un rol:", roles)
    rol = roles[idx]

    j = Jugador(nombre=nombre, rol=rol)
    print(CLR_G + f"Creado {j.nombre} ({j.rol}) — Vida {j.vida}/{j.vida_max}, Arsenal: {', '.join(j.arsenal)}" + CLR_RST)
    return j

def listar_jugadores(jugadores: List[Jugador]):
    if not jugadores:
        print(CLR_Y + "No hay jugadores guardados." + CLR_RST)
        return
    print(CLR_B + "\n=== Jugadores ===" + CLR_RST)
    for i, j in enumerate(jugadores, 1):
        print(f"{i}. {j.nombre} | Rol: {j.rol} | Nivel: {j.nivel} | Vida: {j.vida}/{j.vida_max} | XP: {j.xp} | Cap: {j.capitulo}/{len(CHAPTER_TEXT)}")
        if j.logros:
            print("   Logros: " + ", ".join(j.logros))

def seleccionar_jugador(jugadores: List[Jugador]) -> Optional[Jugador]:
    if not jugadores:
        print(CLR_Y + "No hay jugadores para seleccionar." + CLR_RST)
        return None
    listar_jugadores(jugadores)
    idx = ask_int("Elige número de jugador: ", 1, len(jugadores)) - 1
    return jugadores[idx]

def eliminar_jugador(jugadores: List[Jugador]) -> List[Jugador]:
    if not jugadores:
        print(CLR_Y + "No hay jugadores para eliminar." + CLR_RST)
        return jugadores
    listar_jugadores(jugadores)
    idx = ask_int("Elige número a eliminar: ", 1, len(jugadores)) - 1
    j = jugadores.pop(idx)
    print(CLR_R + f"Jugador {j.nombre} eliminado." + CLR_RST)
    return jugadores

def renombrar_jugador(jugadores: List[Jugador]):
    if not jugadores:
        print(CLR_Y + "No hay jugadores para renombrar." + CLR_RST)
        return
    listar_jugadores(jugadores)
    idx = ask_int("Elige número a renombrar: ", 1, len(jugadores)) - 1
    nuevo = input("Nuevo nombre: ").strip()
    if nuevo:
        jugadores[idx].nombre = nuevo
        print(CLR_G + "Nombre actualizado." + CLR_RST)

# =========================
# Menú principal
# =========================
def menu():
    jugadores = cargar_jugadores()
    while True:
        print(CLR_M + "\n=== MENÚ PRINCIPAL ===" + CLR_RST)
        print("1) Crear jugador")
        print("2) Ver jugadores")
        print("3) Jugar campaña con un jugador")
        print("4) Jugar campaña con TODOS los jugadores")
        print("5) Renombrar jugador")
        print("6) Eliminar jugador")
        print("7) Guardar y salir")

        op = ask_int("> ", 1, 7)
        if op == 1:
            j = crear_jugador()
            jugadores.append(j)
            guardar_jugadores(jugadores)
        elif op == 2:
            listar_jugadores(jugadores)
            pause()
        elif op == 3:
            j = seleccionar_jugador(jugadores)
            if j:
                aventura_larga(j)
                guardar_jugadores(jugadores)
                pause()
        elif op == 4:
            if not jugadores:
                print(CLR_Y + "No hay jugadores registrados." + CLR_RST)
                pause()
                continue
            for j in jugadores:
                print(CLR_W + f"\n>>> Jugando con {j.nombre}..." + CLR_RST)
                aventura_larga(j)
            guardar_jugadores(jugadores)
            pause()
        elif op == 5:
            renombrar_jugador(jugadores)
            guardar_jugadores(jugadores)
        elif op == 6:
            jugadores = eliminar_jugador(jugadores)
            guardar_jugadores(jugadores)
        else:
            guardar_jugadores(jugadores)
            print(CLR_C + "¡Hasta la próxima!" + CLR_RST)
            break

# =========================
# Main
# =========================
if __name__ == "__main__":
    try:
        clear()
        print(CLR_W + "RPG de Consola — Aventura de Culiacán (Texto Interactivo)\n" + CLR_RST)
        menu()
    except KeyboardInterrupt:
        print("\nSalida por teclado. Progreso auto-guardado (si hubo cambios).")

