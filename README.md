<div align="center">
  <h1>⚙️ Proyecto Compilador - Equipo 12 (7SB)</h1>
  <p><i>Analizador Léxico y Semántico con Interfaz Gráfica</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/CustomTkinter-GUI-darkgreen?style=for-the-badge" alt="CustomTkinter">
    <img src="https://img.shields.io/badge/Status-Completado-success?style=for-the-badge" alt="Status">
  </p>
</div>

---

## 📖 Descripción del proyecto

Este proyecto consiste en el desarrollo de un compilador personalizado para la asignatura de **Lenguajes y Autómatas II** del **Instituto Tecnológico de Mérida**.

El sistema recibe código fuente escrito en un lenguaje definido por el equipo, realiza el **análisis léxico** para identificar y clasificar tokens, y posteriormente ejecuta un **análisis semántico** para validar la coherencia del programa conforme a reglas previamente establecidas.

Además, el proyecto incluye una **interfaz gráfica moderna** desarrollada con `CustomTkinter`, que permite visualizar de manera clara el código fuente, los resultados del análisis y las tablas generadas durante el proceso.

---

## ✨ Características principales

- **Análisis léxico**
  - Reconocimiento de tipos de dato como `One`, `Two` y `Tree`
  - Identificación de variables como `$var`
  - Detección de operadores, estructuras de control y funciones como `$func()`

- **Análisis semántico**
  - Prevención de variables duplicadas
  - Detección de variables y funciones no definidas
  - Validación de incompatibilidad de tipos en asignaciones
  - Verificación de tipos de retorno en funciones

- **Interfaz gráfica**
  - Editor de código con desplazamiento vertical
  - Conteo de líneas
  - Visualización en tiempo real de resultados y tablas

- **Exportación de datos**
  - Generación automática de archivos `.csv`
  - Exportación de la tabla de símbolos
  - Exportación de la tabla de errores en la carpeta `salida/`

---

## 🚀 Instalación y uso

### 1. Requisitos previos

Asegúrate de tener instalado:

- **Python 3.x**
- **pip** para la instalación de dependencias

### 2. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

### 3. Instalar dependencias 
```bash
pip install customtkinter
```

### 4. Ejecutar proyecto 
```bash
python main.py
```
