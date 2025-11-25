#!/usr/bin/env python3
"""
Script para executar testes do backend CryptoQuest de forma organizada.
"""

import sys
import subprocess
import argparse


def run_command(command, description):
    """Executa comando e exibe resultado"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    if isinstance(command, list):
        print(f"Comando: {' '.join(command)}")
    else:
        print(f"Comando: {command}")
    print(f"{'='*60}")
    
    try:
        if isinstance(command, list):
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        else:
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
    parser = argparse.ArgumentParser(description="Executar testes do backend CryptoQuest")
    parser.add_argument("--type", choices=["unit", "integration", "api", "all"], 
                       default="all", help="Tipo de teste a executar")
    parser.add_argument("--coverage", "-c", action="store_true", 
                       help="Executar com cobertura de código")
    parser.add_argument("--firebase", action="store_true", 
                       help="Incluir testes que requerem Firebase")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Modo verboso")
    parser.add_argument("--file", help="Executar teste específico")
    parser.add_argument("--marker", help="Executar testes com marcador específico")
    
    args = parser.parse_args()
    
    # Se arquivo específico foi fornecido, executar apenas esse arquivo
    if args.file:
        base_cmd = ["python", "-m", "pytest", args.file]
        if args.verbose:
            base_cmd.append("-v")
        if args.coverage:
            base_cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
        if args.marker:
            base_cmd.extend(["-m", args.marker])
        if not args.firebase:
            base_cmd.extend(["-m", "not firebase"])
        
        success = run_command(base_cmd, f"Executando teste: {args.file}")
        
        if success:
            print(f"\n{'='*60}")
            print("✅ Teste executado com sucesso!")
            print(f"{'='*60}")
            if args.coverage:
                print("\nRelatório de cobertura gerado em: htmlcov/index.html")
        else:
            print(f"\n{'='*60}")
            print("❌ Teste falhou!")
            print(f"{'='*60}")
            sys.exit(1)
        return
    
    # Comando base
    base_cmd = ["python", "-m", "pytest"]
    
    # Adicionar opções
    if args.verbose:
        base_cmd.append("-v")
    
    if args.coverage:
        base_cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Adicionar marcador específico se fornecido
    if args.marker:
        base_cmd.extend(["-m", args.marker])
    
    # Excluir testes que requerem Firebase se não especificado
    if not args.firebase:
        if args.marker:
            # Se já tem um marcador, combinar com not firebase
            base_cmd[-1] = f"{args.marker} and not firebase"
        else:
            base_cmd.extend(["-m", "not firebase"])
    
    # Executar testes
    success = True
    
    if args.type == "all":
        # Executar todos os tipos em sequência
        test_types = ["unit", "integration", "api"]
        for test_type in test_types:
            # Construir comando do zero para evitar conflitos
            cmd = ["python", "-m", "pytest", f"tests/{test_type}/"]
            
            # Adicionar opções
            if args.verbose:
                cmd.append("-v")
            
            if args.coverage:
                cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
            
            # Construir marcador corretamente
            if args.marker:
                if not args.firebase:
                    cmd.extend(["-m", f"{args.marker} and not firebase"])
                else:
                    cmd.extend(["-m", args.marker])
            else:
                if not args.firebase:
                    cmd.extend(["-m", f"{test_type} and not firebase"])
                else:
                    cmd.extend(["-m", test_type])
            
            if not run_command(cmd, f"Executando testes {test_type}"):
                success = False
    else:
        # Executar tipo específico
        # Construir comando do zero para evitar conflitos
        cmd = ["python", "-m", "pytest", f"tests/{args.type}/"]
        
        # Adicionar opções
        if args.verbose:
            cmd.append("-v")
        
        if args.coverage:
            cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
        
        # Construir marcador corretamente
        if args.marker:
            if not args.firebase:
                cmd.extend(["-m", f"{args.marker} and not firebase"])
            else:
                cmd.extend(["-m", args.marker])
        else:
            if not args.firebase:
                cmd.extend(["-m", f"{args.type} and not firebase"])
            else:
                cmd.extend(["-m", args.type])
        
        if not run_command(cmd, f"Executando testes {args.type}"):
            success = False
    
    # Resultado final
    print(f"\n{'='*60}")
    if success:
        print("✅ Todos os testes executados com sucesso!")
        if args.coverage:
            print("\nRelatório de cobertura gerado em: htmlcov/index.html")
    else:
        print("❌ Alguns testes falharam!")
        sys.exit(1)
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
