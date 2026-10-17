"""TaskAnalyzer - analisador de métricas de tarefas.

Código gerado com apoio de assistente de IA a partir de
specs/task_analyzer_spec.md e CONTEXT_RULES.md, e revisado/homologado
manualmente antes do merge.

Requisitos atendidos (CONTEXT_RULES):
- Python 3.11+
- Type hints em todas as funções e parâmetros
- Exceção específica (TaskValidationError) e nenhuma divisão por zero
- Somente biblioteca padrão
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

STATUS_PENDENTE = "pendente"
STATUS_CONCLUIDA = "concluida"
STATUS_VALIDOS: frozenset[str] = frozenset({STATUS_PENDENTE, STATUS_CONCLUIDA})
PRIORIDADES_VALIDAS: tuple[str, ...] = ("alta", "media", "baixa")


class TaskValidationError(ValueError):
    """Erro de validação ou de consistência nos dados de uma tarefa."""


def _parse_datetime(valor: Any, campo: str, task_id: Any) -> datetime:
    """Converte string ISO 8601 ou datetime em datetime sem fuso (naive).

    Raises:
        TaskValidationError: se o valor estiver ausente, em formato inválido
            ou contiver informação de fuso horário (proibido pela spec para
            evitar comparação entre datas naive e aware).
    """
    if isinstance(valor, datetime):
        data = valor
    elif isinstance(valor, str):
        try:
            data = datetime.fromisoformat(valor)
        except ValueError as exc:
            raise TaskValidationError(
                f"Tarefa {task_id}: campo '{campo}' com formato inválido: {valor!r}"
            ) from exc
    else:
        raise TaskValidationError(
            f"Tarefa {task_id}: campo '{campo}' ausente ou com tipo inválido."
        )

    if data.tzinfo is not None:
        raise TaskValidationError(
            f"Tarefa {task_id}: campo '{campo}' não pode conter fuso horário."
        )
    return data


def _media(valores: list[float]) -> float:
    """Média aritmética arredondada em 2 casas; 0.0 para lista vazia."""
    if not valores:
        return 0.0
    return round(sum(valores) / len(valores), 2)


def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula as métricas consolidadas de uma lista de tarefas.

    Args:
        tasks: lista de dicionários com as chaves ``id``, ``status``
            ("pendente" | "concluida"), ``prioridade`` ("alta" | "media" |
            "baixa"), ``data_criacao``, ``data_conclusao`` (obrigatória se
            concluída) e ``data_prevista`` (opcional).

    Returns:
        Dicionário com total_tarefas, total_concluidas, total_pendentes,
        tempo_medio_conclusao_horas, tempo_medio_por_prioridade_horas e
        taxa_atraso_percentual.

    Raises:
        TaskValidationError: dados inválidos ou inconsistentes, incluindo
            data_conclusao anterior a data_criacao.
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("A entrada deve ser uma lista de tarefas.")

    total_concluidas = 0
    total_pendentes = 0
    duracoes: list[float] = []
    duracoes_por_prioridade: dict[str, list[float]] = {
        p: [] for p in PRIORIDADES_VALIDAS
    }
    concluidas_com_prazo = 0
    concluidas_atrasadas = 0

    for task in tasks:
        if not isinstance(task, dict):
            raise TaskValidationError("Cada tarefa deve ser um dicionário.")

        task_id = task.get("id", "?")
        status = task.get("status")
        prioridade = task.get("prioridade")

        if status not in STATUS_VALIDOS:
            raise TaskValidationError(
                f"Tarefa {task_id}: status inválido {status!r}."
            )
        if prioridade not in PRIORIDADES_VALIDAS:
            raise TaskValidationError(
                f"Tarefa {task_id}: prioridade inválida {prioridade!r}."
            )

        data_criacao = _parse_datetime(task.get("data_criacao"), "data_criacao", task_id)

        if status == STATUS_PENDENTE:
            total_pendentes += 1
            continue

        total_concluidas += 1
        data_conclusao = _parse_datetime(
            task.get("data_conclusao"), "data_conclusao", task_id
        )
        if data_conclusao < data_criacao:
            raise TaskValidationError(
                f"Tarefa {task_id}: inconsistência cronológica - data_conclusao "
                f"({data_conclusao.isoformat()}) anterior a data_criacao "
                f"({data_criacao.isoformat()})."
            )

        horas = (data_conclusao - data_criacao).total_seconds() / 3600
        duracoes.append(horas)
        duracoes_por_prioridade[prioridade].append(horas)

        if task.get("data_prevista") is not None:
            data_prevista = _parse_datetime(
                task["data_prevista"], "data_prevista", task_id
            )
            concluidas_com_prazo += 1
            if data_conclusao > data_prevista:
                concluidas_atrasadas += 1

    taxa_atraso = (
        round(concluidas_atrasadas / concluidas_com_prazo * 100, 2)
        if concluidas_com_prazo > 0
        else 0.0
    )

    return {
        "total_tarefas": len(tasks),
        "total_concluidas": total_concluidas,
        "total_pendentes": total_pendentes,
        "tempo_medio_conclusao_horas": _media(duracoes),
        "tempo_medio_por_prioridade_horas": {
            p: _media(v) for p, v in duracoes_por_prioridade.items()
        },
        "taxa_atraso_percentual": taxa_atraso,
    }


if __name__ == "__main__":
    exemplo: list[dict[str, Any]] = [
        {"id": 101, "status": "concluida", "prioridade": "alta",
         "data_criacao": "2026-03-01T08:00:00", "data_conclusao": "2026-03-01T12:00:00",
         "data_prevista": "2026-03-01T10:00:00"},
        {"id": 102, "status": "concluida", "prioridade": "alta",
         "data_criacao": "2026-03-02T08:00:00", "data_conclusao": "2026-03-02T10:00:00",
         "data_prevista": "2026-03-02T12:00:00"},
        {"id": 103, "status": "concluida", "prioridade": "baixa",
         "data_criacao": "2026-03-03T08:00:00", "data_conclusao": "2026-03-03T14:00:00",
         "data_prevista": "2026-03-03T18:00:00"},
        {"id": 104, "status": "pendente", "prioridade": "media",
         "data_criacao": "2026-03-04T08:00:00"},
    ]
    for chave, valor in analyze_tasks(exemplo).items():
        print(f"{chave}: {valor}")
