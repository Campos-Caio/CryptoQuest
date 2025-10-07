from typing import Optional
from app.models.ranking import Ranking, RankingType
from app.core.firebase import get_firestore_db_async
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

class RankingRepository:
    def __init__(self, db_client):
        self.db = db_client

    def save_ranking(self, ranking: Ranking):
        """Salva ranking no banco"""
        try:
            doc_id = f"{ranking.type.value}_{ranking.period}"
            doc_ref = self.db.collection("rankings").document(doc_id)
            doc_ref.set(ranking.model_dump())
        except Exception as e:
            logger.error(f"Erro ao salvar ranking: {e}")
            raise

    def get_latest_ranking(self, ranking_type: RankingType) -> Optional[Ranking]:
        """Busca o ranking mais recente do tipo especificado"""
        try:
            query = self.db.collection("rankings").where("type", "==", ranking_type.value).order_by("generated_at", direction="DESCENDING").limit(1)
            docs = query.stream()
            
            for doc in docs:
                return Ranking(**doc.to_dict())
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar ranking: {e}")
            return None

    def get_ranking_by_period(self, ranking_type: RankingType, period: str) -> Optional[Ranking]:
        """Busca ranking por período específico"""
        try:
            doc_id = f"{ranking_type.value}_{period}"
            doc_ref = self.db.collection("rankings").document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return Ranking(**doc.to_dict())
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar ranking por período: {e}")
            return None

def get_ranking_repository(db_client = Depends(get_firestore_db_async)) -> RankingRepository:
    return RankingRepository(db_client)