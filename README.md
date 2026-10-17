# sdd-taskanalyzer

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![Tests](https://img.shields.io/badge/pytest-passing-brightgreen) ![Status](https://img.shields.io/badge/fase-2%20intermedi%C3%A1ria-orange)

Projeto da disciplina **Bootcamp III** — implementação do **TaskAnalyzer** com desenvolvimento
guiado por especificação (SDD), código gerado com apoio de IA e validado por um Test Harness em `pytest`.

## Estrutura

```
sdd-taskanalyzer/
├── README.md               # Este arquivo
├── CONTEXT_RULES.md        # Regras de governança da IA
├── .gitignore
├── requirements.txt        # Dependências autorizadas
├── specs/
│   └── task_analyzer_spec.md   # Contrato SDD
├── tests/
│   └── test_harness.py     # Test Harness (pytest)
└── src/
    └── task_analyzer.py    # analyze_tasks + TaskValidationError
```

## Como executar

Requer Python 3.11+.

```bash
git clone https://github.com/carlosEmanuelSS/sdd-taskanalyzer.git
cd sdd-taskanalyzer
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

python src/task_analyzer.py   # execução de exemplo
pytest -v                     # Test Harness
```

No Google Colab:

```python
!git clone https://github.com/carlosEmanuelSS/sdd-taskanalyzer.git
%cd sdd-taskanalyzer
!pip install -q -r requirements.txt
!pytest -v
```

## Uso

```python
from src.task_analyzer import analyze_tasks, TaskValidationError

tarefas = [
    {"id": 1, "titulo": "Configurar repositório", "prioridade": "ALTA",
     "data_criacao": "2026-03-01T08:00:00", "data_limite": "2026-03-01T10:00:00",
     "data_conclusao": "2026-03-01T12:00:00", "status": "CONCLUIDA"},
    {"id": 2, "titulo": "Gravar vídeo", "prioridade": "BAIXA",
     "data_criacao": "2026-03-02T08:00:00", "data_limite": "2026-03-03T08:00:00",
     "data_conclusao": None, "status": "PENDENTE"},
]

try:
    print(analyze_tasks(tarefas))
except TaskValidationError as erro:
    print(erro.code, erro.message)
```

Códigos de erro: `INVALID_TASK_DATA`, `INVALID_PRIORITY`, `INVALID_DATE`, `DUPLICATE_TASK_ID`, `EMPTY_TASK_LIST`.

## Testes cobertos

| Teste | Cenário de aceite |
|---|---|
| `test_cenario1_*` | 1 — Tempo médio de conclusão (e totais) |
| `test_cenario2_taxa_atraso` | 2 — Taxa de atraso |
| `test_cenario3_indicadores_por_prioridade` | 3 — Indicadores por BAIXA, MEDIA e ALTA |
| `test_cenario4_lista_vazia` | 4 — `EMPTY_TASK_LIST` |
| `test_cenario5_dados_invalidos` | 5 — `INVALID_TASK_DATA` |
| `test_cenario6_prioridade_invalida` | 6 — `INVALID_PRIORITY` |
| `test_cenario7_id_duplicado` | 7 — `DUPLICATE_TASK_ID` |
| `test_cenario8_*` | 8 — `INVALID_DATE` (inclui conclusão anterior à criação) |
| `test_borda_*` | Casos de borda — só pendentes retorna `0.0`; saída sempre consistente |

## Fluxo de trabalho Git

- `main` — branch estável
- `feature/sdd-specification` — especificação e regras de contexto
- `feature/task-analyzer-impl` — implementação gerada via IA
- `feature/test-harness` — suíte de testes
- `feature/alinhamento-fase1` — alinhamento ao contrato da Fase 1

Toda integração na `main` acontece por Pull Request revisado.

## Fases

- [x] Fase 1 — Especificação SDD e CONTEXT_RULES
- [x] Fase 2 — Implementação com IA, Test Harness e versionamento
- [ ] Fase 3 — CI/CD (GitHub Actions), Docker e relatório de governança
