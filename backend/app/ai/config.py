"""
Configurações do sistema de IA do CryptoQuest.
"""
import os
from typing import Dict, Any, List
from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    """Configurações do sistema de IA"""
    
    # Configurações gerais
    ai_enabled: bool = True
    ai_debug_mode: bool = False
    ai_version: str = "1.0.0"
    
    # Configurações de modelos ML
    ml_models_path: str = "models/"
    model_retrain_threshold: int = 100  # Retreinar após 100 novas amostras
    model_accuracy_threshold: float = 0.75  # Threshold mínimo de precisão
    
    # Configurações de coleta de dados
    min_quiz_responses_for_analysis: int = 5  # Mínimo de respostas para análise
    behavioral_data_retention_days: int = 365  # Retenção de dados comportamentais
    
    # Configurações de recomendação
    max_recommendations_per_user: int = 10
    recommendation_confidence_threshold: float = 0.6
    content_freshness_weight: float = 0.3  # Peso para conteúdo recente
    
    # Configurações de dificuldade
    difficulty_adaptation_rate: float = 0.1  # Taxa de adaptação de dificuldade
    min_difficulty: float = 0.1
    max_difficulty: float = 0.9
    
    # Configurações de domínios de conhecimento
    knowledge_domains: List[str] = [
        "bitcoin_basics",
        "blockchain_technology", 
        "crypto_trading",
        "defi",
        "nft",
        "smart_contracts",
        "crypto_security",
        "regulation"
    ]
    
    # Configurações de estilos de aprendizado
    learning_styles: List[str] = [
        "visual",
        "auditory", 
        "kinesthetic",
        "reading_writing",
        "mixed"
    ]
    
    # Configurações de cache
    ai_cache_ttl_minutes: int = 30
    max_cache_size: int = 1000
    
    # Configurações de logging
    ai_log_level: str = "INFO"
    log_predictions: bool = True
    log_user_behavior: bool = True
    
    # Configurações de performance
    max_concurrent_ai_requests: int = 10
    ai_request_timeout: int = 30  # segundos
    
    # Configurações de privacidade
    anonymize_user_data: bool = False
    data_encryption_enabled: bool = True
    
    class Config:
        env_prefix = "AI_"
        case_sensitive = False


# Instância global de configuração
ai_config = AIConfig()


# Configurações específicas por domínio
DOMAIN_DIFFICULTY_MAP = {
    "bitcoin_basics": 0.3,
    "blockchain_technology": 0.4,
    "crypto_trading": 0.6,
    "defi": 0.7,
    "nft": 0.5,
    "smart_contracts": 0.8,
    "crypto_security": 0.7,
    "regulation": 0.6
}

# Mapeamento de conteúdo recomendado por domínio
DOMAIN_CONTENT_MAP = {
    "bitcoin_basics": [
        "bitcoin_fundamentals_quiz",
        "bitcoin_history_lesson",
        "bitcoin_wallet_basics"
    ],
    "blockchain_technology": [
        "blockchain_101_quiz",
        "consensus_mechanisms_lesson",
        "blockchain_security_quiz"
    ],
    "crypto_trading": [
        "trading_basics_quiz",
        "market_analysis_lesson",
        "risk_management_quiz"
    ],
    "defi": [
        "defi_overview_quiz",
        "liquidity_pools_lesson",
        "yield_farming_quiz"
    ],
    "nft": [
        "nft_basics_quiz",
        "nft_marketplace_lesson",
        "nft_creation_guide"
    ],
    "smart_contracts": [
        "smart_contracts_101",
        "solidity_basics_lesson",
        "contract_security_quiz"
    ],
    "crypto_security": [
        "wallet_security_quiz",
        "phishing_prevention_lesson",
        "secure_storage_guide"
    ],
    "regulation": [
        "crypto_regulations_quiz",
        "legal_aspects_lesson",
        "compliance_guide"
    ]
}

# Configurações de padrões de aprendizado
LEARNING_PATTERN_THRESHOLDS = {
    "fast_learner": {
        "max_response_time": 15.0,
        "min_confidence": 0.7,
        "max_hints_used": 0.2
    },
    "methodical_learner": {
        "min_response_time": 25.0,
        "max_hints_used": 0.5,
        "min_attempts": 1.2
    },
    "visual_learner": {
        "prefers_visual_content": True,
        "response_time_variance": 0.3
    },
    "auditory_learner": {
        "prefers_audio_content": True,
        "consistency_score": 0.8
    }
}

# Configurações de métricas de performance
PERFORMANCE_METRICS = {
    "response_time_weight": 0.3,
    "accuracy_weight": 0.4,
    "confidence_weight": 0.2,
    "engagement_weight": 0.1
}

# Configurações de cache para diferentes tipos de dados
CACHE_CONFIG = {
    "user_profiles": {"ttl": 1800, "max_size": 500},  # 30 min, 500 usuários
    "recommendations": {"ttl": 900, "max_size": 1000},  # 15 min, 1000 recomendações
    "predictions": {"ttl": 600, "max_size": 2000},  # 10 min, 2000 predições
    "insights": {"ttl": 3600, "max_size": 300}  # 1 hora, 300 insights
}


def get_domain_difficulty(domain: str) -> float:
    """Retorna a dificuldade base para um domínio"""
    return DOMAIN_DIFFICULTY_MAP.get(domain, 0.5)


def get_domain_content(domain: str) -> List[str]:
    """Retorna conteúdo recomendado para um domínio"""
    return DOMAIN_CONTENT_MAP.get(domain, [])


def get_learning_pattern_config(pattern_type: str) -> Dict[str, Any]:
    """Retorna configuração para um tipo de padrão de aprendizado"""
    return LEARNING_PATTERN_THRESHOLDS.get(pattern_type, {})


def get_cache_config(cache_type: str) -> Dict[str, Any]:
    """Retorna configuração de cache para um tipo de dados"""
    return CACHE_CONFIG.get(cache_type, {"ttl": 600, "max_size": 100})
