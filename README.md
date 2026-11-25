# Software FJ – Fase 4
Proyecto académico del curso Programación 213023 (UNAD).

## Requisitos
- Python 3.9 o superior.
- No requiere instalar paquetes externos.

## Ejecución
Desde la terminal, dentro de esta carpeta:
```bash
python main.py
```

El programa ejecuta 15 escenarios de prueba y crea automáticamente `logs/software_fj.log`.
Los datos de clientes, servicios y reservas se mantienen en listas durante la ejecución.
No se utiliza motor de base de datos.

## Organización
- `main.py`: clases, validaciones, excepciones, gestor y demostración.
- `logs/`: archivo generado durante la ejecución.

## Subir a GitHub
1. Crear un repositorio llamado `Software-FJ-Fase4`.
2. Agregar `main.py` y `README.md`.
3. Realizar un commit con un mensaje como `Implementación inicial del sistema Software FJ`.
4. Copiar el enlace público del repositorio y colocarlo en el informe.
5. Cada integrante debe realizar aportes identificables al repositorio, según el trabajo colaborativo solicitado.

## Nota académica
Python no implementa sobrecarga tradicional por firma como otros lenguajes. En este proyecto se demuestra una variante flexible mediante parámetros opcionales (`cantidad`, `impuesto`, `descuento`) y un método de conveniencia `calcular_costo_detallado`.
