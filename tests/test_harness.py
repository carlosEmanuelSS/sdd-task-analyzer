"""Test Harness do TaskAnalyzer (pytest).

Traduz os cenários de aceite da Fase 1 (Dado-Quando-Então):
- Cenário 1: sucesso no cálculo das métricas
- Cenário 2: data_conclusao < data_criacao dispara TaskValidationError
- Casos de borda: entrada vazia e apenas tarefas pendentes
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from task_analyzer import TaskValidationError, analyze_tasks  # noqa: E402


@pytest.fixture
def tarefas_validas() -> list[dict]:
    return [
        {"id": 101, "status": "concluida", "prioridade": "alta",
         "data_criacao": "2026-03-01T08:00:00", "data_conclusao": "2026-03-01T12:00:00",
         "data_prevista": "2026-03-01T10:00:00"},  # 4h, atrasada
        {"id": 102, "status": "concluida", "prioridade": "alta",
         "data_criacao": "2026-03-02T08:00:00", "data_conclusao": "2026-03-02T10:00:00",
         "data_prevista": "2026-03-02T12:00:00"},  # 2h, no prazo
        {"id": 103, "status": "concluida", "prioridade": "baixa",
         "data_criacao": "2026-03-03T08:00:00", "data_conclusao": "2026-03-03T14:00:00",
         "data_prevista": "2026-03-03T18:00:00"},  # 6h, no prazo
        {"id": 104, "status": "pendente", "prioridade": "media",
         "data_criacao": "2026-03-04T08:00:00"},
    ]


# ---------- Cenário 1: sucesso ----------

def test_cenario1_totais(tarefas_validas: list[dict]) -> None:
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["total_tarefas"] == 4
    assert resultado["total_concluidas"] == 3
    assert resultado["total_pendentes"] == 1


def test_cenario1_tempo_medio_geral(tarefas_validas: list[dict]) -> None:
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["tempo_medio_conclusao_horas"] == 4.0


def test_cenario1_tempo_medio_por_prioridade(tarefas_validas: list[dict]) -> None:
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["tempo_medio_por_prioridade_horas"] == {
        "alta": 3.0, "media": 0.0, "baixa": 6.0,
    }


def test_cenario1_taxa_atraso(tarefas_validas: list[dict]) -> None:
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["taxa_atraso_percentual"] == pytest.approx(33.33)


# ---------- Cenário 2: exceção de datas inconsistentes ----------

def test_cenario2_conclusao_antes_da_criacao() -> None:
    tarefas = [
        {"id": 999, "status": "concluida", "prioridade": "media",
         "data_criacao": "2026-03-01T12:00:00", "data_conclusao": "2026-03-01T08:00:00"},
    ]
    with pytest.raises(TaskValidationError, match="inconsistência cronológica"):
        analyze_tasks(tarefas)


# ---------- Casos de borda ----------

def test_borda_lista_vazia() -> None:
    resultado = analyze_tasks([])
    assert resultado["total_tarefas"] == 0
    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0
    assert all(v == 0.0 for v in resultado["tempo_medio_por_prioridade_horas"].values())


def test_borda_apenas_pendentes() -> None:
    tarefas = [
        {"id": i, "status": "pendente", "prioridade": p,
         "data_criacao": "2026-03-10T09:00:00"}
        for i, p in enumerate(["alta", "media", "baixa", "alta", "media"], start=1)
    ]
    resultado = analyze_tasks(tarefas)
    assert resultado["total_tarefas"] == 5
    assert resultado["total_pendentes"] == 5
    assert resultado["total_concluidas"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0


# ---------- Validações extras exigidas pelas CONTEXT_RULES ----------

@pytest.mark.parametrize("tarefa", [
    {"id": 1, "status": "em_andamento", "prioridade": "alta",
     "data_criacao": "2026-03-01T08:00:00"},
    {"id": 2, "status": "pendente", "prioridade": "urgente",
     "data_criacao": "2026-03-01T08:00:00"},
    {"id": 3, "status": "concluida", "prioridade": "alta",
     "data_criacao": "2026-03-01T08:00:00"},
    {"id": 4, "status": "pendente", "prioridade": "alta",
     "data_criacao": "01/03/2026"},
    {"id": 5, "status": "concluida", "prioridade": "alta",
     "data_criacao": "2026-03-01T08:00:00", "data_conclusao": "2026-03-01T12:00:00Z"},
])
def test_dados_invalidos_disparam_task_validation_error(tarefa: dict) -> None:
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])
