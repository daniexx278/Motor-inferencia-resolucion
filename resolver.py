"""
============================================================
MOTOR DE INFERENCIA BASADO EN RESOLUCIÓN Y UNIFICACIÓN
============================================================

Implementa un motor de inferencia lógica mediante el algoritmo de
resolución por refutación, capaz de manejar predicados con variables
mediante unificación. Se utiliza una base de conocimiento en forma
normal conjuntiva (CNF) cargada desde un archivo .txt o .cnf.

El sistema combina cláusulas con literales complementarios (por ejemplo,
P y ~P) considerando las sustituciones necesarias entre variables y
constantes. Si se deriva la cláusula vacía, se demuestra la conclusión.
"""

import os
from datetime import datetime
import re


# ============================================================
#  FUNCIONES DE CARGA Y PARSEO DE LA BASE DE CONOCIMIENTO
# ============================================================

def cargar_base_conocimiento(ruta_archivo):
    """Carga la base de conocimiento desde un archivo de texto (.cnf/.txt)."""
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
    
    clausulas = []
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            clausula = [lit.strip() for lit in linea.replace("∨", "|").split("|")]
            clausulas.append(clausula)
    return clausulas


# ============================================================
#  FUNCIONES AUXILIARES DE PARSEO Y UNIFICACIÓN
# ============================================================

def parsear_literal(lit):
    """
    Divide un literal en (signo, predicado, argumentos[]).
    Ejemplo: ~Odia(Marco,Cesar) → ('~', 'Odia', ['Marco','Cesar'])
    """
    signo = "~" if lit.startswith("~") else ""
    contenido = lit[1:] if signo else lit
    match = re.match(r"([A-Za-z_][A-Za-z_0-9]*)\((.*)\)", contenido)
    if match:
        predicado = match.group(1)
        args = [a.strip() for a in match.group(2).split(",")] if match.group(2) else []
        return signo, predicado, args
    return signo, contenido, []


def unificar(x, y, sustitucion=None):
    """
    Algoritmo de unificación de términos.
    Retorna un diccionario de sustituciones o None si no pueden unificarse.
    """
    if sustitucion is None:
        sustitucion = {}
    if x == y:
        return sustitucion
    if isinstance(x, str) and x.islower():
        return _unificar_variable(x, y, sustitucion)
    if isinstance(y, str) and y.islower():
        return _unificar_variable(y, x, sustitucion)
    if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        for xi, yi in zip(x, y):
            sustitucion = unificar(xi, yi, sustitucion)
            if sustitucion is None:
                return None
        return sustitucion
    return None


def _unificar_variable(var, x, sustitucion):
    """Apoya la unificación reemplazando variables según el contexto actual."""
    if var in sustitucion:
        return unificar(sustitucion[var], x, sustitucion)
    elif x in sustitucion:
        return unificar(var, sustitucion[x], sustitucion)
    elif var == x:
        return sustitucion
    else:
        sustitucion[var] = x
        return sustitucion


def aplicar_sustitucion(literal, sustitucion):
    """Aplica una sustitución de variables sobre un literal."""
    signo, pred, args = parsear_literal(literal)
    nuevos_args = [sustitucion.get(a, a) for a in args]
    if args:
        return f"{signo}{pred}({','.join(nuevos_args)})"
    return literal


# ============================================================
#  FUNCIONES PRINCIPALES DEL MOTOR DE RESOLUCIÓN
# ============================================================

def son_complementarios(l1, l2):
    """
    Determina si dos literales son complementarios considerando unificación.
    """
    s1, p1, a1 = parsear_literal(l1)
    s2, p2, a2 = parsear_literal(l2)
    if p1 != p2:
        return False, None
    if s1 == s2:
        return False, None
    sustitucion = unificar(a1, a2)
    return (sustitucion is not None), sustitucion


def resolver(cl1, cl2):
    """
    Aplica la regla de resolución entre dos cláusulas con posible unificación.
    Devuelve una lista de nuevas cláusulas resolventes.
    """
    resolventes = []
    for lit1 in cl1:
        for lit2 in cl2:
            comp, sustitucion = son_complementarios(lit1, lit2)
            if comp:
                nueva = [aplicar_sustitucion(l, sustitucion) for l in cl1 if l != lit1] + \
                        [aplicar_sustitucion(l, sustitucion) for l in cl2 if l != lit2]
                nueva = sorted(set(nueva))
                if not any(son_complementarios(a, b)[0] for a in nueva for b in nueva if a != b):
                    resolventes.append(nueva)
    return resolventes


def clausula_vacia(cl):
    """Verifica si una cláusula es vacía."""
    return len(cl) == 0


def algoritmo_resolucion(KB):
    """
    Ejecuta el proceso de resolución paso a paso hasta hallar contradicción.
    Muestra el progreso en consola y devuelve True si se demuestra la conclusión.
    """
    nuevas = []
    paso = 1
    print("\n=== INICIO DEL PROCESO DE RESOLUCIÓN ===")

    while True:
        pares = [(KB[i], KB[j]) for i in range(len(KB)) for j in range(i + 1, len(KB))]
        for (ci, cj) in pares:
            resolventes = resolver(ci, cj)
            for r in resolventes:
                print(f"Paso {paso}: resolviendo {ci} con {cj} => {r}")
                paso += 1
                if clausula_vacia(r):
                    print("\n⚡ Se ha obtenido la CLÁUSULA VACÍA ⚡")
                    print("✅ La conclusión está demostrada por refutación.")
                    return True
                if r not in nuevas and r not in KB:
                    nuevas.append(r)

        if not nuevas:
            print("\n❌ No se pudo demostrar la conclusión. No se obtuvo cláusula vacía.")
            return False

        for n in nuevas:
            KB.append(n)
        nuevas.clear()


# ============================================================
#  UTILIDAD PARA GUARDAR RESULTADOS EN ARCHIVO
# ============================================================

def guardar_resultado(texto):
    """Guarda el resultado del proceso en un archivo dentro de /outputs."""
    os.makedirs("outputs", exist_ok=True)
    archivo_salida = f"outputs/resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write(texto)
    print(f"\n📝 Resultado guardado en: {archivo_salida}")


# ============================================================
#  FUNCIÓN PRINCIPAL
# ============================================================

def main():
    """Punto de entrada del programa."""
    print("=== MOTOR DE INFERENCIA BASADO EN RESOLUCIÓN ===")
    ruta = input("👉 Ingrese la ruta del archivo de base de conocimiento (.txt o .cnf): ").strip()

    try:
        KB = cargar_base_conocimiento(ruta)
        print("\nBase de conocimiento cargada correctamente:")
        for i, c in enumerate(KB, 1):
            print(f"{i}: {c}")

        print("\n-------------------------------------------------")
        resultado = algoritmo_resolucion(KB)
        texto_resultado = f"Resultado final: {'DEMONSTRADO ✅' if resultado else 'NO DEMOSTRADO ❌'}"
        print("\n" + texto_resultado)
        guardar_resultado(texto_resultado)

    except Exception as e:
        print(f"Error: {e}")


# ============================================================
#  EJECUCIÓN DIRECTA
# ============================================================

if __name__ == "__main__":
    main()
