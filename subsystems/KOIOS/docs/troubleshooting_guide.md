# EGOS Troubleshooting Guide (KOIOS)

Este guia fornece procedimentos passo a passo para diagnosticar e resolver problemas comuns de desenvolvimento encontrados no ambiente do projeto EGOS, particularmente ao trabalhar com ferramentas como o Cursor IDE.

## Índice

1.  [Problemas de Dependências (`ModuleNotFoundError`, `ImportError`)](#problemas-de-dependências)
2.  [Erros de Python Path e Importação](#erros-de-python-path--importação)
3.  [Erros de Validação de Schema Pydantic](#erros-de-validação-de-schema-pydantic)
4.  [Erros de Mocking e Patching em Testes Unitários](#erros-de-mocking--patching-em-testes-unitários)
5.  [Resolução de Erros do Linter (`ruff`)](#resolução-de-erros-do-linter-ruff)

---

## 1. Problemas de Dependências

**Sintomas:**
*   `ModuleNotFoundError: No module named 'some_package'`
*   `ImportError: cannot import name 'SomeClass' from 'some_package'`

**Diagnóstico e Resolução:**
*   **Verificar Ambiente Virtual:** Assegure-se de que o ambiente virtual Python correto (`.venv`) está ativado no seu terminal/IDE.
*   **Verificar `requirements.txt`:** Verifique se o pacote ausente está listado no arquivo principal `requirements.txt` ou em arquivos de requisitos específicos de subsistemas (se houver).
*   **Instalar/Atualizar Dependências:** Execute `pip install -r requirements.txt` a partir da raiz do projeto.
*   **Verificar Conflitos:** Execute `pip check` para identificar potenciais conflitos de versão entre pacotes instalados. Resolva os conflitos ajustando as versões no `requirements.txt`.
*   **Reinstalação Limpa (Se Necessário):** Exclua o diretório `.venv` e recrie/reinstale:
    ```bash
    rm -rf .venv
    python -m venv .venv
    source .venv/Scripts/activate # ou .venv/bin/activate no Linux/macOS
    pip install -r requirements.txt
    ```

---

## 2. Erros de Python Path & Importação

**Sintomas:**
*   `ModuleNotFoundError: No module named 'subsystems'` (ao importar entre subsistemas)
*   `AttributeError: module 'subsystems.X' has no attribute 'Y'` (ao importar submódulos)
*   `ImportError: attempted relative import with no known parent package`

**Diagnóstico e Resolução:**
*   **Garantir Execução a partir da Raiz do Projeto:** Execute scripts Python e testes *a partir do diretório raiz do projeto* (`C:/Eva Guarani EGOS` neste caso). Use comandos como `python -m unittest discover ...` ou `python subsystems/CORUJA/some_script.py`. Evite executar scripts diretamente de dentro dos diretórios de subsistemas.
*   **Verificar Arquivos `__init__.py`:** Verifique se todos os diretórios que devem ser tratados como pacotes Python (por exemplo, `subsystems/`, `subsystems/CORUJA/`, `subsystems/CORUJA/core/`, etc.) contêm um arquivo `__init__.py` (mesmo que vazio). Esses arquivos indicam ao Python que um diretório é um pacote.
*   **Verificar Importações em `__init__.py`:** Se você pretende importar submódulos diretamente (por exemplo, `from subsystems import CORUJA`), verifique se as importações necessárias e definições de `__all__` estão presentes no arquivo `__init__.py` do pacote pai.
*   **Verificar `sys.path` (Depuração):** Adicione `import sys; print(sys.path)` temporariamente em seu script ou teste para ver se o diretório raiz do projeto está incluído. Arquivos de teste frequentemente precisam adicionar manualmente a raiz do projeto ao path.

---

## 3. Erros de Validação de Schema Pydantic

**Sintomas:**
*   `pydantic.ValidationError: ... [type=extra_forbidden, ...]`
*   `pydantic.ValidationError: ... [type=missing, ...]`
*   `pydantic.ValidationError: ... [type=value_error, ...]`
*   `pydantic.errors.PydanticUserError: "Config" and "model_config" cannot be used together`

**Diagnóstico e Resolução:**
*   **Ler o Erro:** Leia atentamente a mensagem de erro do Pydantic. Geralmente, ela aponta para o campo específico e o tipo de erro (`extra_forbidden`, `missing`, `value_error`, incompatibilidade de tipo).
*   **Verificar Definição do Schema:** Abra o arquivo de schema relevante (geralmente em `subsystems/KOIOS/schemas/`) e compare a definição do campo problemático (nome, tipo, `Optional`, restrições de `Field`) com os dados sendo passados.
*   **`extra_forbidden`:** Você está passando um nome de campo que *não* está definido no modelo Pydantic. Verifique se há erros de digitação ou remova o campo extra. Certifique-se de que a configuração do modelo permite campos extras (`extra='allow'`) apenas se for realmente necessário.
*   **`missing`:** Um campo obrigatório (não marcado como `Optional` e sem um valor padrão) não foi fornecido. Certifique-se de que os dados de entrada incluam este campo.
*   **`value_error` / Incompatibilidade de Tipo:** Os dados fornecidos para um campo não correspondem ao tipo esperado (por exemplo, passar uma string para um campo `int`). Corrija o tipo de dados.
*   **Erro `"Config" and "model_config"`:** Evite nomear um *campo* no seu modelo Pydantic como `model_config`, pois isso conflita com o mecanismo de configuração do Pydantic v2. Renomeie seu campo (por exemplo, para `model_configuration`).

---

## 4. Erros de Mocking & Patching em Testes Unitários

**Sintomas:**
*   `TypeError: test_method() missing X required positional arguments: 'mock_...'`
*   `AttributeError: <MagicMock name='...' id='...'> does not have attribute '...'`
*   `AttributeError: 'module' object has no attribute '...'` (quando o alvo do patch está errado)

**Diagnóstico e Resolução:**
*   **Verificar Alvo do Patch:** Certifique-se de que a string passada para `@patch(...)` ou `patch(...)` aponta para onde o objeto é *consultado* (importado/usado), não necessariamente onde ele é definido. Exemplo: Se `module_a.py` importa `func` de `module_b.py` (`from module_b import func`), e você quer fazer mock de `func` dentro de `module_a`, você deve usar patch em `'module_a.func'`.
*   **Verificar Nomes dos Argumentos Mock:** Ao usar decoradores de classe/método (`@patch`), o `unittest` passa os objetos mock como argumentos para o método de teste, geralmente na *ordem inversa* dos decoradores. Certifique-se de que a assinatura do seu método de teste nomeia e aceita corretamente esses argumentos (por exemplo, `def test_something(self, mock_c, mock_b, mock_a): ...`).
*   **Configurar Valores de Retorno/Side Effects do Mock:** Se o código em teste chama métodos no objeto mockado, certifique-se de que o mock está configurado com valores de retorno ou side effects apropriados *antes* que a chamada aconteça (frequentemente em `setUp` ou dentro do teste). Use `AsyncMock` para mockar funções `async`.
*   **Usar `spec=...`:** Ao criar um `MagicMock`, usar `spec=ClasseOriginal` ajuda a detectar erros de atributo se você tentar acessar métodos/atributos no mock que não existem na classe original.
*   **Depurar com `print` ou Debugger:** Imprima temporariamente o objeto mock ou use um debugger para inspecionar seu estado, atributos e argumentos de chamada (`mock_obj.call_args`, `mock_obj.method_calls`).

---

## 5. Resolução de Erros do Linter (`ruff`)

**Sintomas:**
*   Erros reportados pelo `ruff` durante verificações de pré-commit ou no IDE.
*   Erros comuns: `F841` (variável não utilizada), `E501` (linha muito longa), `F401` (importação não utilizada), `E712` (comparação com True/False/None deve ser `is`/`is not`), `F821` (nome indefinido).

**Diagnóstico e Resolução:**
*   **Priorizar Erros do Linter:** Corrija os erros do linter *primeiro*. Eles frequentemente indicam problemas subjacentes de qualidade de código ou bugs potenciais.
*   **Ler Mensagem de Erro:** `ruff` geralmente fornece mensagens claras e códigos de erro. Procure o código (por exemplo, `ruff F841`) online se não tiver certeza.
*   **Integração com IDE:** Certifique-se de que o `ruff` está integrado com seu IDE (como VS Code/Cursor) para feedback em tempo real.
*   **Variáveis/Importações Não Utilizadas (`F841`/`F401`):** Remova a variável ou importação não utilizada. Se intencionalmente não utilizada (por exemplo, parte de uma interface), prefixe com um underscore (`_unused_var`).
*   **Linha Muito Longa (`E501`):** Quebre linhas longas usando parênteses, colchetes, chaves ou barras invertidas (menos preferido). Refatore linhas complexas em partes menores ou funções auxiliares. Siga as diretrizes de `python_coding_standards.mdc`.
*   **Nome Indefinido (`F821`):**
    *   Verifique se há erros de digitação no nome da variável, função ou classe.
    *   Certifique-se de que o nome foi definido (atribuído a) *antes* de ser usado no fluxo do código.
    *   Verifique se o nome foi importado corretamente do módulo apropriado (`from module import name`).
    *   **Caso Especial: Aliases em `__init__.py`:** Se `F821` ocorrer para um nome que *parece* estar definido, verifique se ele é um *alias* definido em um arquivo `__init__.py` de um pacote pai. Por exemplo, se `subsystems/CORUJA/interfaces/__init__.py` contém `from .model_interface import ModelInterface as AIModelInterface`, então um arquivo que usa `AIModelInterface` deve importar diretamente do pacote de interfaces: `from subsystems.CORUJA.interfaces import AIModelInterface`, e não de `subsystems.CORUJA.interfaces.model_interface`.
    *   **Cache do Linter:** Se a importação parece correta, limpe o cache do linter (ex: `rm -rf .ruff_cache`) e reinicie o IDE, pois informações antigas podem estar sendo usadas.
*   **Executar Manualmente:** Use `ruff check .` e `ruff format .` na linha de comando para verificar correções. Use `ruff check <file_path> --select <ERROR_CODE>` (ex: `ruff check path/to/file.py --select F821`) para focar em erros específicos durante a depuração.

---

*Este guia deve ser continuamente atualizado à medida que novos problemas comuns são identificados.*
