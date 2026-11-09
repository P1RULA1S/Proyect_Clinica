# Especificación de Requisitos del Sistema (SRS)
**Proyecto:** Sistema Automatizado de Termografía Médica
**Fecha de Generación:** 2026-11-08 21:21:23
**Desarrollador:** Elvis Paúl García Acevedo - Q.Web 

---

## 1. Descripción General del Proyecto
El presente proyecto consiste en el diseño y desarrollo de una aplicación de escritorio local para entornos clínicos (Windows). Su propósito es modernizar, digitalizar y automatizar el flujo de trabajo de consultas médicas basadas en termografía. El sistema reemplazará plantillas manuales y software obsoleto (tipo LabVIEW) mediante una solución moderna, intuitiva y altamente responsiva.

## 2. Objetivos del Sistema
*   **Automatización de Tiempos:** Reducir el tiempo de registro por paciente a menos de 5 minutos mediante el autocompletado de historiales previos.
*   **Captura Multicámara Sincronizada:** Mostrar y capturar streams en vivo de tres cámaras independientes (Frontal, Izquierda, Derecha) simultáneamente y sin latencia en la interfaz.
*   **Gestión Centralizada:** Eliminar el uso de papel almacenando la historia clínica, características somáticas, carga genética y síntomas en una base de datos estructurada.
*   **Generación de Informes:** Automatizar la creación del diagnóstico final en formato PDF, inyectando las plantillas institucionales de la clínica junto con los datos y fotogramas térmicos recortados.

## 3. Requisitos Funcionales
1.  **Módulo de Autenticación y Búsqueda:** Búsqueda en tiempo real de pacientes mediante Cédula o CURP.
2.  **Módulo de Historia Clínica:** Formularios clasificados en tarjetas (Datos Principales, Características Físicas, Síntomas y Molestias, Carga Genética, Diagnóstico).
3.  **Módulo de Motor de Video:** Conexión a dispositivos de captura de video (termográficos). La captura debe congelar los 3 fotogramas en el instante exacto y asociarlos al ID del paciente.
4.  **Módulo de Reportes:** Generación, previsualización y exportación a PDF de la historia clínica y observaciones finales.

## 4. Requisitos No Funcionales y Entorno de Ejecución
*   **Plataforma de Ejecución:** El sistema debe ejecutarse como una aplicación de escritorio nativa en Windows 10/11 sin necesidad de conexión a internet (offline-first por privacidad médica).
*   **Despliegue:** Será empaquetado en un archivo ejecutable único (`.exe`) independiente del entorno de desarrollo.
*   **Rendimiento (Multithreading):** La interfaz no debe congelarse durante la transmisión de video. Se utilizará programación concurrente (hilos separados) para las lecturas de OpenCV.
*   **Base de Datos:** Almacenamiento local mediante SQLite (archivo `.db`), utilizando SQLAlchemy para la seguridad transaccional y prevención de inyección SQL.
*   **Stack Tecnológico:** Python 3.10+, PySide6 (Qt6), OpenCV, SQLAlchemy, ReportLab.

## 5. Lineamientos de Interfaz Gráfica (UI/UX)
La apariencia del sistema es fundamental para garantizar una curva de aprendizaje corta para el personal médico.
*   **Estética Clínica (Flat UI):** Uso exclusivo de una paleta de colores institucional: Fondos claros (blanco y gris azulado `#f8fafc`), textos oscuros de alto contraste (`#334155`) y acentos en azul médico (`#0ea5e9`).
*   **Sobriedad Absoluta:** Prohibición estricta de emojis o iconos informales. El sistema debe proyectar seriedad y rigor médico.
*   **Estructura Visual:** Distribución mediante `QTabWidget` (pestañas) para separar flujos de trabajo (Captura vs. Formulario Clínico). Uso de `QGroupBox` con bordes suaves para encapsular lógicamente la información clínica.
*   **Componentes Nativos Claros:** Las casillas de verificación (Checkboxes), menús desplegables (ComboBoxes) y campos de texto deben tener padding espacioso, bordes definidos y cambio de color al seleccionarse (efecto hover/focus) para confirmar la acción visualmente al usuario.

## 6. Proyección y Escalabilidad (Fases Futuras)
La arquitectura base está preparada para el crecimiento tecnológico de la clínica. En futuras iteraciones, el software será capaz de integrar **Visión por Computador e Inteligencia Artificial** para la segmentación automática de anomalías térmicas (detección de masas o asimetrías térmicas en tiempo real), convirtiéndose en una suite médica integral.
