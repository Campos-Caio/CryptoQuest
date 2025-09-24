"""
Sistema de EventBus para gerenciar eventos do sistema de recompensas.
Permite desacoplamento entre componentes através de eventos.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any
from collections import defaultdict
from app.models.events import BaseEvent, EventType

logger = logging.getLogger(__name__)


class EventBus:
    """
    Sistema de eventos para desacoplar componentes do sistema de recompensas.
    
    Permite:
    - Emitir eventos de forma assíncrona
    - Registrar handlers para tipos específicos de eventos
    - Processar eventos em paralelo
    - Log de auditoria de eventos
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._event_log: List[BaseEvent] = []
        self._max_log_size = 1000  # Limite de eventos no log
        
    async def emit(self, event: BaseEvent) -> None:
        """
        Emite um evento para todos os handlers registrados.
        
        Args:
            event: Evento a ser emitido
        """
        try:
            logger.info(f"🚀 Emitindo evento: {event.event_type} para usuário {event.user_id}")
            
            # Adicionar ao log de auditoria
            self._add_to_log(event)
            
            # Buscar handlers para este tipo de evento
            handlers = self._handlers.get(event.event_type, [])
            
            if not handlers:
                logger.warning(f"Nenhum handler registrado para evento {event.event_type}")
                return
            
            # Executar handlers em paralelo
            tasks = []
            for handler in handlers:
                task = asyncio.create_task(self._execute_handler(handler, event))
                tasks.append(task)
            
            # Aguardar todos os handlers completarem
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verificar se algum handler falhou
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Handler {i} falhou para evento {event.event_type}: {result}")
                    
        except Exception as e:
            logger.error(f"Erro ao emitir evento {event.event_type}: {e}")
            raise
    
    async def subscribe(self, event_type: EventType, handler: Callable[[BaseEvent], None]) -> None:
        """
        Registra um handler para um tipo específico de evento.
        
        Args:
            event_type: Tipo de evento
            handler: Função que processa o evento
        """
        self._handlers[event_type].append(handler)
        logger.info(f"📝 Handler registrado para evento {event_type}")
    
    async def unsubscribe(self, event_type: EventType, handler: Callable[[BaseEvent], None]) -> None:
        """
        Remove um handler de um tipo específico de evento.
        
        Args:
            event_type: Tipo de evento
            handler: Handler a ser removido
        """
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.info(f"🗑️ Handler removido para evento {event_type}")
    
    def get_event_log(self, event_type: EventType = None, user_id: str = None, limit: int = 100) -> List[BaseEvent]:
        """
        Retorna o log de eventos com filtros opcionais.
        
        Args:
            event_type: Filtrar por tipo de evento
            user_id: Filtrar por usuário
            limit: Limite de eventos retornados
            
        Returns:
            Lista de eventos filtrados
        """
        events = self._event_log.copy()
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        return events[-limit:]  # Retorna os mais recentes
    
    def get_handler_count(self, event_type: EventType) -> int:
        """
        Retorna o número de handlers registrados para um tipo de evento.
        
        Args:
            event_type: Tipo de evento
            
        Returns:
            Número de handlers
        """
        return len(self._handlers.get(event_type, []))
    
    async def _execute_handler(self, handler: Callable, event: BaseEvent) -> None:
        """
        Executa um handler de forma segura.
        
        Args:
            handler: Handler a ser executado
            event: Evento a ser processado
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Erro no handler para evento {event.event_type}: {e}")
            raise
    
    def _add_to_log(self, event: BaseEvent) -> None:
        """
        Adiciona evento ao log de auditoria.
        
        Args:
            event: Evento a ser adicionado
        """
        self._event_log.append(event)
        
        # Manter apenas os eventos mais recentes
        if len(self._event_log) > self._max_log_size:
            self._event_log = self._event_log[-self._max_log_size:]
    
    def clear_log(self) -> None:
        """Limpa o log de eventos."""
        self._event_log.clear()
        logger.info("🧹 Log de eventos limpo")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do EventBus.
        
        Returns:
            Dicionário com estatísticas
        """
        event_counts = defaultdict(int)
        for event in self._event_log:
            event_counts[event.event_type] += 1
        
        return {
            "total_events": len(self._event_log),
            "event_counts": dict(event_counts),
            "handlers_per_type": {
                event_type.value: len(handlers) 
                for event_type, handlers in self._handlers.items()
            }
        }


# Instância global do EventBus
event_bus = EventBus()


def get_event_bus() -> EventBus:
    """
    Retorna a instância singleton do EventBus.
    
    Returns:
        Instância do EventBus
    """
    return event_bus
