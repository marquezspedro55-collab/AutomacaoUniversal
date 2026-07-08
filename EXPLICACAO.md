# 📚 EXPLICAÇÃO COMPLETA DO CÓDIGO — Automação Universal

Este documento é um mini-curso de Python que percorre o projeto módulo por módulo, explicando o que cada trecho faz, por que foi escrito assim, qual biblioteca usa e como o Python o interpreta.

---

## 1. Visão geral do fluxo de execução

Quando você roda `python main.py`, acontece o seguinte:

1. O Python lê `main.py` de cima para baixo. Os `import` no topo carregam os outros módulos **uma única vez** (o Python guarda módulos importados em cache, em `sys.modules`).
2. A linha `if __name__ == "__main__":` verifica se o arquivo está sendo executado diretamente (e não importado por outro). Só então chama `main()`.
3. `main()` garante que as pastas existem (`ensure_directories`), imprime o cabeçalho e entra em um laço `while True` — o "coração" do programa.
4. Cada texto digitado é interpretado pelo **parser**, executado pelo **launcher** e registrado pelo **database** dentro do **json_manager**.

```
usuário → main.py → parser.py → launcher.py → database.py → json_manager.py → database.json
                                     └──────────→ logger.py → app.log
```

---

## 2. config.py — a fonte única de configuração

### Por que existe
Se caminhos, nomes de aplicativos e constantes ficassem espalhados pelos arquivos, qualquer mudança exigiria caçar ocorrências pelo projeto inteiro. Centralizar em `config.py` é Clean Code básico: **uma fonte de verdade**.

### Conceitos linha a linha

```python
from __future__ import annotations
```
Faz o Python tratar as anotações de tipo como texto avaliado sob demanda, permitindo sintaxes modernas (`dict[str, str]`, `int | None`) mesmo em versões mais antigas do 3.x. É convenção colocá-la em todos os módulos.

```python
BASE_DIR: Path = Path(__file__).resolve().parent
```
- `__file__` é uma variável mágica: o caminho do arquivo atual.
- `Path(...)` (do módulo **pathlib**) transforma a string em um objeto de caminho orientado a objetos, com métodos como `.exists()`, `.is_dir()`, e o operador `/` sobrecarregado para juntar caminhos (`DATA_DIR = BASE_DIR / "data"`). Isso substitui o antigo `os.path.join` com muito mais legibilidade.
- `.resolve()` converte para caminho absoluto; `.parent` sobe um nível (a pasta do projeto).
- `: Path` é um **type hint**: não muda a execução, mas documenta o tipo e permite que editores e ferramentas (mypy, pylance) detectem erros antes de rodar.

```python
class OperatingSystem(Enum):
    WINDOWS = "Windows"
```
**Enum** cria um conjunto fechado de valores nomeados. Comparar `CURRENT_OS is OperatingSystem.WINDOWS` é mais seguro do que comparar strings soltas ("windows"? "Windows"? "WINDOWS"?), porque erros de digitação viram `AttributeError` imediato em vez de bug silencioso. O macOS aparece como `"Darwin"` porque é isso que `platform.system()` retorna — Darwin é o núcleo do macOS.

```python
def detect_os() -> OperatingSystem:
    system = platform.system()
    for os_member in OperatingSystem: ...
```
O módulo **platform** consulta o sistema operacional em tempo de execução. O laço `for` itera sobre os membros do Enum (Enums são iteráveis) e devolve o membro cujo `.value` bate com o retorno.

```python
def get_apps_map() -> dict[str, str]:
    match CURRENT_OS:
        case OperatingSystem.WINDOWS: return APPS_WINDOWS
```
**match/case** (Python 3.10+) é o "structural pattern matching": compara o valor contra padrões, de cima para baixo. `case _:` é o coringa (equivale ao `else`). Aqui substitui uma cadeia de `if/elif` com mais clareza.

```python
directory.mkdir(parents=True, exist_ok=True)
```
Cria a pasta; `parents=True` cria intermediárias (como `mkdir -p`), `exist_ok=True` não lança erro se já existir. Isso torna a função **idempotente**: pode ser chamada mil vezes com o mesmo resultado.

Os dicionários `APPS_WINDOWS`, `APPS_LINUX`, `APPS_MACOS` mapeiam *o que o usuário digita* → *o executável real*. **Dicionários** (`dict`) são tabelas de chave/valor com busca em tempo praticamente constante — a estrutura ideal para "traduções" como essa.

