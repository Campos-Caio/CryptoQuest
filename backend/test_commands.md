# Comandos de Teste do Sistema de IA

## 1. Testar Coleta de Dados

```bash
# Completar uma missão com dados enriquecidos
curl -X POST "http://localhost:8000/learning-paths/{path_id}/missions/{mission_id}/complete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {seu_token}" \
  -d '{
    "answers": [1, 2, 1, 3, 2],
    "time_per_question": [15.5, 12.3, 18.7, 10.2, 14.8],
    "confidence_levels": [0.8, 0.6, 0.9, 0.7, 0.8],
    "hints_used": [0, 1, 0, 0, 1],
    "attempts_per_question": [1, 2, 1, 1, 1]
  }'
```

## 2. Testar Endpoints de IA

```bash
# Perfil de IA
curl -X GET "http://localhost:8000/ai/profile/{user_id}" \
  -H "Authorization: Bearer {seu_token}"

# Recomendações
curl -X GET "http://localhost:8000/ai/recommendations/{user_id}" \
  -H "Authorization: Bearer {seu_token}"

# Insights
curl -X GET "http://localhost:8000/ai/insights/{user_id}" \
  -H "Authorization: Bearer {seu_token}"

# Sugestão de dificuldade
curl -X GET "http://localhost:8000/ai/difficulty-suggestion/{user_id}?domain=bitcoin_basics" \
  -H "Authorization: Bearer {seu_token}"

# Métricas dos modelos
curl -X GET "http://localhost:8000/ai/model-metrics" \
  -H "Authorization: Bearer {seu_token}"
```

## 3. Verificar Dados no Firestore

```bash
# Verificar coleções criadas
- ai_behavioral_data
- ai_knowledge_profiles
- ai_learning_sessions
```

## 4. Cenários de Teste

### Usuário Visual (Respostas Rápidas)
```json
{
  "time_per_question": [8.5, 7.2, 9.1, 6.8, 8.3],
  "confidence_levels": [0.9, 0.8, 0.95, 0.85, 0.9],
  "hints_used": [0, 0, 0, 0, 0],
  "attempts_per_question": [1, 1, 1, 1, 1]
}
```

### Usuário Metódico (Tempo Longo)
```json
{
  "time_per_question": [25.3, 28.7, 22.1, 30.2, 26.8],
  "confidence_levels": [0.6, 0.7, 0.5, 0.8, 0.65],
  "hints_used": [1, 2, 1, 0, 1],
  "attempts_per_question": [2, 3, 2, 1, 2]
}
```

### Usuário Misto
```json
{
  "time_per_question": [15.2, 18.7, 12.3, 20.1, 16.8],
  "confidence_levels": [0.7, 0.8, 0.6, 0.9, 0.75],
  "hints_used": [0, 1, 0, 0, 1],
  "attempts_per_question": [1, 2, 1, 1, 2]
}
```

## 5. O que Esperar

### Resposta de Sucesso
```json
{
  "success": true,
  "score": 85.5,
  "points_earned": 200,
  "xp_earned": 100,
  "ai_insights": {
    "learning_pattern": {
      "type": "visual_learner",
      "strength": 0.85
    },
    "recommendations": [...],
    "difficulty_suggestion": {...},
    "performance_summary": {...}
  },
  "behavioral_data_collected": true,
  "session_id": "user123_quiz456_20240115_103000"
}
```

### Padrões Esperados
- **visual_learner**: Tempo < 15s, confiança > 0.8, poucas dicas
- **methodical_learner**: Tempo > 25s, confiança variável, muitas dicas
- **mixed_learner**: Tempo médio, confiança média, uso moderado de dicas

### Recomendações Esperadas
- Baseadas em gaps de conhecimento identificados
- Score de relevância > 0.6
- Dificuldade adequada ao perfil do usuário
- Conteúdo do domínio com menor proficiência
