from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from app.models.user import FirebaseUser
from app.dependencies.auth import get_current_user
from app.ai.services.ml_engine import get_ml_engine
from app.ai.services.recommendation_engine import get_recommendation_engine
from app.ai.data.behavioral_data_collector import get_behavioral_collector
from app.ai.config import ai_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Services"])


@router.get("/profile/{user_id}", response_model=Dict[str, Any])
async def get_user_ai_profile(
    user_id: str,
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Retorna perfil de IA do usuário com análise de padrões de aprendizado.
    """
    try:
        # Verificar se o usuário pode acessar este perfil
        if current_user.uid != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado ao perfil de outro usuário"
            )
        
        # Buscar dados comportamentais
        behavioral_collector = get_behavioral_collector()
        performance_summary = await behavioral_collector.get_user_performance_summary(user_id)
        
        # Buscar histórico para análise de padrões
        behavioral_history = await behavioral_collector.get_user_behavioral_history(user_id, limit=20)
        
        # Gerar análise de padrões
        ml_engine = get_ml_engine()
        learning_pattern = await ml_engine.analyze_user_patterns(user_id, behavioral_history)
        
        profile = {
            "user_id": user_id,
            "performance_summary": performance_summary,
            "learning_pattern": {
                "type": learning_pattern.pattern_type,
                "strength": learning_pattern.strength,
                "context": learning_pattern.context
            },
            "ai_enabled": ai_config.ai_enabled,
            "data_points": len(behavioral_history)
        }
        
        return {"success": True, "data": profile}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar perfil de IA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar perfil de IA"
        )


@router.get("/recommendations/{user_id}", response_model=List[Dict[str, Any]])
async def get_ai_recommendations(
    user_id: str,
    limit: int = 5,
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Retorna recomendações personalizadas de IA para o usuário.
    """
    try:
        # Verificar permissões
        if current_user.uid != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        # Validar limite
        if limit > ai_config.max_recommendations_per_user:
            limit = ai_config.max_recommendations_per_user
        
        # Gerar recomendações
        recommendation_engine = get_recommendation_engine()
        recommendations = await recommendation_engine.get_recommendations(user_id, limit)
        
        # Converter para formato de resposta
        response_data = [
            {
                "content_id": rec.content_id,
                "content_type": rec.content_type,
                "relevance_score": rec.relevance_score,
                "difficulty_level": rec.difficulty_level.value,
                "estimated_time": rec.estimated_time,
                "reasoning": rec.reasoning,
                "learning_objectives": rec.learning_objectives
            }
            for rec in recommendations
        ]
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar recomendações: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar recomendações"
        )


