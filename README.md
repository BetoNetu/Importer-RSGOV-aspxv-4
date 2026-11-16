# 🕸️ <Nome do Projeto>

Scripts em Python para coleta e extração de dados de um portal web legado (mal estruturado), com o objetivo de automatizar a obtenção de informações que seriam trabalhosas de coletar manualmente.

> ⚠️ **Aviso:** Este projeto é destinado a uso pessoal/educacional. Respeite os termos de uso do site, `robots.txt` e limites de requisições. Não faça scraping agressivo.

---

## 📋 Sobre o projeto

O portal alvo é **muito mal estruturado** (HTML inconsistente, sem API pública, seletores frágeis, etc.), o que torna a coleta manual um processo lento e sujeito a erros. Este projeto encapsula a lógica de scraping em scripts simples e reutilizáveis.

Atualmente o projeto conta com:

- Uma função **`main()`** — ponto de entrada do script, responsável por orquestrar o fluxo de execução.
- Uma função **extratora** — responsável por fazer a requisição, parsear o conteúdo e **salvar os dados coletados**.

---

## 📁 Estrutura atual

    <nome-do-projeto>/
    ├── src                      # Contém main() e a função extratora
    ├── <pasta_de_saida>/        # Onde os dados extraídos são salvos
    └── README.md

---

## ⚙️ Como funciona

### `main()`

Ponto de entrada do script. É responsável por:

1. Definir os parâmetros da coleta (URLs, filtros, período, etc.).
2. Chamar a função extratora.
3. Tratar erros e exibir logs no terminal.

Exemplo de uso:

    python <arquivo_principal>.py

### Função extratora (`<nome_da_funcao>`)

Responsável por:

1. Fazer a requisição HTTP ao portal.
2. Parsear o HTML (geralmente com `BeautifulSoup` ou `lxml`).
3. Extrair os campos de interesse.
4. **Salvar os dados** no formato definido (`.csv`, `.json`, `.xlsx`, etc.) na pasta de saída.

Assinatura aproximada:

    def <nome_da_funcao>(<parametros>):
        ...
        return <dados_extraidos>

---

## 🛠️ Requisitos

- Python 3.8+
- Bibliotecas utilizadas:
  - `requests`
  - `beautifulsoup4`
  - `lxml`
  - <adicione outras conforme o caso>

Instalação:

    pip install -r requirements.txt

---

## ▶️ Uso

    # Clone o repositório
    git clone <url-do-repo>
    cd <nome-do-projeto>

    # (Opcional) Crie um ambiente virtual
    python -m venv venv
    source venv/bin/activate    # Linux/macOS
    venv\Scripts\activate       # Windows

    # Instale as dependências
    pip install -r requirements.txt

    # Execute
    python <arquivo_principal>.py

Os dados extraídos serão salvos em `<pasta_de_saida>/<nome_do_arquivo>`.

---

## 🗺️ Roadmap (ideias futuras)

- [ ] Adicionar logging estruturado
- [ ] Suporte a múltiplas páginas / paginação
- [ ] Retry automático em caso de falha de requisição
- [ ] Exportação em múltiplos formatos (CSV, JSON, SQLite)
- [ ] Testes unitários para a função extratora
- [ ] CLI com argumentos (`argparse` / `click`)

---

## 📌 Observações

- O HTML do portal pode mudar sem aviso — seletores podem quebrar e precisar de ajustes.
- Recomenda-se rodar com delays entre requisições para não sobrecarregar o servidor.