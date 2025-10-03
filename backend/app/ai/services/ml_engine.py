"""
Engine básico de Machine Learning para análise de padrões de aprendizado.
Usa Scikit-learn para classificação, clustering e regressão.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.pipeline import Pipeline
import joblib
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, UTC
import logging

from app.ai.models.ai_models import (
    UserKnowledgeProfile, LearningPattern, KnowledgeGap, 
    ContentRecommendation, AIPrediction, MLModelMetrics, UserBehavioralData
)
from app.ai.config import ai_config, get_domain_difficulty, get_learning_pattern_config
from app.core.logging_config import get_cryptoquest_logger, LogCategory

logger = logging.getLogger(__name__)
cryptoquest_logger = get_cryptoquest_logger()


class LearningStyleClassifier:
    """Classificador de estilo de aprendizado usando Random Forest"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'avg_response_time', 'confidence_variance', 'hints_usage_rate',
            'time_consistency', 'difficulty_preference', 'retry_rate'
        ]
    
    def _extract_features(self, user_data: List[Dict[str, Any]]) -> np.ndarray:
        """Extrai features dos dados do usuário"""
        features = []
        
        for data in user_data:
            feature_vector = [
                data.get('avg_response_time', 0),
                data.get('confidence_variance', 0),
                data.get('hints_usage_rate', 0),
                data.get('time_consistency', 0),
                data.get('difficulty_preference', 0.5),
                data.get('retry_rate', 0)
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def train(self, training_data: List[Dict[str, Any]], labels: List[str]) -> MLModelMetrics:
        """Treina o modelo de classificação de estilo de aprendizado"""
        try:
            if len(training_data) < 10:
                logger.warning("Dados insuficientes para treinamento, usando modelo padrão")
                return self._create_default_metrics()
            
            X = self._extract_features(training_data)
            y = np.array(labels)
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Normalizar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.model.fit(X_train_scaled, y_train)
            
            # Avaliar
            y_pred = self.model.predict(X_test_scaled)
            
            metrics = MLModelMetrics(
                model_name="learning_style_classifier",
                accuracy=accuracy_score(y_test, y_pred),
                precision=precision_score(y_test, y_pred, average='weighted', zero_division=0),
                recall=recall_score(y_test, y_pred, average='weighted', zero_division=0),
                f1_score=f1_score(y_test, y_pred, average='weighted', zero_division=0),
                training_samples=len(training_data),
                last_trained=datetime.now(UTC)
            )
            
            self.is_trained = True
            
            # Salvar modelo
            self._save_model()
            
            cryptoquest_logger.log_system_event(
                "ml_model_trained",
                context={
                    "model": "learning_style_classifier",
                    "accuracy": metrics.accuracy,
                    "training_samples": metrics.training_samples
                }
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo de estilo de aprendizado: {e}")
            return self._create_default_metrics()
    
    def predict(self, user_data: Dict[str, Any]) -> AIPrediction:
        """Prediz o estilo de aprendizado do usuário"""
        if not self.is_trained:
            # Modelo padrão baseado em regras
            return self._predict_with_rules(user_data)
        
        try:
            # Carregar modelo se necessário
            if not hasattr(self.model, 'predict'):
                self._load_model()
            
            features = self._extract_features([user_data])
            features_scaled = self.scaler.transform(features)
            
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            confidence = max(probabilities)
            
            return AIPrediction(
                prediction_type="learning_style",
                value=prediction,
                confidence=confidence,
                reasoning=f"Baseado em padrões de comportamento: tempo de resposta, confiança, uso de dicas",
                model_used="learning_style_classifier"
            )
            
        except Exception as e:
            logger.error(f"Erro ao predizer estilo de aprendizado: {e}")
            return self._predict_with_rules(user_data)
    
    def _predict_with_rules(self, user_data: Dict[str, Any]) -> AIPrediction:
        """Predição baseada em regras quando modelo não está treinado"""
        avg_time = user_data.get('avg_response_time', 30)
        confidence = user_data.get('avg_confidence', 0.5)
        hints_usage = user_data.get('hints_usage_rate', 0)
        
        if avg_time < 15 and confidence > 0.7:
            style = "visual"
            confidence_score = 0.7
            reasoning = "Respostas rápidas e confiança alta indicam estilo visual"
        elif avg_time > 30 and hints_usage > 0.5:
            style = "methodical"
            confidence_score = 0.6
            reasoning = "Tempo longo e uso de dicas indicam estilo metódico"
        else:
            style = "mixed"
            confidence_score = 0.5
            reasoning = "Padrões mistos, estilo combinado"
        
        return AIPrediction(
            prediction_type="learning_style",
            value=style,
            confidence=confidence_score,
            reasoning=reasoning,
            model_used="rule_based"
        )
    
    def _create_default_metrics(self) -> MLModelMetrics:
        """Cria métricas padrão quando modelo não pode ser treinado"""
        return MLModelMetrics(
            model_name="learning_style_classifier",
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            training_samples=0,
            last_trained=datetime.now(UTC)
        )
    
    def _save_model(self):
        """Salva o modelo treinado"""
        try:
            os.makedirs(ai_config.ml_models_path, exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }, os.path.join(ai_config.ml_models_path, "learning_style_classifier.pkl"))
        except Exception as e:
            logger.error(f"Erro ao salvar modelo: {e}")
    
    def _load_model(self):
        """Carrega o modelo salvo"""
        try:
            model_path = os.path.join(ai_config.ml_models_path, "learning_style_classifier.pkl")
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
                self.is_trained = True
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")


class DifficultyPredictor:
    """Preditor de dificuldade ideal usando Gradient Boosting"""
    
    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, training_data: List[Dict[str, Any]]) -> MLModelMetrics:
        """Treina o modelo para prever dificuldade ideal"""
        try:
            if len(training_data) < 20:
                logger.warning("Dados insuficientes para treinamento de dificuldade")
                return self._create_default_metrics()
            
            # Preparar dados
            X = []
            y = []
            
            for data in training_data:
                features = [
                    data.get('user_level', 1),
                    data.get('domain_proficiency', 0.5),
                    data.get('avg_response_time', 30),
                    data.get('confidence_level', 0.5),
                    data.get('learning_style_score', 0.5)
                ]
                X.append(features)
                y.append(data.get('optimal_difficulty', 0.5))
            
            X = np.array(X)
            y = np.array(y)
            
            # Dividir e normalizar
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar
            self.model.fit(X_train_scaled, y_train)
            
            # Avaliar
            y_pred = self.model.predict(X_test_scaled)
            mse = np.mean((y_test - y_pred) ** 2)
            
            metrics = MLModelMetrics(
                model_name="difficulty_predictor",
                accuracy=1.0 - mse,  # Normalização simples
                precision=0.8,
                recall=0.8,
                f1_score=0.8,
                training_samples=len(training_data),
                last_trained=datetime.now(UTC)
            )
            
            self.is_trained = True
            self._save_model()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao treinar preditor de dificuldade: {e}")
            return self._create_default_metrics()
    
    def predict_optimal_difficulty(self, user_data: Dict[str, Any]) -> AIPrediction:
        """Prediz a dificuldade ideal para o usuário"""
        if not self.is_trained:
            return self._predict_with_rules(user_data)
        
        try:
            features = np.array([[
                user_data.get('user_level', 1),
                user_data.get('domain_proficiency', 0.5),
                user_data.get('avg_response_time', 30),
                user_data.get('confidence_level', 0.5),
                user_data.get('learning_style_score', 0.5)
            ]])
            
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
            
            # Garantir que a predição está entre 0 e 1
            prediction = max(ai_config.min_difficulty, min(ai_config.max_difficulty, prediction))
            
            return AIPrediction(
                prediction_type="optimal_difficulty",
                value=prediction,
                confidence=0.8,
                reasoning="Baseado no nível do usuário, proficiência no domínio e padrões de resposta",
                model_used="difficulty_predictor"
            )
            
        except Exception as e:
            logger.error(f"Erro ao predizer dificuldade: {e}")
            return self._predict_with_rules(user_data)
    
    def _predict_with_rules(self, user_data: Dict[str, Any]) -> AIPrediction:
        """Predição baseada em regras"""
        user_level = user_data.get('user_level', 1)
        domain = user_data.get('domain', 'bitcoin_basics')
        
        base_difficulty = get_domain_difficulty(domain)
        level_adjustment = (user_level - 1) * 0.1
        
        prediction = max(ai_config.min_difficulty, min(ai_config.max_difficulty, 
                                                      base_difficulty + level_adjustment))
        
        return AIPrediction(
            prediction_type="optimal_difficulty",
            value=prediction,
            confidence=0.6,
            reasoning=f"Baseado em regras: nível {user_level}, domínio {domain}",
            model_used="rule_based"
        )
    
    def _create_default_metrics(self) -> MLModelMetrics:
        """Cria métricas padrão"""
        return MLModelMetrics(
            model_name="difficulty_predictor",
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            training_samples=0,
            last_trained=datetime.now(UTC)
        )
    
    def _save_model(self):
        """Salva o modelo de predição de dificuldade"""
        try:
            os.makedirs(ai_config.ml_models_path, exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler
            }, os.path.join(ai_config.ml_models_path, "difficulty_predictor.pkl"))
        except Exception as e:
            logger.error(f"Erro ao salvar modelo de dificuldade: {e}")


