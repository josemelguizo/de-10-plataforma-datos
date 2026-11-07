# Proyecto 10 · Plataforma de datos de punta a punta

Parte de mi [ruta de ingeniería de datos](https://github.com/josemelguizo/ruta-datos).

![nivel](https://img.shields.io/badge/nivel-4_portafolio-purple) ![tiempo](https://img.shields.io/badge/tiempo-4--6_semanas-lightgrey)

> **Este es tu proyecto de portafolio.** No tiene una solución única: las decisiones son tuyas y son justamente lo que vas a mostrar en una entrevista. Aquí tienes la estructura, una guía por hitos, una rúbrica y una pieza reutilizable con pruebas (el validador de contratos de datos). Todo lo demás lo construyes reutilizando lo que aprendiste en los proyectos 1 a 9.

## El reto

Construye una plataforma que responda una pregunta real sobre Antioquia con datos abiertos, desde la ingesta hasta un dashboard, con calidad, orquestación, infraestructura como código y CI/CD.

Elige **una** pregunta (o propón la tuya):

| Pregunta | Fuentes posibles |
|---|---|
| ¿Cómo se relacionan la calidad del aire y el clima en el Valle de Aburrá? | Redes de monitoreo de calidad del aire en [datos.gov.co](https://www.datos.gov.co/) o [SIATA](https://siata.gov.co/), clima de Open-Meteo (proyecto 4) |
| ¿Cómo afecta la TRM a los precios de los combustibles en Antioquia? | TRM (proyecto 3), precios de combustibles en datos.gov.co |
| ¿Dónde y cuándo ocurren más incidentes de tránsito en Medellín? | Incidentes viales en el portal de datos abiertos de Medellín, clima de Open-Meteo |

Antes de escribir código, verifica que tus fuentes existen, se actualizan y tienen suficiente historia. Ese chequeo es el hito 0.

## Componentes obligatorios

| Componente | Herramienta sugerida | Lo practicaste en |
|---|---|---|
| Ingesta batch (y streaming si tu fuente lo permite) | Python | Proyectos 1, 3 y 8 |
| Data lake | GCS, S3 o MinIO | Proyecto 6 |
| Warehouse | BigQuery, Snowflake (prueba) o DuckDB | Proyectos 2 y 5 |
| Transformación | dbt | Proyecto 5 |
| Orquestación | Airflow | Proyecto 4 |
| Calidad de datos | `quality/contracts.py` + pruebas de dbt | Este proyecto |
| Infraestructura como código | Terraform | Este proyecto |
| Contenedores | Docker Compose | Todos |
| CI/CD | GitHub Actions | Todos |
| Dashboard | Metabase, Superset o Streamlit | Este proyecto |

## Estructura

```
├── ingestion/               extractores por fuente
├── orchestration/dags/      DAGs de Airflow
├── transform/               proyecto dbt
├── quality/
│   ├── contracts.py         validador de contratos (reto con pruebas)
│   └── contratos/*.yml      un contrato por dataset
├── infra/terraform/         bucket + datasets en Google Cloud
├── dashboard/               capturas y definición de tableros
├── docs/
│   ├── arquitectura.md      tu diagrama y explicación (créalo)
│   └── decisiones/          un registro por cada decisión importante
└── tests/
```

## Hitos

| # | Hito | Entregable |
|---|---|---|
| 0 | **Pregunta y fuentes** | `docs/arquitectura.md` con la pregunta, las fuentes verificadas y un primer diagrama |
| 1 | **Contratos** | `quality/contracts.py` con `pytest` en verde (ver abajo) y un contrato YAML por fuente |
| 2 | **Ingesta** | Extractores que guardan crudo en el lago y validan con su contrato |
| 3 | **Infraestructura** | `terraform apply` crea tu bucket y datasets; `terraform destroy` los borra |
| 4 | **Warehouse y dbt** | Modelos staging → marts con pruebas, cargados desde el lago |
| 5 | **Orquestación** | Un DAG diario que encadena ingesta → validación → dbt, con reintentos y alertas |
| 6 | **Dashboard** | 3 a 5 gráficos que respondan tu pregunta, con capturas en `dashboard/` |
| 7 | **CI/CD y cierre** | CI en verde, README final con resultados y un video corto (2–3 min) mostrando la plataforma |

Registra en `docs/decisiones/` cada decisión importante con la plantilla `0000-plantilla.md` (ya hay una de ejemplo). En una entrevista, poder explicar *por qué* elegiste algo vale más que la herramienta misma.

## Hito 1 · El validador de contratos

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate en macOS/Linux)
pip install -e ".[dev]"
pytest                          # en rojo hasta que completes quality/contracts.py
ruff check --fix .              # estilo del código; también corre en CI
```

Lee `quality/contratos/calidad_aire_horaria.yml` y luego los docstrings de `quality/contracts.py`. Cuando las pruebas pasen, úsalo así en tu ingesta:

```python
from quality.contracts import load_contract, validate

result = validate(df, load_contract("quality/contratos/mi_fuente.yml"))
if not result.passed:
    raise ValueError(f"{result.dataset} no cumple su contrato: {result.violations}")
```

## Hito 3 · Infraestructura

`infra/terraform/` crea un bucket y tres datasets de BigQuery en Google Cloud. Google da créditos gratis a cuentas nuevas y una capa gratuita permanente; aun así, **configura una alerta de presupuesto** en la consola antes de crear nada, y corre `terraform destroy` cuando no estés usando la plataforma. Las instrucciones están al inicio de `main.tf`.

Si prefieres no usar la nube, cambia el bucket por MinIO (proyecto 6) y BigQuery por DuckDB o PostgreSQL, y documenta esa decisión.

## Rúbrica de autoevaluación

| Criterio | Básico | Sólido | Destacado |
|---|---|---|---|
| Datos | Una fuente, carga manual | Dos fuentes, carga diaria | Batch + streaming, con historia completa |
| Calidad | Algunas pruebas | Contrato por fuente y pruebas de dbt | El pipeline se detiene y alerta ante datos malos |
| Idempotencia | Re-ejecutar duplica | Re-ejecutar es seguro | Backfills documentados y probados |
| Infraestructura | Manual | Terraform para lo principal | Todo reproducible desde cero con un comando |
| Documentación | README básico | Arquitectura y decisiones | Alguien que no te conoce puede levantarla y entenderla |
| Resultado | Gráficos sueltos | Dashboard que responde la pregunta | Hallazgos explicados con conclusiones |

## Recursos

- [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp): su proyecto final tiene esta misma forma, y puedes ver cientos de ejemplos de otros estudiantes
- [Terraform: tutorial de Google Cloud](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started)
- [Architecture Decision Records](https://adr.github.io/)
