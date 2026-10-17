# CONTEXT_RULES — Governança do Assistente de IA

Regras fornecidas como contexto ao assistente de IA antes de qualquer geração de código.
Todo código gerado é revisado por um humano contra estas regras antes do merge na `main`.

## 1. Fonte da verdade
- A única fonte de requisitos é `specs/task_analyzer_spec.md`.
- É proibido inventar campos, métricas, status ou prioridades que não estejam na especificação.
- Em caso de ambiguidade, a IA deve perguntar em vez de supor.

## 2. Linguagem e ambiente
- Python **3.11 ou superior**.
- Somente biblioteca padrão no código de produção (`datetime`, `typing`).
- Dependência de teste autorizada: `pytest` (ver `requirements.txt`).
- Proibido adicionar bibliotecas que não estejam em `requirements.txt`.

## 3. Qualidade do código
- Type hints em **100%** das funções, parâmetros e retornos.
- Docstrings em português explicando argumentos, retorno e exceções.
- Funções pequenas, nomes descritivos em português, sem código morto.

## 4. Tratamento de erros
- Erros de dados devem lançar a exceção específica `TaskValidationError`.
- Proibido `except Exception` genérico ou silenciar erros.
- **Nenhuma divisão por zero**: métricas sem base de cálculo retornam `0.0`.

## 5. Saída
- O retorno de `analyze_tasks` deve conter exatamente as chaves definidas na spec.
- Valores de tempo em horas (`float`), arredondados em 2 casas.

## 6. Testes
- Todo cenário de aceite da spec deve ter teste correspondente em `tests/test_harness.py`.
- O merge só acontece com **100% dos testes passando** no pytest.

## 7. Versionamento
- Uma branch `feature/*` por funcionalidade, commits pequenos no padrão Conventional Commits.
- Integração na `main` somente via Pull Request revisado.
