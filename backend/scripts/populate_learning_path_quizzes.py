"""
Script para popular o banco de dados Firestore com quizzes das trilhas de aprendizado.
"""

import json
import sys
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def _configure_credentials():
    """Configura as credenciais para o ambiente"""
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

def get_learning_path_quizzes():
    """Retorna os quizzes das trilhas de aprendizado"""
    return {
        "escambo_questionnaire": {
            "title": "A Origem do Dinheiro - Escambo",
            "questions": [
                {
                    "text": "O que é o escambo?",
                    "options": [
                        {"text": "Troca direta de mercadorias sem uso de dinheiro"},
                        {"text": "Sistema de crédito bancário"},
                        {"text": "Uso de moedas de ouro"},
                        {"text": "Sistema de pagamento digital"}
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Qual era o principal problema do escambo?",
                    "options": [
                        {"text": "Falta de confiança entre as pessoas"},
                        {"text": "Dificuldade de encontrar alguém que quisesse o que você tinha e tivesse o que você queria"},
                        {"text": "Falta de tecnologia"},
                        {"text": "Problemas de transporte"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Por que o escambo era ineficiente?",
                    "options": [
                        {"text": "Era muito caro"},
                        {"text": "Requeria coincidência de desejos entre as partes"},
                        {"text": "Era muito lento"},
                        {"text": "Não era aceito por todos"}
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        "debasement_questionnaire": {
            "title": "Problemas Históricos do Dinheiro - Desvalorização",
            "questions": [
                {
                    "text": "O que é desvalorização (debasement) de moedas?",
                    "options": [
                        {"text": "Redução do valor real de uma moeda através da adição de metais menos valiosos"},
                        {"text": "Aumento do valor de uma moeda"},
                        {"text": "Criação de novas moedas"},
                        {"text": "Destruição de moedas antigas"}
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Qual império foi conhecido por desvalorizar suas moedas?",
                    "options": [
                        {"text": "Império Romano"},
                        {"text": "Império Chinês"},
                        {"text": "Império Egípcio"},
                        {"text": "Império Grego"}
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Qual foi uma consequência da desvalorização das moedas romanas?",
                    "options": [
                        {"text": "Inflação e perda de confiança na moeda"},
                        {"text": "Aumento do comércio"},
                        {"text": "Estabilidade econômica"},
                        {"text": "Crescimento da economia"}
                    ],
                    "correct_answer_index": 0
                }
            ]
        },
        "ouro_caracteristicas_questionnaire": {
            "title": "O Ouro como Reserva de Valor",
            "questions": [
                {
                    "text": "Por que o ouro foi usado como dinheiro por milhares de anos?",
                    "options": [
                        {"text": "É raro, durável, divisível e facilmente transportável"},
                        {"text": "É muito barato"},
                        {"text": "É fácil de falsificar"},
                        {"text": "É controlado pelos governos"}
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Qual característica do ouro o torna ideal como reserva de valor?",
                    "options": [
                        {"text": "Sua escassez natural"},
                        {"text": "Sua abundância"},
                        {"text": "Sua facilidade de produção"},
                        {"text": "Seu baixo valor"}
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "O que acontece quando governos controlam o suprimento de ouro?",
                    "options": [
                        {"text": "Podem manipular o valor e causar inflação"},
                        {"text": "Garantem estabilidade total"},
                        {"text": "Eliminam todos os problemas monetários"},
                        {"text": "Criam moedas mais valiosas"}
                    ],
                    "correct_answer_index": 0
                }
            ]
        },
        "inflacao_causas_questionnaire": {
            "title": "A Inflação Moderna",
            "questions": [
                {
                    "text": "O que é inflação?",
                    "options": [
                        {"text": "Aumento geral dos preços ao longo do tempo"},
                        {"text": "Diminuição dos preços"},
                        {"text": "Estabilidade dos preços"},
                        {"text": "Aumento do valor da moeda"}
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Qual é uma das principais causas da inflação moderna?",
                    "options": [
                        {"text": "Impressão excessiva de dinheiro pelos bancos centrais"},
                        {"text": "Falta de dinheiro em circulação"},
                        {"text": "Aumento da produção"},
                        {"text": "Diminuição da demanda"}
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Como a inflação afeta o poder de compra?",
                    "options": [
                        {"text": "Reduz o poder de compra ao longo do tempo"},
                        {"text": "Aumenta o poder de compra"},
                        {"text": "Mantém o poder de compra constante"},
                        {"text": "Não afeta o poder de compra"}
                    ],
                    "correct_answer_index": 0
                }
            ]
        },
        "bitcoin_caracteristicas_questionnaire": {
            "title": "A Solução do Bitcoin",
            "questions": [
                {
                    "text": "Como o Bitcoin resolve o problema da inflação?",
                    "options": [
                        {"text": "Através de um suprimento limitado e previsível (21 milhões de bitcoins)"},
                        {"text": "Através de impressão ilimitada"},
                        {"text": "Através de controle governamental"},
                        {"text": "Através de bancos centrais"}
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Qual é a principal característica do Bitcoin que o torna descentralizado?",
                    "options": [
                        {"text": "Não é controlado por nenhuma autoridade central"},
                        {"text": "É controlado por bancos"},
                        {"text": "É controlado por governos"},
                        {"text": "É controlado por empresas"}
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Como o Bitcoin resolve o problema da confiança?",
                    "options": [
                        {"text": "Através de criptografia e consenso distribuído"},
                        {"text": "Através de autoridades centrais"},
                        {"text": "Através de bancos"},
                        {"text": "Através de governos"}
                    ],
                    "correct_answer_index": 0
                }
            ]
        }
    }

def populate_quizzes():
    """Popula os quizzes das trilhas no Firestore"""
    try:
        db = firestore.client()
        quizzes_collection = db.collection('quizzes')
        
        quizzes_data = get_learning_path_quizzes()
        
        print(f"📝 Populando {len(quizzes_data)} quizzes das trilhas...")
        
        for quiz_id, quiz_data in quizzes_data.items():
            print(f"  📋 Criando quiz: {quiz_id}")
            
            # Adiciona metadados
            quiz_data['created_at'] = datetime.utcnow()
            quiz_data['updated_at'] = None
            quiz_data['is_active'] = True
            quiz_data['category'] = 'learning_path'
            
            # Salva no Firestore
            quizzes_collection.document(quiz_id).set(quiz_data)
            print(f"    ✅ Quiz {quiz_id} criado com sucesso!")
        
        print(f"🎉 Todos os {len(quizzes_data)} quizzes foram populados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao popular quizzes: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("🚀 Iniciando população de quizzes das trilhas de aprendizado...")
    
    try:
        _configure_credentials()
        initialize_firebase()
        populate_quizzes()
        
        print("✅ Processo concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
