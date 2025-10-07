"""
Script para criar os 10 quizzes específicos das trilhas de aprendizado.
Cada quiz é focado no tópico específico do módulo correspondente.
"""

import sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Adicionar o diretório pai ao path para importar os módulos
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

def get_learning_path_quizzes():
    """Retorna os 10 quizzes específicos das trilhas de aprendizado"""
    return [
        # ===== TRILHA: Aprofundando no Bitcoin =====
        
        # Módulo 1: A Blockchain e a Criptografia
        {
            "id": "blockchain_conceitos_questionnaire",
            "title": "A Blockchain e a Criptografia",
            "questions": [
                {
                    "text": "O que é uma blockchain no contexto do Bitcoin?",
                    "options": [
                        {"text": "Um banco de dados centralizado controlado por uma empresa"},
                        {"text": "Um livro-razão distribuído e imutável de transações"},
                        {"text": "Um tipo de carteira digital para armazenar Bitcoin"},
                        {"text": "Uma rede social para usuários de criptomoedas"}
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual é a principal função da criptografia de chaves públicas e privadas no Bitcoin?",
                    "options": [
                        "Aumentar a velocidade das transações",
                        "Garantir a autenticidade e propriedade dos bitcoins",
                        "Reduzir o custo das taxas de transação",
                        "Permitir transações anônimas"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que acontece quando você 'assina' uma transação Bitcoin com sua chave privada?",
                    "options": [
                        "A transação é enviada imediatamente para a rede",
                        "Você prova que é o dono dos bitcoins sem revelar a chave privada",
                        "A transação fica mais barata",
                        "A transação é processada mais rapidamente"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Por que a blockchain é considerada 'imutável'?",
                    "options": [
                        "Porque é controlada por uma autoridade central",
                        "Porque alterar um bloco exigiria recalcular todos os blocos subsequentes",
                        "Porque as transações são criptografadas",
                        "Porque é armazenada em um único servidor"
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        
        # Módulo 2: Mineração e Prova de Trabalho
        {
            "id": "proof_of_work_questionnaire",
            "title": "Mineração e Prova de Trabalho",
            "questions": [
                {
                    "text": "O que é a 'Prova de Trabalho' (Proof of Work) no Bitcoin?",
                    "options": [
                        "Um sistema que prova que você trabalhou para ganhar Bitcoin",
                        "Um mecanismo que exige poder computacional para validar transações",
                        "Um certificado de que você completou um curso sobre Bitcoin",
                        "Uma prova de que você investiu dinheiro em Bitcoin"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual é o principal objetivo da mineração de Bitcoin?",
                    "options": [
                        "Ganhar dinheiro facilmente",
                        "Validar transações e manter a segurança da rede",
                        "Consumir energia elétrica",
                        "Criar novos tipos de criptomoedas"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que é um 'hash' no contexto da mineração Bitcoin?",
                    "options": [
                        "Uma função matemática que gera um resultado único e fixo",
                        "Um tipo de carteira digital",
                        "Uma taxa paga aos mineradores",
                        "Um bloco de transações"
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Por que a dificuldade de mineração do Bitcoin ajusta automaticamente?",
                    "options": [
                        "Para aumentar os lucros dos mineradores",
                        "Para manter o tempo médio de criação de blocos em 10 minutos",
                        "Para reduzir o consumo de energia",
                        "Para permitir que mais pessoas minerem"
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        
        # Módulo 3: Anatomia de uma Transação
        {
            "id": "utxo_questionnaire",
            "title": "Anatomia de uma Transação",
            "questions": [
                {
                    "text": "O que significa UTXO no contexto do Bitcoin?",
                    "options": [
                        "Unified Transaction Output - Saída de Transação Unificada",
                        "Unspent Transaction Output - Saída de Transação Não Gasta",
                        "Universal Transaction Order - Ordem Universal de Transações",
                        "User Transaction Operation - Operação de Transação do Usuário"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Como funciona o modelo UTXO do Bitcoin?",
                    "options": [
                        "Cada transação consome UTXOs existentes e cria novos UTXOs",
                        "UTXOs são criados apenas quando você compra Bitcoin",
                        "UTXOs são destruídos quando você vende Bitcoin",
                        "UTXOs são transferidos diretamente entre usuários"
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "O que são as 'taxas de rede' (network fees) no Bitcoin?",
                    "options": [
                        "Taxas pagas ao governo para usar Bitcoin",
                        "Incentivos pagos aos mineradores para incluir sua transação em um bloco",
                        "Taxas de conversão entre Bitcoin e outras moedas",
                        "Custos de manutenção da carteira digital"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Por que uma transação Bitcoin pode ter múltiplas entradas e saídas?",
                    "options": [
                        "Para aumentar a segurança da transação",
                        "Para combinar múltiplos UTXOs e enviar para múltiplos destinatários",
                        "Para reduzir o custo das taxas",
                        "Para acelerar o processamento"
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        
        # Módulo 4: Carteiras e a Guarda das Chaves
        {
            "id": "chaves_privadas_questionnaire",
            "title": "Carteiras e a Guarda das Chaves",
            "questions": [
                {
                    "text": "O que é uma 'chave privada' no Bitcoin?",
                    "options": [
                        "Uma senha para acessar sua conta em uma exchange",
                        "Um número secreto que prova sua propriedade sobre bitcoins",
                        "Uma chave física para abrir uma carteira de hardware",
                        "Um código de verificação enviado por SMS"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual é a principal diferença entre carteiras 'hot' e 'cold'?",
                    "options": [
                        "Carteiras hot são mais caras que carteiras cold",
                        "Carteiras hot estão conectadas à internet, carteiras cold não",
                        "Carteiras hot armazenam mais Bitcoin que carteiras cold",
                        "Carteiras hot são mais fáceis de usar que carteiras cold"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que acontece se você perder sua chave privada?",
                    "options": [
                        "Você pode recuperar seus bitcoins através do suporte técnico",
                        "Seus bitcoins ficam permanentemente inacessíveis",
                        "Você pode criar uma nova chave privada para acessar os mesmos bitcoins",
                        "O governo pode ajudar a recuperar seus bitcoins"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que é uma 'seed phrase' (frase semente) em uma carteira Bitcoin?",
                    "options": [
                        "Uma senha complexa para proteger a carteira",
                        "Uma sequência de palavras que pode regenerar suas chaves privadas",
                        "Um código de backup fornecido pela exchange",
                        "Uma mensagem de boas-vindas da carteira"
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        
        # Módulo 5: A Rede Bitcoin e os Nós (Nodes)
        {
            "id": "nodes_descentralizacao_questionnaire",
            "title": "A Rede Bitcoin e os Nós (Nodes)",
            "questions": [
                {
                    "text": "O que é um 'nó' (node) na rede Bitcoin?",
                    "options": [
                        "Um computador que minera Bitcoin",
                        "Um computador que mantém uma cópia completa da blockchain",
                        "Um servidor central que controla a rede",
                        "Uma carteira digital para armazenar Bitcoin"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Por que a descentralização é importante para o Bitcoin?",
                    "options": [
                        "Para reduzir o custo das transações",
                        "Para evitar que uma única entidade controle a rede",
                        "Para aumentar a velocidade das transações",
                        "Para facilitar a regulamentação governamental"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que acontece quando um nó recebe uma nova transação?",
                    "options": [
                        "A transação é processada imediatamente",
                        "O nó valida a transação e a propaga para outros nós",
                        "O nó cobra uma taxa para processar a transação",
                        "A transação é armazenada apenas localmente"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual é a diferença entre um 'full node' e um 'light node'?",
                    "options": [
                        "Full nodes são mais caros que light nodes",
                        "Full nodes mantêm a blockchain completa, light nodes não",
                        "Light nodes são mais seguros que full nodes",
                        "Full nodes são mais rápidos que light nodes"
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        
        # ===== TRILHA: Bitcoin no Ecossistema Financeiro =====
        
        # Módulo 1: A Lightning Network
        {
            "id": "lightning_network_questionnaire",
            "title": "A Lightning Network",
            "questions": [
                {
                    "text": "O que é a Lightning Network?",
                    "options": [
                        "Uma rede de mineradores Bitcoin",
                        "Uma solução de segunda camada para transações Bitcoin rápidas e baratas",
                        "Uma nova criptomoeda baseada no Bitcoin",
                        "Um tipo de carteira Bitcoin"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual é o principal problema que a Lightning Network resolve?",
                    "options": [
                        "A volatilidade do preço do Bitcoin",
                        "A lentidão e alto custo das transações Bitcoin na rede principal",
                        "A falta de privacidade nas transações Bitcoin",
                        "A dificuldade de mineração do Bitcoin"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Como funcionam os 'canais de pagamento' na Lightning Network?",
                    "options": [
                        "São conexões diretas entre dois usuários para transações instantâneas",
                        "São canais de comunicação entre exchanges",
                        "São rotas de mineração mais eficientes",
                        "São tipos especiais de carteiras Bitcoin"
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Por que a Lightning Network é considerada uma 'segunda camada'?",
                    "options": [
                        "Porque funciona sobre a blockchain principal do Bitcoin",
                        "Porque é mais segura que a rede principal",
                        "Porque é controlada por uma empresa diferente",
                        "Porque usa uma criptografia diferente"
                    ],
                    "correct_answer_index": 0
                }
            ]
        },
        
        # Módulo 2: Segurança e Soberania Pessoal
        {
            "id": "autocustodia_multisig_questionnaire",
            "title": "Segurança e Soberania Pessoal",
            "questions": [
                {
                    "text": "O que significa 'auto-custódia' (self-custody) no contexto do Bitcoin?",
                    "options": [
                        "Guardar Bitcoin em uma carteira física",
                        "Manter controle total sobre suas chaves privadas",
                        "Usar apenas carteiras gratuitas",
                        "Mineração de Bitcoin em casa"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que é uma carteira 'multisig' (multi-signature)?",
                    "options": [
                        "Uma carteira que aceita múltiplas criptomoedas",
                        "Uma carteira que requer múltiplas assinaturas para autorizar transações",
                        "Uma carteira com múltiplas senhas",
                        "Uma carteira que pode ser usada por múltiplas pessoas"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Por que hardware wallets são consideradas mais seguras?",
                    "options": [
                        "Porque são mais caras",
                        "Porque mantêm as chaves privadas offline, isoladas de malware",
                        "Porque são mais difíceis de usar",
                        "Porque são feitas de metal"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual é o principal risco de manter Bitcoin em exchanges?",
                    "options": [
                        "As exchanges podem ser hackeadas ou falir",
                        "As exchanges cobram taxas muito altas",
                        "As exchanges são mais lentas para processar transações",
                        "As exchanges não aceitam todos os tipos de Bitcoin"
                    ],
                    "correct_answer_index": 0
                }
            ]
        },
        
        # Módulo 3: Bitcoin como Ativo de Investimento
        {
            "id": "ciclos_mercado_questionnaire",
            "title": "Bitcoin como Ativo de Investimento",
            "questions": [
                {
                    "text": "O que são os 'ciclos de mercado' do Bitcoin?",
                    "options": [
                        "Períodos de alta e baixa volatilidade que se repetem ao longo do tempo",
                        "Dias da semana em que o Bitcoin sobe ou desce",
                        "Horários específicos para comprar e vender Bitcoin",
                        "Regras governamentais sobre Bitcoin que mudam periodicamente"
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Por que o Bitcoin é frequentemente chamado de 'ouro digital'?",
                    "options": [
                        "Porque tem a mesma cor dourada do ouro",
                        "Porque é escasso, durável e serve como reserva de valor",
                        "Porque é extraído da terra como o ouro",
                        "Porque é aceito em joalherias"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que é o 'halving' do Bitcoin e como afeta o preço?",
                    "options": [
                        "É quando o preço do Bitcoin cai pela metade",
                        "É a redução pela metade da recompensa de mineração, reduzindo a oferta",
                        "É quando metade dos bitcoins são destruídos",
                        "É um evento que acontece quando o Bitcoin perde 50% do valor"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Por que o Bitcoin é considerado uma proteção contra inflação?",
                    "options": [
                        "Porque seu preço sempre sobe",
                        "Porque sua oferta é limitada e não pode ser inflacionada por governos",
                        "Porque é aceito em todos os países",
                        "Porque é mais estável que o dólar"
                    ],
                    "correct_answer_index": 1
                }
            ]
        },
        
        # Módulo 4: Regulação e Adoção Global
        {
            "id": "regulacao_adocao_questionnaire",
            "title": "Regulação e Adoção Global",
            "questions": [
                {
                    "text": "Como diferentes países têm abordado a regulação do Bitcoin?",
                    "options": [
                        "Todos os países proibiram o Bitcoin",
                        "Cada país tem sua própria abordagem, desde aceitação total até proibição",
                        "Todos os países legalizaram o Bitcoin completamente",
                        "Apenas os Estados Unidos regulamentaram o Bitcoin"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "O que significa 'El Salvador' ter adotado o Bitcoin como moeda legal?",
                    "options": [
                        "O Bitcoin substituiu completamente o dólar americano",
                        "O Bitcoin pode ser usado para pagar impostos e dívidas governamentais",
                        "Apenas turistas podem usar Bitcoin em El Salvador",
                        "O Bitcoin é aceito apenas em algumas lojas"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Por que alguns governos são cautelosos com o Bitcoin?",
                    "options": [
                        "Porque é muito caro de usar",
                        "Porque pode desafiar o controle monetário tradicional e ser usado para atividades ilegais",
                        "Porque é muito lento para transações",
                        "Porque consome muita energia"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Como a adoção institucional do Bitcoin tem evoluído?",
                    "options": [
                        "Empresas e fundos têm aumentado suas reservas em Bitcoin",
                        "Apenas pequenas empresas adotaram o Bitcoin",
                        "Nenhuma empresa grande investiu em Bitcoin",
                        "Apenas bancos centrais compram Bitcoin"
                    ],
                    "correct_answer_index": 0
                }
            ]
        },
        
        # Módulo 5: Altcoins e o Debate do Ecossistema
        {
            "id": "comparativo_cripto_questionnaire",
            "title": "Altcoins e o Debate do Ecossistema",
            "questions": [
                {
                    "text": "O que são 'altcoins'?",
                    "options": [
                        "Versões mais baratas do Bitcoin",
                        "Todas as criptomoedas que não são Bitcoin",
                        "Bitcoins que valem menos de $1",
                        "Criptomoedas criadas apenas para especulação"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Qual é a principal diferença entre Bitcoin e Ethereum?",
                    "options": [
                        "Bitcoin é mais caro que Ethereum",
                        "Bitcoin foca em dinheiro digital, Ethereum foca em contratos inteligentes",
                        "Bitcoin é mais rápido que Ethereum",
                        "Bitcoin é mais seguro que Ethereum"
                    ],
                    "correct_answer_index": 1
                },
                {
                    "text": "Por que o Bitcoin é considerado o 'rei das criptomoedas'?",
                    "options": [
                        "Porque foi a primeira criptomoeda e tem a maior capitalização de mercado",
                        "Porque é a mais rápida",
                        "Porque é a mais barata",
                        "Porque é a mais fácil de usar"
                    ],
                    "correct_answer_index": 0
                },
                {
                    "text": "Qual é o principal argumento dos defensores do Bitcoin contra altcoins?",
                    "options": [
                        "Altcoins são mais caras",
                        "Bitcoin tem a maior segurança, descentralização e adoção",
                        "Altcoins são mais lentas",
                        "Altcoins são mais difíceis de usar"
                    ],
                    "correct_answer_index": 1
                }
            ]
        }
    ]

def create_learning_path_quizzes():
    """Cria os quizzes das trilhas no Firestore"""
    try:
        db = firestore.client()
        quizzes_collection = db.collection('quizzes')
        
        quizzes_data = get_learning_path_quizzes()
        
        print(f"📝 Criando {len(quizzes_data)} quizzes das trilhas de aprendizado...")
        
        for quiz_data in quizzes_data:
            quiz_id = quiz_data['id']
            print(f"  📚 Criando quiz: {quiz_id}")
            
            try:
                # Preparar dados para Firestore (remover id do payload)
                firestore_data = quiz_data.copy()
                firestore_data.pop('id', None)
                
                # Salvar no Firestore
                quizzes_collection.document(quiz_id).set(firestore_data)
                print(f"    ✅ Quiz '{quiz_id}' criado com sucesso!")
                print(f"    📊 Perguntas: {len(quiz_data['questions'])}")
                print(f"    🎯 Título: {quiz_data['title']}")
                
            except Exception as e:
                print(f"    ❌ Erro ao criar quiz '{quiz_id}': {e}")
                continue
        
        print(f"🎉 Processo de criação concluído!")
        print(f"📈 Total de quizzes criados: {len(quizzes_data)}")
        
    except Exception as e:
        print(f"❌ Erro ao criar quizzes: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("🚀 Iniciando criação dos quizzes das trilhas de aprendizado...")
    
    try:
        _configure_credentials()
        initialize_firebase()
        create_learning_path_quizzes()
        
        print("✅ Processo concluído com sucesso!")
        print("\n📋 Quizzes criados:")
        print("🔹 Aprofundando no Bitcoin:")
        print("  - blockchain_conceitos_questionnaire")
        print("  - proof_of_work_questionnaire")
        print("  - utxo_questionnaire")
        print("  - chaves_privadas_questionnaire")
        print("  - nodes_descentralizacao_questionnaire")
        print("🔹 Bitcoin no Ecossistema Financeiro:")
        print("  - lightning_network_questionnaire")
        print("  - autocustodia_multisig_questionnaire")
        print("  - ciclos_mercado_questionnaire")
        print("  - regulacao_adocao_questionnaire")
        print("  - comparativo_cripto_questionnaire")
        
        print("\n🎯 Próximos passos:")
        print("1. ✅ Quizzes das trilhas criados")
        print("2. ✅ Trilhas de aprendizado criadas")
        print("3. ✅ Sistema de questionário integrado")
        print("4. 🧪 Testar fluxo completo")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
