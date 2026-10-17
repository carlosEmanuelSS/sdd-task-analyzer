"""TaskAnalyzer - análise de métricas de produtividade de tarefas.

Código gerado com apoio de assistente de IA a partir de
``specs/task_analyzer_spec.md`` e ``CONTEXT_RULES.md`` e homologado
manualmente antes do merge.

Requisitos atendidos (CONTEXT_RULES):
    - Python 3.11+, type hints, PEP 8 e docstrings no padrão Google.
    - Exceção específica ``TaskValidationError`` com os códigos de erro da spec.
    - Nenhuma divisão por zero e somente biblioteca padrão.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

PRIORIDADES: tuple[str, ...] = ("BAIXA", "MEDIA", "ALTA")
CAMPOS_OBRIGATORIOS: tuple[str, ...] = (
    "id",
    "titulo",
    "prioridade",
    "data_criacao",
    "data_limite",
    "data_conclusao",
    "status",
)

INVALID_TASK_DATA = "INVALID_TASK_DATA"
INVALID_PRIORITY = "INVALID_PRIORITY"
INVALID_DATE = "INVALID_DATE"
DUPLICATE_TASK_ID = "DUPLICATE_TASK_ID"
EMPTY_TASK_LIST = "EMPTY_TASK_LIST"


class TaskValidationError(ValueError):
    """Erro de validação dos dados de entrada do TaskAnalyzer.

    Attributes:
        code: Código de erro definido na especificação.
        message: Descrição legível do problema.
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


# --------------------------------------------------------------------------
# Validação
# --------------------------------------------------------------------------


def _parse_datetime(valor: Any, campo: str, task_id: Any) -> datetime:
    """Converte um valor em ``datetime`` sem fuso horário.

    Args:
        valor: ``datetime`` ou texto ISO 8601.
        campo: Nome do campo, usado na mensagem de erro.
        task_id: Identificador da tarefa, usado na mensagem de erro.

    Returns:
        O valor convertido para ``datetime``.

    Raises:
        TaskValidationError: Com código ``INVALID_DATE`` se o valor não for
            uma data válida ou contiver fuso horário.
    """
    if isinstance(valor, datetime):
        data = valor
    elif isinstance(valor, str):
        try:
            data = datetime.fromisoformat(valor)
        except ValueError as exc:
            raise TaskValidationError(
                INVALID_DATE, f"Tarefa {task_id}: '{campo}' inválida: {valor!r}."
            ) from exc
    else:
        raise TaskValidationError(
            INVALID_DATE, f"Tarefa {task_id}: '{campo}' deve ser uma data/hora."
        )

    if data.tzinfo is not None:
        raise TaskValidationError(
            INVALID_DATE, f"Tarefa {task_id}: '{campo}' não pode conter fuso horário."
        )
    return data


def _validar_estrutura(task: Any) -> None:
    """Confere se a tarefa segue a estrutura definida na especificação.

    Args:
        task: Item recebido na lista de tarefas.

    Raises:
        TaskValidationError: Com código ``INVALID_TASK_DATA``.
    """
    if not isinstance(task, dict):
        raise TaskValidationError(INVALID_TASK_DATA, "Cada tarefa deve ser um dicionário.")

    faltando = [campo for campo in CAMPOS_OBRIGATORIOS if campo not in task]
    if faltando:
        raise TaskValidationError(
            INVALID_TASK_DATA,
            f"Tarefa {task.get('id', '?')}: campos ausentes: {', '.join(faltando)}.",
        )

    task_id = task["id"]
    if not isinstance(task_id, int) or isinstance(task_id, bool):
        raise TaskValidationError(INVALID_TASK_DATA, f"'id' deve ser inteiro: {task_id!r}.")

    for campo in ("titulo", "prioridade", "status"):
        if not isinstance(task[campo], str) or not task[campo].strip():
            raise TaskValidationError(
                INVALID_TASK_DATA, f"Tarefa {task_id}: '{campo}' deve ser um texto não vazio."
            )


def _validar_tarefa(task: Any, ids_vistos: set[int]) -> dict[str, Any]:
    """Valida uma tarefa e devolve uma versão normalizada para o cálculo.

    Args:
        task: Tarefa recebida na entrada.
        ids_vistos: Identificadores já validados, para detectar duplicidade.

    Returns:
        Dicionário com ``prioridade``, ``data_criacao``, ``data_limite`` e
        ``data_conclusao`` já convertidas.

    Raises:
        TaskValidationError: Com o código correspondente ao problema encontrado.
    """
    _validar_estrutura(task)
    task_id = task["id"]

    if task_id in ids_vistos:
        raise TaskValidationError(DUPLICATE_TASK_ID, f"Identificador duplicado: {task_id}.")
    ids_vistos.add(task_id)

    prioridade = task["prioridade"]
    if prioridade not in PRIORIDADES:
        raise TaskValidationError(
            INVALID_PRIORITY, f"Tarefa {task_id}: prioridade não permitida {prioridade!r}."
        )

    data_criacao = _parse_datetime(task["data_criacao"], "data_criacao", task_id)
    data_limite = _parse_datetime(task["data_limite"], "data_limite", task_id)
    data_conclusao: datetime | None = None
    if task["data_conclusao"] is not None:
        data_conclusao = _parse_datetime(task["data_conclusao"], "data_conclusao", task_id)
        if data_conclusao < data_criacao:
            raise TaskValidationError(
                INVALID_DATE,
                f"Tarefa {task_id}: data_conclusao ({data_conclusao.isoformat()}) "
                f"anterior a data_criacao ({data_criacao.isoformat()}).",
            )

    return {
        "prioridade": prioridade,
        "data_criacao": data_criacao,
        "data_limite": data_limite,
        "data_conclusao": data_conclusao,
    }