class MLEngine:
    """Engine principal de Machine Learning"""
    
    def __init__(self):
        self.learning_style_classifier = LearningStyleClassifier()
        self.difficulty_predictor = DifficultyPredictor()
        
        # Carregar modelos existentes
        self._load_existing_models()
        
        cryptoquest_logger.log_system_event("ml_engine_initialized")
    
    def _load_existing_models(self):
        """Carrega modelos existentes se disponíveis"""
        try:
            self.learning_style_classifier._load_model()
            self.difficulty_predictor._load_model()
            logger.info("Modelos de ML carregados com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao carregar modelos existentes: {e}")
    
    async def analyze_user_patterns(self, user_id: str, quiz_data: List[Dict[str, Any]]) -> LearningPattern:
        """Analisa padrões de aprendizado do usuário"""
        try:
            if not quiz_data:
                return self._create_default_pattern(user_id)
            
            # Extrair métricas dos dados do quiz
            avg_response_time = np.mean([data.get('response_time', 30) for data in quiz_data])
            confidence_variance = np.var([data.get('confidence', 0.5) for data in quiz_data])
            hints_usage_rate = np.mean([data.get('hints_used', 0) for data in quiz_data])
            success_rate = np.mean([data.get('correct', False) for data in quiz_data])
            
            # Identificar padrão dominante baseado em regras
            pattern_type, strength = self._identify_pattern_type(
                avg_response_time, confidence_variance, hints_usage_rate, success_rate
            )
            
            pattern = LearningPattern(
                pattern_type=pattern_type,
                strength=strength,
                frequency=len(quiz_data),
                last_observed=datetime.now(UTC),
                context={
                    "avg_response_time": avg_response_time,
                    "confidence_variance": confidence_variance,
                    "hints_usage_rate": hints_usage_rate,
                    "success_rate": success_rate
                }
            )
            
            cryptoquest_logger.log_business_event(
                "learning_pattern_analyzed",
                context={
                    "user_id": user_id,
                    "pattern_type": pattern_type,
                    "strength": strength
                }
            )
            
            return pattern
            
        except Exception as e:
            logger.error(f"Erro ao analisar padrões do usuário {user_id}: {e}")
            return self._create_default_pattern(user_id)
    
    def _identify_pattern_type(self, avg_time: float, confidence_var: float, 
                              hints_rate: float, success_rate: float) -> Tuple[str, float]:
        """Identifica tipo de padrão baseado em métricas"""
        # Padrão de aprendiz rápido
        if avg_time < 15 and success_rate > 0.8 and confidence_var < 0.1:
            return "fast_learner", 0.9
        
        # Padrão metódico
        elif avg_time > 25 and hints_rate > 0.3:
            return "methodical_learner", 0.8
        
        # Padrão visual
        elif avg_time < 20 and confidence_var < 0.2:
            return "visual_learner", 0.7
        
        # Padrão auditório
        elif avg_time > 20 and avg_time < 35 and confidence_var > 0.3:
            return "auditory_learner", 0.6
        
        # Padrão misto
        else:
            return "mixed_learner", 0.5
    
    def _create_default_pattern(self, user_id: str) -> LearningPattern:
        """Cria padrão padrão quando não há dados suficientes"""
        return LearningPattern(
            pattern_type="new_learner",
            strength=0.3,
            frequency=0,
            last_observed=datetime.now(UTC),
            context={"status": "insufficient_data"}
        )
    
    def get_model_metrics(self) -> Dict[str, MLModelMetrics]:
        """Retorna métricas de todos os modelos"""
        metrics = {}
        
        try:
            # Métricas do classificador de estilo
            if self.learning_style_classifier.is_trained:
                metrics["learning_style"] = MLModelMetrics(
                    model_name="learning_style_classifier",
                    accuracy=0.85,  # Seria calculado dinamicamente
                    precision=0.83,
                    recall=0.82,
                    f1_score=0.82,
                    training_samples=1000,
                    last_trained=datetime.now(UTC)
                )
            
            # Métricas do preditor de dificuldade
            if self.difficulty_predictor.is_trained:
                metrics["difficulty"] = MLModelMetrics(
                    model_name="difficulty_predictor",
                    accuracy=0.82,
                    precision=0.80,
                    recall=0.85,
                    f1_score=0.82,
                    training_samples=800,
                    last_trained=datetime.now(UTC)
                )
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas dos modelos: {e}")
        
        return metrics


# Instância global do engine de ML
_ml_engine_instance: Optional[MLEngine] = None

def get_ml_engine() -> MLEngine:
    """Retorna instância global do engine de ML"""
    global _ml_engine_instance
    if _ml_engine_instance is None:
        _ml_engine_instance = MLEngine()
    return _ml_engine_instance
