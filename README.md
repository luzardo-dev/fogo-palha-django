# Fogo de Palha — projeto Django de referência

Projeto didático do Dia 18 da disciplina Desenvolvimento de Aplicações Web. Ele continua os exemplos dos Dias 16 e 17 e mostra como guardar produtos no SQLite usando o ORM e a administração do Django.

## O que o projeto demonstra

- Python 3.12 e Django 5.2 LTS;
- projeto Django `config` e aplicação `cardapio`;
- modelo `Produto` com `nome`, `preco_centavos` e `ativo`;
- migrations e banco SQLite local;
- cadastro de produtos pelo Django Admin;
- consulta ao banco com `Produto.objects.filter(ativo=True)`;
- template que mostra somente produtos ativos;
- funções `formatar_preco` e `produtos_disponiveis`, preservadas dos dias anteriores;
- testes automatizados e verificação de código no GitHub Actions.

## Criar sua própria cópia

No GitHub, clique em **Use this template** e depois em **Create a new repository**. Escolha um nome para sua versão e faça o clone do novo repositório.

Também é possível clonar esta referência diretamente:

```bash
git clone https://github.com/luzardo-dev/fogo-palha-django.git
cd fogo-palha-django
```

Para alterar o projeto e enviar mudanças para seu próprio GitHub, prefira a opção **Use this template**.

## Instalação no Linux ou macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Instalação no Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abra:

- catálogo: `http://127.0.0.1:8000/`;
- administração: `http://127.0.0.1:8000/admin/`.

A conta criada por `createsuperuser` existe somente no banco SQLite local. Ela não é uma conta Firebase e não deve ser enviada ao GitHub.

## Dados opcionais de demonstração

Depois de executar as migrations, você pode carregar três registros de exemplo:

```bash
python manage.py loaddata produtos_exemplo
```

O produto inativo é guardado no banco e aparece no admin, mas não aparece no catálogo público.

## Fluxo principal

```text
requisição
    ↓
config/urls.py
    ↓
cardapio/urls.py
    ↓
cardapio/views.py
    ↓
Produto.objects.filter(ativo=True)
    ↓
contexto {"produtos": produtos}
    ↓
cardapio/templates/cardapio/index.html
    ↓
resposta HTML
```

## Estrutura importante

```text
.
├── cardapio/
│   ├── fixtures/produtos_exemplo.json
│   ├── migrations/0001_initial.py
│   ├── static/cardapio/css/estilo.css
│   ├── templates/cardapio/index.html
│   ├── admin.py
│   ├── models.py
│   ├── regras.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

## Alterações sugeridas para sua versão

1. Troque o nome e as cores do estabelecimento.
2. Cadastre seus próprios produtos no admin.
3. Altere o ícone e a organização dos cartões.
4. Acrescente um novo campo ao modelo, como `descricao`.
5. Crie e aplique uma nova migration após mudar o modelo:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Testes e qualidade

Instale as dependências de desenvolvimento:

```bash
python -m pip install -r requirements-dev.txt
```

Execute as verificações:

```bash
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## O que não deve ir para o GitHub

O arquivo `.gitignore` exclui o banco `db.sqlite3`, o ambiente `.venv`, arquivos `.env` e caches. Não publique senhas, superusuários, chaves, tokens ou dados pessoais.

Este servidor é para desenvolvimento e aprendizagem local. Não use `python manage.py runserver` como servidor de produção.

## Licença

MIT. Você pode copiar, estudar e modificar o projeto.