---

## 3. logger.py — registro profissional de eventos

O módulo **logging** da biblioteca padrão é o jeito certo de registrar eventos (em vez de `print` espalhado):

```python
handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
```
- Um **handler** define o destino do log (aqui, o arquivo `logs/app.log`).
- Um **formatter** define o layout: `%(asctime)s` (data/hora), `%(levelname)s` (INFO/ERROR), `%(module)s` (arquivo de origem), `%(message)s`.

```python
_configured = False
def get_logger(name): 
    global _configured
```
A flag de módulo garante que o handler seja adicionado **uma única vez** (senão cada import duplicaria as linhas no log). `global` indica que a função altera a variável do módulo, não uma local. O próprio módulo `logging` já funciona como **Singleton**: `logging.getLogger("x")` sempre devolve a mesma instância para o mesmo nome.

Os módulos usam `logger.info(...)`, `logger.error(...)` e `logger.exception(...)` — este último grava também o *traceback* completo, essencial para depurar erros inesperados.

---

## 4. json_manager.py — o guardião do banco JSON único

### Responsabilidade única
Somente este módulo abre `database.json`. Se um dia o armazenamento migrar para SQLite, só este arquivo muda — o resto do projeto nem percebe. Isso é o **S** de SOLID (Single Responsibility) na prática.

### Pontos-chave

```python
with DATABASE_FILE.open("r", encoding="utf-8") as file:
    return json.load(file)
```
- `with` é um **gerenciador de contexto**: garante que o arquivo será fechado mesmo se ocorrer erro no meio (o Python chama `__exit__` automaticamente).
- **json.load** converte o texto JSON em estruturas Python (objeto→`dict`, array→`list`, string→`str`, number→`int/float`). `json.dump` faz o caminho inverso; `ensure_ascii=False` preserva acentos e `indent=2` deixa o arquivo legível.

```python
except json.JSONDecodeError:
    backup = DATABASE_FILE.with_suffix(".corrompido.bak")
    shutil.copy2(DATABASE_FILE, backup)
```
Se o arquivo estiver corrompido (editado à mão, queda de energia), o programa **não trava nem apaga dados silenciosamente**: usa **shutil** para copiar o arquivo defeituoso como backup (`copy2` preserva metadados) e recria a estrutura padrão.

```python
tmp_file = DATABASE_FILE.with_suffix(".tmp")
with tmp_file.open("w", ...) as file:
    json.dump(data, file, ...)
tmp_file.replace(DATABASE_FILE)
```
**Escrita atômica**: grava primeiro num arquivo temporário e só depois o move por cima do original. `Path.replace` é uma operação atômica no sistema de arquivos — ou acontece por inteiro, ou não acontece. Assim, uma queda no meio da gravação jamais corrompe o banco. Essa técnica é usada em software profissional de verdade.

```python
data = json.loads(json.dumps(DEFAULT_STRUCTURE))
```
Truque de **cópia profunda**: serializa e desserializa a estrutura padrão para obter um clone independente (alterar o clone não altera o molde). Alternativa: `copy.deepcopy`.

---

## 5. database.py — regras de negócio da persistência

```python
@dataclass
class ExecutionRecord:
    comando: str
    tipo: str
    ...
```
O decorador **@dataclass** gera automaticamente `__init__`, `__repr__` e `__eq__` a partir dos atributos anotados. Sem ele, seriam ~15 linhas de boilerplate. É orientação a objetos pragmática: uma classe que existe para **carregar dados com tipo e nome**, não para esconder lógica.

`asdict(record)` converte a dataclass em `dict` — perfeito para gravar em JSON.

```python
contadores[key] = contadores.get(key, 0) + 1
```
`dict.get(chave, padrão)` devolve o valor ou o padrão se a chave não existir. É o idioma clássico de **contador** em Python (alternativa: `collections.Counter`).

```python
mais_usados = sorted(data["contadores"].items(), key=lambda par: par[1], reverse=True)[:10]
```
- `.items()` devolve pares `(chave, valor)`.
- `sorted(..., key=lambda par: par[1])` ordena pelos **valores** (posição 1 da tupla). Uma **lambda** é uma função anônima de uma expressão só.
- `reverse=True` = decrescente; `[:10]` é **fatiamento** de lista (os 10 primeiros).