@router.get("/insights/{user_id}", response_model=Dict[str, Any])
async def get_ai_insights(
    user_id: str,
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Retorna insights de IA sobre o usuário.
    """
    try:
        # Verificar permissões
        if current_user.uid != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        # Buscar dados comportamentais
        behavioral_collector = get_behavioral_collector()
        behavioral_history = await behavioral_collector.get_user_behavioral_history(user_id, limit=50)
        performance_summary = await behavioral_collector.get_user_performance_summary(user_id)
        
        # Gerar insights
        ml_engine = get_ml_engine()
        recommendation_engine = get_recommendation_engine()
        
        # Análise de padrões
        learning_pattern = await ml_engine.analyze_user_patterns(user_id, behavioral_history)
        
        # Recomendações
        recommendations = await recommendation_engine.get_recommendations(user_id, limit=3)
        
        # Métricas dos modelos
        model_metrics = ml_engine.get_model_metrics()
        
        # ✅ CORREÇÃO: Formato compatível com frontend
        insights = {
            "user_id": user_id,
            "ideal_time": _calculate_ideal_time(behavioral_history),
            "avg_response_time": performance_summary.get("avg_response_time", 0.0),
            "focus_area": _calculate_focus_area(performance_summary),
            "learning_pattern": {
                "type": learning_pattern.pattern_type,
                "strength": learning_pattern.strength,
                "frequency": learning_pattern.frequency,
                "context": learning_pattern.context
            },
            "performance_analysis": performance_summary,
            "top_recommendations": [
                {
                    "content_id": rec.content_id,
                    "type": rec.content_type,
                    "relevance_score": rec.relevance_score,
                    "reasoning": rec.reasoning
                }
                for rec in recommendations[:3]
            ],
            "ai_model_status": {
                "learning_style_trained": "learning_style" in model_metrics,
                "difficulty_predictor_trained": "difficulty" in model_metrics,
                "total_models": len(model_metrics)
            },
            "data_quality": {
                "total_sessions": len(behavioral_history),
                "data_sufficiency": "sufficient" if len(behavioral_history) >= 5 else "insufficient",
                "last_activity": behavioral_history[-1]['collected_at'] if behavioral_history else None
            }
        }
        
        return {"success": True, "data": insights}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar insights"
        )


@router.get("/difficulty-suggestion/{user_id}", response_model=Dict[str, Any])
async def get_difficulty_suggestion(
    user_id: str,
    domain: str,
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Retorna sugestão de dificuldade ideal para um domínio específico.
    """
    try:
        # Verificar permissões
        if current_user.uid != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        # Validar domínio
        if domain not in ai_config.knowledge_domains:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Domínio '{domain}' não é válido"
            )
        
        # Buscar dados do usuário
        behavioral_collector = get_behavioral_collector()
        performance_summary = await behavioral_collector.get_user_performance_summary(user_id)
        
        # Gerar predição de dificuldade
        ml_engine = get_ml_engine()
        user_data = {
            "user_level": 2,  # Seria buscado do perfil do usuário
            "domain": domain,
            "domain_proficiency": performance_summary.get("avg_confidence", 0.5),
            "avg_response_time": performance_summary.get("avg_response_time", 30),
            "confidence_level": performance_summary.get("avg_confidence", 0.5)
        }
        
        difficulty_prediction = ml_engine.difficulty_predictor.predict_optimal_difficulty(user_data)
        
        suggestion = {
            "user_id": user_id,
            "domain": domain,
            "optimal_difficulty": difficulty_prediction.value,
            "confidence": difficulty_prediction.confidence,
            "reasoning": difficulty_prediction.reasoning,
            "model_used": difficulty_prediction.model_used,
            "difficulty_level": _map_difficulty_to_level(difficulty_prediction.value)
        }
        
        return {"success": True, "data": suggestion}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar sugestão de dificuldade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar sugestão de dificuldade"
        )


