"""Database configuration and session management."""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError
from functools import lru_cache

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Base class for models
Base = declarative_base()

# Lazy initialization - don't create engine until needed
_engine = None
_SessionLocal = None


@lru_cache()
def _get_engine():
    """Get or create database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(
                settings.database_url_sync,
                poolclass=NullPool,
                echo=settings.DEBUG,
                connect_args={"connect_timeout": 2} if "postgresql" in settings.database_url_sync else {},
            )
        except Exception as e:
            logger.warning("Failed to create database engine", error=str(e))
            return None
    return _engine


def _get_session_factory():
    """Get or create session factory (lazy initialization)."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = _get_engine()
        if engine is None:
            return None
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


# Export SessionLocal for backward compatibility - create a dummy one at module level
# that will be replaced when first accessed
def _create_SessionLocal():
    """Create SessionLocal factory."""
    factory = _get_session_factory()
    if factory is None:
        # Return a dummy that will fail gracefully
        class _DummySessionLocal:
            def __call__(self, *args, **kwargs):
                raise RuntimeError("Database not available. Cannot create session in prototype mode.")
            def __enter__(self):
                raise RuntimeError("Database not available. Cannot create session in prototype mode.")
            def __exit__(self, *args):
                pass
        return _DummySessionLocal()
    return factory

# Create SessionLocal - it will lazily initialize when first used
# For direct usage like SessionLocal(), we need a callable that returns a session
class _SessionLocalFactory:
    """SessionLocal factory that lazily initializes."""
    def __call__(self):
        factory = _get_session_factory()
        if factory is None:
            raise RuntimeError("Database not available. Cannot create session in prototype mode.")
        return factory()
    
    def __getattr__(self, name):
        # If accessed as an attribute (for sessionmaker methods), get the actual factory
        factory = _get_session_factory()
        if factory is None:
            raise RuntimeError("Database not available. Cannot access session factory in prototype mode.")
        return getattr(factory, name)

SessionLocal = _SessionLocalFactory()


def get_db():
    """Get database session. Returns None if database is not available (prototype mode)."""
    db = None
    try:
        SessionLocal = _get_session_factory()
        if SessionLocal is None:
            yield None
            return
        
        db = SessionLocal()
        # Test connection
        db.execute(text("SELECT 1"))
        yield db
    except (OperationalError, Exception) as e:
        logger.warning("Database not available, using prototype mode", error=str(e))
        if db:
            try:
                db.close()
            except:
                pass
        yield None
    finally:
        if db:
            try:
                db.close()
            except:
                pass

