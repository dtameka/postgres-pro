import click
from log import logger
from utils import ServerScratcher, SshExecutor
from installer import PostgreSQLInstaller


@click.command()
@click.argument("servers")
def main(servers: str):
    logger.info("Начало обработки серверов: [%s]", servers)
    server_list = servers.split(",")

    logger.info("Проверяем загрузку серверов: %s", server_list)
    server_scratcher = ServerScratcher(SshExecutor, server_list)

    logger.info("Вырибаем два лучших сервера: %s", server_list)
    best_servers = server_scratcher.get_best_servers()

    if best_servers[0] and best_servers[1]:
        logger.info(
            "Выбран сервер для установки: %s и для доступа: %s",
            best_servers[0],
            best_servers[1],
        )
    else:
        logger.warning("Доступных серверов < 2. Завершаем работу.")
        return

    installer = PostgreSQLInstaller(
        best_servers[0], allow_ip=best_servers[1], db_password=123
    )

    installer.install_via_ansible()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
