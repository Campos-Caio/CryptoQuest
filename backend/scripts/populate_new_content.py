"""
Script para popular o Firestore com novo conteúdo educacional:
- 10 novas trilhas de aprendizado (learning paths)
- 35+ quizzes de módulos
- 25+ missões diárias

Uso:
    python scripts/populate_new_content.py
"""

import sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).resolve().parents[1]))

def _configure_credentials():
    """Configura as credenciais para o ambiente"""
    import os
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    
    if creds_json_str:
        temp_credentials_path = "/tmp/firebase_credentials.json"
        with open(temp_credentials_path, "w") as f:
            f.write(creds_json_str)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path
        print("✅ Credenciais configuradas a partir da variável de ambiente.")
    else:
        print("🔧 Configurando credenciais a partir de arquivo local...")
        cred_path = Path(__file__).resolve().parents[1] / "firebase_key.json"
        if not cred_path.exists():
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path)
        print("✅ Credenciais configuradas a partir do arquivo local.")

def initialize_firebase():
    """Inicializa o Firebase Admin SDK"""
    if not firebase_admin._apps:
        try:
            print("🚀 Inicializando Firebase App...")
            firebase_admin.initialize_app()
            print("✅ Firebase inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar Firebase: {e}")
            sys.exit(1)

# ============================================================
# NOVOS QUIZZES - PARTE 1/3
# ============================================================
def get_new_quizzes_part1():
    """Retorna primeiros 15 quizzes novos"""
    return [
        # TRILHA 1: Ethereum e Smart Contracts
        {
            "id": "ethereum_intro_quiz",
            "title": "Introdução ao Ethereum",
            "questions": [
                {
                    "text": "O que diferencia o Ethereum do Bitcoin?",
                    "options": [
                        {"text": "Ethereum é apenas uma criptomoeda como Bitcoin"},
                        {"text": "Ethereum permite programar contratos inteligentes na blockchain"},
                        {"text": "Ethereum é mais antigo que Bitcoin"},
                        {"text": "Ethereum não usa blockchain"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual é a criptomoeda nativa do Ethereum?",
                    "options": [
                        {"text": "Bitcoin"},
                        {"text": "Ether (ETH)"},
                        {"text": "Tether"},
                        {"text": "Cardano"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que são 'smart contracts'?",
                    "options": [
                        {"text": "Contratos em papel digitalizados"},
                        {"text": "Programas auto-executáveis armazenados na blockchain"},
                        {"text": "Contratos com advogados inteligentes"},
                        {"text": "Acordos que não podem ser alterados"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Quem criou o Ethereum?",
                    "options": [
                        {"text": "Satoshi Nakamoto"},
                        {"text": "Vitalik Buterin"},
                        {"text": "Elon Musk"},
                        {"text": "Mark Zuckerberg"}
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        {
            "id": "smart_contracts_basics_quiz",
            "title": "Fundamentos de Smart Contracts",
            "questions": [
                {
                    "text": "Qual a principal vantagem dos smart contracts?",
                    "options": [
                        {"text": "São mais baratos que contratos tradicionais"},
                        {"text": "Executam automaticamente sem intermediários"},
                        {"text": "Podem ser alterados a qualquer momento"},
                        {"text": "Funcionam sem blockchain"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Em que linguagem são escritos contratos inteligentes no Ethereum?",
                    "options": [
                        {"text": "Python"},
                        {"text": "Solidity"},
                        {"text": "JavaScript"},
                        {"text": "C++"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que é 'gas' no Ethereum?",
                    "options": [
                        {"text": "Um tipo de criptomoeda"},
                        {"text": "Taxa paga para executar transações e contratos"},
                        {"text": "Combustível para minerar Ethereum"},
                        {"text": "Uma carteira digital"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Quem paga o 'gas' de um smart contract?",
                    "options": [
                        {"text": "O criador do contrato sempre"},
                        {"text": "Quem executa a transação"},
                        {"text": "O Ethereum Foundation"},
                        {"text": "Ninguém, é grátis"}
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        {
            "id": "solidity_intro_quiz",
            "title": "Introdução ao Solidity",
            "questions": [
                {
                    "text": "O que é Solidity?",
                    "options": [
                        {"text": "Uma criptomoeda"},
                        {"text": "Linguagem de programação para smart contracts"},
                        {"text": "Uma exchange de criptomoedas"},
                        {"text": "Um tipo de carteira"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual a extensão de arquivos Solidity?",
                    "options": [
                        {"text": ".py"},
                        {"text": ".sol"},
                        {"text": ".eth"},
                        {"text": ".js"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que são 'modifiers' em Solidity?",
                    "options": [
                        {"text": "Variáveis especiais"},
                        {"text": "Código que modifica o comportamento de funções"},
                        {"text": "Tipos de dados"},
                        {"text": "Comentários no código"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que é uma 'view function' em Solidity?",
                    "options": [
                        {"text": "Função que altera o estado da blockchain"},
                        {"text": "Função que apenas lê dados sem modificá-los"},
                        {"text": "Função privada"},
                        {"text": "Função que custa gas"}
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        {
            "id": "dapps_fundamentals_quiz",
            "title": "Fundamentos de DApps",
            "questions": [
                {
                    "text": "O que significa DApp?",
                    "options": [
                        {"text": "Digital Application"},
                        {"text": "Decentralized Application"},
                        {"text": "Data Application"},
                        {"text": "Dynamic Application"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual a principal característica de um DApp?",
                    "options": [
                        {"text": "Roda em um servidor central"},
                        {"text": "Código aberto e roda em blockchain"},
                        {"text": "Requer aprovação de empresas"},
                        {"text": "Funciona apenas offline"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que é Web3.js?",
                    "options": [
                        {"text": "Uma criptomoeda"},
                        {"text": "Biblioteca para interagir com Ethereum"},
                        {"text": "Um navegador web"},
                        {"text": "Uma rede social"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Exemplo de DApp famoso:",
                    "options": [
                        {"text": "Facebook"},
                        {"text": "Uniswap"},
                        {"text": "Instagram"},
                        {"text": "WhatsApp"}
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        
        # TRILHA 2: DeFi (Finanças Descentralizadas)
        {
            "id": "defi_fundamentals_quiz",
            "title": "Fundamentos de DeFi",
            "questions": [
                {
                    "text": "O que significa DeFi?",
                    "options": [
                        {"text": "Digital Finance"},
                        {"text": "Decentralized Finance"},
                        {"text": "Definite Finance"},
                        {"text": "Developer Finance"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Principal vantagem do DeFi sobre finanças tradicionais?",
                    "options": [
                        {"text": "Precisa de bancos"},
                        {"text": "Acesso sem intermediários 24/7"},
                        {"text": "Regulamentação rigorosa"},
                        {"text": "Atendimento ao cliente"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que é yield farming?",
                    "options": [
                        {"text": "Plantar criptomoedas"},
                        {"text": "Emprestar cripto para ganhar retornos"},
                        {"text": "Minerar Bitcoin"},
                        {"text": "Comprar NFTs"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que é TVL em DeFi?",
                    "options": [
                        {"text": "Taxa de Valor Local"},
                        {"text": "Total Value Locked (valor total bloqueado)"},
                        {"text": "Transação Validada Lenta"},
                        {"text": "Token Value Level"}
                    ],
                    "correct_answer_index": 1
                }
            ]
        }
    ]

# CONTINUA NA PRÓXIMA FUNÇÃO...


