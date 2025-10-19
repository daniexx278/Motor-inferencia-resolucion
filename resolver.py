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
    s = lit[1:] if es_negado(lit) else lit
    if "(" not in s:
        return s, []
    pred, rest = s.split("(", 1)
    args = rest.rstrip(")").split(",") if rest.rstrip(")") else []
    return pred.strip(), [a.strip() for a in args]

def es_variable(t):
    return bool(t) and t[0].islower()

# -------------------------
# Unificación simple
# -------------------------
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

def unificar_term(x, y, theta):
    # aplica sustituciones ya conocidas
    if theta is None:
        return None
    if x == y:
        return theta
    # si x es variable
    if is_var(x):
        return unify_var(x, y, theta)
    if is_var(y):
        return unify_var(y, x, theta)
    # constantes distintas -> fallo
    return None

def is_var(t):
    return es_variable(t)

def unify_var(var, x, theta):
    if var in theta:
        return unificar_term(theta[var], x, theta)
    if x in theta:
        return unificar_term(var, theta[x], theta)
    # occurs-check no implementado (entrada simple)
    theta2 = dict(theta)
    theta2[var] = x
    return theta2

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
                # aplicar theta a ambas cláusulas y quitar literales resueltos
                c1_sub = aplicar_theta_clausula(cl1, theta)
                c2_sub = aplicar_theta_clausula(cl2, theta)
                # remover l1 y l2 (aplicados) — hay que comparar por su forma aplicada
                l1_ap = aplicar_theta_literal(l1, theta)
                l2_ap = aplicar_theta_literal(l2, theta)
                nueva = [x for x in c1_sub if x != l1_ap] + [x for x in c2_sub if x != l2_ap]
                # normalizar: quitar duplicados
                nueva_norm = sorted(set(nueva))
                # evitar tautologías P y ~P dentro de la misma cláusula
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
# Búsqueda dirigida: preferir unidades y generar clausulas
# -------------------------
def buscar_resolucion(kb_meta):
    claus_set = { tuple(sorted(m['lit'])): m['id'] for m in kb_meta }
    next_id = max(m['id'] for m in kb_meta) + 1

    # cola de pares a explorar: empezamos con pares que incluyan unitarias
    unidades = [m for m in kb_meta if len(m['lit']) == 1]
    no_unidades = [m for m in kb_meta if len(m['lit']) != 1]

    # procesar primero (unidad, cualquier)
    pares_prioritarios = []
    for u in unidades:
        for other in kb_meta:
            if u['id'] != other['id']:
                pares_prioritarios.append((u, other))

    procesados = set()  # pares (id1,id2) ya intentados
    # procesamos en ondas, primero prioridad, luego todas combinaciones nuevas
    cola = pares_prioritarios + list(itertools.combinations(kb_meta, 2))

    # Para eficiencia, su uso un índice simple.
    # generando resolventes hasta encontrar la vacía.
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
            # asingar id y registrar
            rmeta['id'] = next_id
            next_id += 1
            claus_set[key] = rmeta['id']
            kb_meta.append(rmeta)
            # si es vacía retornar y reconstruir prueba
            if len(rmeta['lit']) == 0:
                return rmeta, kb_meta
    # Si agotamos sin vacío, seguimos explorando combinaciones ampliadas (iterativo)
    # Hacemos un bucle BFS sencillo hasta un tope
    max_iter = 10000
    it = 0
    i = 0
    while it < max_iter:
        it += 1
        # generar lista actual de pares no intentados
        all_pairs = []
        n = len(kb_meta)
        for idx1 in range(n):
            for idx2 in range(idx1+1, n):
                idpair = (kb_meta[idx1]['id'], kb_meta[idx2]['id'])
                idpair_sorted = tuple(sorted(idpair))
                if idpair_sorted in procesados:
                    continue
                all_pairs.append((kb_meta[idx1], kb_meta[idx2]))
                procesados.add(idpair_sorted)
        if not all_pairs:
            break
        progressed = False
        for (a,b) in all_pairs:
            resolvs = generar_resolventes(a,b)
            for rmeta in resolvs:
                key = tuple(sorted(rmeta['lit']))
                if key in claus_set:
                    continue
                rmeta['id'] = next_id
                next_id += 1
                claus_set[key] = rmeta['id']
                kb_meta.append(rmeta)
                progressed = True
                if len(rmeta['lit']) == 0:
                    return rmeta, kb_meta
        if not progressed:
            break
    return None, kb_meta

