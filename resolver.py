import os
import itertools

# -------------------------
# Parser / carga de CNF
# -------------------------
def cargar_base_conocimiento(ruta):
    kb = []
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            # admitir ' v ' o '|' o ' v' etc.
            linea_norm = linea.replace("∨", " v ").replace("|", " v ")
            literales = [lit.strip() for lit in linea_norm.split(" v ") if lit.strip()]
            kb.append(literales)
    return kb

# -------------------------
# Operaciones con literales
# -------------------------
def es_negado(lit):
    return lit.startswith("~")

def opuesto(lit):
    return lit[1:] if es_negado(lit) else "~" + lit

def pred_y_args(lit):
    """
    Extrae el nombre del predicado en minúscula + lista de argumentos.
    Ej: ~Mata(x,F(y)) -> ('mata', ['x','F(y)'])
    """
    s = lit[1:] if es_negado(lit) else lit
    if "(" not in s:
        return s.strip().lower(), []   # predicado normalizado a minúscula
    pred, rest = s.split("(", 1)
    args = rest.rstrip(")").split(",") if rest.rstrip(")") else []
    return pred.strip().lower(), [a.strip() for a in args]

def es_variable(t):
    """Una variable es una cadena que empieza en minúscula."""
    return bool(t) and t[0].islower()

def is_var(t):
    return es_variable(t)

# -------------------------
# Unificación con soporte de funciones
# -------------------------
def descomponer_funcion(t):
    """
    Detecta términos funcionales tipo F(x,y) y retorna (nombre, [args]).
    Si no es función, retorna (t, None)
    """
    if "(" in t and t.endswith(")"):
        fname, inner = t.split("(", 1)
        args = [a.strip() for a in inner[:-1].split(",")]
        return fname.strip(), args
    return t, None

def unify_var(var, x, theta):
    if var in theta:
        return unificar_term(theta[var], x, theta)
    if x in theta:
        return unificar_term(var, theta[x], theta)
    # occurs-check no implementado (entrada simple)
    theta2 = dict(theta)
    theta2[var] = x
    return theta2

def unificar_term(x, y, theta):
    if theta is None:
        return None
    if x == y:
        return theta
    if is_var(x):
        return unify_var(x, y, theta)
    if is_var(y):
        return unify_var(y, x, theta)

    fx, x_args = descomponer_funcion(x)
    fy, y_args = descomponer_funcion(y)

    # Unificación estructural de funciones f(x1,..) y f(y1,..)
    if x_args is not None and y_args is not None and fx == fy and len(x_args) == len(y_args):
        for xa, ya in zip(x_args, y_args):
            theta = unificar_term(xa, ya, theta)
            if theta is None:
                return None
        return theta

    return None

def unificar_args(a_list, b_list, theta=None):
    if theta is None:
        theta = {}
    if len(a_list) != len(b_list):
        return None
    for a, b in zip(a_list, b_list):
        theta = unificar_term(a, b, theta)
        if theta is None:
            return None
    return theta

# -------------------------
# Unificar literales
# -------------------------
def unificar_literales(l1, l2):
    # deben tener mismo predicado y signos opuestos
    s1 = es_negado(l1)
    s2 = es_negado(l2)
    if s1 == s2:
        return None
    p1, a1 = pred_y_args(l1)
    p2, a2 = pred_y_args(l2)
    if p1 != p2 or len(a1) != len(a2):
        return None
    theta = unificar_args(a1, a2, {})
    return theta

def aplicar_theta_literal(lit, theta):
    pred, args = pred_y_args(lit)
    if not args:
        return lit
    new_args = [theta.get(a, a) for a in args]
    pref = "~" if es_negado(lit) else ""
    return f"{pref}{pred}({','.join(new_args)})"

def aplicar_theta_clausula(clausula, theta):
    return [aplicar_theta_literal(l, theta) for l in clausula]

# -------------------------
# Generar resolvente con unificación
# -------------------------
def generar_resolventes(meta1, meta2):
    cl1 = meta1['lit']
    cl2 = meta2['lit']
    resolventes = []
    for l1 in cl1:
        for l2 in cl2:
            theta = unificar_literales(l1, l2)
            if theta is not None:
                c1_sub = aplicar_theta_clausula(cl1, theta)
                c2_sub = aplicar_theta_clausula(cl2, theta)
                l1_ap = aplicar_theta_literal(l1, theta)
                l2_ap = aplicar_theta_literal(l2, theta)
                nueva = [x for x in c1_sub if x != l1_ap] + [x for x in c2_sub if x != l2_ap]
                nueva_norm = sorted(set(nueva))
                taut = False
                for a in nueva_norm:
                    if opuesto(a) in nueva_norm:
                        taut = True
                        break
                if not taut:
                    resolventes.append({
                        'lit': nueva_norm,
                        'padres': (meta1['id'], meta2['id']),
                        'resol_lits': (l1, l2),
                        'theta': theta
                    })
    return resolventes

