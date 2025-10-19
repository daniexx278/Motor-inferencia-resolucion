# ==============================================================
# MOTOR DE INFERENCIA BASADO EN RESOLUCIÓN - PYTHON
# --------------------------------------------------------------
# Autor: Daniel Bohorquez
# Descripción: Implementa el método de resolución por refutación
# para demostrar conclusiones lógicas a partir de una base de conocimiento.
# Incluye unificación de variables y control de redundancias.
# ==============================================================

import itertools
import datetime
import os

# --------------------------------------------------------------
# Función: cargar_base_conocimiento
# Carga y convierte las cláusulas desde un archivo .txt o .cnf
# --------------------------------------------------------------
def cargar_base_conocimiento(ruta_archivo):
    base = []
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("#"):
                clausula = [literal.strip() for literal in linea.replace("∨", "v").split(" v ")]
                base.append(clausula)
    return base

# --------------------------------------------------------------
# Función: es_literal_negado
# Devuelve True si el literal comienza con '~'
# --------------------------------------------------------------
def es_literal_negado(literal):
    return literal.startswith("~")

# --------------------------------------------------------------
# Función: literal_opuesto
# Devuelve el literal negado correspondiente
# --------------------------------------------------------------
def literal_opuesto(literal):
    return literal[1:] if es_literal_negado(literal) else "~" + literal

# --------------------------------------------------------------
# Función: obtener_predicado_y_args
# Extrae el nombre del predicado y sus argumentos
# --------------------------------------------------------------
def obtener_predicado_y_args(literal):
    nombre = literal.replace("~", "")
    if "(" not in nombre:
        return nombre, []
    pred, args = nombre.split("(", 1)
    args = args.replace(")", "").split(",")
    return pred.strip(), [a.strip() for a in args]

# --------------------------------------------------------------
# Función: es_variable
# Determina si el término es una variable (minúscula)
# --------------------------------------------------------------
def es_variable(t):
    return t and t[0].islower()

# --------------------------------------------------------------
# Función: unificar
# Realiza la unificación de términos con variables
# --------------------------------------------------------------
def unificar(lit1, lit2):
    if lit1 == lit2:
        return {}
    if es_literal_negado(lit1) != es_literal_negado(lit2):
        return {}
    nombre1, args1 = obtener_predicado_y_args(lit1)
    nombre2, args2 = obtener_predicado_y_args(lit2)
    if nombre1 != nombre2 or len(args1) != len(args2):
        return None
    sustituciones = {}
    for a1, a2 in zip(args1, args2):
        if a1 != a2:
            if es_variable(a1):
                sustituciones[a1] = a2
            elif es_variable(a2):
                sustituciones[a2] = a1
            else:
                return None
    return sustituciones

# --------------------------------------------------------------
# Función: aplicar_sustitucion
# Aplica las sustituciones a todos los literales de una cláusula
# --------------------------------------------------------------
def aplicar_sustitucion(clausula, sustituciones):
    if not sustituciones:
        return clausula
    nueva = []
    for literal in clausula:
        for var, val in sustituciones.items():
            literal = literal.replace(var, val)
        nueva.append(literal)
    return nueva

# --------------------------------------------------------------
# Función: resolver
# Realiza la resolución entre dos cláusulas eliminando redundancias
# --------------------------------------------------------------
def resolver(cl1, cl2):
    for lit1 in cl1:
        for lit2 in cl2:
            if literal_opuesto(lit1).split("(")[0] == lit2.split("(")[0] or literal_opuesto(lit2).split("(")[0] == lit1.split("(")[0]:
                sustituciones = unificar(lit1, literal_opuesto(lit2))
                if sustituciones is not None:
                    nueva = [
                        l for l in aplicar_sustitucion(cl1 + cl2, sustituciones)
                        if l not in [lit1, lit2, literal_opuesto(lit1), literal_opuesto(lit2)]
                    ]
                    nueva = list(set(nueva))
                    if not any(literal_opuesto(x) in nueva for x in nueva):  # evita tautologías
                        return nueva
    return None

# --------------------------------------------------------------
# Función principal: main
# Ejecuta el motor de resolución paso a paso (Opción 1 simplificada)
# --------------------------------------------------------------
def main():
    print("=== MOTOR DE INFERENCIA BASADO EN RESOLUCIÓN ===")
    ruta = input("👉 Ingrese la ruta del archivo de base de conocimiento (.txt o .cnf): ").strip()

    base = cargar_base_conocimiento(ruta)
    print("\nBase de conocimiento cargada correctamente:")
    for i, c in enumerate(base, 1):
        print(f"{i}: {c}")

    print("\n-------------------------------------------------\n")
    print("=== INICIO DEL PROCESO DE RESOLUCIÓN ===")

    pasos = 0
    nuevas = list(base)
    vistos = set()  # evita resoluciones duplicadas

    while True:
        pares = list(itertools.combinations(nuevas, 2))
        generado = []

        for (c1, c2) in pares:
            clave = (tuple(sorted(c1)), tuple(sorted(c2)))
            if clave in vistos:
                continue
            vistos.add(clave)

            resolvente = resolver(c1, c2)
            if resolvente is not None:
                pasos += 1
                print(f"Paso {pasos}: resolviendo {c1} con {c2} => {resolvente}")

                if resolvente == []:
                    print("\n⚡ Se ha obtenido la CLÁUSULA VACÍA ⚡")
                    print("✅ La conclusión está demostrada por refutación.\n")
                    guardar_resultado(ruta, True, pasos)
                    return

                if resolvente not in nuevas and resolvente not in generado:
                    generado.append(resolvente)

        if not generado:
            print("\n❌ No se pudo demostrar la conclusión.\n")
            guardar_resultado(ruta, False, pasos)
            return

        nuevas.extend(generado)

# --------------------------------------------------------------
# Función: guardar_resultado
# Guarda el resultado en outputs/resultado_<nombre_base>.txt
# --------------------------------------------------------------
def guardar_resultado(ruta_base, demostrado, pasos):
    nombre_base = os.path.splitext(os.path.basename(ruta_base))[0]
    os.makedirs("outputs", exist_ok=True)
    ruta_salida = f"outputs/resultado_{nombre_base}.txt"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("=== RESULTADO DE LA RESOLUCIÓN ===\n\n")
        f.write(f"Base: {nombre_base}\n")
        f.write(f"Pasos realizados: {pasos}\n")
        f.write(f"Resultado final: {'DEMONSTRADO ✅' if demostrado else 'NO DEMOSTRADO ❌'}\n")
    print(f"📝 Resultado guardado en: {ruta_salida}")

# --------------------------------------------------------------
# Ejecución directa del programa
# --------------------------------------------------------------
if __name__ == "__main__":
    main()
