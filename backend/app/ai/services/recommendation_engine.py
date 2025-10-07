"""
Engine de recomendação inteligente para personalização de conteúdo.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, UTC
import numpy as np

from app.ai.models.ai_models import (
    ContentRecommendation, KnowledgeGap, UserKnowledgeProfile,
    LearningPattern, DifficultyLevel
)
from app.ai.config import ai_config, get_domain_content, get_domain_difficulty
from app.core.logging_config import get_cryptoquest_logger, LogCategory

logger = logging.getLogger(__name__)
cryptoquest_logger = get_cryptoquest_logger()


class BasicRecommendationEngine:
    """Engine básico de recomendações personalizadas"""
    
    def __init__(self):
        self.content_database = self._initialize_content_database()
        self.recommendation_cache = {}
        
        cryptoquest_logger.log_system_event("recommendation_engine_initialized")
    
    def _initialize_content_database(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa banco de dados de conteúdo"""
        return {
            # Conteúdo de Bitcoin
            "bitcoin_fundamentals_quiz": {
                "id": "bitcoin_fundamentals_quiz",
                "type": "quiz",
                "domain": "bitcoin_basics",
                "difficulty": 0.3,
                "estimated_time": 15,
                "prerequisites": [],
                "learning_objectives": ["Entender conceitos básicos do Bitcoin", "Conhecer história da criptomoeda"]
            },
            "bitcoin_history_lesson": {
                "id": "bitcoin_history_lesson",
                "type": "lesson",
                "domain": "bitcoin_basics",
                "difficulty": 0.2,
                "estimated_time": 20,
                "prerequisites": [],
                "learning_objectives": ["Conhecer a história do Bitcoin", "Entender o whitepaper original"]
            },
            
            # Conteúdo de Blockchain
            "blockchain_101_quiz": {
                "id": "blockchain_101_quiz",
                "type": "quiz",
                "domain": "blockchain_technology",
                "difficulty": 0.4,
                "estimated_time": 20,
                "prerequisites": ["bitcoin_fundamentals_quiz"],
                "learning_objectives": ["Entender conceitos de blockchain", "Conhecer tipos de consenso"]
            },
            "consensus_mechanisms_lesson": {
                "id": "consensus_mechanisms_lesson",
                "type": "lesson",
                "domain": "blockchain_technology",
                "difficulty": 0.5,
                "estimated_time": 25,
                "prerequisites": ["blockchain_101_quiz"],
                "learning_objectives": ["Conhecer PoW, PoS e outros consensos", "Entender segurança de redes"]
            },
            
            # Conteúdo de DeFi
            "defi_overview_quiz": {
                "id": "defi_overview_quiz",
                "type": "quiz",
                "domain": "defi",
                "difficulty": 0.6,
                "estimated_time": 20,
                "prerequisites": ["blockchain_101_quiz"],
                "learning_objectives": ["Entender conceitos de DeFi", "Conhecer principais protocolos"]
            },
            "liquidity_pools_lesson": {
                "id": "liquidity_pools_lesson",
                "type": "lesson",
                "domain": "defi",
                "difficulty": 0.7,
                "estimated_time": 30,
                "prerequisites": ["defi_overview_quiz"],
                "learning_objectives": ["Entender AMMs", "Conhecer impermanent loss"]
            },
            
            # Conteúdo de Trading
            "trading_basics_quiz": {
                "id": "trading_basics_quiz",
                "type": "quiz",
                "domain": "crypto_trading",
                "difficulty": 0.5,
                "estimated_time": 15,
                "prerequisites": ["bitcoin_fundamentals_quiz"],
                "learning_objectives": ["Conhecer conceitos básicos de trading", "Entender análise técnica"]
            },
            "market_analysis_lesson": {
                "id": "market_analysis_lesson",
                "type": "lesson",
                "domain": "crypto_trading",
                "difficulty": 0.6,
                "estimated_time": 25,
                "prerequisites": ["trading_basics_quiz"],
                "learning_objectives": ["Análise técnica e fundamentalista", "Gestão de risco"]
            }
        }
    
    async def _get_user_profile_from_firestore(self, user_id: str) -> Dict[str, Any]:
        """Busca perfil real do usuário do Firestore"""
        try:
            from app.core.firebase import get_firestore_db_async
            db = await get_firestore_db_async()
            
            # Buscar perfil de conhecimento
            profile_ref = db.collection("ai_knowledge_profiles").document(user_id)
            profile_doc = await profile_ref.get()
            
            if profile_doc.exists:
                profile_data = profile_doc.to_dict()
                return {
                    "user_id": user_id,
                    "domains": profile_data.get("domains", {}),
                    "learning_style": profile_data.get("learning_style", "mixed"),
                    "engagement_score": profile_data.get("engagement_score", 0.5),
                    "data_points": profile_data.get("total_questions", 0)
                }
            else:
                # Perfil não existe - retornar perfil padrão
                return {
                    "user_id": user_id,
                    "domains": {},
                    "learning_style": "mixed",
                    "engagement_score": 0.5,
                    "data_points": 0
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar perfil do usuário: {e}")
            # Retornar perfil padrão em caso de erro
            return {
                "user_id": user_id,
                "domains": {},
                "learning_style": "mixed",
                "engagement_score": 0.5,
                "data_points": 0
            }
    
    async def get_recommendations(self, user_id: str, limit: int = 5) -> List[ContentRecommendation]:
        """Gera recomendações personalizadas para o usuário"""
        try:
            # Verificar cache
            cache_key = f"recommendations_{user_id}"
            if cache_key in self.recommendation_cache:
                cached_time = self.recommendation_cache[cache_key].get('timestamp', 0)
                if datetime.now(UTC).timestamp() - cached_time < 900:  # 15 minutos
                    return self.recommendation_cache[cache_key]['recommendations']
            
            # ✅ CORREÇÃO: Buscar perfil real do usuário do Firestore
            user_profile = await self._get_user_profile_from_firestore(user_id)
            
            # Identificar gaps de conhecimento
            knowledge_gaps = self._identify_knowledge_gaps(user_profile)
            
            # Gerar recomendações
            recommendations = []
            
            # ✅ ESTRATÉGIA 1: Recomendar conteúdo para gaps prioritários
            for gap in knowledge_gaps[:limit]:
                content_items = self._find_content_for_gap(gap)
                
                for content_item in content_items:
                    if len(recommendations) >= limit:
                        break
                    
                    # Calcular score de relevância
                    relevance_score = self._calculate_relevance_score(
                        content_item, gap, user_profile
                    )
                    
                    if relevance_score >= ai_config.recommendation_confidence_threshold:
                        recommendation = ContentRecommendation(
                            content_id=content_item['id'],
                            content_type=content_item['type'],
                            relevance_score=relevance_score,
                            difficulty_level=self._map_difficulty(content_item['difficulty']),
                            estimated_time=content_item['estimated_time'],
                            reasoning=f"Identificado gap em {gap.domain} (severidade: {gap.gap_severity:.2f})",
                            learning_objectives=content_item['learning_objectives']
                        )
                        recommendations.append(recommendation)
            
            # ✅ ESTRATÉGIA 2: Se não há gaps ou poucas recomendações, sugerir próximo nível
            if len(recommendations) < limit:
                next_level_recommendations = self._get_next_level_recommendations(user_profile, limit - len(recommendations))
                recommendations.extend(next_level_recommendations)
            
            # ✅ ESTRATÉGIA 3: Se ainda não há recomendações suficientes, sugerir conteúdo popular
            if len(recommendations) < limit:
                popular_recommendations = self._get_popular_recommendations(user_profile, limit - len(recommendations))
                recommendations.extend(popular_recommendations)
            
            # Ordenar por score de relevância
            recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Cachear resultado
            self.recommendation_cache[cache_key] = {
                'recommendations': recommendations,
                'timestamp': datetime.now(UTC).timestamp()
            }
            
            cryptoquest_logger.log_business_event(
                "recommendations_generated",
                {
                    "user_id": user_id,
                    "recommendations_count": len(recommendations),
                    "top_score": recommendations[0].relevance_score if recommendations else 0
                }
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações para usuário {user_id}: {e}")
            return []
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Busca perfil do usuário (simulado - seria do banco de dados)"""
        # Simulação de dados do usuário
        # Em implementação real, buscar do banco de dados
        return {
            "user_id": user_id,
            "level": 2,
            "domains": {
                "bitcoin_basics": 0.8,
                "blockchain_technology": 0.6,
                "defi": 0.2,
                "crypto_trading": 0.4
            },
            "learning_style": "visual",
            "completed_content": [
                "bitcoin_fundamentals_quiz",
                "bitcoin_history_lesson"
            ],
            "preferred_difficulty": 0.5,
            "average_session_time": 20
        }
    
    def _identify_knowledge_gaps(self, user_profile: Dict[str, Any]) -> List[KnowledgeGap]:
        """Identifica gaps de conhecimento do usuário"""
        gaps = []
        domains = user_profile.get('domains', {})
        
        for domain, proficiency in domains.items():
            if proficiency < 0.5:  # Threshold básico para gap
                gap = KnowledgeGap(
                    domain=domain,
                    gap_severity=1.0 - proficiency,
                    recommended_content=get_domain_content(domain),
                    priority=self._calculate_gap_priority(domain, proficiency),
                    identified_at=datetime.now(UTC)
                )
                gaps.append(gap)
        
        # Ordenar por prioridade (maior severidade primeiro)
        gaps.sort(key=lambda x: x.gap_severity, reverse=True)
        
        return gaps
    
    def _calculate_gap_priority(self, domain: str, proficiency: float) -> int:
        """Calcula prioridade de um gap de conhecimento"""
        severity = 1.0 - proficiency
        
        # Prioridade baseada na severidade e domínio
        if severity > 0.7:
            return 5  # Crítico
        elif severity > 0.5:
            return 4  # Alto
        elif severity > 0.3:
            return 3  # Médio
        else:
            return 2  # Baixo
    
    def _find_content_for_gap(self, gap: KnowledgeGap) -> List[Dict[str, Any]]:
        """Encontra conteúdo adequado para um gap de conhecimento"""
        suitable_content = []
        
        for content_id, content_data in self.content_database.items():
            # Verificar se o conteúdo é do domínio correto
            if content_data['domain'] == gap.domain:
                # Verificar se a dificuldade é adequada para o gap
                if gap.gap_severity > 0.7:  # Gap crítico - conteúdo básico
                    if content_data['difficulty'] <= 0.4:
                        suitable_content.append(content_data)
                elif gap.gap_severity > 0.5:  # Gap alto - conteúdo básico a intermediário
                    if content_data['difficulty'] <= 0.6:
                        suitable_content.append(content_data)
                else:  # Gap médio - qualquer conteúdo do domínio
                    suitable_content.append(content_data)
        
        return suitable_content
    
    def _get_next_level_recommendations(self, user_profile: Dict[str, Any], limit: int) -> List[ContentRecommendation]:
        """Recomenda conteúdo do próximo nível baseado no progresso do usuário"""
        recommendations = []
        domains = user_profile.get('domains', {})
        
        for domain, domain_data in domains.items():
            if len(recommendations) >= limit:
                break
                
            proficiency = domain_data.get('proficiency_level', 0.0)
            
            # Se o usuário tem boa proficiência (>= 0.7), sugerir próximo nível
            if proficiency >= 0.7:
                next_level_content = self._find_next_level_content(domain, proficiency)
                for content_item in next_level_content:
                    if len(recommendations) >= limit:
                        break
                    
                    recommendation = ContentRecommendation(
                        content_id=content_item['id'],
                        content_type=content_item['type'],
                        relevance_score=0.8,  # Score alto para próximo nível
                        difficulty_level=self._map_difficulty(content_item['difficulty']),
                        estimated_time=content_item['estimated_time'],
                        reasoning=f"Próximo nível em {domain} (proficiência atual: {proficiency:.2f})",
                        learning_objectives=content_item['learning_objectives']
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _get_popular_recommendations(self, user_profile: Dict[str, Any], limit: int) -> List[ContentRecommendation]:
        """Recomenda conteúdo popular para usuários novos ou sem gaps específicos"""
        recommendations = []
        
        # Conteúdo popular baseado em domínios fundamentais
        popular_content = [
            'bitcoin_fundamentals_quiz',
            'blockchain_101_quiz',
            'wallet_security_quiz',
            'trading_basics_quiz',
            'defi_overview_quiz'
        ]
        
        for content_id in popular_content:
            if len(recommendations) >= limit:
                break
                
            if content_id in self.content_database:
                content_item = self.content_database[content_id]
                
                recommendation = ContentRecommendation(
                    content_id=content_item['id'],
                    content_type=content_item['type'],
                    relevance_score=0.6,  # Score médio para conteúdo popular
                    difficulty_level=self._map_difficulty(content_item['difficulty']),
                    estimated_time=content_item['estimated_time'],
                    reasoning="Conteúdo fundamental recomendado para todos os usuários",
                    learning_objectives=content_item['learning_objectives']
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _find_next_level_content(self, domain: str, current_proficiency: float) -> List[Dict[str, Any]]:
        """Encontra conteúdo do próximo nível para um domínio"""
        next_level_content = []
        
        # Mapear domínios para conteúdo de próximo nível
        next_level_mapping = {
            'bitcoin_basics': ['blockchain_101_quiz', 'consensus_mechanisms_lesson'],
            'blockchain_technology': ['defi_overview_quiz', 'smart_contracts_101'],
            'defi': ['liquidity_pools_lesson', 'yield_farming_quiz'],
            'crypto_trading': ['market_analysis_lesson', 'risk_management_quiz'],
        }
        
        # Buscar conteúdo do próximo nível
        next_content_ids = next_level_mapping.get(domain, [])
        for content_id in next_content_ids:
            if content_id in self.content_database:
                content_item = self.content_database[content_id]
                # Verificar se a dificuldade é apropriada para o próximo nível
                if content_item['difficulty'] > current_proficiency + 0.1:
                    next_level_content.append(content_item)
        
        return next_level_content
    
    def _calculate_relevance_score(self, content_item: Dict[str, Any], 
                                 gap: KnowledgeGap, user_profile: Dict[str, Any]) -> float:
        """Calcula score de relevância do conteúdo"""
        score = 0.0
        
        # Score baseado na severidade do gap
        score += gap.gap_severity * 0.4
        
        # Score baseado na adequação da dificuldade
        user_level = user_profile.get('level', 1)
        preferred_difficulty = user_profile.get('preferred_difficulty', 0.5)
        difficulty_diff = abs(content_item['difficulty'] - preferred_difficulty)
        score += (1.0 - difficulty_diff) * 0.3
        
        # Score baseado no tempo estimado vs preferência do usuário
        estimated_time = content_item['estimated_time']
        avg_session_time = user_profile.get('average_session_time', 20)
        time_ratio = min(estimated_time, avg_session_time) / max(estimated_time, avg_session_time)
        score += time_ratio * 0.2
        
        # Score baseado no tipo de conteúdo vs estilo de aprendizado
        learning_style = user_profile.get('learning_style', 'mixed')
        content_type = content_item['type']
        
        if learning_style == 'visual' and content_type == 'lesson':
            score += 0.1
        elif learning_style == 'kinesthetic' and content_type == 'quiz':
            score += 0.1
        elif learning_style == 'mixed':
            score += 0.05  # Bonus pequeno para estilo misto
        
        return min(1.0, score)  # Garantir que não exceda 1.0
    
    def _map_difficulty(self, difficulty_float: float) -> DifficultyLevel:
        """Mapeia dificuldade numérica para enum"""
        if difficulty_float <= 0.3:
            return DifficultyLevel.BEGINNER
        elif difficulty_float <= 0.6:
            return DifficultyLevel.INTERMEDIATE
        elif difficulty_float <= 0.8:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.EXPERT
    
    async def get_content_suggestions(self, user_id: str, domain: str, 
                                    limit: int = 3) -> List[ContentRecommendation]:
        """Sugere conteúdo específico para um domínio"""
        try:
            user_profile = await self._get_user_profile(user_id)
            domain_proficiency = user_profile.get('domains', {}).get(domain, 0.0)
            
            suggestions = []
            
            for content_id, content_data in self.content_database.items():
                if content_data['domain'] == domain and len(suggestions) < limit:
                    # Verificar se o usuário já completou
                    if content_id not in user_profile.get('completed_content', []):
                        # Verificar se a dificuldade é adequada
                        if abs(content_data['difficulty'] - domain_proficiency) <= 0.3:
                            suggestion = ContentRecommendation(
                                content_id=content_id,
                                content_type=content_data['type'],
                                relevance_score=0.7,  # Score padrão para sugestões
                                difficulty_level=self._map_difficulty(content_data['difficulty']),
                                estimated_time=content_data['estimated_time'],
                                reasoning=f"Sugestão para domínio {domain} baseada no nível atual",
                                learning_objectives=content_data['learning_objectives']
                            )
                            suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erro ao gerar sugestões para domínio {domain}: {e}")
            return []
    
    async def get_adaptive_difficulty(self, user_id: str, content_id: str) -> float:
        """Calcula dificuldade adaptativa para um conteúdo específico"""
        try:
            user_profile = await self._get_user_profile(user_id)
            content_data = self.content_database.get(content_id)
            
            if not content_data:
                return 0.5  # Dificuldade padrão
            
            base_difficulty = content_data['difficulty']
            domain = content_data['domain']
            domain_proficiency = user_profile.get('domains', {}).get(domain, 0.5)
            
            # Ajustar dificuldade baseada na proficiência no domínio
            proficiency_factor = domain_proficiency * 0.3
            adjusted_difficulty = base_difficulty + proficiency_factor
            
            # Garantir limites
            adjusted_difficulty = max(ai_config.min_difficulty, 
                                    min(ai_config.max_difficulty, adjusted_difficulty))
            
            return adjusted_difficulty
            
        except Exception as e:
            logger.error(f"Erro ao calcular dificuldade adaptativa: {e}")
            return 0.5


# Instância global do engine de recomendação
_recommendation_engine_instance: Optional[BasicRecommendationEngine] = None

def get_recommendation_engine() -> BasicRecommendationEngine:
    """Retorna instância global do engine de recomendação"""
    global _recommendation_engine_instance
    if _recommendation_engine_instance is None:
        _recommendation_engine_instance = BasicRecommendationEngine()
    return _recommendation_engine_instance