@router.get("/content-suggestions/{user_id}", response_model=List[Dict[str, Any]])
async def get_content_suggestions(
    user_id: str,
    domain: str,
    limit: int = 3,
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Retorna sugestões de conteúdo específicas para um domínio.
    """
    try:
        # Verificar permissões
        if current_user.uid != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        # Validar domínio
        if domain not in ai_config.knowledge_domains:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Domínio '{domain}' não é válido"
            )
        
        # Gerar sugestões
        recommendation_engine = get_recommendation_engine()
        suggestions = await recommendation_engine.get_content_suggestions(user_id, domain, limit)
        
        # Converter para formato de resposta
        response_data = [
            {
                "content_id": sug.content_id,
                "content_type": sug.content_type,
                "relevance_score": sug.relevance_score,
                "difficulty_level": sug.difficulty_level.value,
                "estimated_time": sug.estimated_time,
                "reasoning": sug.reasoning,
                "learning_objectives": sug.learning_objectives
            }
            for sug in suggestions
        ]
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar sugestões de conteúdo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar sugestões"
        )


@router.get("/model-metrics", response_model=Dict[str, Any])
async def get_ai_model_metrics(
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Retorna métricas de performance dos modelos de IA.
    """
    try:
        # Verificar se é admin (implementar lógica de admin)
        # Por enquanto, permitir para todos os usuários autenticados
        
        ml_engine = get_ml_engine()
        model_metrics = ml_engine.get_model_metrics()
        
        # Converter métricas para formato de resposta
        metrics_data = {}
        for model_name, metrics in model_metrics.items():
            metrics_data[model_name] = {
                "accuracy": metrics.accuracy,
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1_score": metrics.f1_score,
                "training_samples": metrics.training_samples,
                "last_trained": metrics.last_trained.isoformat(),
                "version": metrics.version
            }
        
        return {
            "success": True,
            "data": {
                "model_metrics": metrics_data,
                "total_models": len(metrics_data),
                "ai_config": {
                    "enabled": ai_config.ai_enabled,
                    "debug_mode": ai_config.ai_debug_mode,
                    "version": ai_config.ai_version
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar métricas dos modelos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar métricas"
        )


def _map_difficulty_to_level(difficulty: float) -> str:
    """Mapeia dificuldade numérica para nível descritivo"""
    if difficulty <= 0.3:
        return "beginner"
    elif difficulty <= 0.6:
        return "intermediate"
    elif difficulty <= 0.8:
        return "advanced"
    else:
        return "expert"


def _calculate_focus_area(performance_summary: Dict[str, Any]) -> str:
    """Calcula área de foco baseada na menor proficiência do usuário"""
    try:
        # Buscar proficiências dos domínios
        bitcoin_proficiency = performance_summary.get("bitcoin_proficiency", 0.0)
        ethereum_proficiency = performance_summary.get("ethereum_proficiency", 0.0)
        defi_proficiency = performance_summary.get("defi_proficiency", 0.0)
        trading_proficiency = performance_summary.get("trading_proficiency", 0.0)
        security_proficiency = performance_summary.get("security_proficiency", 0.0)
        
        # Mapear domínios e suas proficiências
        domains = {
            "Bitcoin": bitcoin_proficiency,
            "Ethereum": ethereum_proficiency,
            "DeFi": defi_proficiency,
            "Trading": trading_proficiency,
            "Segurança": security_proficiency
        }
        
        # Encontrar domínio com menor proficiência
        min_domain = min(domains.items(), key=lambda x: x[1])
        
        # Se a menor proficiência for muito alta (>80%), sugerir próximo nível
        if min_domain[1] > 0.8:
            # Encontrar segundo menor
            sorted_domains = sorted(domains.items(), key=lambda x: x[1])
            if len(sorted_domains) > 1:
                min_domain = sorted_domains[1]
        
        # Se todas as proficiências são altas, sugerir avançado
        if min_domain[1] > 0.7:
            return f"{min_domain[0]} Avançado"
        elif min_domain[1] > 0.4:
            return f"{min_domain[0]} Intermediário"
        else:
            return f"{min_domain[0]} Básico"
            
    except Exception as e:
        logger.error(f"Erro ao calcular área de foco: {e}")
        return "Bitcoin Básico"  # Fallback


def _calculate_ideal_time(behavioral_history: List[Dict[str, Any]]) -> str:
    """Calcula horário ideal baseado nos padrões de performance do usuário"""
    try:
        if not behavioral_history:
            return "Manhã (9h-11h)"  # Default
        
        # Analisar performance por hora do dia
        performance_by_hour = {}
        
        for session in behavioral_history:
            # Extrair hora do timestamp
            collected_at = session.get('collected_at')
            if isinstance(collected_at, str):
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(collected_at.replace('Z', '+00:00'))
                    hour = dt.hour
                except (ValueError, TypeError):
                    continue
            else:
                continue
            
            # Obter métricas de performance
            performance_metrics = session.get('performance_metrics', {})
            success_rate = performance_metrics.get('success_rate', 0.5)
            avg_response_time = performance_metrics.get('avg_response_time', 30)
            
            # Calcular score de performance (sucesso alto + tempo baixo = melhor)
            performance_score = success_rate * (1.0 - min(avg_response_time / 60.0, 1.0))
            
            if hour not in performance_by_hour:
                performance_by_hour[hour] = []
            performance_by_hour[hour].append(performance_score)
        
        if not performance_by_hour:
            return "Manhã (9h-11h)"  # Default
        
        # Calcular performance média por hora
        avg_performance_by_hour = {
            hour: sum(scores) / len(scores) 
            for hour, scores in performance_by_hour.items()
        }
        
        # Encontrar melhor horário
        best_hour = max(avg_performance_by_hour.items(), key=lambda x: x[1])[0]
        
        # Mapear para períodos do dia
        if 6 <= best_hour < 12:
            return "Manhã (6h-12h)"
        elif 12 <= best_hour < 18:
            return "Tarde (12h-18h)"
        elif 18 <= best_hour < 22:
            return "Noite (18h-22h)"
        else:
            return "Madrugada (22h-6h)"
            
    except Exception as e:
        logger.error(f"Erro ao calcular horário ideal: {e}")
        return "Manhã (9h-11h)"  # Fallback
