#!/usr/bin/env python3
"""
Script para executar testes do backend CryptoQuest.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Executa comando e exibe resultado"""
    print(f"\n{'='*60}")
    print(f"Executando: {description}")
    print(f"Comando: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERRO: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar testes do CryptoQuest")
    parser.add_argument("--type", choices=["unit", "integration", "api", "all"], 
                       default="all", help="Tipo de teste a executar")
    parser.add_argument("--coverage", action="store_true", 
                       help="Executar com cobertura de código")
    parser.add_argument("--firebase", action="store_true", 
                       help="Incluir testes que requerem Firebase")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Modo verboso")
    parser.add_argument("--file", help="Executar teste específico")
    parser.add_argument("--marker", help="Executar testes com marcador específico")
    
    args = parser.parse_args()
    
    # Comando base
    base_cmd = ["python", "-m", "pytest"]
    
    # Adicionar opções
    if args.verbose:
        base_cmd.append("-v")
    
    if args.coverage:
        base_cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Adicionar tipo de teste
    if args.type == "unit":
        base_cmd.extend(["tests/unit/", "-m", "unit"])
    elif args.type == "integration":
        base_cmd.extend(["tests/integration/", "-m", "integration"])
    elif args.type == "api":
        base_cmd.extend(["tests/api/", "-m", "api"])
    else:  # all
        base_cmd.append("tests/")
    
    # Adicionar arquivo específico
    if args.file:
        base_cmd = ["python", "-m", "pytest", args.file]
        if args.verbose:
            base_cmd.append("-v")
    
    # Adicionar marcador específico
    if args.marker:
        base_cmd.extend(["-m", args.marker])
    
    # Excluir testes que requerem Firebase se não especificado
    if not args.firebase:
        base_cmd.extend(["-m", "not firebase"])
    
    # Executar testes
    success = run_command(base_cmd, "Testes do CryptoQuest")
    
    if success:
        print(f"\n{'='*60}")
        print("SUCESSO: Todos os testes passaram!")
        print(f"{'='*60}")
        
        if args.coverage:
            print("\nRelatório de cobertura gerado em: htmlcov/index.html")
    else:
        print(f"\n{'='*60}")
        print("FALHA: Alguns testes falharam!")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == "__main__":
    main()