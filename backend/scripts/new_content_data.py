"""
Dados de novos quizzes, learning paths e missões para o CryptoQuest.
Este arquivo contém apenas os dados estruturados.
"""

# ============================================================
# NOVOS QUIZZES (35 quizzes)
# ============================================================

NEW_QUIZZES = [
    # TRILHA 1: Ethereum e Smart Contracts (4 quizzes)
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
        "id": "solidity_basics_quiz",
        "title": "Solidity Básico",
        "questions": [
            {
                "text": "O que é Solidity?",
                "options": [
                    {"text": "Uma criptomoeda"},
                    {"text": "Linguagem de programação para smart contracts"},
                    {"text": "Uma exchange"},
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
                    {"text": "Comentários"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é uma 'view function' em Solidity?",
                "options": [
                    {"text": "Função que altera a blockchain"},
                    {"text": "Função que apenas lê dados"},
                    {"text": "Função privada"},
                    {"text": "Função cara"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    {
        "id": "dapps_development_quiz",
        "title": "Desenvolvimento de DApps",
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
                "text": "Componentes de um DApp típico:",
                "options": [
                    {"text": "Apenas smart contract"},
                    {"text": "Smart contract + frontend + carteira"},
                    {"text": "Apenas frontend"},
                    {"text": "Apenas backend centralizado"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é MetaMask?",
                "options": [
                    {"text": "Uma criptomoeda"},
                    {"text": "Carteira de navegador para interagir com DApps"},
                    {"text": "Uma blockchain"},
                    {"text": "Um smart contract"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Como um DApp armazena dados?",
                "options": [
                    {"text": "Em servidores AWS"},
                    {"text": "Na blockchain ou IPFS"},
                    {"text": "Em bancos de dados SQL"},
                    {"text": "No Google Drive"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    
    # TRILHA 2: DeFi (4 quizzes)
    {
        "id": "defi_intro_quiz",
        "title": "Introdução a DeFi",
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
                "text": "Principal característica do DeFi:",
                "options": [
                    {"text": "Necessita de bancos tradicionais"},
                    {"text": "Serviços financeiros sem intermediários"},
                    {"text": "Apenas para empresas"},
                    {"text": "Requer aprovação governamental"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é yield farming?",
                "options": [
                    {"text": "Minerar Bitcoin"},
                    {"text": "Emprestar cripto para ganhar retornos"},
                    {"text": "Comprar NFTs"},
                    {"text": "Fazer staking"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é TVL (Total Value Locked)?",
                "options": [
                    {"text": "Taxa de validação"},
                    {"text": "Valor total bloqueado em protocolos DeFi"},
                    {"text": "Tipo de token"},
                    {"text": "Transação validada"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    {
        "id": "lending_protocols_quiz",
        "title": "Protocolos de Lending",
        "questions": [
            {
                "text": "O que é lending em DeFi?",
                "options": [
                    {"text": "Vender criptomoedas"},
                    {"text": "Emprestar e tomar emprestado cripto sem banco"},
                    {"text": "Minerar cripto"},
                    {"text": "Comprar NFTs"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é colateral em protocolos de lending?",
                "options": [
                    {"text": "Taxa de juros"},
                    {"text": "Cripto depositada como garantia do empréstimo"},
                    {"text": "Lucro do empréstimo"},
                    {"text": "Tipo de moeda"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Exemplo de protocolo de lending:",
                "options": [
                    {"text": "Bitcoin"},
                    {"text": "Aave ou Compound"},
                    {"text": "Ethereum"},
                    {"text": "MetaMask"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que acontece se o colateral desvalorizar muito?",
                    "options": [
                    {"text": "Nada, é seguro"},
                    {"text": "Liquidação automática do colateral"},
                    {"text": "Você ganha mais tokens"},
                    {"text": "O empréstimo é cancelado"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    {
        "id": "dex_amm_quiz",
        "title": "DEXs e Automated Market Makers",
        "questions": [
            {
                "text": "O que é uma DEX?",
                "options": [
                    {"text": "Decentralized Exchange (exchange descentralizada)"},
                    {"text": "Digital Exchange"},
                    {"text": "Developer Exchange"},
                    {"text": "Data Exchange"}
                ],
                "correct_answer_index": 0
            },
            {
                "text": "Diferença entre DEX e exchange centralizada:",
                "options": [
                    {"text": "DEX é mais lenta"},
                    {"text": "DEX não custodia seus fundos"},
                    {"text": "DEX é mais cara"},
                    {"text": "DEX requer KYC"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é um AMM (Automated Market Maker)?",
                "options": [
                    {"text": "Um trader automático"},
                    {"text": "Sistema que usa pools de liquidez para trocas"},
                    {"text": "Um tipo de carteira"},
                    {"text": "Uma criptomoeda"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Exemplo famoso de DEX:",
                "options": [
                    {"text": "Binance"},
                    {"text": "Uniswap"},
                    {"text": "Coinbase"},
                    {"text": "Kraken"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    {
        "id": "yield_farming_strategies_quiz",
        "title": "Estratégias de Yield Farming",
        "questions": [
            {
                "text": "O que é impermanent loss?",
                "options": [
                    {"text": "Perda garantida de dinheiro"},
                    {"text": "Perda temporária ao fornecer liquidez em pools"},
                    {"text": "Taxa de transação"},
                    {"text": "Lucro temporário"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que são liquidity pools?",
                "options": [
                    {"text": "Piscinas com água"},
                    {"text": "Reservas de tokens para facilitar trocas"},
                    {"text": "Grupos de mineradores"},
                    {"text": "Carteiras compartilhadas"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é APY em yield farming?",
                "options": [
                    {"text": "Annual Percentage Yield (rendimento anual)"},
                    {"text": "Automated Protocol Yield"},
                    {"text": "Annual Pool Yield"},
                    {"text": "Average Price Yearly"}
                ],
                "correct_answer_index": 0
            },
            {
                "text": "Principal risco do yield farming:",
                "options": [
                    {"text": "Ganhar muito dinheiro"},
                    {"text": "Smart contracts com bugs ou hacks"},
                    {"text": "Pagar muitos impostos"},
                    {"text": "Ter que minerar"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    
    # TRILHA 3: NFTs (3 quizzes)
    {
        "id": "nft_basics_quiz",
        "title": "O que são NFTs",
        "questions": [
            {
                "text": "O que significa NFT?",
                "options": [
                    {"text": "New Financial Token"},
                    {"text": "Non-Fungible Token"},
                    {"text": "Network File Transfer"},
                    {"text": "Next Future Technology"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que torna um NFT único?",
                "options": [
                    {"text": "Seu preço alto"},
                    {"text": "Cada NFT tem um ID único na blockchain"},
                    {"text": "Sua aparência"},
                    {"text": "O dono do NFT"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Diferença entre NFT e criptomoeda:",
                "options": [
                    {"text": "NFTs são mais caros"},
                    {"text": "NFTs são únicos, criptomoedas são fungíveis"},
                    {"text": "Não há diferença"},
                    {"text": "NFTs não usam blockchain"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Padrão de token NFT no Ethereum:",
                "options": [
                    {"text": "ERC-20"},
                    {"text": "ERC-721 ou ERC-1155"},
                    {"text": "BEP-20"},
                    {"text": "TRC-20"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    {
        "id": "creating_nfts_quiz",
        "title": "Criando e Vendendo NFTs",
        "questions": [
            {
                "text": "O que é 'minting' de NFT?",
                "options": [
                    {"text": "Vender um NFT"},
                    {"text": "Criar e registrar um NFT na blockchain"},
                    {"text": "Comprar um NFT"},
                    {"text": "Deletar um NFT"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que são 'royalties' em NFTs?",
                "options": [
                    {"text": "Taxa de criação"},
                    {"text": "Porcentagem paga ao criador em cada revenda"},
                    {"text": "Imposto governamental"},
                    {"text": "Taxa de rede"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Onde são armazenadas as imagens dos NFTs?",
                "options": [
                    {"text": "Diretamente na blockchain"},
                    {"text": "IPFS ou servidores descentralizados"},
                    {"text": "No Google Drive"},
                    {"text": "Em bancos de dados SQL"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que determina o valor de um NFT?",
                "options": [
                    {"text": "Apenas o custo de criação"},
                    {"text": "Raridade, demanda e utilidade"},
                    {"text": "O tamanho do arquivo"},
                    {"text": "A blockchain usada"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    {
        "id": "nft_marketplaces_quiz",
        "title": "Marketplaces de NFTs",
        "questions": [
            {
                "text": "Exemplo de marketplace de NFTs:",
                "options": [
                    {"text": "Amazon"},
                    {"text": "OpenSea"},
                    {"text": "eBay"},
                    {"text": "Alibaba"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é uma 'collection' de NFTs?",
                "options": [
                    {"text": "Uma carteira de NFTs"},
                    {"text": "Conjunto de NFTs do mesmo projeto/artista"},
                    {"text": "Tipo de blockchain"},
                    {"text": "Protocolo de venda"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que são 'floor price'?",
                "options": [
                    {"text": "Preço máximo"},
                    {"text": "Menor preço de venda na coleção"},
                    {"text": "Preço médio"},
                    {"text": "Taxa de marketplace"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Qual taxa cobrada por marketplaces?",
                "options": [
                    {"text": "50% do valor"},
                    {"text": "Geralmente 2-5% do valor de venda"},
                    {"text": "Taxa fixa de $100"},
                    {"text": "Não há taxas"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    
    # TRILHA 4: Segurança (4 quizzes)
    {
        "id": "crypto_security_fundamentals_quiz",
        "title": "Fundamentos de Segurança",
        "questions": [
            {
                "text": "Regra principal de segurança em cripto:",
                "options": [
                    {"text": "Compartilhar suas chaves com amigos"},
                    {"text": "Nunca compartilhe sua chave privada/seed phrase"},
                    {"text": "Usar sempre exchanges centralizadas"},
                    {"text": "Manter tudo na mesma carteira"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é autenticação de dois fatores (2FA)?",
                "options": [
                    {"text": "Ter duas carteiras"},
                    {"text": "Segundo fator de verificação além da senha"},
                    {"text": "Duas chaves privadas"},
                    {"text": "Dois tipos de criptomoedas"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Melhor lugar para guardar grandes quantias de cripto:",
                "options": [
                    {"text": "Exchange centralizada"},
                    {"text": "Hardware wallet (carteira fria)"},
                    {"text": "Carteira de celular"},
                    {"text": "Papel com senha"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que fazer se suspeitar que sua carteira foi comprometida?",
                "options": [
                    {"text": "Esperar para ver o que acontece"},
                    {"text": "Transferir fundos imediatamente para nova carteira segura"},
                    {"text": "Deletar o aplicativo"},
                    {"text": "Mudar apenas a senha"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    {
        "id": "wallet_security_quiz",
        "title": "Segurança de Carteiras",
        "questions": [
            {
                "text": "O que é uma 'seed phrase'?",
                "options": [
                    {"text": "Senha da carteira"},
                    {"text": "12-24 palavras que recuperam sua carteira"},
                    {"text": "Código de verificação"},
                    {"text": "Nome de usuário"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Onde guardar sua seed phrase?",
                "options": [
                    {"text": "No celular ou computador"},
                    {"text": "Anotada em papel em local seguro"},
                    {"text": "Em e-mail"},
                    {"text": "Na nuvem"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é uma hardware wallet?",
                "options": [
                    {"text": "Carteira de software"},
                    {"text": "Dispositivo físico que armazena chaves offline"},
                    {"text": "Aplicativo de celular"},
                    {"text": "Site de exchange"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Vantagem das cold wallets:",
                "options": [
                    {"text": "Mais rápidas para transações"},
                    {"text": "Protegidas contra hacks online"},
                    {"text": "Não precisam de seed phrase"},
                    {"text": "São grátis"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    {
        "id": "phishing_scams_quiz",
        "title": "Phishing e Golpes",
        "questions": [
            {
                "text": "O que é phishing?",
                "options": [
                    {"text": "Minerar criptomoedas"},
                    {"text": "Golpe que tenta roubar suas credenciais"},
                    {"text": "Tipo de trading"},
                    {"text": "Protocolo de segurança"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Como identificar um site phishing?",
                "options": [
                    {"text": "Pela cor do site"},
                    {"text": "URL suspeita, erros de digitação, não usa HTTPS"},
                    {"text": "Pelo logo"},
                    {"text": "Não é possível identificar"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que é 'rug pull'?",
                "options": [
                    {"text": "Estratégia de trading"},
                    {"text": "Golpe onde criadores abandonam projeto com dinheiro dos investidores"},
                    {"text": "Tipo de NFT"},
                    {"text": "Protocolo DeFi"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Red flag comum em projetos de cripto:",
                "options": [
                    {"text": "Time doxxado (identificado)"},
                    {"text": "Promessas de retornos garantidos irrealistas"},
                    {"text": "Código open source"},
                    {"text": "Auditoria de segurança"}
                ],
                "correct_answer_index": 1
            }
        ]
    },
    {
        "id": "backup_recovery_quiz",
        "title": "Backup e Recuperação",
        "questions": [
            {
                "text": "Por que fazer backup da seed phrase?",
                "options": [
                    {"text": "Para compartilhar com amigos"},
                    {"text": "Única forma de recuperar carteira se perder acesso"},
                    {"text": "Para aumentar segurança"},
                    {"text": "Não é necessário"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Melhor forma de backup de seed phrase:",
                "options": [
                    {"text": "Screenshot no celular"},
                    {"text": "Papel/metal em cofre ou local muito seguro"},
                    {"text": "Arquivo em nuvem criptografado"},
                    {"text": "Memorizar"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "O que fazer se perder a seed phrase?",
                "options": [
                    {"text": "Entrar em contato com suporte da blockchain"},
                    {"text": "Os fundos são irrecuperáveis"},
                    {"text": "Pagar para recuperar"},
                    {"text": "Esperar alguns dias"}
                ],
                "correct_answer_index": 1
            },
            {
                "text": "Quantas cópias de backup recomendadas:",
                "options": [
                    {"text": "1 apenas"},
                    {"text": "2-3 em locais diferentes e seguros"},
                    {"text": "10 ou mais"},
                    {"text": "Nenhuma"}
                ],
                "correct_answer_index": 1
            }
        ]
    }
]

# Continua nos próximos arquivos devido ao tamanho...


