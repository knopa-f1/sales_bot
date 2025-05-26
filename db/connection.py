from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from config_data.config import config_settings


class Database:

    def __init__(self) -> None:
        self.__engine: AsyncEngine = create_async_engine(config_settings.db.dsn,
                                                         echo=config_settings.env_type == "test")
        session = async_sessionmaker(bind=self.__engine)
        self.__session: AsyncSession = session()

    @property
    def engine(self) -> AsyncEngine:
        return self.__engine

    @property
    def session(self) -> AsyncSession:
        return self.__session


database: Database = Database()
