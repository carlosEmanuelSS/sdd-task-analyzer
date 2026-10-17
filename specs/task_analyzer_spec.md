# Especificação SDD — TaskAnalyzer

> Contrato técnico executável transposto da Fase 1 (Spec-Driven Development).
> Autor: Carlos Emanuel Santos da Silva — Análise e Desenvolvimento de Sistemas, Asa Norte, Turma A.
> Qualquer mudança que altere o comportamento esperado do TaskAnalyzer deve ser refletida primeiro nesta especificação.

## 1. Propósito do módulo

O TaskAnalyzer analisa um conjunto de tarefas e gera métricas de produtividade:
tempo médio de conclusão, taxa de atraso e indicadores separados por prioridade.
O módulo recebe os dados, valida, processa conforme esta especificação e retorna
os resultados de forma organizada e consistente.

## 2. Contrato executável de interface

```python
class TaskValidationError(ValueError):
    code: str  # um dos códigos da seção 5

def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]: ...
```

### 2.1 Entrada

Lista de tarefas. Cada tarefa segue a estrutura:

| Campo            | Tipo              | Descrição                    |
|------------------|-------------------|------------------------------|
| `id`             | inteiro           | Identificador único          |
| `titulo`         | texto             | Título da tarefa             |
| `prioridade`     | texto             | Prioridade da tarefa         |
| `data_criacao`   | data/hora         | Data e hora de criação       |
| `data_limite`    | data/hora         | Prazo para conclusão         |
| `data_conclusao` | data/hora ou nulo | Data e hora de conclusão     |
| `status`         | texto             | Situação atual da tarefa     |

- Prioridades aceitas: `BAIXA`, `MEDIA` e `ALTA`.
- `data_conclusao` pode ser nula enquanto a tarefa não estiver concluída.
- Datas aceitas como `datetime` ou texto ISO 8601 (`AAAA-MM-DDTHH:MM:SS`), sem fuso horário.

### 2.2 Saída

```json
{
  "total_tarefas": 4,
  "total_concluidas": 3,
  "total_pendentes": 1,
  "tempo_medio_conclusao_horas": 4.0,
  "taxa_atraso_percentual": 33.33,
  "indicadores_por_prioridade": {
    "BAIXA": {"total": 1, "concluidas": 1, "tempo_medio_conclusao_horas": 6.0, "taxa_atraso_percentual": 0.0},
    "MEDIA": {"total": 1, "concluidas": 0, "tempo_medio_conclusao_horas": 0.0, "taxa_atraso_percentual": 0.0},
    "ALTA":  {"total": 2, "concluidas": 2, "tempo_medio_conclusao_horas": 3.0, "taxa_atraso_percentual": 50.0}
  }
}
```

| Métrica                      | Descrição |
|------------------------------|-----------|
| `tempo_medio_conclusao_horas`| Média do tempo entre criação e conclusão das tarefas concluídas |
| `taxa_atraso_percentual`     | Percentual de tarefas concluídas após a `data_limite` |
| `indicadores_por_prioridade` | Métricas agrupadas por `BAIXA`, `MEDIA` e `ALTA` (sempre as três) |

## 3. Regras e validações

1. A entrada deve ser uma lista de tarefas válida.
2. Os dados devem ser validados antes dos cálculos.
3. Cada tarefa deve possuir um `id` único.
4. A prioridade deve ser `BAIXA`, `MEDIA` ou `ALTA`.
5. Os campos de data devem possuir valores válidos.
6. Dados inválidos não podem ser utilizados no cálculo das métricas.
7. Cálculos dependentes de conclusão utilizam somente tarefas que possuam `data_conclusao`.
8. Uma lista vazia deve ser tratada de forma previsível (erro `EMPTY_TASK_LIST`).
9. Entradas inválidas devem gerar o código de erro correspondente.
10. A estrutura de saída deve permanecer consistente.

### 3.1 Regras de cálculo (detalhamento da Fase 2)

- Tarefa concluída = possui `data_conclusao`; pendente = `data_conclusao` nula.
- Tempo de conclusão (horas) = `data_conclusao - data_criacao`.
- Tarefa atrasada = concluída com `data_conclusao > data_limite`.
- `taxa_atraso_percentual` = atrasadas / concluídas × 100.
- Médias e percentuais arredondados em 2 casas; sem base de cálculo retornam `0.0` (nunca divisão por zero).
- `data_conclusao` anterior a `data_criacao` é data inválida (`INVALID_DATE`).

## 4. Tratamento de erros

Todos os erros são lançados como `TaskValidationError`, com o atributo `code`:

| Código              | Situação |
|---------------------|----------|
| `INVALID_TASK_DATA` | Dados da tarefa não seguem a estrutura definida |
| `INVALID_PRIORITY`  | Prioridade não permitida |
| `INVALID_DATE`      | Data informada é inválida (formato, fuso ou conclusão antes da criação) |
| `DUPLICATE_TASK_ID` | Identificador duplicado |
| `EMPTY_TASK_LIST`   | Lista de tarefas vazia |

## 5. Cenários de aceite (Dado-Quando-Então)

1. **Tempo médio de conclusão** — Dado um conjunto válido de tarefas concluídas com datas de criação e conclusão, quando o TaskAnalyzer processar as tarefas, então deverá calcular e retornar o tempo médio de conclusão.
2. **Taxa de atraso** — Dado um conjunto de tarefas concluídas com datas limite e datas de conclusão, quando o TaskAnalyzer analisar as tarefas, então deverá identificar as concluídas fora do prazo e calcular a taxa de atraso.
3. **Indicadores por prioridade** — Dado um conjunto de tarefas classificadas como BAIXA, MEDIA ou ALTA, quando o TaskAnalyzer processar os dados, então deverá apresentar os indicadores de cada prioridade.
4. **Lista vazia** — Dado que nenhuma tarefa tenha sido fornecida, quando uma análise for solicitada, então deverá ser retornado o erro `EMPTY_TASK_LIST`.
5. **Dados inválidos** — Dado uma tarefa que não siga a estrutura definida, quando o TaskAnalyzer tentar processá-la, então deverá ser retornado o erro `INVALID_TASK_DATA`.
6. **Prioridade inválida** — Dado uma tarefa cuja prioridade não seja BAIXA, MEDIA ou ALTA, quando os dados forem validados, então deverá ser retornado o erro `INVALID_PRIORITY`.
7. **Identificador duplicado** — Dado duas tarefas com o mesmo identificador, quando a lista for validada, então deverá ser retornado o erro `DUPLICATE_TASK_ID`.
8. **Data inválida** — Dado uma tarefa contendo uma data inválida (incluindo conclusão anterior à criação), quando os dados forem validados, então deverá ser retornado o erro `INVALID_DATE`.

### 5.1 Casos de borda (exigidos na Fase 2)

- Lista apenas com tarefas pendentes: médias e taxa de atraso retornam `0.0`, sem exceção.
- Lista vazia: exceção **tratada** `TaskValidationError` com código `EMPTY_TASK_LIST` (cenário 4).

## 6. Plano de homologação humana

Antes da aprovação do código gerado com auxílio de IA, é verificado:

1. **Conformidade com a especificação** — o código segue o que foi definido.
2. **Qualidade e organização** — o código está claro e compreensível.
3. **Comportamento esperado** — as funcionalidades estão corretas.
4. **Testes e tratamento de erros** — testes e possíveis erros verificados.
5. **Aprovação humana** — sem alterações não previstas, aprovado antes do versionamento.
