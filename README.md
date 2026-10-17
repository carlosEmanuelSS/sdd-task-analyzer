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
    {"id": 1, "status": "concluida", "prioridade": "alta",
     "data_criacao": "2026-03-01T08:00:00", "data_conclusao": "2026-03-01T12:00:00",
     "data_prevista": "2026-03-01T10:00:00"},
    {"id": 2, "status": "pendente", "prioridade": "baixa",
     "data_criacao": "2026-03-02T08:00:00"},
]
print(analyze_tasks(tarefas))
```

## Testes cobertos

| Teste | Cenário |
|---|---|
| `test_cenario1_*` | Cenário 1 — totais, tempo médio geral e por prioridade, taxa de atraso |
| `test_cenario2_conclusao_antes_da_criacao` | Cenário 2 — `TaskValidationError` para datas inconsistentes |
| `test_borda_lista_vazia` / `test_borda_apenas_pendentes` | Casos de borda — médias retornam `0.0` |
| `test_dados_invalidos_disparam_task_validation_error` | Validações das CONTEXT_RULES (status, prioridade, formato e fuso) |

## Fluxo de trabalho Git

- `main` — branch estável
- `feature/sdd-specification` — especificação e regras de contexto
- `feature/task-analyzer-impl` — implementação gerada via IA
- `feature/test-harness` — suíte de testes

Toda integração na `main` acontece por Pull Request revisado.

## Fases

- [x] Fase 1 — Especificação SDD e CONTEXT_RULES
- [x] Fase 2 — Implementação com IA, Test Harness e versionamento
- [ ] Fase 3 — CI/CD (GitHub Actions), Docker e relatório de governança
