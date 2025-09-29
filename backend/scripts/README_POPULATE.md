# 🚀 Guia para Popular o Banco de Dados - CryptoQuest

Este guia explica como popular o banco de dados Firestore com missões e quizzes para testar o sistema de missões diárias.

## 📋 Pré-requisitos

1. **Firebase configurado**: Certifique-se de que o arquivo `firebase_key.json` está na pasta `backend/`
2. **Python 3.8+**: Com as dependências instaladas
3. **Acesso ao Firestore**: Credenciais configuradas corretamente

## 🗂️ Estrutura dos Arquivos

```
backend/scripts/
├── seed_expanded.json          # Dados expandidos para popular o banco
├── populate_missions.py        # Script principal para popular o banco
├── seed_firestore.py          # Script alternativo (mais simples)
└── README_POPULATE.md         # Este arquivo
```

## 📊 Estrutura dos Dados

### Quizzes
```json
{
  "quiz_id": {
    "title": "Título do Quiz",
    "questions": [
      {
        "text": "Pergunta?",
        "options": [
          {"text": "Opção 1"},
          {"text": "Opção 2"},
          {"text": "Opção 3"}
        ],
        "correct_answer_index": 0
      }
    ]
  }
}
```

### Missões
```json
{
  "mission_id": {
    "title": "Título da Missão",
    "description": "Descrição da missão",
    "type": "QUIZ",  // QUIZ, ARTICLE_READ, CHALLENGE
    "reward_points": 50,
    "required_level": 1,
    "content_id": "quiz_id"  // Referência ao quiz
  }
}
```

## 🛠️ Como Usar

### 1. Validar os Dados (Recomendado)

Primeiro, valide se os dados estão corretos:

```bash
cd backend/scripts
python populate_missions.py --validate-only
```

### 2. Popular o Banco (Adicionar aos Existentes)

Para adicionar novos dados sem apagar os existentes:

```bash
cd backend/scripts
python populate_missions.py
```

### 3. Popular o Banco (Limpar e Recriar)

Para limpar as coleções existentes e recriar tudo:

```bash
cd backend/scripts
python populate_missions.py --clear-existing
```

### 4. Usar Arquivo Personalizado

Para usar um arquivo de dados diferente:

```bash
cd backend/scripts
python populate_missions.py --seed-file meu_arquivo.json
```

## 📝 Dados Incluídos no seed_expanded.json

### Quizzes (5 quizzes)
- **btc_quiz_01**: Fundamentos do Bitcoin (2 perguntas)
- **btc_quiz_02**: Mineração e Consenso (2 perguntas)
- **eth_quiz_01**: Introdução ao Ethereum (2 perguntas)
- **defi_quiz_01**: DeFi - Finanças Descentralizadas (2 perguntas)
- **wallet_quiz_01**: Carteiras Digitais (2 perguntas)

### Missões (8 missões)
- **quiz_btc_basico_1**: Quiz básico Bitcoin (nível 1, 50 pontos)
- **quiz_btc_mineracao_1**: Quiz mineração (nível 2, 75 pontos)
- **quiz_eth_intro_1**: Quiz Ethereum (nível 2, 60 pontos)
- **quiz_defi_basico_1**: Quiz DeFi (nível 3, 80 pontos)
- **quiz_wallet_seguranca_1**: Quiz carteiras (nível 2, 70 pontos)
- **leitura_wallets_1**: Leitura sobre carteiras (nível 3, 30 pontos)
- **leitura_defi_1**: Leitura sobre DeFi (nível 4, 40 pontos)
- **desafio_btc_1**: Desafio cálculo (nível 5, 100 pontos)

## 🔍 Como o Sistema Funciona

### Seleção de Missões Diárias
1. O sistema busca todas as missões da coleção `missions`
2. Filtra por:
   - Nível do usuário (missão.required_level <= user.level)
   - Missões não completadas hoje
3. Seleciona até 3 missões aleatoriamente
4. Salva no perfil do usuário como `daily_missions`

### Tipos de Missão
- **QUIZ**: Usuário responde perguntas (precisa acertar 70%+)
- **ARTICLE_READ**: Usuário lê um artigo (implementação futura)
- **CHALLENGE**: Desafio específico (implementação futura)

## 🧪 Como Testar

### 1. Iniciar o Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Iniciar o Frontend
```bash
cd frontend/cryptoquest
flutter run
```

### 3. Testar o Fluxo
1. Faça login no app
2. Vá para a página inicial
3. Clique no card "Missão Diária"
4. Verifique se as missões aparecem
5. Clique em uma missão para fazer o quiz
6. Responda as perguntas e submeta
7. Verifique se recebeu os pontos

### 4. Verificar no Firestore
- Coleção `users`: Verifique se o usuário tem `daily_missions` e `completed_missions`
- Coleção `missions`: Verifique se as missões foram criadas
- Coleção `quizzes`: Verifique se os quizzes foram criados

## 🐛 Solução de Problemas

### Erro: "Firebase não inicializado"
- Verifique se o arquivo `firebase_key.json` existe
- Verifique se as credenciais estão corretas

### Erro: "Coleção não encontrada"
- Execute o script com `--clear-existing` para recriar as coleções

### Erro: "Validação falhou"
- Verifique a estrutura do JSON
- Certifique-se de que todos os campos obrigatórios estão presentes

### Missões não aparecem
- Verifique se o usuário tem nível suficiente
- Verifique se as missões não foram completadas hoje
- Verifique os logs do backend

## 📈 Próximos Passos

1. **Adicionar mais conteúdo**: Crie mais quizzes e missões
2. **Implementar outros tipos**: ARTICLE_READ e CHALLENGE
3. **Sistema de ranking**: Baseado nos pontos dos usuários
4. **Histórico de missões**: Mostrar missões completadas
5. **Streak diário**: Recompensas por completar missões consecutivas

## 🔧 Personalização

Para adicionar seus próprios dados:

1. Copie o arquivo `seed_expanded.json`
2. Modifique os dados conforme necessário
3. Execute o script com seu arquivo personalizado
4. Teste o sistema

### Exemplo de Quiz Personalizado
```json
{
  "meu_quiz": {
    "title": "Meu Quiz Personalizado",
    "questions": [
      {
        "text": "Sua pergunta aqui?",
        "options": [
          {"text": "Resposta A"},
          {"text": "Resposta B"},
          {"text": "Resposta C"}
        ],
        "correct_answer_index": 1
      }
    ]
  }
}
```

### Exemplo de Missão Personalizada
```json
{
  "minha_missao": {
    "title": "Minha Missão",
    "description": "Descrição da minha missão",
    "type": "QUIZ",
    "reward_points": 100,
    "required_level": 1,
    "content_id": "meu_quiz"
  }
}
```
