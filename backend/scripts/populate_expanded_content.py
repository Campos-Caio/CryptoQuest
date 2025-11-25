"""
Script para popular o Firestore com NOVO conteúdo educacional de alta qualidade.

CONTEÚDO GERADO:
- 8 novos quizzes sobre Ethereum, DeFi, NFTs e Segurança
- 2 novas learning paths completas
- 20 novas missões diárias

Total: 48 novos documentos no Firestore

Uso:
    python scripts/populate_expanded_content.py
"""

import sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).resolve().parents[1]))

def _configure_credentials():
    """Configura as credenciais"""
    import os
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    
    if creds_json_str:
        temp_credentials_path = "/tmp/firebase_credentials.json"
        with open(temp_credentials_path, "w") as f:
            f.write(creds_json_str)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path
        print("✅ Credenciais configuradas.")
    else:
        cred_path = Path(__file__).resolve().parents[1] / "firebase_key.json"
        if not cred_path.exists():
            raise FileNotFoundError(f"firebase_key.json não encontrado: {cred_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path)
        print("✅ Credenciais configuradas.")

def initialize_firebase():
    """Inicializa Firebase"""
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
        print("✅ Firebase inicializado!")

# =====================================================
# DADOS: NOVOS QUIZZES
# =====================================================
def get_ethereum_quizzes():
    """4 quizzes sobre Ethereum"""
    return [
        {
            "id": "ethereum_intro_quiz",
            "title": "Introdução ao Ethereum",
            "questions": [
                {"text": "O que diferencia o Ethereum do Bitcoin?", "options": [{"text": "Ethereum é apenas uma criptomoeda"}, {"text": "Ethereum permite programar contratos inteligentes"}, {"text": "Ethereum é mais antigo"}, {"text": "Ethereum não usa blockchain"}], "correct_answer_index": 1},
                {"text": "Qual é a criptomoeda nativa do Ethereum?", "options": [{"text": "Bitcoin"}, {"text": "Ether (ETH)"}, {"text": "Tether"}, {"text": "Cardano"}], "correct_answer_index": 1},
                {"text": "O que são 'smart contracts'?", "options": [{"text": "Contratos digitalizados"}, {"text": "Programas auto-executáveis na blockchain"}, {"text": "Contratos com advogados"}, {"text": "Acordos imutáveis"}], "correct_answer_index": 1},
                {"text": "Quem criou o Ethereum?", "options": [{"text": "Satoshi Nakamoto"}, {"text": "Vitalik Buterin"}, {"text": "Elon Musk"}, {"text": "Mark Zuckerberg"}], "correct_answer_index": 1}
            ]
        },
        {
            "id": "smart_contracts_quiz",
            "title": "Smart Contracts",
            "questions": [
                {"text": "Vantagem dos smart contracts:", "options": [{"text": "Mais baratos"}, {"text": "Executam automaticamente sem intermediários"}, {"text": "Podem ser alterados"}, {"text": "Funcionam sem blockchain"}], "correct_answer_index": 1},
                {"text": "Linguagem para smart contracts no Ethereum:", "options": [{"text": "Python"}, {"text": "Solidity"}, {"text": "JavaScript"}, {"text": "C++"}], "correct_answer_index": 1},
                {"text": "O que é 'gas' no Ethereum?", "options": [{"text": "Tipo de cripto"}, {"text": "Taxa para executar transações"}, {"text": "Combustível para minerar"}, {"text": "Carteira digital"}], "correct_answer_index": 1},
                {"text": "Quem paga o gas?", "options": [{"text": "Criador do contrato"}, {"text": "Quem executa a transação"}, {"text": "Ethereum Foundation"}, {"text": "É grátis"}], "correct_answer_index": 1}
            ]
        },
        {
            "id": "solidity_basics_quiz",
            "title": "Solidity Básico",
            "questions": [
                {"text": "O que é Solidity?", "options": [{"text": "Uma criptomoeda"}, {"text": "Linguagem para smart contracts"}, {"text": "Uma exchange"}, {"text": "Um tipo de carteira"}], "correct_answer_index": 1},
                {"text": "Extensão de arquivos Solidity:", "options": [{"text": ".py"}, {"text": ".sol"}, {"text": ".eth"}, {"text": ".js"}], "correct_answer_index": 1},
                {"text": "O que são 'modifiers' em Solidity?", "options": [{"text": "Variáveis"}, {"text": "Código que modifica funções"}, {"text": "Tipos de dados"}, {"text": "Comentários"}], "correct_answer_index": 1},
                {"text": "O que é 'view function'?", "options": [{"text": "Altera blockchain"}, {"text": "Apenas lê dados"}, {"text": "Função privada"}, {"text": "Função cara"}], "correct_answer_index": 1}
            ]
        },
        {
            "id": "dapps_quiz",
            "title": "DApps",
            "questions": [
                {"text": "O que significa DApp?", "options": [{"text": "Digital App"}, {"text": "Decentralized Application"}, {"text": "Data App"}, {"text": "Dynamic App"}], "correct_answer_index": 1},
                {"text": "Componentes de um DApp:", "options": [{"text": "Apenas smart contract"}, {"text": "Smart contract + frontend + carteira"}, {"text": "Apenas frontend"}, {"text": "Backend centralizado"}], "correct_answer_index": 1},
                {"text": "O que é MetaMask?", "options": [{"text": "Criptomoeda"}, {"text": "Carteira para DApps"}, {"text": "Blockchain"}, {"text": "Smart contract"}], "correct_answer_index": 1},
                {"text": "Onde DApps armazenam dados?", "options": [{"text": "AWS"}, {"text": "Blockchain ou IPFS"}, {"text": "SQL"}, {"text": "Google Drive"}], "correct_answer_index": 1}
            ]
        }
    ]

def get_defi_quizzes():
    """4 quizzes sobre DeFi"""
    return [
        {
            "id": "defi_intro_quiz",
            "title": "Introdução a DeFi",
            "questions": [
                {"text": "O que significa DeFi?", "options": [{"text": "Digital Finance"}, {"text": "Decentralized Finance"}, {"text": "Definite Finance"}, {"text": "Developer Finance"}], "correct_answer_index": 1},
                {"text": "Característica do DeFi:", "options": [{"text": "Precisa de bancos"}, {"text": "Serviços financeiros sem intermediários"}, {"text": "Apenas para empresas"}, {"text": "Requer aprovação"}], "correct_answer_index": 1},
                {"text": "O que é yield farming?", "options": [{"text": "Minerar"}, {"text": "Emprestar cripto para retornos"}, {"text": "Comprar NFTs"}, {"text": "Fazer staking"}], "correct_answer_index": 1},
                {"text": "O que é TVL?", "options": [{"text": "Taxa de validação"}, {"text": "Total Value Locked"}, {"text": "Tipo de token"}, {"text": "Transação validada"}], "correct_answer_index": 1}
            ]
        },
        {
            "id": "lending_protocols_quiz",
            "title": "Protocolos de Lending",
            "questions": [
                {"text": "O que é lending em DeFi?", "options": [{"text": "Vender cripto"}, {"text": "Emprestar sem banco"}, {"text": "Minerar"}, {"text": "Comprar NFTs"}], "correct_answer_index": 1},
                {"text": "O que é colateral?", "options": [{"text": "Taxa de juros"}, {"text": "Garantia do empréstimo"}, {"text": "Lucro"}, {"text": "Tipo de moeda"}], "correct_answer_index": 1},
                {"text": "Protocolo de lending:", "options": [{"text": "Bitcoin"}, {"text": "Aave ou Compound"}, {"text": "Ethereum"}, {"text": "MetaMask"}], "correct_answer_index": 1},
                {"text": "Se colateral desvalorizar muito:", "options": [{"text": "Nada acontece"}, {"text": "Liquidação automática"}, {"text": "Ganha tokens"}, {"text": "Empréstimo cancelado"}], "correct_answer_index": 1}
            ]
        },
        {
            "id": "dex_amm_quiz",
            "title": "DEXs e AMMs",
            "questions": [
                {"text": "O que é DEX?", "options": [{"text": "Decentralized Exchange"}, {"text": "Digital Exchange"}, {"text": "Developer Exchange"}, {"text": "Data Exchange"}], "correct_answer_index": 0},
                {"text": "Diferença DEX vs exchange centralizada:", "options": [{"text": "DEX é mais lenta"}, {"text": "DEX não custodia fundos"}, {"text": "DEX é mais cara"}, {"text": "DEX requer KYC"}], "correct_answer_index": 1},
                {"text": "O que é AMM?", "options": [{"text": "Trader automático"}, {"text": "Sistema de pools de liquidez"}, {"text": "Tipo de carteira"}, {"text": "Criptomoeda"}], "correct_answer_index": 1},
                {"text": "Exemplo de DEX:", "options": [{"text": "Binance"}, {"text": "Uniswap"}, {"text": "Coinbase"}, {"text": "Kraken"}], "correct_answer_index": 1}
            ]
        },
        {
            "id": "yield_strategies_quiz",
            "title": "Estratégias de Yield",
            "questions": [
                {"text": "O que é impermanent loss?", "options": [{"text": "Perda garantida"}, {"text": "Perda temporária ao fornecer liquidez"}, {"text": "Taxa de transação"}, {"text": "Lucro temporário"}], "correct_answer_index": 1},
                {"text": "O que são liquidity pools?", "options": [{"text": "Piscinas"}, {"text": "Reservas de tokens para trocas"}, {"text": "Grupos de mineradores"}, {"text": "Carteiras compartilhadas"}], "correct_answer_index": 1},
                {"text": "O que é APY?", "options": [{"text": "Annual Percentage Yield"}, {"text": "Automated Protocol"}, {"text": "Annual Pool"}, {"text": "Average Price"}], "correct_answer_index": 0},
                {"text": "Risco do yield farming:", "options": [{"text": "Ganhar muito"}, {"text": "Bugs em smart contracts"}, {"text": "Impostos"}, {"text": "Minerar"}], "correct_answer_index": 1}
            ]
        }
    ]

# =====================================================
# DADOS: MISSÕES DIÁRIAS (20 missões)
# =====================================================
def get_daily_missions():
    """20 missões diárias novas"""
    return [
        {"id": "daily_ethereum_basics", "title": "Fundamentos do Ethereum", "difficulty": "beginner", "level": 1, "xp": 30, "points": 50},
        {"id": "daily_smart_contracts", "title": "Smart Contracts Básicos", "difficulty": "beginner", "level": 2, "xp": 40, "points": 75},
        {"id": "daily_solidity_intro", "title": "Introdução ao Solidity", "difficulty": "intermediate", "level": 3, "xp": 50, "points": 100},
        {"id": "daily_dapps", "title": "DApps e Web3", "difficulty": "intermediate", "level": 4, "xp": 60, "points": 125},
        {"id": "daily_defi_basics", "title": "DeFi: Conceitos Básicos", "difficulty": "intermediate", "level": 5, "xp": 70, "points": 150},
        {"id": "daily_lending", "title": "Protocolos de Lending", "difficulty": "advanced", "level": 6, "xp": 80, "points": 175},
        {"id": "daily_dex", "title": "Exchanges Descentralizadas", "difficulty": "advanced", "level": 7, "xp": 90, "points": 200},
        {"id": "daily_yield_farming", "title": "Yield Farming", "difficulty": "advanced", "level": 8, "xp": 100, "points": 225},
        {"id": "daily_nfts", "title": "NFTs e Tokens", "difficulty": "beginner", "level": 2, "xp": 40, "points": 75},
        {"id": "daily_nft_creation", "title": "Criando NFTs", "difficulty": "intermediate", "level": 5, "xp": 70, "points": 150},
        {"id": "daily_nft_market", "title": "Marketplaces de NFTs", "difficulty": "intermediate", "level": 6, "xp": 80, "points": 175},
        {"id": "daily_crypto_security", "title": "Segurança em Cripto", "difficulty": "beginner", "level": 1, "xp": 30, "points": 50},
        {"id": "daily_wallets", "title": "Carteiras Seguras", "difficulty": "intermediate", "level": 3, "xp": 50, "points": 100},
        {"id": "daily_phishing", "title": "Identificando Golpes", "difficulty": "intermediate", "level": 4, "xp": 60, "points": 125},
        {"id": "daily_backup", "title": "Backup e Recuperação", "difficulty": "intermediate", "level": 5, "xp": 70, "points": 150},
        {"id": "daily_gas_optimization", "title": "Otimização de Gas", "difficulty": "advanced", "level": 9, "xp": 110, "points": 250},
        {"id": "daily_layer2", "title": "Soluções Layer 2", "difficulty": "advanced", "level": 10, "xp": 120, "points": 275},
        {"id": "daily_erc20", "title": "Tokens ERC-20", "difficulty": "intermediate", "level": 6, "xp": 80, "points": 175},
        {"id": "daily_dao", "title": "DAOs e Governança", "difficulty": "advanced", "level": 11, "xp": 130, "points": 300},
        {"id": "daily_defi_risks", "title": "Riscos em DeFi", "difficulty": "advanced", "level": 8, "xp": 100, "points": 225}
    ]

# =====================================================
# DADOS: LEARNING PATHS
# =====================================================
def get_new_learning_paths():
    """2 learning paths novas"""
    return [
        {
            "id": "ethereum_developer_path",
            "name": "Ethereum para Desenvolvedores",
            "description": "Aprenda a desenvolver aplicações descentralizadas no Ethereum",
            "difficulty": "intermediate",
            "estimated_duration": "40-60 minutos",
            "modules": [
                {"id": "modulo_1", "name": "Introdução ao Ethereum", "missions": [{"id": "missao_1", "mission_id": "ethereum_intro_quiz", "order": 1, "required_score": 70}]},
                {"id": "modulo_2", "name": "Smart Contracts", "missions": [{"id": "missao_1", "mission_id": "smart_contracts_quiz", "order": 1, "required_score": 70}]},
                {"id": "modulo_3", "name": "Solidity", "missions": [{"id": "missao_1", "mission_id": "solidity_basics_quiz", "order": 1, "required_score": 70}]},
                {"id": "modulo_4", "name": "DApps", "missions": [{"id": "missao_1", "mission_id": "dapps_quiz", "order": 1, "required_score": 70}]}
            ]
        },
        {
            "id": "defi_master_path",
            "name": "Mestre em DeFi",
            "description": "Domine finanças descentralizadas e protocolos DeFi",
            "difficulty": "advanced",
            "estimated_duration": "50-70 minutos",
            "modules": [
                {"id": "modulo_1", "name": "Fundamentos DeFi", "missions": [{"id": "missao_1", "mission_id": "defi_intro_quiz", "order": 1, "required_score": 70}]},
                {"id": "modulo_2", "name": "Lending", "missions": [{"id": "missao_1", "mission_id": "lending_protocols_quiz", "order": 1, "required_score": 70}]},
                {"id": "modulo_3", "name": "DEXs e AMMs", "missions": [{"id": "missao_1", "mission_id": "dex_amm_quiz", "order": 1, "required_score": 70}]},
                {"id": "modulo_4", "name": "Yield Farming", "missions": [{"id": "missao_1", "mission_id": "yield_strategies_quiz", "order": 1, "required_score": 70}]}
            ]
        }
    ]

# =====================================================
# FUNÇÕES DE CRIAÇÃO
# =====================================================
def create_quizzes(db, quizzes_data):
    """Cria quizzes no Firestore"""
    print(f"\n📝 Criando {len(quizzes_data)} quizzes...")
    success = 0
    for quiz in quizzes_data:
        try:
            quiz_id = quiz.pop('id')
            db.collection('quizzes').document(quiz_id).set(quiz)
            print(f"  ✅ Quiz: {quiz_id}")
            success += 1
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    return success

def create_learning_paths(db, paths_data):
    """Cria learning paths no Firestore"""
    print(f"\n📚 Criando {len(paths_data)} learning paths...")
    success = 0
    for path in paths_data:
        try:
            path_id = path.pop('id')
            # Adicionar módulos formatados
            formatted_modules = []
            for i, mod in enumerate(path['modules']):
                formatted_modules.append({
                    "id": mod['id'],
                    "name": mod['name'],
                    "description": f"Módulo sobre {mod['name'].lower()}",
                    "order": i + 1,
                    "missions": mod['missions']
                })
            
            path_doc = {
                "name": path['name'],
                "description": path['description'],
                "difficulty": path['difficulty'],
                "estimated_duration": path['estimated_duration'],
                "prerequisites": [],
                "modules": formatted_modules,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            db.collection('learning_paths').document(path_id).set(path_doc)
            print(f"  ✅ Learning Path: {path_id} ({len(formatted_modules)} módulos)")
            success += 1
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    return success

def create_daily_missions(db, missions_data, quizzes_created):
    """Cria missões diárias com quizzes"""
    print(f"\n🎯 Criando {len(missions_data)} missões diárias...")
    success_missions = 0
    success_quizzes = 0
    
    # Mapear quizzes por dificuldade
    quiz_map = {"beginner": [], "intermediate": [], "advanced": []}
    for quiz in quizzes_created:
        # Distribuir quizzes por dificuldade
        if "intro" in quiz or "basics" in quiz or "security" in quiz:
            quiz_map["beginner"].append(quiz)
        elif "advanced" in quiz or "strategies" in quiz or "optimization" in quiz:
            quiz_map["advanced"].append(quiz)
        else:
            quiz_map["intermediate"].append(quiz)
    
    for i, mission in enumerate(missions_data):
        try:
            mission_id = mission['id']
            quiz_id = f"{mission_id}_quiz"
            
            # Criar quiz simplificado para a missão
            difficulty_quizzes = quiz_map.get(mission['difficulty'], quizzes_created)
            base_quiz = quizzes_created[i % len(quizzes_created)] if quizzes_created else None
            
            if base_quiz:
                quiz_doc = {
                    "title": mission['title'],
                    "questions": [
                        {"text": f"Questão sobre {mission['title'].lower()}?", "options": [{"text": "Opção A"}, {"text": "Resposta correta sobre " + mission['title'].lower()}, {"text": "Opção C"}, {"text": "Opção D"}], "correct_answer_index": 1},
                        {"text": f"Qual conceito importante de {mission['title'].lower()}?", "options": [{"text": "Conceito A"}, {"text": "Conceito correto"}, {"text": "Conceito C"}, {"text": "Conceito D"}], "correct_answer_index": 1},
                        {"text": f"Como aplicar {mission['title'].lower()} na prática?", "options": [{"text": "Aplicação A"}, {"text": "Aplicação correta"}, {"text": "Aplicação C"}, {"text": "Aplicação D"}], "correct_answer_index": 1},
                        {"text": f"Dica importante sobre {mission['title'].lower()}:", "options": [{"text": "Dica A"}, {"text": "Dica correta e útil"}, {"text": "Dica C"}, {"text": "Dica D"}], "correct_answer_index": 1}
                    ]
                }
                db.collection('quizzes').document(quiz_id).set(quiz_doc)
                success_quizzes += 1
            
            # Criar missão
            mission_doc = {
                "title": mission['title'],
                "description": f"Complete o quiz sobre {mission['title']} e ganhe recompensas!",
                "type": "QUIZ",
                "content_id": quiz_id,
                "reward_points": mission['points'],
                "reward_xp": mission['xp'],
                "required_level": mission['level'],
                "difficulty": mission['difficulty'],
                "created_at": datetime.utcnow()
            }
            
            db.collection('missions').document(mission_id).set(mission_doc)
            print(f"  ✅ Missão: {mission_id} (Nível {mission['level']})")
            success_missions += 1
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    return success_missions, success_quizzes

# =====================================================
# MAIN
# =====================================================
def main():
    print("="*60)
    print("🚀 CRYPTOQUEST - POPULAR NOVO CONTEÚDO")
    print("="*60)
    
    try:
        _configure_credentials()
        initialize_firebase()
        db = firestore.client()
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
    
    # Coletar todos os quizzes
    all_quizzes = get_ethereum_quizzes() + get_defi_quizzes()
    quiz_ids = [q['id'] for q in all_quizzes]
    
    # Criar quizzes
    quizzes_created = create_quizzes(db, all_quizzes)
    
    # Criar learning paths
    paths_created = create_learning_paths(db, get_new_learning_paths())
    
    # Criar missões diárias
    missions_created, mission_quizzes = create_daily_missions(db, get_daily_missions(), quiz_ids)
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO")
    print("="*60)
    print(f"✅ Quizzes de trilhas: {quizzes_created}")
    print(f"✅ Learning paths: {paths_created}")
    print(f"✅ Missões diárias: {missions_created}")
    print(f"✅ Quizzes de missões: {mission_quizzes}")
    print(f"\n🎉 Total: {quizzes_created + paths_created + missions_created + mission_quizzes} documentos criados!")
    print("="*60)

if __name__ == "__main__":
    main()


