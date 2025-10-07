#!/usr/bin/env python3
"""
Script para fazer merge limpo entre ai e main
"""

import subprocess
import os
import shutil

def run_command(cmd, cwd=None):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🧹 Preparando merge limpo...")
    
    # 1. Remover todos os arquivos __pycache__ do sistema de arquivos
    print("🗑️  Removendo arquivos __pycache__...")
    cache_dirs = [
        "backend/app/__pycache__",
        "backend/app/api/__pycache__", 
        "backend/app/core/__pycache__",
        "backend/app/dependencies/__pycache__",
        "backend/app/models/__pycache__",
        "backend/app/repositories/__pycache__",
        "backend/app/services/__pycache__",
        "backend/tests/__pycache__",
        "backend/tests/api/__pycache__",
        "backend/tests/integration/__pycache__",
        "backend/tests/unit/__pycache__",
        "backend/tests/fixtures/__pycache__",
        "backend/tests/utils/__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"✅ Removido {cache_dir}")
    
    # 2. Remover arquivos __pycache__ do Git (se existirem)
    print("📝 Removendo __pycache__ do Git...")
    success, stdout, stderr = run_command("git rm -r --cached backend/app/__pycache__ backend/app/api/__pycache__ backend/app/core/__pycache__ backend/app/dependencies/__pycache__ backend/app/models/__pycache__ backend/app/repositories/__pycache__ backend/app/services/__pycache__ 2>/dev/null || true")
    
    # 3. Fazer commit das limpezas se necessário
    success, stdout, stderr = run_command("git status --porcelain")
    if "D " in stdout or "A " in stdout:
        print("💾 Commitando limpezas...")
        run_command('git add -A')
        run_command('git commit -m "clean: remove __pycache__ files before merge"')
    
    # 4. Fazer merge da branch ai
    print("🔄 Fazendo merge da branch ai...")
    success, stdout, stderr = run_command("git merge ai")
    
    if not success:
        print("⚠️  Conflitos detectados. Resolvendo...")
        
        # 5. Resolver conflitos automaticamente
        # Remover __pycache__ que ainda possam ter conflitos
        run_command("git rm -r -f backend/app/__pycache__ backend/app/api/__pycache__ backend/app/core/__pycache__ backend/app/dependencies/__pycache__ backend/app/models/__pycache__ backend/app/repositories/__pycache__ backend/app/services/__pycache__ 2>/dev/null || true")
        
        # Resolver conflito no app_config.dart (manter URL de produção)
        if os.path.exists("frontend/cryptoquest/lib/core/config/app_config.dart"):
            with open("frontend/cryptoquest/lib/core/config/app_config.dart", "w") as f:
                f.write('''class AppConfig {
  static const String baseUrl = "https://cryptoquest-backend.onrender.com"; 
  // static const String baseUrl = "http://127.0.0.1:8000";  // Para desenvolvimento local
}''')
            print("✅ Resolvido app_config.dart")
        
        # Adicionar arquivos resolvidos
        run_command("git add frontend/cryptoquest/lib/core/config/app_config.dart")
        run_command("git add backend/requirements.txt")
        
        # Verificar se ainda há conflitos
        success, stdout, stderr = run_command("git status --porcelain")
        if "UU" in stdout or "AA" in stdout or "DD" in stdout:
            print("❌ Ainda há conflitos. Resolva manualmente:")
            print(stdout)
        else:
            print("✅ Todos os conflitos resolvidos!")
            print("💡 Execute: git commit -m 'merge: integrate ai branch with main'")
    
    else:
        print("✅ Merge realizado com sucesso!")
    
    print("🎉 Processo concluído!")

if __name__ == "__main__":
    main()
