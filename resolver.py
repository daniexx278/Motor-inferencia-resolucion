import os
from datetime import datetime

# ============================================================
#        FUNCIONES DE CARGA Y PARSEO DE LA BASE DE CONOCIMIENTO
# ============================================================

# Carga una base de conocimiento desde un archivo de texto en formato CNF.
def cargar_base_conocimiento(ruta_archivo):
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
#        FUNCIONES BÁSICAS DEL MOTOR DE RESOLUCIÓN LÓGICA
# ============================================================

# Determina si dos literales son complementarios (uno es la negación del otro).
def es_complementario(l1, l2):
    if l1.startswith("~") and not l2.startswith("~"):
        return l1[1:] == l2
    if l2.startswith("~") and not l1.startswith("~"):
        return l2[1:] == l1
    return False

# Aplica la regla de resolución entre dos cláusulas.
def resolver(cl1, cl2):
    resolventes = []
    for lit1 in cl1:
        for lit2 in cl2:
            if es_complementario(lit1, lit2):
                nueva = list(set([l for l in cl1 if l != lit1] + [l for l in cl2 if l != lit2]))
                # Se eliminan tautologías internas (P y ~P en la misma cláusula)
                if not any(es_complementario(a, b) for a in nueva for b in nueva if a != b):
                    resolventes.append(sorted(set(nueva)))
    return resolventes

# Verifica si una cláusula es vacía, lo que indica contradicción lógica.
def clausula_vacia(cl):
    return len(cl) == 0


# ============================================================
#        ALGORITMO PRINCIPAL DE RESOLUCIÓN POR REFUTACIÓN
# ============================================================

# Implementa el algoritmo de resolución basado en refutación.
def algoritmo_resolucion(KB):
    
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
                    print("\n Se ha obtenido la CLÁUSULA VACÍA ")
                    print("✅ La conclusión está demostrada por refutación.")
                    return True
                if r not in nuevas and r not in KB:
                    nuevas.append(r)

        # No se generaron nuevas cláusulas
        if not nuevas:
            print("\n❌ No se pudo demostrar la conclusión. No se obtuvo cláusula vacía.")
            return False

        for n in nuevas:
            KB.append(n)
        nuevas.clear()


# ============================================================
#        ALGORITMO DE UNIFICACIÓN DE VARIABLES (EXTENSIÓN)
# ============================================================

def unificar(x, y, sustitucion=None):
    """
    Implementa el algoritmo de unificación de variables simbólicas.
    Retorna un diccionario con las sustituciones necesarias para 
    igualar dos expresiones o None si no pueden unificarse.
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
    """
    Auxiliar de unificación: maneja casos en los que una variable debe 
    ser sustituida por otra constante o variable dentro del conjunto actual.
    """
    if var in sustitucion:
        return unificar(sustitucion[var], x, sustitucion)
    elif x in sustitucion:
        return unificar(var, sustitucion[x], sustitucion)
    elif var == x:
        return sustitucion
    else:
        sustitucion[var] = x
        return sustitucion


# ============================================================
#        UTILIDAD PARA GUARDAR RESULTADOS EN ARCHIVO
# ============================================================

def guardar_resultado(texto):
    """
    Guarda el resultado del proceso de inferencia en un archivo .txt 
    dentro del directorio /outputs, con fecha y hora del análisis.
    """
    os.makedirs("outputs", exist_ok=True)
    archivo_salida = f"outputs/resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write(texto)
    print(f"\n📝 Resultado guardado en: {archivo_salida}")


# ============================================================
#        FUNCIÓN PRINCIPAL DEL PROGRAMA
# ============================================================

def main():
    """
    Función principal del programa.
    - Solicita la ruta del archivo CNF.
    - Carga la base de conocimiento.
    - Ejecuta el proceso de resolución.
    - Muestra y guarda el resultado final.
    """
    print("=== MOTOR DE INFERENCIA BASADO EN RESOLUCIÓN ===")
    ruta = input("👉 Ingrese la ruta del archivo de base de conocimiento (.txt): ").strip()

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
#        EJECUCIÓN DIRECTA DEL PROGRAMA
# ============================================================

if __name__ == "__main__":
    main()
