<div align="center">

# 🚀 Automação Universal

**Assistente de automação em Python: abra qualquer aplicativo, pasta, arquivo ou URL com um comando digitado no terminal.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS-informational)
![Dependências](https://img.shields.io/badge/Depend%C3%AAncias-Zero-brightgreen)
![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow)
![Versão](https://img.shields.io/badge/Vers%C3%A3o-1.0.0-blue)
![Status](https://img.shields.io/badge/Status-Est%C3%A1vel-success)

*100% biblioteca padrão · Arquitetura modular · Banco JSON único · Logs automáticos*

</div>

---

## 📋 Descrição

**Automação Universal** é um mini-assistente de linha de comando. O usuário digita comandos naturais como `abrir chrome`, `abrir downloads` ou `abrir https://github.com`, e o sistema:

1. 🧠 **Interpreta** o comando (parser) e descobre se o alvo é um aplicativo, pasta, arquivo ou URL;
2. 🖥️ **Detecta** o sistema operacional (Windows, Linux ou macOS) e usa o mecanismo nativo correto;
3. ⚡ **Executa** a abertura, medindo o tempo em milissegundos;
4. 🗃️ **Registra** tudo em um **único** arquivo `data/database.json` (histórico, contadores, último acesso) e em `logs/app.log`.

## ✨ Funcionalidades

| # | Funcionalidade | Descrição |
|---|----------------|-----------|
| 1 | 📱 Abrir aplicativos | Chrome, VSCode, Spotify, Discord, Word, Excel, Terminal e dezenas de outros |
| 2 | 📁 Abrir pastas | Downloads, Desktop, Documentos, Imagens ou qualquer caminho do disco |
| 3 | 📄 Abrir arquivos | Qualquer arquivo, pelo caminho relativo ou absoluto |
| 4 | 🌐 Abrir URLs | Sites conhecidos (google, youtube, claude, github) ou qualquer link |
| 5 | 🕘 Histórico | Todos os comandos com data, hora, status e tempo de execução |
| 6 | 📊 Estatísticas | Totais, sucessos, erros, comandos mais usados e último acesso |
| 7 | 🔍 Pesquisa | Busca por termo em todo o histórico |
| 8 | 🧹 Terminal | Menu interativo, limpeza de tela e ajuda embutida |
| 9 | 🛡️ Robustez | Tratamento de JSON corrompido, permissões, Ctrl+C e erros inesperados |

## 🎬 Demonstração

```text
==============================================
          AUTOMAÇÃO UNIVERSAL  v1.0.0
              Sistema: Windows
==============================================
 1 - Abrir aplicativo
 2 - Abrir pasta
 3 - Abrir arquivo
 4 - Abrir URL
 5 - Histórico
 6 - Estatísticas
 7 - Pesquisar comando
 8 - Limpar tela
 9 - Ajuda
 0 - Sair
==============================================
Dica: você também pode digitar direto, ex.: abrir chrome

>>> abrir youtube

[OK] URL aberta no navegador: https://www.youtube.com
```

> 💡 Sugestão para o GitHub: grave um GIF do terminal com [asciinema](https://asciinema.org/) ou [terminalizer](https://github.com/faressoft/terminalizer) e insira aqui.

## 🏗️ Arquitetura

Fluxo de execução (entrada → interpretação → execução → persistência):

```text
┌──────────┐   ┌───────────┐   ┌────────────┐   ┌─────────────┐
│ main.py  │ → │ parser.py │ → │ launcher.py│ → │ database.py │
│  (menu)  │   │ (intenção)│   │ (abre alvo)│   │ (histórico) │
└──────────┘   └───────────┘   └────────────┘   └──────┬──────┘
                                                       │
                                             ┌─────────▼─────────┐
                                             │ json_manager.py   │
                                             │ (database.json)   │
                                             └───────────────────┘
```

Cada módulo tem **uma** responsabilidade (princípio S do SOLID):

```text
AutomacaoUniversal/
│
├── main.py           # Ponto de entrada + loop do menu
├── commands.py       # Ações do menu (padrão Command via dicionário)
├── parser.py         # Interpreta o texto do usuário → ParsedCommand
├── launcher.py       # Abre app/pasta/arquivo/URL conforme o SO
├── database.py       # Regras de negócio: histórico, contadores, stats
├── json_manager.py   # Leitura/gravação atômica e segura do JSON único
├── history.py        # Exibição de histórico e estatísticas
├── config.py         # Constantes, caminhos, mapeamentos de apps por SO
├── logger.py         # Configuração central de logs
├── utils.py          # Utilitários de terminal
│
├── data/             # database.json (criado automaticamente)
├── logs/             # app.log (criado automaticamente)
├── assets/           # Recursos (ícones, GIFs de demonstração)
│
├── requirements.txt
├── LICENSE
├── .gitignore
└── README.md
```

## 🗃️ O banco de dados JSON

Um **único** arquivo `data/database.json`, criado e atualizado automaticamente, nunca apagando registros anteriores:

```json
{
  "meta": {
    "criado_em": "2026-07-07 10:00:00",
    "ultima_atualizacao": "2026-07-07 10:05:12",
    "versao_esquema": "1.0"
  },
  "historico": [
    {
      "comando": "abrir chrome",
      "tipo": "app",
      "alvo": "chrome",
      "status": "sucesso",
      "resultado": "Aplicativo iniciado: chrome",
      "data": "2026-07-07",
      "hora": "10:05:12",
      "tempo_execucao_ms": 34.51
    }
  ],
  "contadores": { "abrir chrome": 1 },
  "ultimo_acesso": { "abrir chrome": "2026-07-07 10:05:12" }
}
```

🔒 A gravação é **atômica** (arquivo temporário + `replace`): se o programa cair no meio da escrita, o JSON não corrompe. Se um JSON corrompido for detectado na leitura, é feito **backup** (`.corrompido.bak`) e o banco é recriado.

## 🧰 Tecnologias

Apenas a **biblioteca padrão** do Python 3.10+:

`os` · `subprocess` · `webbrowser` · `pathlib` · `shutil` · `json` · `logging` · `datetime` · `platform` · `typing` · `enum` · `dataclasses` · `match/case`

## ⚙️ Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/AutomacaoUniversal.git
cd AutomacaoUniversal

# 2. (Opcional) Crie um ambiente virtual
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate

# 3. Execute — não há dependências para instalar!
python main.py
```

## 🕹️ Exemplos de uso

```text
abrir chrome
abrir google
abrir youtube
abrir claude
abrir vscode
abrir spotify
abrir calculadora
abrir bloco de notas
abrir downloads
abrir desktop
abrir pasta documentos
abrir github
abrir https://openai.com
abrir C:/Users/voce/Documents/contrato.pdf
abrir /home/voce/projetos
```

## 🗺️ Roadmap

- [x] v1.0 — Menu interativo, launcher multiplataforma, JSON único, logs
- [ ] v1.1 — Aliases personalizados definidos pelo usuário
- [ ] v1.2 — Modo argumento (`python main.py abrir chrome`) para atalhos do SO
- [ ] v1.3 — Autocompletar comandos no terminal
- [ ] v2.0 — Interface gráfica (Tkinter) e comando de voz

## 🤝 Contribuição

1. Faça um *fork* do projeto
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m "feat: minha feature"`
4. Push: `git push origin feature/minha-feature`
5. Abra um *Pull Request*

## 👤 Autor

**Danilo Barbosa Marques**

[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github)](https://github.com/seu-usuario)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://linkedin.com/in/seu-perfil)
[![Portfólio](https://img.shields.io/badge/Portf%C3%B3lio-FF5722?logo=firefox&logoColor=white)](https://seu-site.com)

## 📄 Licença

Distribuído sob a licença **MIT**. Veja [LICENSE](LICENSE) para detalhes.

---

<div align="center">⭐ Se este projeto te ajudou, deixe uma estrela no repositório!</div>
