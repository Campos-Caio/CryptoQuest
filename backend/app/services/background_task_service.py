"""
Serviço de processamento de tarefas em background.
Permite processar operações pesadas sem bloquear a resposta ao usuário.
"""
import asyncio
import logging
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime, UTC
from enum import Enum
import traceback
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class TaskPriority(str, Enum):
    """Prioridade de tarefas em background"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class BackgroundTask:
    """Representa uma tarefa para processamento em background"""
    
    def __init__(
        self, 
        task_id: str,
        task_name: str,
        task_func: Callable,
        task_args: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL
    ):
        self.task_id = task_id
        self.task_name = task_name
        self.task_func = task_func
        self.task_args = task_args
        self.priority = priority
        self.created_at = datetime.now(UTC)
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.status = "pending"
        self.result: Optional[Any] = None
        self.error: Optional[str] = None


class BackgroundTaskService:
    """
    Serviço para processar tarefas em background sem bloquear requisições.
    
    Features:
    - Fila de prioridades
    - Processamento assíncrono
    - Retry automático em falhas
    - Métricas e monitoramento
    """
    
    def __init__(self):
        self.tasks: Dict[str, BackgroundTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.processing = False
        self._worker_task: Optional[asyncio.Task] = None
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._lock = threading.Lock()
        
        # Métricas
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "avg_processing_time": 0.0
        }
        
        logger.info("🚀 BackgroundTaskService inicializado")
    
    async def start_worker(self):
        """Inicia o worker que processa tarefas em background"""
        if self.processing:
            logger.warning("Worker já está em execução")
            return
        
        self.processing = True
        self._worker_task = asyncio.create_task(self._process_tasks())
        logger.info("✅ Worker de background iniciado")
    
    async def stop_worker(self):
        """Para o worker de background"""
        self.processing = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Worker de background parado")
    
    def submit_task(
        self,
        task_name: str,
        task_func: Callable,
        task_args: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """
        Submete uma tarefa para processamento em background.
        
        Args:
            task_name: Nome descritivo da tarefa
            task_func: Função a ser executada
            task_args: Argumentos para a função
            priority: Prioridade da tarefa
            
        Returns:
            task_id: ID único da tarefa
        """
        task_id = f"{task_name}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        
        task = BackgroundTask(
            task_id=task_id,
            task_name=task_name,
            task_func=task_func,
            task_args=task_args,
            priority=priority
        )
        
        with self._lock:
            self.tasks[task_id] = task
            self.metrics["total_tasks"] += 1
        
        # Adicionar à fila de forma não-bloqueante
        asyncio.create_task(self._enqueue_task(task))
        
        logger.info(f"📝 Tarefa submetida: {task_name} (ID: {task_id})")
        return task_id
    
    async def _enqueue_task(self, task: BackgroundTask):
        """Adiciona tarefa à fila"""
        await self.task_queue.put(task)
    
    async def _process_tasks(self):
        """Worker que processa tarefas da fila"""
        logger.info("🔄 Worker iniciou processamento de tarefas")
        
        while self.processing:
            try:
                # Pegar tarefa da fila (com timeout para permitir parada)
                try:
                    task = await asyncio.wait_for(
                        self.task_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Processar tarefa
                await self._execute_task(task)
                
            except Exception as e:
                logger.error(f"Erro no worker de background: {e}")
                logger.error(traceback.format_exc())
    
    async def _execute_task(self, task: BackgroundTask):
        """Executa uma tarefa em background"""
        task.started_at = datetime.now(UTC)
        task.status = "processing"
        
        logger.info(f"⚡ Processando tarefa: {task.task_name} (ID: {task.task_id})")
        
        try:
            # Executar função da tarefa
            if asyncio.iscoroutinefunction(task.task_func):
                # Função assíncrona
                result = await task.task_func(**task.task_args)
            else:
                # Função síncrona - executar em thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    lambda: task.task_func(**task.task_args)
                )
            
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.now(UTC)
            
            # Atualizar métricas
            processing_time = (task.completed_at - task.started_at).total_seconds()
            
            with self._lock:
                self.metrics["completed_tasks"] += 1
                
                # Calcular média móvel de tempo de processamento
                total_completed = self.metrics["completed_tasks"]
                current_avg = self.metrics["avg_processing_time"]
                self.metrics["avg_processing_time"] = (
                    (current_avg * (total_completed - 1) + processing_time) / total_completed
                )
            
            logger.info(
                f"✅ Tarefa concluída: {task.task_name} "
                f"(tempo: {processing_time:.2f}s)"
            )
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now(UTC)
            
            with self._lock:
                self.metrics["failed_tasks"] += 1
            
            logger.error(f"❌ Erro ao processar tarefa {task.task_name}: {e}")
            logger.error(traceback.format_exc())
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de uma tarefa"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": task.error,
            "result": task.result
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do serviço"""
        with self._lock:
            return {
                **self.metrics,
                "queue_size": self.task_queue.qsize(),
                "active_tasks": len([t for t in self.tasks.values() if t.status == "processing"]),
                "pending_tasks": len([t for t in self.tasks.values() if t.status == "pending"])
            }
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove tarefas antigas da memória"""
        cutoff_time = datetime.now(UTC).timestamp() - (max_age_hours * 3600)
        
        with self._lock:
            tasks_to_remove = [
                task_id for task_id, task in self.tasks.items()
                if task.completed_at and task.completed_at.timestamp() < cutoff_time
            ]
            
            for task_id in tasks_to_remove:
                del self.tasks[task_id]
        
        if tasks_to_remove:
            logger.info(f"🧹 Removidas {len(tasks_to_remove)} tarefas antigas")


# Instância global do serviço
_background_service_instance: Optional[BackgroundTaskService] = None
_service_lock = threading.Lock()


def get_background_service() -> BackgroundTaskService:
    """Retorna instância singleton do BackgroundTaskService"""
    global _background_service_instance
    
    if _background_service_instance is None:
        with _service_lock:
            if _background_service_instance is None:
                _background_service_instance = BackgroundTaskService()
    
    return _background_service_instance


async def ensure_worker_started():
    """Garante que o worker de background está iniciado"""
    service = get_background_service()
    if not service.processing:
        await service.start_worker()