# -------------------------
# Reconstruir prueba desde meta vacía
# -------------------------
def reconstruir_prueba(meta_vacia, kb_meta):
    # mapa id -> meta
    id_map = {m['id']: m for m in kb_meta}
    # caminar padres recursivamente para obtener los pasos hasta las hojas iniciales
    pasos = []
    visit = set()
    def dfs(meta):
        if meta['padres'] is None:
            return
        pid1, pid2 = meta['padres']
        m1 = id_map[pid1]
        m2 = id_map[pid2]
        # primero explorar padres (postorder)
        if pid1 not in visit:
            dfs(m1)
        if pid2 not in visit:
            dfs(m2)
        # registrar este paso si no ya en pasos
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
# Imprimir prueba en formato limpio
# -------------------------
def imprimir_prueba(pasos, kb_meta):
    id_map = {m['id']: m for m in kb_meta}
    # los pasos vienen en orden ascendente de derivación por dfs
    # imprimimos numerados del 1..n con las cláusulas de padres y resolvente
    for i, paso in enumerate(pasos, 1):
        pid1, pid2 = paso['padres']
        c1 = id_map[pid1]['lit']
        c2 = id_map[pid2]['lit']
        resolv = paso['clausula']
        print(f"Paso {i}: resolviendo {c1} con {c2}")
        print(f"       => {resolv}\n")
    # última (vacía)
    print(" Se ha obtenido la CLÁUSULA VACÍA ")
    print(" La conclusión está demostrada por refutación.\n")

# -------------------------
# Guardar resultado
# -------------------------
def guardar_resultado(ruta_base, pasos_count, demostrado):
    nombre = os.path.splitext(os.path.basename(ruta_base))[0]
    os.makedirs("outputs", exist_ok=True)
    ruta_salida = f"outputs/resultado_{nombre}.txt"

    # Mensaje de conclusión personalizada
    if demostrado:
        conclusion_text = (
            "\nConclusión lógica:\n"
            "La negación de la conclusión no es consistente con la base de conocimiento.\n"
            "Por tanto, se confirma que Marco odia a César ✅\n"
        )
    else:
        conclusion_text = (
            "\nConclusión lógica:\n"
            "No se pudo demostrar que Marco odia a César ❌\n"
        )

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("=== RESULTADO DE LA RESOLUCIÓN ===\n\n")
        f.write(f"Base: {nombre}\n")
        f.write(f"Pasos en la prueba: {pasos_count}\n")
        f.write(f"Resultado final: {'DEMONSTRADO ✅' if demostrado else 'NO DEMOSTRADO ❌'}\n")
        f.write(conclusion_text)

    print(f"📝 Resultado guardado en: {ruta_salida}")

# -------------------------
# MAIN: ejecutar todo
# -------------------------
def main():
    print("=== MOTOR DE INFERENCIA BASADO EN RESOLUCIÓN ===")
    ruta = input(" Ingrese la ruta del archivo de base de conocimiento (.txt): ").strip()
    kb = cargar_base_conocimiento(ruta)
    # inicializar metas
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

    # buscar resolución y obtener meta vacía si existe
    meta_vacia, kb_meta = buscar_resolucion(kb_meta)
    if meta_vacia is None:
        print("\n❌ No se pudo demostrar la conclusión (no se halló cláusula vacía).\n")
        guardar_resultado(ruta, 0, False)
        return

    # reconstruir la cadena de resolución y mostrar solo esa
    pasos = reconstruir_prueba(meta_vacia, kb_meta)
    imprimir_prueba(pasos, kb_meta)
    guardar_resultado(ruta, len(pasos), True)

# -------------------------
# run
# -------------------------
if __name__ == "__main__":
    main()
