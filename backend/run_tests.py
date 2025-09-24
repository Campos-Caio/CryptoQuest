#!/usr/bin/env python3
"""
Script para executar testes de forma organizada.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(command, description):
    """Executa comando e exibe resultado"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar testes do backend")
    parser.add_argument("--type", choices=["unit", "integration", "api", "all"], 
                       default="all", help="Tipo de teste a executar")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Modo verboso")
    parser.add_argument("--coverage", "-c", action="store_true", 
                       help="Executar com cobertura de código")
    parser.add_argument("--firebase", action="store_true", 
                       help="Incluir testes que requerem Firebase")
    
    args = parser.parse_args()
    
    # Comando base do pytest
    base_cmd = "python -m pytest"
    
    if args.verbose:
        base_cmd += " -v"
    
    if args.coverage:
        base_cmd += " --cov=app --cov-report=html --cov-report=term"
    
    # Comandos por tipo
    commands = {
        "unit": f"{base_cmd} tests/unit/ -m unit",
        "integration": f"{base_cmd} tests/integration/ -m integration",
        "api": f"{base_cmd} tests/api/ -m api",
        "all": f"{base_cmd} tests/ -m 'unit or integration or api'"
    }
    
    # Adicionar marcadores se necessário
    if not args.firebase:
        for key in commands:
            commands[key] += " -m \"not firebase\""
    
    # Executar testes
    success = True
    
    if args.type == "all":
        # Executar todos os tipos em sequência
        for test_type, command in commands.items():
            if test_type != "all":
                if not run_command(command, f"Executando testes {test_type}"):
                    success = False
    else:
        # Executar tipo específico
        command = commands[args.type]
        if not run_command(command, f"Executando testes {args.type}"):
            success = False
    
    # Resultado final
    print(f"\n{'='*60}")
    if success:
        print("✅ Todos os testes executados com sucesso!")
    else:
        print("❌ Alguns testes falharam!")
        sys.exit(1)
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