def validar_tarefas(tasks: Any) -> list[dict[str, Any]]:
    """Valida toda a entrada antes de qualquer cálculo.

    Args:
        tasks: Entrada recebida por ``analyze_tasks``.

    Returns:
        Lista de tarefas normalizadas.

    Raises:
        TaskValidationError: ``INVALID_TASK_DATA`` se a entrada não for lista,
            ``EMPTY_TASK_LIST`` se estiver vazia, ou o código da tarefa inválida.
    """
    if not isinstance(tasks, list):
        raise TaskValidationError(INVALID_TASK_DATA, "A entrada deve ser uma lista de tarefas.")
    if not tasks:
        raise TaskValidationError(EMPTY_TASK_LIST, "Nenhuma tarefa foi fornecida.")

    ids_vistos: set[int] = set()
    return [_validar_tarefa(task, ids_vistos) for task in tasks]


# --------------------------------------------------------------------------
# Cálculo das métricas
# --------------------------------------------------------------------------


def _percentual(parte: int, total: int) -> float:
    """Calcula ``parte / total * 100`` com 2 casas; 0.0 se ``total`` for zero."""
    if total == 0:
        return 0.0
    return round(parte / total * 100, 2)


def _media(valores: list[float]) -> float:
    """Média aritmética com 2 casas; 0.0 para lista vazia."""
    if not valores:
        return 0.0
    return round(sum(valores) / len(valores), 2)


def _calcular_metricas(tarefas: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula as métricas de um grupo de tarefas já validadas.

    Args:
        tarefas: Tarefas normalizadas por ``validar_tarefas``.

    Returns:
        Totais, tempo médio de conclusão em horas e taxa de atraso.
    """
    concluidas = [t for t in tarefas if t["data_conclusao"] is not None]
    duracoes = [
        (t["data_conclusao"] - t["data_criacao"]).total_seconds() / 3600 for t in concluidas
    ]
    atrasadas = sum(1 for t in concluidas if t["data_conclusao"] > t["data_limite"])
    return {
        "total": len(tarefas),
        "concluidas": len(concluidas),
        "tempo_medio_conclusao_horas": _media(duracoes),
        "taxa_atraso_percentual": _percentual(atrasadas, len(concluidas)),
    }


def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Analisa uma lista de tarefas e retorna as métricas de produtividade.

    Args:
        tasks: Lista de tarefas no formato definido na especificação.

    Returns:
        Dicionário com ``total_tarefas``, ``total_concluidas``,
        ``total_pendentes``, ``tempo_medio_conclusao_horas``,
        ``taxa_atraso_percentual`` e ``indicadores_por_prioridade``.

    Raises:
        TaskValidationError: Se a entrada violar alguma regra da especificação.
    """
    tarefas = validar_tarefas(tasks)
    geral = _calcular_metricas(tarefas)
    por_prioridade = {
        p: _calcular_metricas([t for t in tarefas if t["prioridade"] == p]) for p in PRIORIDADES
    }
    logger.info(
        "analise_concluida",
        extra={"total_tarefas": geral["total"], "total_concluidas": geral["concluidas"]},
    )
    return {
        "total_tarefas": geral["total"],
        "total_concluidas": geral["concluidas"],
        "total_pendentes": geral["total"] - geral["concluidas"],
        "tempo_medio_conclusao_horas": geral["tempo_medio_conclusao_horas"],
        "taxa_atraso_percentual": geral["taxa_atraso_percentual"],
        "indicadores_por_prioridade": por_prioridade,
    }


if __name__ == "__main__":
    exemplo: list[dict[str, Any]] = [
        {"id": 101, "titulo": "Configurar repositório", "prioridade": "ALTA",
         "data_criacao": "2026-03-01T08:00:00", "data_limite": "2026-03-01T10:00:00",
         "data_conclusao": "2026-03-01T12:00:00", "status": "CONCLUIDA"},
        {"id": 102, "titulo": "Escrever spec", "prioridade": "ALTA",
         "data_criacao": "2026-03-02T08:00:00", "data_limite": "2026-03-02T12:00:00",
         "data_conclusao": "2026-03-02T10:00:00", "status": "CONCLUIDA"},
        {"id": 103, "titulo": "Revisar README", "prioridade": "BAIXA",
         "data_criacao": "2026-03-03T08:00:00", "data_limite": "2026-03-03T18:00:00",
         "data_conclusao": "2026-03-03T14:00:00", "status": "CONCLUIDA"},
        {"id": 104, "titulo": "Gravar vídeo", "prioridade": "MEDIA",
         "data_criacao": "2026-03-04T08:00:00", "data_limite": "2026-03-05T08:00:00",
         "data_conclusao": None, "status": "PENDENTE"},
    ]
    for chave, valor in analyze_tasks(exemplo).items():
        print(f"{chave}: {valor}")
