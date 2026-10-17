"""Test Harness do TaskAnalyzer (pytest).

Traduz os 8 cenários de aceite da Especificação SDD (Fase 1) e os casos de
borda exigidos na Fase 2. Cada teste referencia o cenário que cobre.
"""

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from task_analyzer import TaskValidationError, analyze_tasks  # noqa: E402


def tarefa(**campos: Any) -> dict[str, Any]:
    """Cria uma tarefa válida, permitindo sobrescrever campos."""
    base: dict[str, Any] = {
        "id": 1,
        "titulo": "Tarefa de teste",
        "prioridade": "MEDIA",
        "data_criacao": "2026-03-01T08:00:00",
        "data_limite": "2026-03-01T18:00:00",
        "data_conclusao": None,
        "status": "PENDENTE",
    }
    base.update(campos)
    return base


@pytest.fixture
def tarefas_validas() -> list[dict[str, Any]]:
    return [
        tarefa(id=101, prioridade="ALTA", data_criacao="2026-03-01T08:00:00",
               data_limite="2026-03-01T10:00:00", data_conclusao="2026-03-01T12:00:00",
               status="CONCLUIDA"),  # 4h, atrasada
        tarefa(id=102, prioridade="ALTA", data_criacao="2026-03-02T08:00:00",
               data_limite="2026-03-02T12:00:00", data_conclusao="2026-03-02T10:00:00",
               status="CONCLUIDA"),  # 2h, no prazo
        tarefa(id=103, prioridade="BAIXA", data_criacao="2026-03-03T08:00:00",
               data_limite="2026-03-03T18:00:00", data_conclusao="2026-03-03T14:00:00",
               status="CONCLUIDA"),  # 6h, no prazo
        tarefa(id=104, prioridade="MEDIA", data_criacao="2026-03-04T08:00:00",
               data_limite="2026-03-05T08:00:00", data_conclusao=None),  # pendente
    ]


# ---------- Cenário 1: tempo médio de conclusão ----------

def test_cenario1_totais(tarefas_validas: list[dict[str, Any]]) -> None:
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["total_tarefas"] == 4
    assert resultado["total_concluidas"] == 3
    assert resultado["total_pendentes"] == 1


def test_cenario1_tempo_medio_conclusao(tarefas_validas: list[dict[str, Any]]) -> None:
    assert analyze_tasks(tarefas_validas)["tempo_medio_conclusao_horas"] == 4.0


# ---------- Cenário 2: taxa de atraso ----------

def test_cenario2_taxa_atraso(tarefas_validas: list[dict[str, Any]]) -> None:
    assert analyze_tasks(tarefas_validas)["taxa_atraso_percentual"] == pytest.approx(33.33)


# ---------- Cenário 3: indicadores por prioridade ----------

def test_cenario3_indicadores_por_prioridade(tarefas_validas: list[dict[str, Any]]) -> None:
    indicadores = analyze_tasks(tarefas_validas)["indicadores_por_prioridade"]
    assert set(indicadores) == {"BAIXA", "MEDIA", "ALTA"}
    assert indicadores["ALTA"] == {
        "total": 2, "concluidas": 2,
        "tempo_medio_conclusao_horas": 3.0, "taxa_atraso_percentual": 50.0,
    }
    assert indicadores["BAIXA"]["tempo_medio_conclusao_horas"] == 6.0
    assert indicadores["MEDIA"] == {
        "total": 1, "concluidas": 0,
        "tempo_medio_conclusao_horas": 0.0, "taxa_atraso_percentual": 0.0,
    }


# ---------- Cenário 4: lista vazia ----------

def test_cenario4_lista_vazia() -> None:
    with pytest.raises(TaskValidationError) as erro:
        analyze_tasks([])
    assert erro.value.code == "EMPTY_TASK_LIST"


# ---------- Cenário 5: dados inválidos ----------

@pytest.mark.parametrize("entrada", [
    "não é lista",
    ["não é dicionário"],
    [{"id": 1, "titulo": "Sem os demais campos"}],
    [tarefa(id="1")],
    [tarefa(titulo="")],
])
def test_cenario5_dados_invalidos(entrada: Any) -> None:
    with pytest.raises(TaskValidationError) as erro:
        analyze_tasks(entrada)
    assert erro.value.code == "INVALID_TASK_DATA"


# ---------- Cenário 6: prioridade inválida ----------

@pytest.mark.parametrize("prioridade", ["URGENTE", "alta", "CRITICA"])
def test_cenario6_prioridade_invalida(prioridade: str) -> None:
    with pytest.raises(TaskValidationError) as erro:
        analyze_tasks([tarefa(prioridade=prioridade)])
    assert erro.value.code == "INVALID_PRIORITY"


# ---------- Cenário 7: identificador duplicado ----------

def test_cenario7_id_duplicado() -> None:
    with pytest.raises(TaskValidationError) as erro:
        analyze_tasks([tarefa(id=7), tarefa(id=7, titulo="Outra")])
    assert erro.value.code == "DUPLICATE_TASK_ID"


# ---------- Cenário 8: data inválida ----------

@pytest.mark.parametrize("campos", [
    {"data_criacao": "01/03/2026"},
    {"data_limite": "amanhã"},
    {"data_conclusao": "2026-03-01T12:00:00Z"},
    {"data_criacao": 20260301},
])
def test_cenario8_data_invalida(campos: dict[str, Any]) -> None:
    with pytest.raises(TaskValidationError) as erro:
        analyze_tasks([tarefa(**campos)])
    assert erro.value.code == "INVALID_DATE"


def test_cenario8_conclusao_antes_da_criacao() -> None:
    """Exigência da Fase 2: data_conclusao < data_criacao dispara TaskValidationError."""
    with pytest.raises(TaskValidationError) as erro:
        analyze_tasks([tarefa(data_criacao="2026-03-01T12:00:00",
                              data_conclusao="2026-03-01T08:00:00", status="CONCLUIDA")])
    assert erro.value.code == "INVALID_DATE"
    assert "anterior a data_criacao" in str(erro.value)


# ---------- Casos de borda (Fase 2) ----------

def test_borda_apenas_pendentes() -> None:
    tarefas = [tarefa(id=i, prioridade=p) for i, p in
               enumerate(["ALTA", "MEDIA", "BAIXA", "ALTA", "MEDIA"], start=1)]
    resultado = analyze_tasks(tarefas)
    assert resultado["total_tarefas"] == 5
    assert resultado["total_pendentes"] == 5
    assert resultado["total_concluidas"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0
    for indicador in resultado["indicadores_por_prioridade"].values():
        assert indicador["tempo_medio_conclusao_horas"] == 0.0
        assert indicador["taxa_atraso_percentual"] == 0.0


def test_borda_estrutura_de_saida_consistente(tarefas_validas: list[dict[str, Any]]) -> None:
    """Regra 10: a estrutura de saída é sempre a mesma."""
    so_pendentes = analyze_tasks([tarefa()])
    completo = analyze_tasks(tarefas_validas)
    assert so_pendentes.keys() == completo.keys()
    assert (so_pendentes["indicadores_por_prioridade"].keys()
            == completo["indicadores_por_prioridade"].keys())