```python
sucessos = sum(1 for item in historico if item["status"] == "sucesso")
```
**Expressão geradora** dentro de `sum`: percorre a lista sem criar outra lista na memória, somando 1 para cada item que passa no filtro. Elegante e eficiente.

```python
return [item for item in get_history() if term in item["comando"].lower()]
```
**List comprehension**: constrói uma lista filtrada em uma linha, equivalente a um `for` + `if` + `append`, porém mais idiomático.

---

## 6. parser.py — do texto livre à intenção estruturada

O parser implementa uma **cadeia de resolução** com prioridade explícita (documentada na docstring): caminho absoluto → URL → pasta especial → site conhecido → app conhecido → caminho relativo → desconhecido. A ordem importa: o mais específico vence.

```python
path = Path(text).expanduser()
if path.is_absolute() and path.exists():
```
`expanduser()` converte `~` na pasta home do usuário. `is_absolute()` e `exists()` são métodos do pathlib que consultam o sistema de arquivos.

```python
def _looks_like_url(text: str) -> bool:
    return lowered.startswith(("http://", "https://", "www.")) or ...
```
`startswith` aceita uma **tupla** de prefixos — testa todos de uma vez. O `_` no início do nome sinaliza função **privada** do módulo (convenção, não imposição: Python confia no programador).

O retorno é sempre um `ParsedCommand` (dataclass) com um `TargetType` (Enum). Ou seja: o parser transforma texto bagunçado em **dados tipados** que o resto do sistema consome com segurança — um contrato claro entre módulos.

---

## 7. launcher.py — abrindo coisas em qualquer sistema

### As três bibliotecas-chave

- **webbrowser** — `webbrowser.open(url)` abre a URL no navegador padrão do usuário, seja ele qual for. É a maneira multiplataforma oficial.
- **subprocess** — `subprocess.Popen([...])` inicia um processo externo **sem bloquear** o programa (diferente de `subprocess.run`, que espera terminar). Redirecionar `stdout/stderr` para `DEVNULL` evita que o app aberto "suje" nosso terminal.
- **shutil.which(app)** — procura o executável no `PATH` (como o comando `which` do Linux). Permite falhar com mensagem amigável **antes** de tentar executar algo inexistente.

### Diferenças por SO

```python
case OperatingSystem.WINDOWS:
    os.startfile(str(path))
```
`os.startfile` só existe no Windows: abre o arquivo/pasta com o programa associado (equivale a dois cliques). Para aplicativos, usamos `start "" "app"` via shell, porque o `start` do Windows resolve apps registrados e URIs especiais como `shell:RecycleBinFolder` (a Lixeira).

```python
case OperatingSystem.MACOS:
    subprocess.Popen(["open", "-a", app])
```
No macOS, `open -a "Nome do App"` abre aplicativos de `/Applications` pelo nome amigável; `open caminho` abre pastas/arquivos no Finder.

```python
case OperatingSystem.LINUX:
    subprocess.Popen(["xdg-open", str(path)])
```
No Linux, `xdg-open` é o padrão freedesktop para abrir qualquer coisa com o aplicativo associado.

### Medição de tempo e registro

```python
start = time.perf_counter()
...
elapsed_ms = (time.perf_counter() - start) * 1000
```
`perf_counter` é o relógio de **maior resolução** disponível, feito exatamente para medir durações (não use `time.time()` para isso — pode retroceder com ajustes do relógio do sistema).

Ao final, `register_execution(...)` grava o resultado no JSON **sempre** — sucesso ou erro — para que histórico e estatísticas reflitam a realidade.

### Tratamento de erros
Cada função captura exceções **específicas** (`FileNotFoundError`, `PermissionError`, `OSError`, `webbrowser.Error`) e devolve um `LaunchResult(success, message)` em vez de deixar a exceção subir. O chamador decide o que fazer com o resultado — este é o padrão "erros como valores" combinado com exceções, muito usado em código robusto.

---

## 8. commands.py + history.py + utils.py — a camada de interface

