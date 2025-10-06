#!/usr/bin/env python3
"""
Script para testar o endpoint de IA com dados enriquecidos.
"""
import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
USER_ID = "test_user_ai_123"

def test_ai_endpoint():
    """Testa o endpoint de IA com dados enriquecidos"""
    
    # Dados de submissão enriquecidos
    enhanced_submission = {
        "answers": [1, 2, 1, 3, 2],
        "time_per_question": [15.5, 12.3, 18.7, 10.2, 14.8],
        "confidence_levels": [0.8, 0.6, 0.9, 0.7, 0.8],
        "hints_used": [0, 1, 0, 0, 1],
        "attempts_per_question": [1, 2, 1, 1, 1],
        "session_metadata": {
            "device_type": "desktop",
            "browser": "chrome",
            "session_duration": 300
        },
        "device_info": {
            "os": "Windows",
            "version": "11",
            "screen_resolution": "1920x1080"
        }
    }
    
    print("🧠 TESTANDO ENDPOINT DE IA COM DADOS ENRIQUECIDOS")
    print("=" * 60)
    
    # Testar completar missão com IA
    url = f"{BASE_URL}/learning-paths/bitcoin_ecossistema_financeiro/missions/missao_comparativo_cripto/complete"
    
    try:
        response = requests.post(
            url,
            json=enhanced_submission,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Missão completada com sucesso!")
            print(f"📊 Score: {result.get('score', 'N/A')}")
            print(f"🎯 Success: {result.get('success', 'N/A')}")
            print(f"💰 Points: {result.get('points_earned', 'N/A')}")
            print(f"⭐ XP: {result.get('xp_earned', 'N/A')}")
            
            # Verificar se há dados de IA
            if "ai_insights" in result:
                print("\n🤖 DADOS DE IA COLETADOS:")
                ai_insights = result["ai_insights"]
                
                if "learning_pattern" in ai_insights:
                    pattern = ai_insights["learning_pattern"]
                    print(f"   📈 Padrão: {pattern.get('type', 'N/A')}")
                    print(f"   💪 Força: {pattern.get('strength', 'N/A')}")
                
                if "recommendations" in ai_insights:
                    recommendations = ai_insights["recommendations"]
                    print(f"   🎯 Recomendações: {len(recommendations)}")
                    for i, rec in enumerate(recommendations[:3]):
                        print(f"      {i+1}. {rec.get('content_id', 'N/A')} (Score: {rec.get('relevance_score', 'N/A')})")
                
                if "difficulty_suggestion" in ai_insights:
                    difficulty = ai_insights["difficulty_suggestion"]
                    print(f"   🎚️ Dificuldade sugerida: {difficulty.get('optimal_difficulty', 'N/A')}")
                    print(f"   🎯 Confiança: {difficulty.get('confidence', 'N/A')}")
                
                if "performance_summary" in ai_insights:
                    performance = ai_insights["performance_summary"]
                    print(f"   📊 Engajamento: {performance.get('engagement_score', 'N/A')}")
                    print(f"   ⏱️ Tempo médio: {performance.get('avg_response_time', 'N/A')}s")
                
                print(f"   🆔 Session ID: {result.get('session_id', 'N/A')}")
                print(f"   📊 Dados coletados: {result.get('behavioral_data_collected', 'N/A')}")
            else:
                print("❌ Nenhum dado de IA encontrado na resposta")
                
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def test_ai_apis():
    """Testa os endpoints de IA"""
    
    print("\n🌐 TESTANDO ENDPOINTS DE IA")
    print("=" * 60)
    
    endpoints = [
        f"/ai/profile/{USER_ID}",
        f"/ai/recommendations/{USER_ID}?limit=3",
        f"/ai/insights/{USER_ID}",
        f"/ai/difficulty-suggestion/{USER_ID}?domain=bitcoin_basics",
        f"/ai/content-suggestions/{USER_ID}?domain=defi&limit=2",
        "/ai/model-metrics"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url)
            
            print(f"📡 {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "success" in data:
                    print(f"   ✅ Success: {data['success']}")
                elif isinstance(data, list):
                    print(f"   📊 Items: {len(data)}")
                else:
                    print(f"   📄 Response: {str(data)[:100]}...")
            else:
                print(f"   ❌ Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print()

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE IA")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Testar endpoint principal
    test_ai_endpoint()
    
    # Testar APIs de IA
    test_ai_apis()
    
    print("🏁 TESTES CONCLUÍDOS")
