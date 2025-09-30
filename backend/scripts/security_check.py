#!/usr/bin/env python3
"""
Script para validar as correções de segurança do CryptoQuest
"""

import os
import sys
import requests
from pathlib import Path

def check_environment_variables():
    """Verifica se as variáveis de ambiente de segurança estão configuradas"""
    print("🔍 Verificando variáveis de ambiente de segurança...")
    
    required_vars = [
        "ALLOWED_ORIGINS",
        "ALLOWED_HOSTS", 
        "FIREBASE_CREDENTIALS_JSON"
    ]
    
    optional_vars = [
        "LOG_LEVEL",
        "ENVIRONMENT",
        "API_VERSION"
    ]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Variáveis de ambiente obrigatórias ausentes: {missing_required}")
        print("💡 Configure essas variáveis usando o arquivo env.example como referência")
        return False
    
    print("✅ Variáveis de ambiente obrigatórias configuradas")
    
    # Verificar variáveis opcionais
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        print(f"⚠️  Variáveis de ambiente opcionais ausentes: {missing_optional}")
        print("💡 Configure essas variáveis para melhor segurança")
    
    return True

def check_file_security():
    """Verifica se os arquivos de credenciais não estão expostos"""
    print("\n🔍 Verificando segurança dos arquivos...")
    
    # Verificar se firebase_key.json existe (não deveria em produção)
    firebase_key_path = Path("firebase_key.json")
    if firebase_key_path.exists():
        print("⚠️  firebase_key.json encontrado - NÃO RECOMENDADO PARA PRODUÇÃO")
        print("💡 Use FIREBASE_CREDENTIALS_JSON em produção")
    else:
        print("✅ firebase_key.json não encontrado (bom para produção)")
    
    # Verificar se .env.example existe
    env_example_path = Path("env.example")
    if env_example_path.exists():
        print("✅ env.example encontrado - documentação de variáveis disponível")
    else:
        print("❌ env.example não encontrado - documentação ausente")
        return False
    
    return True

def check_code_security():
    """Verifica se há problemas de segurança no código"""
    print("\n🔍 Verificando segurança do código...")
    
    # Verificar se há prints de debug
    backend_path = Path("app")
    debug_prints = 0
    
    for py_file in backend_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'print(' in content:
                    debug_prints += 1
        except Exception:
            continue
    
    if debug_prints > 0:
        print(f"⚠️  {debug_prints} arquivos ainda contêm print() - considere usar logging")
    else:
        print("✅ Nenhum print() encontrado no código")
    
    # Verificar se há logs de tokens (apenas logs que expõem o token)
    token_logs = 0
    for py_file in backend_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Verificar apenas logs que realmente expõem o token
                if ('token[:' in content and ('print(' in content or 'logger.' in content)) or \
                   ('f"Token' in content and 'print(' in content):
                    token_logs += 1
        except Exception:
            continue
    
    if token_logs > 0:
        print(f"❌ {token_logs} arquivos podem estar logando tokens - RISCO DE SEGURANÇA")
        return False
    else:
        print("✅ Nenhum log de token encontrado")
    
    return True

def check_middleware_security():
    """Verifica se os middlewares de segurança estão configurados"""
    print("\n🔍 Verificando middlewares de segurança...")
    
    try:
        # Tentar importar os middlewares
        sys.path.append('.')
        from app.middleware.security import SecurityHeadersMiddleware, RateLimitMiddleware
        print("✅ Middlewares de segurança importados com sucesso")
        
        # Verificar se estão sendo usados no main.py
        with open('app/main.py', 'r') as f:
            main_content = f.read()
            
        if 'SecurityHeadersMiddleware' in main_content:
            print("✅ SecurityHeadersMiddleware configurado")
        else:
            print("❌ SecurityHeadersMiddleware não encontrado no main.py")
            return False
            
        if 'RateLimitMiddleware' in main_content:
            print("✅ RateLimitMiddleware configurado")
        else:
            print("❌ RateLimitMiddleware não encontrado no main.py")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar middlewares de segurança: {e}")
        return False

def main():
    """Função principal de validação"""
    print("🛡️  VALIDAÇÃO DE SEGURANÇA - CRYPTOQUEST")
    print("=" * 50)
    
    checks = [
        ("Variáveis de Ambiente", check_environment_variables),
        ("Segurança de Arquivos", check_file_security),
        ("Segurança do Código", check_code_security),
        ("Middlewares de Segurança", check_middleware_security),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ Erro na verificação {check_name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} verificações passaram")
    
    if passed == total:
        print("🎉 TODAS AS VERIFICAÇÕES DE SEGURANÇA PASSARAM!")
        print("✅ O sistema está pronto para produção (com as devidas configurações)")
    else:
        print("⚠️  ALGUMAS VERIFICAÇÕES FALHARAM")
        print("🔧 Corrija os problemas identificados antes de ir para produção")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
