from pathlib import Path

import pandas as pd
import pytest

from quality.contracts import ContractError, load_contract, validate

CONTRATO = Path(__file__).parents[1] / "quality" / "contratos" / "calidad_aire_horaria.yml"


@pytest.fixture
def contract():
    return load_contract(CONTRATO)


def datos(**cambios):
    df = pd.DataFrame({
        "estacion_id": ["MED-ITA", "MED-ITA", "MED-BEL"],
        "fecha_hora": pd.to_datetime(["2026-03-10 07:00", "2026-03-10 08:00", "2026-03-10 07:00"]),
        "pm25": [28.5, 41.0, None],
        "estado": ["valido", "valido", "faltante"],
    })
    for col, values in cambios.items():
        df[col] = values
    return df


def checks(result):
    return result.checks_failed()


# ---------- cargar el contrato ----------

def test_carga_el_contrato(contract):
    assert contract["dataset"] == "calidad_aire_horaria"
    assert [c["nombre"] for c in contract["columnas"]] == ["estacion_id", "fecha_hora", "pm25", "estado"]


def test_contrato_con_tipo_desconocido(tmp_path):
    p = tmp_path / "malo.yml"
    p.write_text("dataset: x\ncolumnas:\n  - nombre: a\n    tipo: decimalote\n", encoding="utf-8")
    with pytest.raises(ContractError):
        load_contract(p)


def test_contrato_sin_columnas(tmp_path):
    p = tmp_path / "malo.yml"
    p.write_text("dataset: x\n", encoding="utf-8")
    with pytest.raises(ContractError):
        load_contract(p)


# ---------- validar ----------

def test_datos_buenos_pasan(contract):
    result = validate(datos(), contract)
    assert result.passed and result.violations == []
    assert result.dataset == "calidad_aire_horaria"


def test_columna_faltante(contract):
    result = validate(datos().drop(columns=["estado"]), contract)
    assert ("columna_faltante", "estado") in checks(result)


def test_columna_extra_no_permitida(contract):
    result = validate(datos(humedad=[80, 81, 79]), contract)
    assert checks(result) == [("columna_extra", "humedad")]


def test_columna_extra_permitida_si_el_contrato_lo_dice(contract):
    contract["permitir_columnas_extra"] = True
    assert validate(datos(humedad=[80, 81, 79]), contract).passed


def test_tipo_equivocado(contract):
    result = validate(datos(fecha_hora=["2026-03-10 07:00", "2026-03-10 08:00", "2026-03-10 07:00"]), contract)  # texto
    assert checks(result) == [("tipo", "fecha_hora")]


def test_enteros_valen_como_float(contract):
    assert validate(datos(pm25=[28, 41, 10]), contract).passed


def test_nulos_en_columna_requerida(contract):
    result = validate(datos(estacion_id=["MED-ITA", None, "MED-BEL"]), contract)
    [v] = result.violations
    assert (v.check, v.column, v.rows) == ("requerida", "estacion_id", 1)


def test_nulos_en_columna_opcional_estan_bien(contract):
    assert validate(datos(pm25=[None, None, None]), contract).passed


def test_rango(contract):
    result = validate(datos(pm25=[-3.0, 1500.0, 20.0]), contract)
    assert checks(result) == [("max", "pm25"), ("min", "pm25")]
    assert all(v.rows == 1 for v in result.violations)


def test_valores_permitidos(contract):
    result = validate(datos(estado=["valido", "VALIDO", "roto"]), contract)
    [v] = result.violations
    assert (v.check, v.rows) == ("valores_permitidos", 2)


def test_llave_primaria_repetida(contract):
    result = validate(datos(estacion_id=["MED-ITA", "MED-ITA", "MED-ITA"],
                            fecha_hora=pd.to_datetime(["2026-03-10 07:00"] * 2 + ["2026-03-10 09:00"])), contract)
    [v] = result.violations
    assert (v.check, v.rows) == ("primary_key", 2)


def test_minimo_de_filas(contract):
    result = validate(datos().iloc[0:0], contract)
    assert ("min_filas", None) in checks(result)


def test_reporta_todos_los_problemas_a_la_vez(contract):
    df = datos(pm25=[-1.0, 2.0, 3.0], estado=["valido", "roto", "valido"]).drop(columns=["estacion_id"])
    found = {c for c, _ in checks(validate(df, contract))}
    assert found == {"columna_faltante", "min", "valores_permitidos"}
