# Police Operation API

API RESTful para gerenciamento de operações policiais, construída com Python, Flask e SQLAlchemy.

---

## Sumário

- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e execução](#instalação-e-execução)
- [Configuração do banco de dados](#configuração-do-banco-de-dados)
- [Documentação Swagger](#documentação-swagger)
- [Endpoints](#endpoints)
- [Tipos de operação e regras de negócio](#tipos-de-operação-e-regras-de-negócio)
- [Constantes válidas](#constantes-válidas)
- [Payloads de exemplo](#payloads-de-exemplo)
- [Testes via Postman](#testes-via-postman)
- [Padrão de resposta](#padrão-de-resposta)
- [Tratamento de erros](#tratamento-de-erros)
- [Estrutura de arquivos](#estrutura-de-arquivos)

---

## Tecnologias

| Tecnologia | Versão |
|---|---|
| Python | 3.12+ |
| Flask | 3.0.3 |
| Flask-RESTful | 0.3.10 |
| Flask-SQLAlchemy | 3.1.1 |
| Flask-Migrate | 4.0.7 |
| SQLite | (embutido) |
| python-dotenv | 1.0.1 |
| ReportLab | 4.2.0 |
| Flasgger (Swagger) | 0.9.7.1 |

---

## Arquitetura

O projeto segue separação em camadas com responsabilidades bem definidas:

```
Controller  →  recebe request, devolve response, sem regra de negócio
Service     →  orquestra regras de negócio e validações
Repository  →  único ponto de acesso ao banco de dados
Validator   →  valida dados de entrada contra as regras de cada tipo de operação
Entity      →  modelos SQLAlchemy que mapeiam as tabelas
```

---

## Pré-requisitos

- Python 3.12 ou superior
- pip

---

## Instalação e execução

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd police-operation-api

# 2. Crie e ative um ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o arquivo .env (já está criado com os valores padrão)
# DATABASE_URL=sqlite:///police.db

# 5. Execute as migrações
flask db init
flask db migrate -m "initial migration"
flask db upgrade

# 6. Inicie o servidor
python run.py
```

A API estará disponível em: `http://localhost:5000`

---

## Configuração do banco de dados

### Comandos Flask-Migrate

```bash
# Inicializar pasta migrations (apenas na primeira vez)
flask db init

# Gerar arquivo de migração
flask db migrate -m "initial migration"

# Aplicar migrações ao banco
flask db upgrade

# Ver histórico de migrações
flask db history

# Reverter última migração
flask db downgrade
```

---

## Documentação Swagger

A documentação interativa da API está disponível em:

```
http://localhost:5000/apidocs
```

No Swagger UI você pode:
- Visualizar todos os endpoints organizados por tag (**Operations** e **Reports**)
- Testar os endpoints diretamente pelo navegador
- Ver os schemas de request e response
- Ver exemplos de payload para cada operação

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/operations` | Listar todas as operações |
| `POST` | `/operations` | Criar nova operação |
| `GET` | `/operations/<id>` | Buscar operação por ID |
| `PUT` | `/operations/<id>` | Atualizar operação |
| `DELETE` | `/operations/<id>` | Excluir operação |
| `GET` | `/operations/<id>/report` | Baixar relatório PDF |
| `GET` | `/apidocs` | Documentação Swagger UI |

---

## Tipos de operação e regras de negócio

### OSTENSIVE — Operações Ostensivas e Preservação da Ordem

| Requisito | Mínimo |
|-----------|--------|
| Viaturas | 1 |
| Armamentos |  1 |
| Cargos | 1 |

### INVESTIGATIVE — Operações de Polícia Judiciária e Investigativa

| Requisito | Regra |
|-----------|-------|
| Armamentos | Somente `pistola` (nenhum outro aceito) |
| Equipamentos investigativos | 1 |
| Cargos | 1  |

### TACTICAL — Operações de Forças Táticas e Especiais

| Requisito | Mínimo |
|-----------|--------|
| Viaturas | 2 |
| Armamentos | 5 |
| Cargos | 5 |

---

## Constantes válidas

### Armamentos válidos

```
pistola, fuzil, carabina, espingarda, submetralhadora,
rifle de precisão, revólver, metralhadora
```

### Cargos válidos

```
soldado, cabo, sargento, tenente, capitão, major,
tenente-coronel, coronel, delegado, investigador,
agente, inspetor, atirador de elite, comandante tático, especialista
```

### Equipamentos investigativos válidos

```
câmera, gravador, laptop, kit forense, rastreador GPS,
visão noturna, drone, rádio comunicador, binóculo,
kit de impressão digital, kit de vigilância
```

---

## Payloads de exemplo

### POST /operations — Operação Ostensiva

```json
{
  "name": "Operação Verão",
  "operation_type": "OSTENSIVE",
  "location": "Petrópolis - RJ",
  "description": "Policiamento ostensivo em evento público de grande porte.",
  "weapons": [
    "pistola",
    "carabina"
  ],
  "vehicles": [
    { "name": "Viatura 01", "armored": false },
    { "name": "Viatura 02", "armored": true }
  ],
  "roles": [
    "soldado",
    "sargento",
    "tenente"
  ],
  "investigation_equipments": []
}
```

### POST /operations — Operação Investigativa

```json
{
  "name": "Operação Sombra",
  "operation_type": "INVESTIGATIVE",
  "location": "Rio de Janeiro - RJ",
  "description": "Investigação de organização criminosa no tráfico de drogas.",
  "weapons": [
    "pistola"
  ],
  "vehicles": [],
  "roles": [
    "delegado",
    "investigador",
    "agente"
  ],
  "investigation_equipments": [
    "câmera",
    "gravador",
    "kit forense",
    "rastreador GPS"
  ]
}
```

### POST /operations — Operação Tática

```json
{
  "name": "Operação Trovão",
  "operation_type": "TACTICAL",
  "location": "Complexo do Alemão - RJ",
  "description": "Operação de alto risco para desarticulação de grupo armado.",
  "weapons": [
    "pistola",
    "fuzil",
    "submetralhadora",
    "rifle de precisão",
    "espingarda"
  ],
  "vehicles": [
    { "name": "Blindado Alpha", "armored": true },
    { "name": "Blindado Bravo", "armored": true },
    { "name": "Viatura de Apoio", "armored": false }
  ],
  "roles": [
    "comandante tático",
    "atirador de elite",
    "especialista",
    "soldado",
    "sargento",
    "tenente"
  ],
  "investigation_equipments": [
    "drone",
    "visão noturna"
  ]
}
```

### PUT /operations/1 — Atualizar operação

Mesmo payload do POST. Todos os campos são obrigatórios na atualização.

---

## Testes via Postman

### 1. Importar a coleção

Crie uma nova coleção no Postman com as requests abaixo.

### 2. Variáveis de ambiente sugeridas

| Variável | Valor |
|----------|-------|
| `base_url` | `http://localhost:5000` |

### Listar operações

```
GET {{base_url}}/operations
```

### Criar operação ostensiva

```
POST {{base_url}}/operations
Content-Type: application/json

{
  "name": "Operação Verão",
  "operation_type": "OSTENSIVE",
  "location": "Petrópolis",
  "description": "Policiamento ostensivo.",
  "weapons": ["pistola"],
  "vehicles": [{"name": "Viatura 01", "armored": false}],
  "roles": ["soldado"],
  "investigation_equipments": []
}
```

### Buscar operação por ID

```
GET {{base_url}}/operations/1
```

### Atualizar operação

```
PUT {{base_url}}/operations/1
Content-Type: application/json

{
  "name": "Operação Verão Atualizada",
  "operation_type": "OSTENSIVE",
  "location": "Teresópolis",
  "description": "Descrição atualizada.",
  "weapons": ["pistola", "carabina"],
  "vehicles": [{"name": "Viatura 01", "armored": true}],
  "roles": ["soldado", "sargento"],
  "investigation_equipments": []
}
```

### Excluir operação

```
DELETE {{base_url}}/operations/1
```

### Baixar relatório PDF

```
GET {{base_url}}/operations/1/report
```

> No Postman, clique em **Send and Download** para salvar o arquivo PDF.

### Testar validação — operação tática sem armamentos suficientes

```
POST {{base_url}}/operations
Content-Type: application/json

{
  "name": "Op. Inválida",
  "operation_type": "TACTICAL",
  "location": "São Paulo",
  "weapons": ["pistola"],
  "vehicles": [{"name": "V1", "armored": false}, {"name": "V2", "armored": false}],
  "roles": ["soldado", "cabo", "sargento", "tenente", "capitão"]
}
```

Resposta esperada (`400`):
```json
{
  "success": false,
  "error": "Uma operação de forças táticas e especiais deve possuir ao menos 5 armamentos."
}
```

### Testar validação — operação investigativa com arma proibida

```
POST {{base_url}}/operations
Content-Type: application/json

{
  "name": "Op. Investigativa Inválida",
  "operation_type": "INVESTIGATIVE",
  "location": "Brasília",
  "weapons": ["pistola", "fuzil"],
  "vehicles": [],
  "roles": ["delegado"],
  "investigation_equipments": ["câmera"]
}
```

Resposta esperada (`400`):
```json
{
  "success": false,
  "error": "Operações investigativas permitem somente o armamento 'pistola'. Armamento inválido: 'fuzil'."
}
```

---

## Padrão de resposta

### Sucesso

```json
{
  "success": true,
  "message": "Operation created successfully",
  "data": {
    "id": 1,
    "name": "Operação Verão",
    "operation_type": "OSTENSIVE",
    "location": "Petrópolis",
    "description": "Policiamento ostensivo.",
    "created_at": "2024-01-15T10:00:00",
    "weapons": [{"id": 1, "name": "pistola", "operation_id": 1}],
    "vehicles": [{"id": 1, "name": "Viatura 01", "armored": false, "operation_id": 1}],
    "roles": [{"id": 1, "name": "soldado", "operation_id": 1}],
    "investigation_equipments": []
  }
}
```

### Erro

```json
{
  "success": false,
  "error": "Mensagem de erro clara e amigável."
}
```

---

## Tratamento de erros

| Código HTTP | Situação |
|-------------|----------|
| `200` | Sucesso |
| `201` | Criação bem-sucedida |
| `400` | Erro de validação (regra de negócio violada, campo inválido) |
| `404` | Recurso não encontrado |
| `405` | Método HTTP não permitido |
| `500` | Erro interno do servidor / banco de dados |

---

## Estrutura de arquivos

```
police-operation-api/
│
├── app/
│   ├── controllers/
│   │   └── operation_controller.py   # Request/Response/Status codes
│   │
│   ├── services/
│   │   └── operation_service.py      # Regras de negócio e orquestração
│   │
│   ├── repositories/
│   │   └── operation_repository.py   # Acesso ao banco de dados
│   │
│   ├── entities/
│   │   ├── operation.py
│   │   ├── weapon.py
│   │   ├── vehicle.py
│   │   ├── role.py
│   │   └── investigation_equipment.py
│   │
│   ├── routes/
│   │   └── operation_routes.py       # Registro de rotas e Blueprint
│   │
│   ├── validators/
│   │   └── operation_validator.py    # Validações de regras de negócio
│   │
│   ├── utils/
│   │   ├── pdf_generator.py          # Geração de PDF com ReportLab
│   │   └── response.py               # Helpers de resposta padronizada
│   │
│   ├── database/
│   │   └── connection.py             # Inicialização de db e migrate
│   │
│   ├── constants/
│   │   ├── operation_types.py
│   │   ├── weapons.py
│   │   ├── roles.py
│   │   └── equipments.py
│   │
│   └── __init__.py                   # Factory da aplicação Flask
│
├── migrations/                       # Gerado pelo Flask-Migrate
├── .env
├── config.py
├── run.py
├── requirements.txt
└── README.md
```
