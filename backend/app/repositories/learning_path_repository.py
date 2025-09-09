import logging
from typing import List, Optional, Union
from datetime import datetime
from firebase_admin import firestore
from app.models.learning_path import LearningPath, UserPathProgress

logger = logging.getLogger(__name__)

class LearningPathRepository:
    """Repositorio para operacoes de trilhas de aprendizado no Firestore"""

    def __init__(self):
        self.db = firestore.client()
        self.learning_paths_collection = self.db.collection("learning_paths")
        self.progress_collection = self.db.collection("user_path_progress")


    def get_all_learning_paths(self) -> List[LearningPath]:
        """Busca todas as trilhas de aprendizado ativas"""
        try: 
            docs = self.learning_paths_collection.where("is_active", "==", True).stream()
            paths = []

            for doc in docs: 
                data = doc.to_dict()
                data["id"] = doc.id
                paths.append(LearningPath(**data))

            logger.info(f"Encontradas {len(paths)} trilhas de aprendizado ativas")
            return paths 

        except Exception as e:
            logger.error(f"Erro ao buscar trilhas de aprendizado: {e}")
            raise 

    def get_learning_path_by_id(self, path_id: str) -> Optional[LearningPath]:
        """Busca uma trilha de aprendizado por ID"""
        try: 
            doc = self.learning_paths_collection.document(path_id).get()

            if not doc.exists:
                logger.warning(f"Trilha {path_id} nao encontrada")
                return None 
            
            data = doc.to_dict()
            data["id"] = doc.id
            
            # Corrige a estrutura das missões se necessário
            if "modules" in data:
                for module in data["modules"]:
                    if "missions" in module:
                        for mission in module["missions"]:
                            # Garante que os campos obrigatórios existam
                            if "order" not in mission:
                                mission["order"] = 1
                            if "required_score" not in mission:
                                mission["required_score"] = 70
                            if "mission_id" not in mission:
                                mission["mission_id"] = mission.get("id", "")
            
            logger.info(f"Trilha {path_id} encontrada")
            return LearningPath(**data)

        except Exception as e:
            logger.error(f"Erro ao buscar trilha {path_id}: {e}")
            logger.error(f"Dados recebidos: {data if 'data' in locals() else 'N/A'}")
            raise 

    def create_learning_path(self, learning_path: LearningPath) -> LearningPath:
        """Cria uma nova trilha de aprendizado"""
        try: 
            path_data = learning_path.model_dump()
            path_data.pop('id', None) # Remove ID para Firestore gerar 

            doc_ref = self.learning_paths_collection.document(learning_path.id)
            doc_ref.set(path_data)

            logger.info(f"Trilha {learning_path.id} criada com sucesso")
            return learning_path 

        except Exception as e:
            logger.error(f"Erro ao criar trilha {learning_path.id}: {e}")
            raise 

    def get_user_progress(self, user_id: str, path_id: str) -> Optional[UserPathProgress]: 
        """Busca o progresso de uma trilha de aprendizado de um usuario"""         
        try: 
            doc_id = f"{user_id}_{path_id}"
            doc = self.progress_collection.document(doc_id).get()

            if not doc.exists:
                logger.info(f"Progresso nao encontrado para o usuario {user_id} na trilha {path_id}")
                return None 
            
            data = doc.to_dict() 
            return UserPathProgress(**data)
        except Exception as e: 
            logger.error(f"Erro ao buscar progresso do usuario {user_id} na trilha {path_id}: {e}")
            raise 

    def get_all_user_progress(self, user_id: str) -> List[UserPathProgress]:
        """Busca todo o progresso do usuario em todas as trilhas""" 
        try: 
            docs = self.progress_collection.where("user_id", "==", user_id).stream()
            progress_list = []

            for doc in docs: 
                data = doc.to_dict()
                progress_list.append(UserPathProgress(**data)) 

            logger.info(f'Encontrado progresso para {len(progress_list)} trilhas para usuario {user_id}')
            return progress_list 
        
        except Exception as e: 
            logger.error(f'Erro ao buscar progresso do usuario {user_id}: {e}')
            raise 
    
    def start_learning_path(self, user_id: str, path_id: str) -> UserPathProgress:
        """Inicia uma trilha de aprendizado para um usuario"""
        try:
            # Verifica se já existe progresso
            existing_progress = self.get_user_progress(user_id, path_id)
            if existing_progress:
                logger.info(f"Usuário {user_id} já iniciou a trilha {path_id}")
                return existing_progress
            
            # Cria novo progresso
            progress = UserPathProgress(
                user_id=user_id,
                path_id=path_id,
                started_at=datetime.utcnow()
            )
            
            doc_id = f"{user_id}_{path_id}"
            self.progress_collection.document(doc_id).set(progress.model_dump())
            
            logger.info(f"Trilha {path_id} iniciada para usuário {user_id}")
            return progress
            
        except Exception as e:
            logger.error(f"Erro ao iniciar trilha: {e}")
            raise
    
    def update_progress(self, progress: UserPathProgress) -> UserPathProgress:
        """Atualiza o progresso do usuário"""
        try:
            doc_id = f"{progress.user_id}_{progress.path_id}"
            self.progress_collection.document(doc_id).set(progress.model_dump())
            
            logger.info(f"Progresso atualizado para usuário {progress.user_id} na trilha {progress.path_id}")
            return progress
            
        except Exception as e:
            logger.error(f"Erro ao atualizar progresso: {e}")
            raise
    
    def complete_mission(self, user_id: str, path_id: str, mission_id: str, score: int) -> UserPathProgress:
        """Marca uma missão como concluída"""
        try:
            progress = self.get_user_progress(user_id, path_id)
            if not progress:
                raise ValueError(f"Progresso não encontrado para usuário {user_id} na trilha {path_id}")
            
            # Adiciona missão concluída se não estiver na lista
            if mission_id not in progress.completed_missions:
                progress.completed_missions.append(mission_id)
                progress.total_score += score
            
            # Atualiza progresso
            self.update_progress(progress)
            
            logger.info(f"Missão {mission_id} concluída para usuário {user_id}")
            return progress
            
        except Exception as e:
            logger.error(f"Erro ao concluir missão: {e}")
            raise
    
    def complete_module(self, user_id: str, path_id: str, module_id: str) -> UserPathProgress:
        """Marca um módulo como concluído"""
        try:
            progress = self.get_user_progress(user_id, path_id)
            if not progress:
                raise ValueError(f"Progresso não encontrado para usuário {user_id} na trilha {path_id}")
            
            # Adiciona módulo concluído se não estiver na lista
            if module_id not in progress.completed_modules:
                progress.completed_modules.append(module_id)
            
            # Atualiza progresso
            self.update_progress(progress)
            
            logger.info(f"Módulo {module_id} concluído para usuário {user_id}")
            return progress
            
        except Exception as e:
            logger.error(f"Erro ao concluir módulo: {e}")
            raise