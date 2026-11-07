"""Contratos de datos: validar que un DataFrame cumple lo prometido.

Lo usarás en varias capas de tu plataforma: al ingerir (¿la fuente cambió?),
después de transformar (¿mi lógica rompió algo?) y antes del dashboard.
Ejemplo de contrato: quality/contratos/calidad_aire_horaria.yml
"""

from dataclasses import dataclass, field
from pathlib import Path  # noqa: F401  (lo usarás en load_contract)

import pandas as pd
import yaml  # noqa: F401  (lo usarás en load_contract)

# Cómo verificar cada tipo del contrato contra el dtype de pandas.
TYPE_CHECKS = {
    "string": lambda s: pd.api.types.is_string_dtype(s) or pd.api.types.is_object_dtype(s),
    "integer": pd.api.types.is_integer_dtype,
    "float": lambda s: pd.api.types.is_float_dtype(s) or pd.api.types.is_integer_dtype(s),
    "boolean": pd.api.types.is_bool_dtype,
    "datetime": pd.api.types.is_datetime64_any_dtype,
    "date": lambda s: pd.api.types.is_datetime64_any_dtype(s)
    or s.dropna().map(lambda v: hasattr(v, "isoformat")).all(),
}


@dataclass(frozen=True)
class Violation:
    check: str            # "columna_faltante", "columna_extra", "tipo", "requerida",
                          # "min", "max", "valores_permitidos", "primary_key", "min_filas"
    column: str | None    # None si no aplica a una columna (min_filas)
    detail: str           # mensaje para humanos
    rows: int = 0         # cuántas filas violan la regla (0 si no aplica)


@dataclass
class ValidationResult:
    dataset: str
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.violations

    def checks_failed(self) -> list[tuple[str, str | None]]:
        """Pares (check, column) únicos y ordenados. Ya resuelto."""
        return sorted({(v.check, v.column) for v in self.violations}, key=lambda t: (t[0], t[1] or ""))


class ContractError(ValueError):
    """El contrato mismo está mal escrito."""


def load_contract(path) -> dict:
    """Lee el YAML y devuelve un dict.

    TODO:
      * yaml.safe_load del archivo (encoding utf-8).
      * ContractError si falta "dataset" o "columnas".
      * ContractError si alguna columna tiene un "tipo" que no está en TYPE_CHECKS.
    """
    raise NotImplementedError("TODO: load_contract")


def validate(df: pd.DataFrame, contract: dict) -> ValidationResult:
    """Revisa TODAS las reglas y devuelve TODAS las violaciones (no pares en la primera).

    TODO, una Violation por cada problema:
      * min_filas: menos filas que contract["min_filas"] (si existe).
      * columna_faltante: columna del contrato que no está en df.
      * columna_extra: columna de df que no está en el contrato, solo si
        contract["permitir_columnas_extra"] es False (si no viene, se permiten).
      * Para cada columna que sí existe:
          - tipo: usa TYPE_CHECKS. Una columna sin ningún valor (todo nulo) no
            falla por tipo. Si el tipo falla, no revises más reglas de esa columna.
          - requerida: si "requerida" es true, cuenta los nulos.
          - min / max: cuenta los valores fuera del rango (si están definidos).
          - valores_permitidos: cuenta los valores no nulos que no están en la lista.
      * primary_key: filas cuya combinación de llave se repite (cuenta TODAS las
        filas involucradas, pista: duplicated(keep=False)). Solo si todas las
        columnas de la llave existen.

    En `rows` va cuántas filas violan la regla.
    """
    raise NotImplementedError("TODO: validate")
