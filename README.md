# MACROpad 3D Pro - Configurador y Hardware 🕹️🛠️

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Arduino](https://img.shields.io/badge/Hardware-Arduino-00979D.svg)
![Autodesk Fusion](https://img.shields.io/badge/Design-Autodesk%20Fusion-0F9D58.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-2fa5d6.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

(Arquitecto Técnico_JMC) Herramienta integral (Hardware impreso en 3D + Software de escritorio) diseñada específicamente para acelerar el flujo de trabajo en modelado 3D (Autodesk Fusion, Blender, etc.). Este macropad ergonómico, adaptado a la mano izquierda, es el compañero perfecto para un ratón óptico 3Dconnexion, permitiendo mantener ambas manos en los controles sin tocar el teclado.

Vídeo de ejemplo: [Ver en YouTube](https://youtu.be/fc4IcWASTRE). Este video muestra un ejemplo de cómo funciona el proyecto.

## 🚀 La Filosofía del Setup (Left-Hand + 3D Mouse)

Mientras tu mano derecha controla la órbita, el paneo y el zoom con fluidez analógica a través del 3Dconnexion, tu mano izquierda descansa sobre este macropad para disparar herramientas, modificadores y macros complejas al instante. 

El software actúa como el "cerebro" que traduce las señales del Arduino a través del puerto Serial y las convierte en atajos de teclado nativos usando la librería `pynput`.

## 🧠 Características del Software (v6.2)

*   **Matriz de 27 Acciones:** Configura hasta 3 acciones distintas por cada uno de los 9 botones físicos (Pulsación Corta, Larga y Doble)[cite: 11].
*   **Creador de Secuencias (Macros):** No te limites a un solo atajo. Construye secuencias que combinen pulsaciones de teclas, inserción de texto, retardos (ms) y comandos de sistema[cite: 11].
*   **Gestor de Perfiles:** Guarda tus configuraciones en archivos `.json` locales[cite: 11]. Crea un perfil para Autodesk Fusion, otro para tu software de renderizado y otro para uso general de Windows.
*   **Integración OBS Studio:** Incluye un módulo nativo mediante `obs-websocket-py` para controlar grabaciones o streamings de tus sesiones de modelado con un solo toque[cite: 11].
*   **Interfaz Minimalista Dark Mode:** UI limpia, sin etiquetas innecesarias, con asistentes de bienvenida y registro de actividad (Logs) en tiempo real[cite: 11].

## 📂 Estructura del Repositorio

*   📁 **`CAPTURAS/`**: Galería visual completa del proyecto. Incluye capturas de pantalla de la interfaz, renders fotorealistas del diseño creados en Autodesk Fusion, y fotos del producto final impreso en 3D y ensamblado en el escritorio.
*   📁 **`EJECUTABLE/`**: Contiene el programa compilado listo para descargar y usar en Windows, sin necesidad de instalar Python.
*   📄 **`macropad.py`**: El código fuente de la interfaz gráfica y la lógica de control.

## ⚙️ Requisitos para el Código Fuente

Si prefieres ejecutar el software desde el código fuente, necesitarás:

1. Clonar el repositorio y navegar a la carpeta.
2. Instalar las dependencias necesarias:
   ```bash
   pip install customtkinter pyserial pynput Pillow

(Opcional: instalar obs-websocket-py si deseas usar la integración con OBS[cite: 11]).

3. Ejecutar el programa y seleccionar el puerto COM de tu Arduino[cite: 11].

## 👨‍💻 Autor

Jose Manuel Caamaño González | Arquitecto Técnico & BIM Manager.
Digital Product Lead | ConTech & Digital Twin SaaS | BIM, Energy Modeling & Sustainability | Data Analytics (SQL, Power BI)

Hecho con código y café desde A Coruña. ☕

Jose Manuel Caamaño González | [LinkedIn](https://www.linkedin.com/in/jmcaamanog/)
