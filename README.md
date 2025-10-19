<!-- Encabezado animado -->
<h1 align="center">
  <span style="font-size:2.5rem; font-weight:bold;">
      Motor de Inferencia por Resolución
  </span>
  <br>
  <span style="font-size:1.2rem; color:gray; font-family:monospace;">
    <span id="typed"></span>
  </span>
</h1>

<!-- Badge de estado -->
<p align="center">
  <a href="#">
    <img src="https://img.shields.io/badge/Estado-Proyecto%20Terminado-success?style=for-the-badge&logo=github" alt="Estado/>
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python" alt="Python"/>
  </a>
</p>

<!-- Subtítulo -->
<p>
  Proyecto académico de <strong>Introducción a la Inteligencia Artificial</strong>.<br>
  Implementación en <strong>Python</strong> de un motor de inferencia por resolución que trabaja con <strong>bases de conocimiento en Forma Normal Conjuntiva (CNF)</strong>.
</p>

---

## 🧍‍♂️ Colaboradores

<div align="center">

<table>
<thead>
<tr>
<th>Estudiante</th>
<th>Rol</th>
<th>Universidad</th>
</tr>
</thead>
<tbody>
<tr style="transition: all 0.3s ease-in-out;">
<td><strong>Daniel Felipe Bórquez Casas</strong></td>
<td>Estudiante Ingeniería en Sistemas</td>
<td><em>Pontificia Universidad Javeriana</em></td>
</tr>
<tr>
<td><strong>Johan Sebastian Berrío</strong></td>
<td>Estudiante Ingeniería en Sistemas</td>
<td><em>Pontificia Universidad Javeriana</em></td>
</tr>
<tr>
<td><strong>Juan Esteban Díaz Toledo</strong></td>
<td>Estudiante Ingeniería en Sistemas</td>
<td><em>Pontificia Universidad Javeriana</em></td>
</tr>
<tr>
<td><strong>Nicolás Mateo Morales</strong></td>
<td>Estudiante Ingeniería en Sistemas</td>
<td><em>Pontificia Universidad Javeriana</em></td>
</tr>
</tbody>
</table>

</div>

---

## 🧰 Herramientas y Tecnologías

<div>

| Herramienta | Uso Principal |
|------------|---------------|
|  **Python 3.x** | Lenguaje de implementación |
|  **Resolución por Refutación** | Inferencia lógica |
|  **Algoritmo de Unificación** | Variables y funciones simbólicas |
|  **Archivos `.txt`** | Definición de KB en CNF |
|  **Git / GitHub** | Control de versiones y trabajo colaborativo |

</div>

---

## 📌 Descripción del Proyecto

Este proyecto implementa un **motor de inferencia basado en resolución por refutación** para **demostrar teoremas de lógica de primer orden**.

✅ **Características principales**:
- Carga KB en CNF desde archivos `.txt`
- Aplica unificación entre literales y funciones simbólicas
- Deriva la cláusula vacía si la conclusión es demostrable
- Muestra en consola y guarda en archivo:
  - Pasos de resolución
  - Sustituciones θ en cada paso
  - Conclusión lógica dinámica

⚡ Ideal para cursos universitarios y demostraciones formales.

---

## 🧭 Estructura del Proyecto

```plaintext
Motor-inferencia-resolucion/
│
├── data/                         # Bases de conocimiento en CNF
│   ├── gato.txt                  # Caso "Curiosidad mató al gato"
│   └── cesar.txt                 # Caso "Marco odia a César"
│
├── outputs/                      # Resultados de las ejecuciones
│   └── resultado_gato.txt
│
├── resolver.py                   # Motor principal (resolución + unificación)
└── README.md                     # Documentación del proyecto
```

--- 

## 🧪 **Comandos para Compilar y Ejecutaro** 

- Ejecutar el motor de inferencia: python resolver.py
- Cuando se solicite la ruta de la base de conocimiento: data/"Ejemplo".txt

---
