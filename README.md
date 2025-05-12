# Calculadora de Costos y Ganancias para Grabados Láser (ERP modular)

Esta es una **aplicación de escritorio tipo ERP modular**, orientada a pequeños emprendimientos de grabado láser, con enfoque en:

- Control de inventario (FIFO)
- Cálculo de costos y ganancias
- Generación de reportes en Excel y PDF
- Registro histórico de costos
- Cálculo automático de precios sugeridos
- Generación automática de SKUs por producto
- Gestión de usuarios con login
- Separación por perfiles de usuario
- Interfaz gráfica con `tkinter`
- Checklist tipo to-do list integrado
- Simulación de envío de información al SII

## Tecnologías utilizadas

- Lenguaje: **Python**
- Interfaz gráfica: **Tkinter**
- Base de datos: **PostgreSQL**
- Organización del proyecto basada en arquitectura por capas:
  - `core/`: lógica de dominio, infraestructura y aplicación
  - `presentacion/`: interfaz de escritorio y futura interfaz web
  - `pruebas/`: scripts de prueba y testeo de lógica

## Características principales

- 🧮 **Cálculo automático de costos y ganancias** por producto
- 🧾 **Registro histórico** de los costos por producto (con fechas y valores anteriores)
- 📦 **Control de inventario** con método FIFO (First In, First Out)
- 💰 **Cálculo de precios sugeridos** según costos, margen deseado y metas de sueldo
- 🔒 **Sistema de login** para acceso de usuarios y separación de datos por perfil
- 🧑‍💻 **Generación de SKUs** automáticos según materiales y características
- ✅ **Checklist tipo To-Do List** para registrar tareas asociadas a productos o procesos
- 📤 **Simulación de envío al SII** para reportes de ventas
- 📊 **Exportación de reportes** en Excel y PDF

## Estructura de carpetas

```
calculadora_de_costo_y_ganancias/
├── core/
│   ├── dominio/
│   ├── infraestructura/
│   └── aplicacion/
├── presentacion/
│   ├── escritorio/
│   └── web/
├── pruebas/
└── README.md
```

## Próximas funcionalidades

- [ ] Integración con sistema de ventas online
- [ ] Gestión de órdenes y pedidos
- [ ] Notificaciones automáticas por bajo stock
- [ ] Control de flujo de caja

---

**Autor:** Grabados Láser 8102GyP

**Licencia:** MIT
