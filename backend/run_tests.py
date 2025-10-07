#!/usr/bin/env python3
"""
<<<<<<< HEAD
Script para executar testes do backend CryptoQuest.
"""

import sys
import subprocess
=======
Script para executar testes de forma organizada.
"""

import subprocess
import sys
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
import argparse
from pathlib import Path


def run_command(command, description):
    """Executa comando e exibe resultado"""
    print(f"\n{'='*60}")
<<<<<<< HEAD
    print(f"Executando: {description}")
    print(f"Comando: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
=======
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
<<<<<<< HEAD
        print(f"ERRO: {e}")
=======
        print(f"❌ Erro: {e}")
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Função principal"""
<<<<<<< HEAD
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
=======
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
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
