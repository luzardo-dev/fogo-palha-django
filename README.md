# Fogo de Palha — projeto Django de referência

Projeto didático do Dia 18 da disciplina Desenvolvimento de Aplicações Web. Ele continua os exemplos dos Dias 16 e 17 e demonstra catálogo, upload de imagens e pedidos persistidos em SQLite.

## O que o projeto demonstra

- Python 3.12, Django 5.2 LTS e Pillow;
- aplicações `cardapio` e `pedidos`;
- modelo `Produto` com o contrato original `nome`, `preco_centavos`, `ativo` e imagem opcional;
- upload pelo Django Admin em `media/produtos/`, com fallback visual quando não há imagem;
- formulário público com CSRF para nome fictício do cliente e quantidades de vários produtos ativos;
- validação no servidor para pedido vazio, nome, quantidade entre 0 e 20 e produto inativo;
- preços relidos do banco: o navegador não informa o preço;
- criação atômica de `Pedido` e `ItemPedido`, com snapshot de nome e preço, total persistido e página de confirmação;
- consulta de pedidos e itens pelo Django Admin;
- funções legadas `formatar_preco` e `produtos_disponiveis` preservadas;
- testes automatizados e verificações no GitHub Actions.

Não há pagamento real, endereço, login de cliente nem integração com WhatsApp.

## Criar sua própria cópia

No GitHub, clique em **Use this template** e depois em **Create a new repository**. Escolha um nome para sua versão e faça o clone do novo repositório.

Também é possível clonar esta referência diretamente:

```bash
git clone https://github.com/luzardo-dev/fogo-palha-django.git
cd fogo-palha-django
```

Para alterar o projeto e enviar mudanças para seu próprio GitHub, prefira a opção **Use this template**.

## Instalação

### Linux ou macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abra:

- cardápio e compra didática: `http://127.0.0.1:8000/`;
- administração: `http://127.0.0.1:8000/admin/`.

A conta administrativa e os pedidos existem somente no banco SQLite local. Use apenas nomes e dados fictícios.

## Produtos e imagens

Cadastre produtos no Django Admin. A imagem é opcional; sem upload, o cardápio mostra um fallback seguro. Durante o desenvolvimento, os arquivos enviados ficam em `media/`, diretório ignorado pelo Git.

O servidor de desenvolvimento do Django entrega esses arquivos quando `DEBUG=True`. Em produção, um servidor de arquivos deve servir `MEDIA_ROOT` separadamente.

## Dados opcionais de demonstração

```bash
python manage.py loaddata produtos_exemplo
```

O produto inativo permanece no banco e no admin, mas não aparece no cardápio e não pode ser comprado.

## Fluxo de compra

```text
GET /
  → lista somente Produto ativo
  → formulário com CSRF, nome e quantidades

POST /pedidos/
  → valida os dados
  → relê produtos e preços no banco
  → transaction.atomic cria Pedido + ItemPedido
  → grava snapshots e total em centavos
  → redireciona para /pedidos/<token-uuid>/
```

A confirmação usa um token UUID não sequencial para não expor pedidos por enumeração. Ela não representa cobrança ou pagamento.

## Estrutura principal

```text
.
├── cardapio/
│   ├── migrations/
│   ├── static/cardapio/css/estilo.css
│   ├── templates/cardapio/index.html
│   ├── admin.py
│   ├── models.py
│   ├── regras.py
│   ├── tests.py
│   └── views.py
├── pedidos/
│   ├── migrations/
│   ├── templates/pedidos/confirmacao.html
│   ├── admin.py
│   ├── models.py
│   ├── servicos.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

## Testes e qualidade

Instale as dependências de desenvolvimento:

```bash
python -m pip install -r requirements-dev.txt
```

Execute:

```bash
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Os testes de upload usam um diretório temporário e uma imagem PNG válida pequena, sem gravar arquivos em `media/`.

## O que não deve ir para o GitHub

O `.gitignore` exclui `db.sqlite3`, ambientes virtuais, arquivos `.env`, caches, arquivos coletados e uploads em `media/`. Não publique senhas, superusuários, chaves, tokens, pedidos reais ou dados pessoais.

Este servidor é para desenvolvimento e aprendizagem local. Não use `python manage.py runserver` como servidor de produção.

## Licença

MIT. Você pode copiar, estudar e modificar o projeto.
