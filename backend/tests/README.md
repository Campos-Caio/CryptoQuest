<<<<<<< HEAD
# Testes do Backend - CryptoQuest

## Estrutura Organizada
=======
# 🧪 Testes do Backend - CryptoQuest

## 📁 Estrutura Organizada
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)

```
tests/
├── unit/                    # Testes unitários
│   ├── test_event_bus.py
│   ├── test_badge_repository.py
│   ├── test_badge_system_legacy.py
│   ├── test_mission_service.py
<<<<<<< HEAD
│   ├── test_questionnaire_service.py
│   ├── test_ranking_repository.py
│   ├── test_ranking_service.py
│   ├── test_reward_service.py
│   ├── test_level_system.py
│   ├── test_learning_path_integration.py
│   └── test_questionnaire_integration.py
├── integration/             # Testes de integração
│   ├── test_badge_system_integration.py
│   ├── test_full_integration.py
│   ├── test_badge_system_manual.py
│   ├── test_frontend_backend_integration.py
│   └── test_unified_system_integration.py
=======
│   └── test_questionnaire_service.py
├── integration/             # Testes de integração
│   ├── test_badge_system_integration.py
│   ├── test_full_integration.py
│   └── test_badge_system_manual.py
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
├── api/                     # Testes de API
│   ├── test_rewards_api.py
│   ├── test_auth_api.py
│   ├── test_questionnaire_api.py
<<<<<<< HEAD
│   ├── test_user_api.py
│   └── test_ranking_api.py
=======
│   └── test_user_api.py
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
├── fixtures/                # Fixtures compartilhadas
│   └── conftest.py
├── utils/                   # Utilitários de teste
│   └── test_helpers.py
└── README.md               # Este arquivo
```

<<<<<<< HEAD
## Como Executar Testes

### Opção 1: Script Automatizado (Recomendado)
=======
## 🚀 Como Executar Testes

### **Opção 1: Script Automatizado (Recomendado)**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```bash
# Todos os testes
python run_tests.py

# Apenas testes unitários
python run_tests.py --type unit

# Apenas testes de integração
python run_tests.py --type integration

# Apenas testes de API
python run_tests.py --type api

# Com cobertura de código
python run_tests.py --coverage

# Incluindo testes que requerem Firebase
python run_tests.py --firebase
```

<<<<<<< HEAD
### Opção 2: Pytest Direto
=======
### **Opção 2: Pytest Direto**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```bash
# Todos os testes
pytest

# Testes unitários
pytest tests/unit/ -m unit

# Testes de integração
pytest tests/integration/ -m integration

# Testes de API
pytest tests/api/ -m api

# Com verbosidade
pytest -v

# Com cobertura
pytest --cov=app --cov-report=html
```

<<<<<<< HEAD
### Opção 3: Testes Específicos
=======
### **Opção 3: Testes Específicos**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```bash
# Arquivo específico
pytest tests/unit/test_event_bus.py

# Classe específica
pytest tests/unit/test_event_bus.py::TestEventBus

# Método específico
pytest tests/unit/test_event_bus.py::TestEventBus::test_emit_event
```

<<<<<<< HEAD
## Marcadores de Teste
=======
## 🏷️ Marcadores de Teste
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)

- `@pytest.mark.unit` - Testes unitários
- `@pytest.mark.integration` - Testes de integração
- `@pytest.mark.api` - Testes de API
- `@pytest.mark.slow` - Testes que demoram para executar
- `@pytest.mark.firebase` - Testes que requerem Firebase
<<<<<<< HEAD
- `@pytest.mark.ranking` - Testes do sistema de ranking
- `@pytest.mark.rewards` - Testes do sistema de recompensas
- `@pytest.mark.badges` - Testes do sistema de badges
- `@pytest.mark.levels` - Testes do sistema de níveis
- `@pytest.mark.learning_paths` - Testes de trilhas de aprendizado
- `@pytest.mark.questionnaire` - Testes do questionário inicial

## Configuração

### pytest.ini
```ini
[tool:pytest]
=======

## 🔧 Configuração

### **pytest.ini**
```ini
[pytest]
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
pythonpath = .
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
markers =
    unit: Testes unitários
    integration: Testes de integração
    api: Testes de API
    slow: Testes que demoram para executar
    firebase: Testes que requerem conexão com Firebase
<<<<<<< HEAD
    ranking: Testes do sistema de ranking
    rewards: Testes do sistema de recompensas
    badges: Testes do sistema de badges
    levels: Testes do sistema de níveis
    learning_paths: Testes de trilhas de aprendizado
    questionnaire: Testes do questionário inicial
```

## Tipos de Teste

### 1. Testes Unitários (`tests/unit/`)
- **Objetivo**: Testar componentes isoladamente
- **Mock**: Usar mocks para dependências externas
- **Velocidade**: Rápidos (< 1s cada)
- **Exemplos**: EventBus, BadgeRepository, ValidationService, RankingService, RewardService, LevelService

### 2. Testes de Integração (`tests/integration/`)
- **Objetivo**: Testar interação entre componentes
- **Dados**: Usar dados reais ou mocks controlados
- **Velocidade**: Médios (1-10s cada)
- **Exemplos**: Fluxo completo de badges, sistema de eventos, sistema unificado

