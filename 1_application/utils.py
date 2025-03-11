from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Type
from fabric import Connection

from log import logger


class ISshExecutor(ABC):
    @abstractmethod
    def execute(self, command: str) -> str:
        pass


class SshExecutor(ISshExecutor):
    """Класс для работы с SSH-соединением.
    ВАЖНО! Может держать 1 открытое соединение, не поддерживает пул соединений."""

    def __init__(
        self,
        host: str = "",
        user: str = "root",
        password: int = None,
        key: str = str(Path("~/.ssh/id_rsa.pub").expanduser()),
    ):
        self.host = host
        self.user = user
        self.password = password
        self.key = key
        self.connection = None

    def _connect(self) -> None:
        """Устанавливает SSH-соединение."""
        if self.connection:
            return  # Если уже подключены, другое подключение не возможно

        connect_kwargs = {"look_for_keys": True, "key_filename": self.key}
        if self.password:
            connect_kwargs["password"] = self.password
        logger.debug(
            "Данные хоста host:%s, user:%s, key:%s",
            self.host,
            self.user,
            self.key,
        )
        try:
            logger.info("Подключаемся к %s@%s", self.user, self.host)
            self.connection = Connection(
                self.host,
                user=self.user,
                connect_kwargs=connect_kwargs,
                connect_timeout=10,
            )
        except Exception as e:
            logger.critical("Ошибка при установке соединения: %s", e)
            raise e

    def close(self) -> None:
        """Закрывает соединение."""
        if self.connection:
            self.connection.close()
            logger.info("SSH-соединение закрыто")
            self.connection = None

    def __enter__(self):
        """Создаёт постоянное SSH-соединение при входе в контекст."""
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Закрывает соединение при выходе из контекста."""
        self.close()

    def execute(self, command: str) -> str:
        """Выполняет команду через постоянное SSH-соединение."""
        if not self.connection:
            raise RuntimeError(
                "SSH-соединение не установлено. Используйте контекстный менеджер"
            )

        try:
            logger.info("Выполняем команду: %s", command)
            result = self.connection.run(command, hide=True, warn=True)
            logger.info("Результат: %s", result.stdout.strip())
            return result.stdout.strip()
        except Exception as e:
            logger.error("Ошибка при выполнении команды: %s", e)
            return None


class ServerScratcher:

    def __init__(self, ssh_class: Type[ISshExecutor], servers: List[str]) -> None:
        self.ssh_class = ssh_class
        self.servers = servers

    def _select_servers(self) -> str:
        "Вернет ip или имя сервера с наименьшей загрузкой"
        result = dict()
        for server in self.servers:
            logger.info("Собираем данные с %s", server)
            with self.ssh_class(host=server) as conn:
                try:
                    load = conn.execute(
                        "uptime | awk -F'load average: ' '{print $2}' | awk -F', ' '{print $2}'"
                    )
                    if load:
                        result[server] = load
                    else:
                        logger.error(
                            "Не удалось получить загрузку с сервера: %s, он будет удален из списка",
                            server,
                        )
                except Exception as e:
                    result[server] = float("inf")
                    logger.error("Ошибка при получении загрузки: %s", e)
                    continue
        return result

    def get_best_servers(self) -> List[str]:
        servers = self._select_servers()
        logger.info("Загрузка северов: %s", servers)
        if servers:
            sorted_ips = sorted(servers, key=servers.get)
            return sorted_ips[:2]
        logger.info("Установка пойдет на сервер: %s", sorted_ips[0])
