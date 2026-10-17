# Especificação SDD — TaskAnalyzer

> Contrato técnico executável transposto da Fase 1 (Spec-Driven Development).
> O código em `src/task_analyzer.py` deve seguir este contrato à risca.

## 1. Objetivo

Receber uma lista de tarefas e devolver métricas consolidadas de produtividade:
quantidade de tarefas, tempo médio de conclusão (geral e por prioridade) e taxa de atraso.

## 2. Interface pública

```python
class TaskValidationError(ValueError): ...

def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]: ...
```

## 3. Entrada

Lista de dicionários. Cada tarefa possui:

| Campo            | Tipo                    | Obrigatório                | Regra |
|------------------|-------------------------|----------------------------|-------|
| `id`             | int / str               | Sim                        | Identificador da tarefa |
| `status`         | str                     | Sim                        | `"pendente"` ou `"concluida"` |
| `prioridade`     | str                     | Sim                        | `"alta"`, `"media"` ou `"baixa"` |
| `data_criacao`   | str ISO 8601 / datetime | Sim                        | Sem fuso horário |
| `data_conclusao` | str ISO 8601 / datetime | Sim, se `status=concluida` | Não pode ser anterior a `data_criacao` |
| `data_prevista`  | str ISO 8601 / datetime | Não                        | Usada no cálculo de atraso |

## 4. Saída

```json
{
  "total_tarefas": 4,
  "total_concluidas": 3,
  "total_pendentes": 1,
  "tempo_medio_conclusao_horas": 4.0,
  "tempo_medio_por_prioridade_horas": {"alta": 3.0, "media": 0.0, "baixa": 6.0},
  "taxa_atraso_percentual": 33.33
}
```

## 5. Regras de negócio

- **RN01** — Tempo de conclusão (horas) = `data_conclusao - data_criacao`, somente para tarefas concluídas.
- **RN02** — `tempo_medio_conclusao_horas` = média dos tempos de conclusão, arredondada em 2 casas.
- **RN03** — `tempo_medio_por_prioridade_horas` traz sempre as três prioridades; prioridade sem tarefa concluída retorna `0.0`.
- **RN04** — Tarefa atrasada = concluída com `data_conclusao > data_prevista`.
- **RN05** — `taxa_atraso_percentual` = atrasadas / concluídas com `data_prevista` × 100 (2 casas).
- **RN06** — Nenhuma divisão por zero: sem base de cálculo, a métrica retorna `0.0`.

## 6. Regras de validação (lançam `TaskValidationError`)

- **RV01** — `data_conclusao < data_criacao` (inconsistência cronológica).
- **RV02** — `status` fora de `pendente`/`concluida`.
- **RV03** — `prioridade` fora de `alta`/`media`/`baixa`.
- **RV04** — Tarefa concluída sem `data_conclusao`.
- **RV05** — Data em formato inválido ou com fuso horário.
- **RV06** — Entrada que não é lista, ou item que não é dicionário.

## 7. Cenários de aceite (Dado-Quando-Então)

**Cenário 1 — Cálculo de métricas com sucesso**
- **Dado** 4 tarefas (3 concluídas em 4h, 2h e 6h; 1 delas após o prazo; 1 pendente)
- **Quando** `analyze_tasks` é executada
- **Então** retorna total 4, concluídas 3, pendentes 1, média geral 4.0h, alta 3.0h, baixa 6.0h, média 0.0h e atraso 33.33%.

**Cenário 2 — Datas inconsistentes**
- **Dado** uma tarefa concluída com `data_conclusao` anterior a `data_criacao`
- **Quando** `analyze_tasks` é executada
- **Então** é lançada `TaskValidationError` informando a inconsistência cronológica.

**Cenário 3 — Casos de borda**
- **Dado** uma lista vazia, ou uma lista apenas com tarefas pendentes
- **Quando** `analyze_tasks` é executada
- **Então** as médias e a taxa de atraso retornam `0.0`, sem exceções não tratadas.