### 3. Testes de API (`tests/api/`)
- **Objetivo**: Testar endpoints HTTP
- **Cliente**: Usar TestClient do FastAPI
- **Velocidade**: Rápidos (< 1s cada)
- **Exemplos**: Endpoints de recompensas, autenticação, ranking

## Novos Testes Implementados

### Sistema de Ranking
- `test_ranking_repository.py` - Testes do repositório de ranking
- `test_ranking_service.py` - Testes do serviço de ranking
- `test_ranking_api.py` - Testes dos endpoints de ranking

### Sistema de Recompensas
- `test_reward_service.py` - Testes do serviço de recompensas
- Integração com sistema de badges e níveis

### Sistema de Níveis
- `test_level_system.py` - Testes do sistema de níveis unificado
- Cálculo de XP, level up, progresso

### Integração de Learning Paths
- `test_learning_path_integration.py` - Testes de integração com recompensas
- `test_questionnaire_integration.py` - Testes do questionário inicial
- `test_unified_system_integration.py` - Testes do sistema unificado

## Utilitários Disponíveis

### TestDataManager
=======
```

## 📊 Tipos de Teste

### **1. Testes Unitários (`tests/unit/`)**
- **Objetivo**: Testar componentes isoladamente
- **Mock**: Usar mocks para dependências externas
- **Velocidade**: Rápidos (< 1s cada)
- **Exemplos**: EventBus, BadgeRepository, ValidationService

### **2. Testes de Integração (`tests/integration/`)**
- **Objetivo**: Testar interação entre componentes
- **Dados**: Usar dados reais ou mocks controlados
- **Velocidade**: Médios (1-10s cada)
- **Exemplos**: Fluxo completo de badges, sistema de eventos

### **3. Testes de API (`tests/api/`)**
- **Objetivo**: Testar endpoints HTTP
- **Cliente**: Usar TestClient do FastAPI
- **Velocidade**: Rápidos (< 1s cada)
- **Exemplos**: Endpoints de recompensas, autenticação

## 🛠️ Utilitários Disponíveis

### **TestDataManager**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```python
# Gerenciar dados de teste
test_data_manager = TestDataManager()
user = await test_data_manager.create_test_user("user123")
await test_data_manager.cleanup_all(db)
```

<<<<<<< HEAD
### EventTestHelper
=======
### **EventTestHelper**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```python
# Criar eventos de teste
event_helper = EventTestHelper()
mission_event = event_helper.create_mission_event("user123")
level_event = event_helper.create_level_up_event("user123")
```

<<<<<<< HEAD
### MockHelper
=======
### **MockHelper**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```python
# Criar mocks
mock_helper = MockHelper()
mock_db = mock_helper.create_firestore_mock()
mock_repo = mock_helper.create_badge_repo_mock()
```

<<<<<<< HEAD
## Cobertura de Código

### Gerar Relatório
=======
## 📈 Cobertura de Código

### **Gerar Relatório**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

<<<<<<< HEAD
### Visualizar Relatório
=======
### **Visualizar Relatório**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```bash
# Abrir relatório HTML
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

<<<<<<< HEAD
## Debugging

### Executar com Debug
=======
## 🐛 Debugging

### **Executar com Debug**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```bash
pytest -v -s --tb=long
```

<<<<<<< HEAD
### Parar no Primeiro Erro
=======
### **Parar no Primeiro Erro**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```bash
pytest -x
```

<<<<<<< HEAD
### Executar Apenas Falhas
=======
### **Executar Apenas Falhas**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```bash
pytest --lf
```

<<<<<<< HEAD
## Boas Práticas

### 1. Nomenclatura
=======
## 📝 Boas Práticas

### **1. Nomenclatura**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
- Arquivos: `test_*.py`
- Classes: `Test*`
- Métodos: `test_*`

<<<<<<< HEAD
### 2. Organização
=======
### **2. Organização**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
- Um arquivo por módulo testado
- Fixtures compartilhadas em `conftest.py`
- Utilitários em `utils/`

<<<<<<< HEAD
### 3. Isolamento
=======
### **3. Isolamento**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
- Cada teste deve ser independente
- Limpar dados após cada teste
- Usar mocks para dependências externas

<<<<<<< HEAD
### 4. Documentação
=======
### **4. Documentação**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
- Docstrings descritivas
- Comentários em testes complexos
- README atualizado

<<<<<<< HEAD
## CI/CD

### GitHub Actions (Exemplo)
=======
## 🔄 CI/CD

### **GitHub Actions (Exemplo)**
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py --coverage
```

<<<<<<< HEAD
## Próximos Passos
=======
## 🎯 Próximos Passos
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)

1. **Adicionar mais testes unitários** para componentes restantes
2. **Implementar testes de performance** para operações críticas
3. **Configurar CI/CD** com GitHub Actions
4. **Adicionar testes de carga** para APIs
5. **Implementar testes de segurança** para endpoints sensíveis

---

<<<<<<< HEAD
**Dica**: Execute `python run_tests.py --help` para ver todas as opções disponíveis!
=======
**💡 Dica**: Execute `python run_tests.py --help` para ver todas as opções disponíveis!
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
