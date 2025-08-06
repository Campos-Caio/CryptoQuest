from app.repositories.user_repository import UserRepository
from app.models.user import UserProfile
from app.core.firebase import get_firestore_db_async 
import random 
from datetime import datetime, timezone 

class MissionService: 
    def __init__(self, user_repo: UserRepository): 
        self.user_repo = user_repo 
        self.db = get_firestore_db_async()

    async def get_daily_missions_for_user(self, user: UserProfile) -> list: 
        # 1 Busca a biblioteca de todas a missoes no firestore
        mission_ref = self.db.collection('missions')
        all_missions_docs = mission_ref.stream()
        all_missions = [doc.to_dict() async for doc in all_missions_docs]

        # Filtra as missoe sque o usuario pode fazer
        elegible_missions = []
        today = datetime.now(timezone.utc).date()

        for mission in all_missions: 
            # Filtro 1: O usuario tem o nivel necessario?
            if user.level < mission.get('required_level', 1): 
                continue 

            # Filtro 2: O usuario ja completou essa missao hoje? 
            mission_id = mission.get('id')
            if mission_id in user.completed_missions: 
                completion_date = user.completed_missions[mission_id].date()
                if completion_date == today: 
                    continue # Ja completou hj   
            
            elegible_missions.append(mission)
        
        # Seleciona aleatoriamente um numero de missoes 
        num_missoes_to_return = min(len(elegible_missions), 3)
        daily_missions = random.sample(elegible_missions, num_missoes_to_return)

        return daily_missions 
    
    async def complete_mission(self, user_id: str, mission_id: str) -> UserProfile: 
        """
            Valida a conclusao de uma missao e atualiza o perfil do usuario
            Esta operacao deve ser transacional para garantir a consistencia dos dados 
        """

        mission_ref = self.db.collection('missions').document(mission_id)
        user_ref = self.db.collection('users').document(user_id)

        # Usando uma transacao para garantir que todas ou nenhuma as atualizacoes acontecam 
        transaction = self.db.transaction()

        @firestore.async_transactional
        async def update_in_transaction(transaction, mission_ref, user_ref): 
            # Busca os docs dentro da transacao 
            mission_doc = await mission_ref.get(transaction=transaction)
            if not mission_doc.exists: 
                raise ValueError("Missao nao encontrado!")
            
            user_doc = await user_ref.get(transaction=transaction)
            if not user_doc.exists: 
                raise ValueError("Usuario nao encontrado!")
            
            mission_data = mission_doc.to_dict() 
            user_data = user_doc.to_dict() 

            #(TODO) Logica de validacao, ex: verificar respostasa do quizz etc 

            # Calcula os novos valores 
            new_points = user_data.get('points', 0) + mission_data.get("reward_points", 0)

            # Adiciona a missao ao mapa de missoes completas 
            completion_field = f'completed_missions.{mission_id}'

            # Prepara a atualizacao 
            transaction.update(user_ref, {
                "points" : new_points, 
                completion_field : datetime.now(timezone.utc)
            })

            # TODO logica de verificacao de level up 

            # retorna o novo total de pontos para API poder usar 
            user_data['points'] = new_points 
            return user_data 

        updated_user_data = await update_in_transaction(transaction, mission_ref, user_ref)
        return UserProfile(**updated_user_data)