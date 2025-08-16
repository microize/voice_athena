"""Dependency injection container for Athena application"""
import logging
from typing import Dict, Any, Callable
from functools import lru_cache

from athena.services.problem_service import ProblemService
from athena.services.user_service import UserService
from athena.services.interview_service import InterviewService
from athena.services.interview_agent_service import InterviewAgentService
from athena.core.security import SecurityManager
from athena.core.config import settings

logger = logging.getLogger(__name__)

class DependencyContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        
        # Register default services
        self._register_default_services()
    
    def _register_default_services(self):
        """Register default application services"""
        # Register services as singletons
        self.register_singleton("problem_service", ProblemService)
        self.register_singleton("user_service", UserService)
        self.register_singleton("interview_service", InterviewService)
        self.register_singleton("interview_agent_service", InterviewAgentService)
        self.register_singleton("security_manager", SecurityManager)
        
        # Register configuration
        self.register_instance("settings", settings)
        
        logger.info("Default services registered in dependency container")
    
    def register_singleton(self, name: str, service_class: type):
        """Register a service as singleton"""
        self._factories[name] = lambda: service_class()
        logger.debug(f"Registered singleton service: {name}")
    
    def register_factory(self, name: str, factory: Callable):
        """Register a factory function for a service"""
        self._factories[name] = factory
        logger.debug(f"Registered factory service: {name}")
    
    def register_instance(self, name: str, instance: Any):
        """Register a pre-created instance"""
        self._singletons[name] = instance
        logger.debug(f"Registered instance: {name}")
    
    def get(self, name: str) -> Any:
        """Get a service instance"""
        # Check if it's a pre-registered instance
        if name in self._singletons:
            return self._singletons[name]
        
        # Check if it's a factory-created singleton
        if name in self._factories:
            if name not in self._singletons:
                self._singletons[name] = self._factories[name]()
                logger.debug(f"Created singleton instance: {name}")
            return self._singletons[name]
        
        raise ValueError(f"Service '{name}' not found in container")
    
    def clear(self):
        """Clear all services (useful for testing)"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        logger.debug("Dependency container cleared")

# Global container instance
_container = DependencyContainer()

def get_container() -> DependencyContainer:
    """Get the global dependency container"""
    return _container

# Dependency provider functions for FastAPI
@lru_cache()
def get_problem_service() -> ProblemService:
    """Get problem service instance"""
    return _container.get("problem_service")

@lru_cache()
def get_user_service() -> UserService:
    """Get user service instance"""
    return _container.get("user_service")

@lru_cache()
def get_interview_service() -> InterviewService:
    """Get interview service instance"""
    return _container.get("interview_service")

@lru_cache()
def get_interview_agent_service() -> InterviewAgentService:
    """Get interview agent service instance"""
    return _container.get("interview_agent_service")

@lru_cache()
def get_security_manager() -> SecurityManager:
    """Get security manager instance"""
    return _container.get("security_manager")

def get_settings():
    """Get application settings"""
    return _container.get("settings")

# Reset cache for testing
def reset_dependency_cache():
    """Reset LRU cache for testing purposes"""
    get_problem_service.cache_clear()
    get_user_service.cache_clear()
    get_interview_service.cache_clear()
    get_interview_agent_service.cache_clear()
    get_security_manager.cache_clear()