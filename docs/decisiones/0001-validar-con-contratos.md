# 0001 · Validar cada capa con contratos de datos

- **Fecha:** (completa)
- **Estado:** aceptada

## Contexto

Las fuentes públicas cambian sin avisar: columnas renombradas, valores nuevos, días faltantes. Si un cambio así llega al dashboard, nadie confía más en él.

## Opciones consideradas

1. **Great Expectations o Soda**: muy completas, pero más configuración de la que necesito para empezar.
2. **Pruebas de dbt**: excelentes para lo que vive en el warehouse, pero no cubren la ingesta.
3. **Un validador propio con contratos en YAML** (`quality/contracts.py`): simple, lo entiendo completo y sirve en cualquier capa.

## Decisión

Empezar con el validador propio en la ingesta y las pruebas de dbt en el warehouse. (Ajusta esto a lo que decidas tú.)

## Consecuencias

(Completa cuando lo hayas usado: ¿qué te faltó?, ¿cuándo migrarías a una herramienta?)
