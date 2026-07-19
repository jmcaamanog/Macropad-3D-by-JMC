# MACROpad 3D Pro - Configurador y Hardware 🕹️🛠️

| 🏗️ Perfil & ConTech | 📈 Repositorio & Enlaces |
| :--- | :--- |
| ![Profesión](https://img.shields.io/badge/Profesi%C3%B3n-Arquitectos%20T%C3%A9cnicos-2e7d32?logo=micro%3Abit&logoColor=white&style=plastic) <br> ![Role](https://img.shields.io/badge/Role-BIM%20%26%20ConTech-007ACC?logo=bim360&style=plastic) <br> ![Location](https://img.shields.io/badge/Location-A%20Coru%C3%B1a%20%F0%9F%8C%8A-005B94?logo=lighthouse&logoColor=white&style=plastic) <br> ![Sector](https://img.shields.io/badge/Sector-ConTech%20%7C%20AECO-E65100?logo=construct3&style=plastic) <br> ![BIM](https://img.shields.io/badge/BIM-IFC%20%2F%20openBIM-009688?style=plastic) <br> ![Maker](https://img.shields.io/badge/Maker-Software%20+%20Hardware-red?logo=makerbot&style=plastic) <br> ![Hardware](https://img.shields.io/badge/Hardware-Arduino-00979D?logo=arduino&logoColor=white&style=plastic) <br> ![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&style=plastic) <br> ![Language](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white&style=plastic) <br> ![Language](https://img.shields.io/badge/Language-C%2B%2B-00599C?logo=c%2B%2B&logoColor=white&style=plastic) | ![Stars](https://img.shields.io/github/stars/jmcaamanog/Macropad-3D-by-JMC?style=plastic&color=yellow&logo=github) <br> ![License](https://img.shields.io/github/license/jmcaamanog/Macropad-3D-by-JMC?style=plastic&color=green) |

(Arquitecto Técnico_JMC) Herramienta integral (Hardware impreso en 3D + Software de escritorio) diseñada específicamente para acelerar el flujo de trabajo en modelado 3D (Autodesk Fusion, Blender, etc.). Este macropad ergonómico, adaptado a la mano izquierda, es el compañero perfecto para un ratón óptico 3Dconnexion, permitiendo mantener ambas manos en los controles sin tocar el teclado.

* Vídeo de ejemplo: [Ver en YouTube](https://youtu.be/fc4IcWASTRE). Este video muestra un ejemplo de cómo funciona el proyecto.
* Modelo 3D interactivo: [Ver en Sketchfab](https://sketchfab.com/3d-models/macropad-by-jmc-c2115bdf29d04d7a988c859baa1c8288).

<div align="center">
  <table border="0" style="border-collapse: collapse; border: none;">
    <tr style="border: none;">
      <td width="50%" align="center" style="border: none; padding: 10px;">
        <p><strong>🕹️ Hardware (Impresión 3D)</strong></p>
        <a href="https://sketchfab.com/3d-models/macropad-by-jmc-c2115bdf29d04d7a988c859baa1c8288" target="_blank">
          <img src="https://raw.githubusercontent.com/jmcaamanog/Macropad-3D-by-JMC/main/CAPTURAS/MACROPAD%20(3).png" alt="Hardware Macropad 3D" style="border-radius: 8px; width: 100%; max-width: 380px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        </a>
      </td>
      <td width="50%" align="center" style="border: none; padding: 10px;">
        <p><strong>💻 Software (Configurador GUI)</strong></p>
        <a href="https://sketchfab.com/3d-models/macropad-by-jmc-c2115bdf29d04d7a988c859baa1c8288" target="_blank">
          <img src="https://raw.githubusercontent.com/jmcaamanog/Macropad-3D-by-JMC/main/CAPTURAS/MACROPAD%20(4).jpg" alt="Software GUI Macropad" style="border-radius: 8px; width: 100%; max-width: 380px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        </a>
      </td>
    </tr>
  </table>
</div>

## 🚀 La Filosofía del Setup (Left-Hand + 3D Mouse)

Mientras tu mano derecha controla la órbita, el paneo y el zoom con fluidez analógica a través del 3Dconnexion, tu mano izquierda descansa sobre este macropad para disparar herramientas, modificadores y macros complejas al instante. 

El software actúa como el "cerebro" que traduce las señales del Arduino a través del puerto Serial y las convierte en atajos de teclado nativos usando la librería `pynput`.

## 🧠 Características del Software (v6.2)

*   **Matriz de 27 Acciones:** Configura hasta 3 acciones distintas por cada uno de los 9 botones físicos (Pulsación Corta, Larga y Doble).
*   **Creador de Secuencias (Macros):** No te limites a un solo atajo. Construye secuencias que combinen pulsaciones de teclas, inserción de texto, retardos (ms) y comandos de sistema.
*   **Gestor de Perfiles:** Guarda tus configuraciones en archivos `.json` locales. Crea un perfil para Autodesk Fusion, otro para tu software de renderizado y otro para uso general de Windows.
*   **Integración OBS Studio:** Incluye un módulo nativo mediante `obs-websocket-py` para controlar grabaciones o streamings de tus sesiones de modelado con un solo toque.
*   **Interfaz Minimalista Dark Mode:** UI limpia, sin etiquetas innecesarias, con asistentes de bienvenida y registro de actividad (Logs) en tiempo real.

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

(Opcional: instalar obs-websocket-py si deseas usar la integración con OBS).

3. Ejecutar el programa y seleccionar el puerto COM de tu Arduino.

## 👨‍💻 Autor

**Jose Manuel Caamaño González** | Arquitecto Técnico & BIM Manager
Digital Product Lead | ConTech & Digital Twin SaaS | Data Analytics (SQL, Power BI)

Hecho con código y café desde A Coruña. ☕
[LinkedIn](https://www.linkedin.com/in/jmcaamanog/) · [Web](https://jmcaamanog.pages.dev)