# -------------------------
# Búsqueda dirigida
# -------------------------
def buscar_resolucion(kb_meta):
    claus_set = { tuple(sorted(m['lit'])): m['id'] for m in kb_meta }
    next_id = max(m['id'] for m in kb_meta) + 1

    unidades = [m for m in kb_meta if len(m['lit']) == 1]
    pares_prioritarios = []
    for u in unidades:
        for other in kb_meta:
            if u['id'] != other['id']:
                pares_prioritarios.append((u, other))

    procesados = set()
    cola = pares_prioritarios + list(itertools.combinations(kb_meta, 2))

    for (a, b) in cola:
        idpair = tuple(sorted((a['id'], b['id'])))
        if idpair in procesados:
            continue
        procesados.add(idpair)
        resolvs = generar_resolventes(a, b)
        for rmeta in resolvs:
            key = tuple(sorted(rmeta['lit']))
            if key in claus_set:
                continue
            rmeta['id'] = next_id
            next_id += 1
            claus_set[key] = rmeta['id']
            kb_meta.append(rmeta)
            if len(rmeta['lit']) == 0:
                return rmeta, kb_meta

    # Exploración BFS extendida
    max_iter = 10000
    it = 0
    while it < max_iter:
        it += 1
        n = len(kb_meta)
        nuevos_pares = []
        for i in range(n):
            for j in range(i+1, n):
                idpair = tuple(sorted((kb_meta[i]['id'], kb_meta[j]['id'])))
                if idpair in procesados:
                    continue
                procesados.add(idpair)
                nuevos_pares.append((kb_meta[i], kb_meta[j]))
        if not nuevos_pares:
            break
        for (a,b) in nuevos_pares:
            resolvs = generar_resolventes(a,b)
            for rmeta in resolvs:
                key = tuple(sorted(rmeta['lit']))
                if key in claus_set:
                    continue
                rmeta['id'] = next_id
                next_id += 1
                claus_set[key] = rmeta['id']
                kb_meta.append(rmeta)
                if len(rmeta['lit']) == 0:
                    return rmeta, kb_meta
    return None, kb_meta

# -------------------------
# Reconstrucción de prueba
# -------------------------
def reconstruir_prueba(meta_vacia, kb_meta):
    id_map = {m['id']: m for m in kb_meta}
    pasos = []
    visit = set()
    def dfs(meta):
        if meta['padres'] is None:
            return
        pid1, pid2 = meta['padres']
        m1 = id_map[pid1]
        m2 = id_map[pid2]
        if pid1 not in visit:
            dfs(m1)
        if pid2 not in visit:
            dfs(m2)
        pasos.append({
            'resol_id': meta['id'],
            'padres': (pid1, pid2),
            'resol_lits': meta.get('resol_lits'),
            'theta': meta.get('theta'),
            'clausula': meta['lit']
        })
        visit.add(meta['id'])
    dfs(meta_vacia)
    return pasos

# -------------------------
# Impresión de prueba
# -------------------------
def imprimir_prueba(pasos, kb_meta):
    id_map = {m['id']: m for m in kb_meta}
    for i, paso in enumerate(pasos, 1):
        pid1, pid2 = paso['padres']
        c1 = id_map[pid1]['lit']
        c2 = id_map[pid2]['lit']
        resolv = paso['clausula']
        theta = paso.get('theta') or {}

        print(f"Paso {i}: resolviendo {c1} con {c2}")
        if theta:
            print(f"       θ = {theta}")
        print(f"       => {resolv}\n")
    print(" Se ha obtenido la CLÁUSULA VACÍA ")
    print(" La conclusión está demostrada por refutación.\n")

# -------------------------
# Guardar resultado 
# -------------------------
def guardar_resultado(ruta_base, pasos_count, demostrado):
    nombre = os.path.splitext(os.path.basename(ruta_base))[0]
    os.makedirs("outputs", exist_ok=True)
    ruta_salida = f"outputs/resultado_{nombre}.txt"

    # Leer la última cláusula del archivo original para reconstruir la conclusión
    with open(ruta_base, "r", encoding="utf-8") as f:
        lineas = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    ultima_clausula = lineas[-1] if lineas else ""
    
    # Si la última cláusula es una negación unitaria (~Pred(...))
    conclusion_texto = ""
    if ultima_clausula.startswith("~") and " v " not in ultima_clausula and "|" not in ultima_clausula:
        # Quitamos la negación para formar la conclusión afirmativa
        conclusion_pred = ultima_clausula[1:]
        conclusion_texto = conclusion_pred
    else:
        # Si no es negación unitaria, usamos la cláusula tal cual
        conclusion_texto = ultima_clausula

    # Armar texto final dinámico
    if demostrado:
        conclusion_logica = (
            "\nConclusión lógica:\n"
            f"La negación de la conclusión no es consistente con la base de conocimiento.\n"
            f"Por tanto, se confirma que {conclusion_texto} ✅\n"
        )
    else:
        conclusion_logica = (
            "\nConclusión lógica:\n"
            f"No se pudo demostrar que {conclusion_texto} ❌\n"
        )

    # Guardar resultado
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("=== RESULTADO DE LA RESOLUCIÓN ===\n\n")
        f.write(f"Base: {nombre}\n")
        f.write(f"Pasos en la prueba: {pasos_count}\n")
        f.write(f"Resultado final: {'DEMONSTRADO ✅' if demostrado else 'NO DEMOSTRADO ❌'}\n")
        f.write(conclusion_logica)

    print(f"📝 Resultado guardado en: {ruta_salida}")


# -------------------------
# MAIN
# -------------------------
def main():
    print("=== MOTOR DE INFERENCIA BASADO EN RESOLUCIÓN ===")
    ruta = input(" Ingrese la ruta del archivo de base de conocimiento (.txt): ").strip()
    kb = cargar_base_conocimiento(ruta)
    kb_meta = []
    cid = 1
    for claus in kb:
        kb_meta.append({
            'id': cid,
            'lit': sorted(set(claus)),
            'padres': None,
            'resol_lits': None,
            'theta': None
        })
        cid += 1
    meta_vacia, kb_meta = buscar_resolucion(kb_meta)
    if meta_vacia is None:
        print("\n❌ No se pudo demostrar la conclusión (no se halló cláusula vacía).\n")
        guardar_resultado(ruta, 0, False)
        return
    pasos = reconstruir_prueba(meta_vacia, kb_meta)
    imprimir_prueba(pasos, kb_meta)
    guardar_resultado(ruta, len(pasos), True)

# -------------------------
# run
# -------------------------
if __name__ == "__main__":
    main()
