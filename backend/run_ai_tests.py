#!/usr/bin/env python3
"""
Script para executar testes específicos do sistema de IA.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_ai_tests(test_type=None, coverage=False, verbose=False, firebase=False):
    """Executa testes de IA"""
    
    # Comando base
    cmd = ["python", "-m", "pytest"]
    
    # Adicionar marcadores de IA
    if test_type == "unit":
        cmd.extend(["-m", "unit and ai"])
        test_path = "tests/unit/test_ai_system_complete.py"
    elif test_type == "integration":
        cmd.extend(["-m", "integration and ai"])
        test_path = "tests/integration/test_ai_integration.py"
    elif test_type == "api":
        cmd.extend(["-m", "api and ai"])
        test_path = "tests/api/test_ai_api.py"
    else:
        # Todos os testes de IA
        cmd.extend(["-m", "ai"])
        test_path = "tests/"
    
    # Adicionar caminho específico
    cmd.append(test_path)
    
    # Opções adicionais
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app.ai", "--cov-report=html", "--cov-report=term"])
    
    if firebase:
        cmd.extend(["-m", "ai and firebase"])
    else:
        cmd.extend(["-m", "ai and not firebase"])
    
    # Executar testes
    print(f"🧠 Executando testes de IA: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
        return 1
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return 1


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar testes do sistema de IA")
    
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "api", "all"],
        default="all",
        help="Tipo de teste a executar"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Executar com cobertura de código"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Modo verboso"
    )
    
    parser.add_argument(
        "--firebase",
        action="store_true",
        help="Incluir testes que requerem Firebase"
    )
    
    parser.add_argument(
        "--help-tests",
        action="store_true",
        help="Mostrar ajuda sobre os testes de IA"
    )
    
    args = parser.parse_args()
    
    if args.help_tests:
        print_help()
        return 0
    
    # Executar testes
    exit_code = run_ai_tests(
        test_type=args.type,
        coverage=args.coverage,
        verbose=args.verbose,
        firebase=args.firebase
    )
    
    return exit_code


def print_help():
    """Mostra ajuda sobre os testes de IA"""
    print("""
🧠 TESTES DO SISTEMA DE IA - CryptoQuest
========================================

📋 TIPOS DE TESTE DISPONÍVEIS:

1. 🧪 Testes Unitários (--type unit)
   - Testa componentes individuais de IA
   - Mocks para dependências externas
   - Rápidos (< 1s cada)
   - Arquivo: tests/unit/test_ai_system_complete.py

2. 🔗 Testes de Integração (--type integration)
   - Testa interação entre componentes de IA
   - Fluxo completo de dados
   - Médios (1-5s cada)
   - Arquivo: tests/integration/test_ai_integration.py

3. 🌐 Testes de API (--type api)
   - Testa endpoints HTTP de IA
   - Validação de respostas
   - Rápidos (< 1s cada)
   - Arquivo: tests/api/test_ai_api.py

4. 🎯 Todos os Testes (--type all)
   - Executa todos os testes de IA
   - Cobertura completa do sistema

📊 COMPONENTES TESTADOS:

✅ Configurações de IA (ai_config)
✅ Modelos de dados (EnhancedQuizSubmission, LearningPattern, etc.)
✅ Coletor de dados comportamentais (BehavioralDataCollector)
✅ Engine de ML (MLEngine, LearningStyleClassifier, DifficultyPredictor)
✅ Engine de recomendações (BasicRecommendationEngine)
✅ Integração com LearningPathService
✅ APIs de IA (/ai/profile, /ai/recommendations, etc.)
✅ Persistência no Firestore
✅ Cache e performance
✅ Tratamento de erros

🚀 EXEMPLOS DE USO:

# Todos os testes de IA
python run_ai_tests.py

# Apenas testes unitários
python run_ai_tests.py --type unit

# Testes com cobertura
python run_ai_tests.py --coverage

# Testes verbosos
python run_ai_tests.py --verbose

# Incluir testes que requerem Firebase
python run_ai_tests.py --firebase

# Combinação de opções
python run_ai_tests.py --type integration --coverage --verbose

📈 MÉTRICAS ESPERADAS:

- Cobertura de código: > 90%
- Tempo de execução: < 30s (todos os testes)
- Taxa de sucesso: 100%
- Testes assíncronos: Suportados

🔧 DEPENDÊNCIAS:

- pytest
- pytest-asyncio
- pytest-cov (para cobertura)
- scikit-learn, pandas, numpy (para ML completo)

💡 DICAS:

1. Execute testes unitários primeiro para verificar componentes básicos
2. Use --coverage para verificar cobertura de código
3. Use --firebase apenas se tiver acesso ao Firebase
4. Testes de integração podem ser mais lentos
5. Verifique logs para debugging de falhas

📝 ESTRUTURA DOS TESTES:

tests/
├── unit/
│   └── test_ai_system_complete.py    # Testes unitários completos
├── integration/
│   └── test_ai_integration.py        # Testes de integração
├── api/
│   └── test_ai_api.py               # Testes de API
└── fixtures/
    └── ai_fixtures.py               # Fixtures específicas de IA

🎯 OBJETIVOS DOS TESTES:

- Validar funcionamento correto da IA
- Garantir integração com sistemas existentes
- Verificar performance e escalabilidade
- Assegurar qualidade dos dados
- Testar cenários de erro
- Validar APIs públicas
""")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
