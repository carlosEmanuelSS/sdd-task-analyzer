# CONTEXT_RULES — Governança de Contexto para Agentes de IA

Transposto da Fase 1 (seção 3 da Especificação SDD do TaskAnalyzer).

Este arquivo é fornecido como contexto ao agente de IA durante a implementação.
O objetivo é manter o desenvolvimento alinhado à especificação (`specs/task_analyzer_spec.md`),
evitar alterações não planejadas e garantir que o código produzido possa ser revisado e testado.

## 1. Diretrizes de arquitetura e desenvolvimento

- Utilizar Python 3.11 ou superior.
- Utilizar type hints.
- Seguir as recomendações da PEP 8.
- Utilizar docstrings no padrão Google.
- Utilizar nomes claros e descritivos.
- Criar funções pequenas e com responsabilidades bem definidas.
- Manter a lógica de negócio separada das operações de entrada e saída.
- Produzir mensagens de exceção específicas.
- Utilizar logging estruturado quando necessário.
- Manter o código legível, organizado e testável.
- Evitar dependências externas que não tenham sido autorizadas.

## 2. Regras para utilização de IA

A IA deverá:

- consultar a especificação antes de realizar alterações;
- respeitar os contratos de entrada e saída;
- preservar os códigos de erro (`INVALID_TASK_DATA`, `INVALID_PRIORITY`, `INVALID_DATE`, `DUPLICATE_TASK_ID`, `EMPTY_TASK_LIST`);
- implementar somente as funcionalidades previstas;
- respeitar os cenários de aceite;
- manter as assinaturas públicas definidas;
- produzir ou atualizar testes quando necessário;
- informar sempre que uma solicitação entrar em conflito com a especificação.

## 3. Restrições para agentes de IA

A IA não deverá:

- criar requisitos sem autorização;
- assumir comportamentos não especificados;
- alterar ou remover cenários de aceite para facilitar a implementação;
- modificar testes para esconder erros;
- ignorar falhas encontradas;
- adicionar bibliotecas externas sem autorização;
- alterar a estrutura prevista do projeto;
- alterar assinaturas públicas sem autorização;
- persistir os dados em arquivos ou banco de dados;
- gerar código sem os testes correspondentes;
- produzir código duplicado e desnecessário.

Qualquer mudança que altere o comportamento esperado do TaskAnalyzer deverá ser refletida
primeiro na especificação.

## 4. Requisitos técnicos da Fase 2

- Type hints em 100% das funções e parâmetros.
- Erros lançados como a exceção específica `TaskValidationError`, carregando o código de erro da spec.
- Prevenção de divisão por zero: métricas sem base de cálculo retornam `0.0`.
- Dependência autorizada: apenas `pytest` (ver `requirements.txt`); o código de produção usa só a biblioteca padrão.
- Merge na `main` somente via Pull Request revisado e com 100% dos testes passando.
