# sdd-task-analyzer

[![CI](https://github.com/carlosEmanuelSS/sdd-task-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/carlosEmanuelSS/sdd-task-analyzer/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/python-3.11-blue) ![Docker](https://img.shields.io/badge/docker-python%3A3.11--slim-2496ED) ![Status](https://img.shields.io/badge/fase-3%20final-brightgreen)

Projeto da disciplina **Bootcamp III** — implementação do **TaskAnalyzer** com desenvolvimento
guiado por especificação (SDD), código gerado com apoio de IA e validado por um Test Harness em `pytest`,
integrado continuamente pelo GitHub Actions e empacotado em contêiner Docker.

## Estrutura

```
sdd-task-analyzer/
├── .github/
│   └── workflows/
│       └── ci.yml          # Pipeline CI/CD (GitHub Actions)
├── Dockerfile              # Imagem python:3.11-slim que roda o Test Harness
├── docker-compose.yml      # Orquestração: um comando para rodar a suíte
├── .dockerignore
├── README.md               # Este arquivo
├── CONTEXT_RULES.md        # Regras de governança da IA
├── .gitignore
├── requirements.txt        # Dependências autorizadas
├── specs/
│   ├── system_design_document.pdf  # Especificação SDD original (Fase 1)
│   ├── requirements.yaml   # Contrato em formato estruturado
│   └── task_analyzer_spec.md       # Contrato SDD transposto
├── tests/
│   └── test_harness.py     # Test Harness (pytest)
└── src/
    └── task_analyzer.py    # analyze_tasks + TaskValidationError
```

## Como executar

Requer Python 3.11+.

```bash
git clone https://github.com/carlosEmanuelSS/sdd-task-analyzer.git
cd sdd-task-analyzer
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

python src/task_analyzer.py   # execução de exemplo
pytest -v                     # Test Harness
```

No Google Colab:

```python
!git clone https://github.com/carlosEmanuelSS/sdd-task-analyzer.git
%cd sdd-task-analyzer
!pip install -q -r requirements.txt
!pytest -v
```

## Executar com Docker

Só é preciso ter o Docker instalado; Python e dependências ficam dentro do contêiner.

```bash
docker compose run --rm task-analyzer          # constrói (se preciso) e roda o Test Harness
```

Ou passo a passo:

```bash
docker build -t sdd-task-analyzer .
docker run --rm sdd-task-analyzer
```

A imagem usa `python:3.11-slim`, instala apenas o `requirements.txt` e roda como usuário sem
privilégios de root. O comando padrão é `pytest tests/test_harness.py -v`.

## Integração contínua (GitHub Actions)

O workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda a cada push e Pull Request
nas branches `main` e `develop`, em `ubuntu-latest` com Python 3.11:

| Job | O que faz |
|---|---|
| Test Harness (pytest) | Instala o `requirements.txt` e executa `pytest tests/test_harness.py -v` |
| Análise de segurança (Bandit) | Análise estática (SAST) de `src/`; qualquer achado quebra o build |
| Build e testes no contêiner | Depois dos testes, constrói a imagem Docker e roda a suíte dentro dela |

Se qualquer job falhar, a esteira para e o Pull Request não pode ser integrado à `main`.

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

- `main` — branch estável, protegida pelo check do CI
- `develop` — integração das funcionalidades da Fase 3
- `feature/sdd-specification` — especificação e regras de contexto
- `feature/task-analyzer-impl` — implementação gerada via IA
- `feature/test-harness` — suíte de testes
- `feature/alinhamento-fase1` — alinhamento ao contrato da Fase 1

Toda integração acontece por Pull Request revisado e com o CI verde.

## Fases

- [x] Fase 1 — Especificação SDD e CONTEXT_RULES
- [x] Fase 2 — Implementação com IA, Test Harness e versionamento
- [x] Fase 3 — CI/CD (GitHub Actions), Docker e relatório de governança