```python
MENU_ACTIONS: dict[str, callable] = {
    "1": open_app,
    "2": open_folder,
    ...
}
```
Este dicionário implementa o padrão de projeto **Command** de forma pythônica: em vez de um `if/elif` gigante no menu, mapeamos a escolha do usuário diretamente para a **função** a executar. Repare: guardamos `open_app` (sem parênteses) — a **referência** à função, não o resultado dela. Funções em Python são objetos de primeira classe: podem ser guardadas em variáveis, passadas como argumento e chamadas depois com `MENU_ACTIONS[escolha]()`.

`_open_generic(prompt)` extrai o fluxo repetido (perguntar → interpretar → executar → mostrar) para uma única função — princípio **DRY** (Don't Repeat Yourself).

`history.py` só **apresenta** dados; quem calcula é `database.py`. Separar cálculo de exibição facilita testes automatizados e futuras interfaces (uma GUI reutilizaria `database.py` sem tocar em nada).

`utils.py` traz truques de formatação de string: `f"{quantidade:>3}x"` alinha à direita em 3 posições; `f"{comando:<30}"` alinha à esquerda em 30; `f"{ms:>8.2f}"` formata float com 2 casas — tudo com **f-strings**, a forma moderna e rápida de interpolar valores em texto.

---

## 9. main.py — o loop principal e a barreira final de erros

```python
while True:
    try:
        escolha = input(">>> ").strip()
    except (KeyboardInterrupt, EOFError):
        return 0
```
- `input()` bloqueia esperando o usuário; `.strip()` remove espaços das pontas.
- **KeyboardInterrupt** é lançada quando o usuário aperta Ctrl+C; **EOFError**, quando fecha a entrada (Ctrl+D/Ctrl+Z). Capturá-las permite despedir-se com elegância em vez de exibir um traceback assustador.

```python
except Exception as exc:
    print(f"\n[ERRO INESPERADO] {exc}\n")
    logger.exception("Erro inesperado no loop principal.")
```
Esta é a **barreira final**: qualquer erro não previsto é registrado com traceback completo no log e o programa **continua rodando**. Capturar `Exception` genérica é má prática no meio do código, mas é a prática correta exatamente aqui, na fronteira externa da aplicação.

```python
if __name__ == "__main__":
    sys.exit(main())
```
`main()` retorna um inteiro; `sys.exit(código)` o entrega ao sistema operacional (0 = sucesso). Isso torna o programa "bem-comportado" em scripts e pipelines.

---

## 10. Resumo dos conceitos cobertos

| Conceito | Onde aparece |
|---|---|
| Módulos e imports | todos os arquivos |
| pathlib (Path, mkdir, exists, replace) | config, json_manager, parser, launcher |
| Enum | config (OperatingSystem), parser (TargetType) |
| dataclasses (@dataclass, asdict) | database, parser, launcher |
| match/case | config, launcher |
| Type hints (typing) | todas as assinaturas |
| Dicionários, listas, tuplas | config, database, commands |
| List/generator comprehensions | database |
| lambda + sorted | database (estatísticas) |
| f-strings e formatação | utils, history |
| with (context manager) | json_manager |
| json (load/dump) | json_manager |
| shutil (copy2, which) | json_manager, launcher |
| subprocess (Popen, DEVNULL) | launcher |
| webbrowser | launcher |
| os (startfile, system) | launcher, utils |
| platform | config |
| logging (handler, formatter, exception) | logger |
| datetime | json_manager, database |
| time.perf_counter | launcher |
| Tratamento de exceções específicas e barreira final | json_manager, launcher, main |
| Escrita atômica de arquivo | json_manager |
| SOLID (SRP), DRY, padrão Command | arquitetura geral |
| Funções como objetos de primeira classe | commands (MENU_ACTIONS) |

---

## 11. Estrutura de commits sugerida (GitHub)

```bash
git init
git add .
git commit -m "feat: estrutura inicial do projeto Automação Universal v1.0"
git branch -M main
git remote add origin https://github.com/seu-usuario/AutomacaoUniversal.git
git push -u origin main
git tag -a v1.0.0 -m "Release v1.0.0 — launcher multiplataforma, JSON único, logs"
git push origin v1.0.0
```

**Descrição curta (GitHub):** Assistente de automação em Python: abre apps, pastas, arquivos e URLs por comandos de terminal, com histórico em JSON e logs. Zero dependências.

**Tags/keywords:** `python` `automation` `cli` `cross-platform` `subprocess` `pathlib` `json` `clean-code` `desktop` `terminal`
