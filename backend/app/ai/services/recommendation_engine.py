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
            # Conteúdo de Bitcoin (IDs corretos do Firestore)
            "btc_quiz_01": {
                "id": "btc_quiz_01",
                "type": "quiz",
                "domain": "bitcoin_basics",
                "difficulty": 0.3,
                "estimated_time": 15,
                "prerequisites": [],
                "learning_objectives": ["Entender conceitos básicos do Bitcoin", "Conhecer história da criptomoeda"]
            },
            "bitcoin_caracteristicas_questionnaire": {
                "id": "bitcoin_caracteristicas_questionnaire",
                "type": "quiz",
                "domain": "bitcoin_basics",
                "difficulty": 0.4,
                "estimated_time": 20,
                "prerequisites": [],
                "learning_objectives": ["Conhecer características do Bitcoin", "Entender propriedades únicas"]
            },
            
            # Conteúdo de Blockchain (IDs corretos do Firestore)
            "blockchain_conceitos_questionnaire": {
                "id": "blockchain_conceitos_questionnaire",
                "type": "quiz",
                "domain": "blockchain_technology",
                "difficulty": 0.4,
                "estimated_time": 20,
                "prerequisites": [],
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
            
            # Conteúdo de Segurança (IDs corretos do Firestore)
            "daily_crypto_security_quiz": {
                "id": "daily_crypto_security_quiz",
                "type": "quiz",
                "domain": "crypto_security",
                "difficulty": 0.5,
                "estimated_time": 15,
                "prerequisites": [],
                "learning_objectives": ["Aprender sobre segurança de carteiras", "Conhecer boas práticas"]
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
                    "data_points": profile_data.get("total_questions", 0),
                    # ✅ NOVO: Incluir dados do questionário inicial
                    "initial_questionnaire_score": profile_data.get("initial_questionnaire_score", 0),
                    "initial_level": profile_data.get("initial_level", 1),
                    "profile_name": profile_data.get("profile_name", "Usuário"),
                    "recommended_paths": profile_data.get("recommended_paths", []),
                    "difficulty_preferences": profile_data.get("difficulty_preferences", {}),
                    "data_source": profile_data.get("data_source", "unknown")
                }
            else:
                # ✅ CORREÇÃO: Buscar dados do questionário inicial como fallback
                logger.info(f"Perfil de IA não encontrado para {user_id}, buscando dados do questionário inicial")
                
                # Buscar dados do usuário na coleção users
                user_ref = db.collection("users").document(user_id)
                user_doc = await user_ref.get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    has_questionnaire = user_data.get("has_completed_questionnaire", False)
                    
                    if has_questionnaire:
                        # Usar dados do questionário inicial para gerar recomendações
                        initial_level = user_data.get("level", 1)
                        return {
                            "user_id": user_id,
                            "domains": {
                                "bitcoin_basics": min(initial_level * 0.2, 0.8),
                                "blockchain_technology": min(initial_level * 0.15, 0.6),
                                "defi_basics": min(initial_level * 0.1, 0.4),
                                "crypto_trading": min(initial_level * 0.1, 0.4),
                                "crypto_security": min(initial_level * 0.1, 0.4)
                            },
                            "learning_style": "mixed",
                            "engagement_score": 0.5,
                            "data_points": 0,
                            "initial_level": initial_level,
                            "data_source": "questionnaire_fallback"
                        }
                
                # Perfil padrão se não há questionário
                return {
                    "user_id": user_id,
                    "domains": {
                        "bitcoin_basics": 0.1,  # Sempre sugerir Bitcoin básico
                        "blockchain_technology": 0.0,
                        "defi_basics": 0.0,
                        "crypto_trading": 0.0,
                        "crypto_security": 0.0
                    },
                    "learning_style": "mixed",
                    "engagement_score": 0.5,
                    "data_points": 0,
                    "data_source": "default_fallback"
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
            # ✅ CORREÇÃO TEMPORÁRIA: Usar apenas recomendações básicas por enquanto
            logger.info(f"Gerando recomendações básicas para {user_id}")
            basic_recommendations = await self._get_basic_recommendations(limit)
            logger.info(f"✅ Recomendações geradas para usuário {user_id}: {len(basic_recommendations)} itens")
            return basic_recommendations
            
            # Gerar recomendações
            recommendations = []
            
            # ✅ ESTRATÉGIA 1: Recomendar conteúdo para gaps prioritários
            for gap in knowledge_gaps[:limit]:
                content_items = self._find_content_for_gap(gap)
                logger.info(f"Content items for gap {gap.domain}: {len(content_items)}")
                
                for content_item in content_items:
                    if len(recommendations) >= limit:
                        break
                    
                    # Calcular score de relevância
                    try:
                        relevance_score = self._calculate_relevance_score(
                            content_item, gap, user_profile
                        )
                    except Exception as e:
                        logger.error(f"Erro ao calcular relevance score: {e}")
                        continue
                    
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
            
            # ✅ ESTRATÉGIA 4: Se ainda está vazio, forçar recomendações básicas
            if len(recommendations) == 0:
                logger.warning(f"Nenhuma recomendação gerada para {user_id}, forçando recomendações básicas")
                basic_recommendations = await self._get_basic_recommendations(limit)
                recommendations.extend(basic_recommendations)
            
            # ✅ CORREÇÃO TEMPORÁRIA: Sempre usar recomendações básicas por enquanto
            if len(recommendations) == 0:
                logger.info(f"Forçando recomendações básicas para {user_id}")
                basic_recommendations = await self._get_basic_recommendations(limit)
                recommendations.extend(basic_recommendations)
            
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
    
    async def recommend_learning_paths(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recomenda learning paths baseado no perfil de IA do usuário"""
        try:
            # Buscar perfil de IA do usuário
            user_profile = await self._get_user_profile_from_firestore(user_id)
            
            # Se não tem perfil de IA, retornar lista vazia
            if not user_profile or not user_profile.get("user_id"):
                logger.warning(f"Perfil de IA não encontrado para usuário {user_id}")
                return []
            
            # Buscar todas as trilhas disponíveis usando repository diretamente
            from app.repositories.learning_path_repository import LearningPathRepository
            learning_path_repository = LearningPathRepository()
            available_paths = learning_path_repository.get_all_learning_paths()
            
            if not available_paths:
                logger.warning("Nenhuma trilha disponível encontrada")
                return []
            
            # Calcular scores de relevância para cada trilha
            path_recommendations = []
            
            for path in available_paths:
                relevance_score = self._calculate_path_relevance_score(user_profile, path)
                
                if relevance_score > 0.1:  # Threshold mínimo
                    path_recommendations.append({
                        "path_id": path.id,
                        "name": path.name,
                        "description": path.description,
                        "difficulty": path.difficulty.value,
                        "estimated_duration": path.estimated_duration,
                        "relevance_score": relevance_score,
                        "reasoning": self._generate_path_reasoning(user_profile, path, relevance_score),
                        "is_recommended": relevance_score >= 0.7
                    })
            
            # Ordenar por score de relevância
            path_recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Limitar resultados
            recommended_paths = path_recommendations[:limit]
            
            logger.info(f"✅ Recomendações geradas para usuário {user_id}: {len(recommended_paths)} trilhas")
            
            return recommended_paths
            
        except Exception as e:
            logger.error(f"Erro ao recomendar learning paths para usuário {user_id}: {e}")
            return []
    
    def _calculate_path_relevance_score(self, user_profile: Dict[str, Any], learning_path) -> float:
        """Calcula score de relevância de uma trilha para o usuário"""
        score = 0.0
        
        # Peso 1: Dados do questionário inicial (40%)
        if user_profile.get("data_source") == "initial_questionnaire":
            questionnaire_score = user_profile.get("initial_questionnaire_score", 0)
            initial_level = user_profile.get("initial_level", 1)
            
            # Verificar se a trilha está nas recomendações originais
            recommended_paths = user_profile.get("recommended_paths", [])
            if learning_path.id in recommended_paths:
                score += 0.4  # Boost se está nas recomendações originais
            
            # Verificar adequação do nível
            path_difficulty_level = self._map_difficulty_to_level(learning_path.difficulty.value)
            level_match = 1.0 - abs(initial_level - path_difficulty_level) / 3.0  # Normalizar
            score += level_match * 0.3
        
        # Peso 2: Domínios de conhecimento (35%)
        domains = user_profile.get("domains", {})
        path_domains = self._extract_domains_from_path(learning_path)
        
        domain_match = 0.0
        for path_domain in path_domains:
            if path_domain in domains:
                domain_proficiency = domains[path_domain].get("proficiency_level", 0.0)
                # Dar boost para domínios onde o usuário tem conhecimento suficiente
                if domain_proficiency >= 0.3:  # Conhecimento mínimo
                    domain_match += min(domain_proficiency, 0.8)  # Cap em 0.8
        
        if path_domains:
            domain_score = domain_match / len(path_domains)
            score += domain_score * 0.35
        
        # Peso 3: Preferências de dificuldade (25%)
        difficulty_prefs = user_profile.get("difficulty_preferences", {})
        comfort_zone = difficulty_prefs.get("comfort_zone", "beginner")
        
        difficulty_match = self._calculate_difficulty_match(learning_path.difficulty.value, comfort_zone)
        score += difficulty_match * 0.25
        
        return min(1.0, score)
    
    def _map_difficulty_to_level(self, difficulty: str) -> int:
        """Mapeia dificuldade da trilha para nível numérico"""
        mapping = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3
        }
        return mapping.get(difficulty.lower(), 2)  # Default: intermediário
    
    def _extract_domains_from_path(self, learning_path) -> List[str]:
        """Extrai domínios de conhecimento baseados no nome/descrição da trilha"""
        domains = []
        path_name = learning_path.name.lower()
        path_desc = learning_path.description.lower()
        
        # Mapear nomes de trilhas para domínios
        if "bitcoin" in path_name or "bitcoin" in path_desc:
            domains.append("bitcoin_basics")
        if "blockchain" in path_name or "blockchain" in path_desc:
            domains.append("blockchain_technology")
        if "defi" in path_name or "defi" in path_desc or "decentralized" in path_desc:
            domains.append("defi_basics")
        if "trading" in path_name or "trading" in path_desc or "market" in path_desc:
            domains.append("crypto_trading")
        if "security" in path_name or "wallet" in path_name or "security" in path_desc:
            domains.append("crypto_security")
        
        return domains if domains else ["bitcoin_basics"]  # Default domain
    
    def _calculate_difficulty_match(self, path_difficulty: str, user_comfort_zone: str) -> float:
        """Calcula quão bem a dificuldade da trilha se adequa ao usuário"""
        # Mapear para valores numéricos
        difficulty_levels = {"beginner": 1, "intermediate": 2, "advanced": 3}
        comfort_levels = {"beginner": 1, "intermediate": 2, "advanced": 3}
        
        path_level = difficulty_levels.get(path_difficulty.lower(), 2)
        comfort_level = comfort_levels.get(user_comfort_zone.lower(), 1)
        
        # Dar score alto se está na zona de conforto ou ligeiramente acima
        if path_level == comfort_level:
            return 1.0
        elif abs(path_level - comfort_level) == 1:
            return 0.7  # Uma dificuldade diferente mas próxima
        else:
            return 0.3  # Muito diferente
    
    def _generate_path_reasoning(self, user_profile: Dict[str, Any], learning_path, relevance_score: float) -> str:
        """Gera explicação para a recomendação da trilha"""
        reasoning_parts = []
        
        # Se vem do questionário inicial
        if user_profile.get("data_source") == "initial_questionnaire":
            questionnaire_score = user_profile.get("initial_questionnaire_score", 0)
            profile_name = user_profile.get("profile_name", "Usuário")
            
            if questionnaire_score <= 3:
                reasoning_parts.append(f"Trilha adequada para seu perfil '{profile_name}' (iniciante)")
            elif questionnaire_score <= 6:
                reasoning_parts.append(f"Baseado no seu nível intermediário ('{profile_name}')")
            else:
                reasoning_parts.append(f"Trilha avançada ideal para seu perfil '{profile_name}'")
        
        # Se tem conhecimento em domínios relevantes
        domains = user_profile.get("domains", {})
        path_domains = self._extract_domains_from_path(learning_path)
        
        for domain in path_domains:
            if domain in domains:
                proficiency = domains[domain].get("proficiency_level", 0.0)
                if proficiency >= 0.5:
                    reasoning_parts.append(f"Você já tem conhecimento em {domain.replace('_', ' ')}")
        
        # Dificuldade adequada
        difficulty_prefs = user_profile.get("difficulty_preferences", {})
        comfort_zone = difficulty_prefs.get("comfort_zone", "beginner")
        
        if learning_path.difficulty.value.lower() == comfort_zone:
            reasoning_parts.append(f"Dificuldade '{comfort_zone}' adequada ao seu nível")
        elif relevance_score >= 0.7:
            reasoning_parts.append("Trilha altamente recomendada pela IA")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Recomendação baseada no seu perfil de aprendizado"
    
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
        
        # ✅ CORREÇÃO: Verificar se domains é um dict
        if not isinstance(domains, dict):
            logger.warning(f"Domains não é um dict: {type(domains)} = {domains}")
            return gaps
        
        for domain, proficiency in domains.items():
            # ✅ CORREÇÃO: Verificar se proficiency é um número
            if isinstance(proficiency, (int, float)) and proficiency < 0.5:
                gap = KnowledgeGap(
                    domain=domain,
                    gap_severity=1.0 - float(proficiency),
                    recommended_content=get_domain_content(domain),  # Lista de strings
                    priority=self._calculate_gap_priority(domain, float(proficiency)),
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
    
    async def _get_basic_recommendations(self, limit: int) -> List[ContentRecommendation]:
        """Força recomendações básicas quando não há dados suficientes"""
        basic_content = [
            {
                'id': 'btc_quiz_01',
                'type': 'quiz',
                'domain': 'bitcoin_basics',
                'difficulty': 0.3,
                'estimated_time': 15,
                'learning_objectives': ['Entender conceitos básicos do Bitcoin', 'Conhecer história da criptomoeda']
            },
            {
                'id': 'blockchain_conceitos_questionnaire',
                'type': 'quiz',
                'domain': 'blockchain_technology',
                'difficulty': 0.4,
                'estimated_time': 20,
                'learning_objectives': ['Entender conceitos de blockchain', 'Conhecer tipos de consenso']
            },
            {
                'id': 'daily_crypto_security_quiz',
                'type': 'quiz',
                'domain': 'crypto_security',
                'difficulty': 0.5,
                'estimated_time': 15,
                'learning_objectives': ['Aprender sobre segurança de carteiras', 'Conhecer boas práticas']
            }
        ]
        
        recommendations = []
        for content_item in basic_content[:limit]:
            # ✅ CORREÇÃO: Buscar título real do quiz
            quiz_title = await self._get_quiz_title(content_item['id'])
            
            recommendation = ContentRecommendation(
                content_id=content_item['id'],
                content_type=content_item['type'],
                relevance_score=0.7,  # Score médio para conteúdo básico
                difficulty_level=self._map_difficulty(content_item['difficulty']),
                estimated_time=content_item['estimated_time'],
                reasoning="Conteúdo fundamental recomendado para iniciantes",
                learning_objectives=content_item['learning_objectives'],
                title=quiz_title  # ✅ ADICIONADO: Título real do quiz
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _get_quiz_title(self, quiz_id: str) -> str:
        """Busca o título real de um quiz no Firestore"""
        try:
            from app.core.firebase import get_firestore_db_async
            db = await get_firestore_db_async()
            
            quiz_ref = db.collection("quizzes").document(quiz_id)
            quiz_doc = await quiz_ref.get()
            
            if quiz_doc.exists:
                quiz_data = quiz_doc.to_dict()
                return quiz_data.get("title", f"Quiz {quiz_id}")
            else:
                return f"Quiz {quiz_id}"
                
        except Exception as e:
            logger.error(f"Erro ao buscar título do quiz {quiz_id}: {e}")
            return f"Quiz {quiz_id}"
    
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
