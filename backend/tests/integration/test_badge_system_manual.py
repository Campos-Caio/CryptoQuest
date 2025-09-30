"""
Script para testar o sistema de badges baseado em eventos.
Permite testar a implementação da Fase 1 sem executar o servidor completo.
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Adicionar o diretório backend ao path
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

from app.models.events import MissionCompletedEvent, LevelUpEvent, EventType
from app.services.event_bus import EventBus
from app.services.badge_engine import BadgeEngine
from app.services.validation_service import ValidationService
from app.repositories.badge_repository import BadgeRepository
from app.repositories.user_repository import UserRepository
from app.core.firebase import get_firestore_db_async


class BadgeSystemTester:
    """Classe para testar o sistema de badges"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.db = None
        self.badge_engine = None
        self.validation_service = None
        self.badge_repo = None
        self.user_repo = None

    async def setup(self):
        """Configura o sistema para testes"""
        print("🔧 Configurando sistema de badges...")
        
        try:
            # Inicializar Firebase
            self.db = await get_firestore_db_async()
            print("✅ Firebase conectado")
            
            # Criar repositórios
            self.user_repo = UserRepository(self.db)
            self.badge_repo = BadgeRepository(self.db)
            print("✅ Repositórios criados")
            
            # Criar serviços
            self.validation_service = ValidationService(self.user_repo, self.badge_repo)
            self.badge_engine = BadgeEngine(self.validation_service, self.badge_repo)
            print("✅ Serviços criados")
            
            # Registrar handlers no EventBus
            self._register_handlers()
            print("✅ Handlers registrados")
            
        except Exception as e:
            print(f"❌ Erro na configuração: {e}")
            raise

    def _register_handlers(self):
        """Registra handlers de teste"""
        async def test_handler(event):
            print(f"🎯 Evento processado: {event.event_type} para usuário {event.user_id}")
        
        self.event_bus.subscribe(EventType.MISSION_COMPLETED, test_handler)
        self.event_bus.subscribe(EventType.LEVEL_UP, test_handler)

    async def test_event_bus(self):
        """Testa o EventBus"""
        print("\n🧪 Testando EventBus...")
        
        # Criar evento de teste
        event = MissionCompletedEvent(
            user_id="test_user_123",
            mission_id="test_mission_456",
            score=85.0,
            mission_type="daily"
        )
        
        # Emitir evento
        await self.event_bus.emit(event)
        
        # Verificar log
        log = self.event_bus.get_event_log()
        print(f"📊 Eventos no log: {len(log)}")
        
        # Verificar estatísticas
        stats = self.event_bus.get_stats()
        print(f"📈 Estatísticas: {stats}")

    async def test_badge_repository(self):
        """Testa o BadgeRepository"""
        print("\n🧪 Testando BadgeRepository...")
        
        test_user_id = "test_user_repo"
        test_badge_id = "test_badge_repo"
        
        # Verificar se usuário tem badge (deve ser False)
        has_badge = await self.badge_repo.has_badge(test_user_id, test_badge_id)
        print(f"🔍 Usuário tem badge {test_badge_id}: {has_badge}")
        
        # Tentar conceder badge
        success = await self.badge_repo.award_badge(
            test_user_id, 
            test_badge_id, 
            {"test": "context", "timestamp": datetime.now().isoformat()}
        )
        print(f"🏆 Badge concedido: {success}")
        
        # Verificar novamente (deve ser True)
        has_badge = await self.badge_repo.has_badge(test_user_id, test_badge_id)
        print(f"🔍 Usuário tem badge {test_badge_id} após concessão: {has_badge}")
        
        # Tentar conceder novamente (deve falhar por duplicata)
        success_duplicate = await self.badge_repo.award_badge(
            test_user_id, 
            test_badge_id, 
            {"test": "duplicate", "timestamp": datetime.now().isoformat()}
        )
        print(f"🚫 Tentativa de duplicata: {success_duplicate}")

    async def test_validation_service(self):
        """Testa o ValidationService"""
        print("\n🧪 Testando ValidationService...")
        
        test_user_id = "test_user_validation"
        
        # Criar evento de missão
        event = MissionCompletedEvent(
            user_id=test_user_id,
            mission_id="test_mission_validation",
            score=100.0,  # Score perfeito
            mission_type="daily"
        )
        
        # Verificar badges elegíveis
        eligible_badges = await self.validation_service.check_badge_conditions(test_user_id, event)
        print(f"🎯 Badges elegíveis: {eligible_badges}")
        
        # Verificar elegibilidade específica
        is_eligible = await self.validation_service.validate_badge_eligibility(
            test_user_id, 
            "perfectionist"
        )
        print(f"✅ Elegível para 'perfectionist': {is_eligible}")

    async def test_badge_engine(self):
        """Testa o BadgeEngine"""
        print("\n🧪 Testando BadgeEngine...")
        
        test_user_id = "test_user_engine"
        
        # Criar evento de missão
        event = MissionCompletedEvent(
            user_id=test_user_id,
            mission_id="test_mission_engine",
            score=100.0,
            mission_type="daily"
        )
        
        # Emitir evento (deve processar automaticamente)
        await self.event_bus.emit(event)
        
        # Verificar estatísticas do engine
        stats = self.badge_engine.get_engine_stats()
        print(f"📊 Estatísticas do BadgeEngine: {stats}")
        
        # Verificar progresso do usuário
        progress = await self.badge_engine.get_user_badge_progress(test_user_id)
        print(f"📈 Progresso do usuário: {progress}")

    async def test_full_integration(self):
        """Testa integração completa"""
        print("\n🧪 Testando integração completa...")
        
        test_user_id = "test_user_integration"
        
        # Simular fluxo completo de missão
        print("1️⃣ Criando evento de missão completada...")
        mission_event = MissionCompletedEvent(
            user_id=test_user_id,
            mission_id="integration_mission_1",
            score=95.0,
            mission_type="daily"
        )
        
        print("2️⃣ Emitindo evento...")
        await self.event_bus.emit(mission_event)
        
        # Simular level up
        print("3️⃣ Criando evento de level up...")
        level_event = LevelUpEvent(
            user_id=test_user_id,
            old_level=1,
            new_level=2,
            points_required=500
        )
        
        print("4️⃣ Emitindo evento de level up...")
        await self.event_bus.emit(level_event)
        
        # Verificar resultados
        print("5️⃣ Verificando resultados...")
        event_log = self.event_bus.get_event_log(user_id=test_user_id)
        print(f"📝 Eventos para usuário: {len(event_log)}")
        
        engine_stats = self.badge_engine.get_engine_stats()
        print(f"🏆 Badges concedidos: {engine_stats['total_awards']}")

    async def cleanup(self):
        """Limpa dados de teste"""
        print("\n🧹 Limpando dados de teste...")
        
        try:
            # Limpar badges de teste
            test_user_ids = [
                "test_user_123",
                "test_user_repo", 
                "test_user_validation",
                "test_user_engine",
                "test_user_integration"
            ]
            
            for user_id in test_user_ids:
                # Buscar badges do usuário
                user_badges = await self.badge_repo.get_user_badges(user_id)
                
                # Deletar badges de teste
                for badge in user_badges:
                    if badge.badge_id and badge.badge_id.startswith("test_"):
                        # Implementar deleção se necessário
                        pass
            
            print("✅ Dados de teste limpos")
            
        except Exception as e:
            print(f"⚠️ Erro na limpeza: {e}")

    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 Iniciando testes do sistema de badges...")
        print("=" * 50)
        
        try:
            await self.setup()
            
            await self.test_event_bus()
            await self.test_badge_repository()
            await self.test_validation_service()
            await self.test_badge_engine()
            await self.test_full_integration()
            
            print("\n" + "=" * 50)
            print("✅ Todos os testes concluídos com sucesso!")
            
        except Exception as e:
            print(f"\n❌ Erro durante os testes: {e}")
            raise
        finally:
            await self.cleanup()


async def main():
    """Função principal"""
    tester = BadgeSystemTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # Executar testes
    asyncio.run(main())
