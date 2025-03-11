import subprocess
from log import logger


class PostgreSQLInstaller:
    def __init__(self, target_server: str, allow_ip: str, db_password: str) -> None:
        self.target_server = target_server
        self.allow_ip = allow_ip
        self.db_password = db_password

    def install_via_ansible(self):
        """Запускает Ansible-плейбук для установки на сервере PostgreSQL и Клиента psql на второй машине"""
        logger.info("Запускаем Ansible для сервера %s", self.target_server)

        command = [
            "ansible-playbook",
            "-i",
            f"{self.target_server},",
            "-u",
            "root",
            "--extra-vars",
            f"allowed_ip={self.allow_ip} db_password={self.db_password}",
            "1_application/ansible-setup/install_postgresql.yml",
        ]

        try:
            subprocess.run(command, text=True, check=True)
            logger.info("Ansible успешно установил PostgreSQL!")
            print("--------------------------------------------------")
            print("Установка PostgreSQL завершилась успешно!")
            print("--------------------------------------------------")
        except subprocess.CalledProcessError as e:
            logger.error("Ошибка установки PostgreSQL! Код: %s", e.returncode)
            logger.error("Вывод ошибки: \n %s", e)
            print("--------------------------------------------------")
            print("Установка PostgreSQL провалилась!")
            print("--------------------------------------------------")
            return

        command = [
            "ansible-playbook",
            "-i",
            f"{self.allow_ip},",
            "-u",
            "root",
            "--extra-vars",
            f"target_ip={self.target_server} db_password={self.db_password}",
            "1_application/ansible-setup/install_psql_client.yml",
        ]

        try:
            subprocess.run(command, text=True, check=True)
            logger.info("Ansible успешно установил Клиент psql на вторую машину!")
            print("--------------------------------------------------")
            print("Установка psql клиента завершилась успешно!")
            print("--------------------------------------------------")
        except subprocess.CalledProcessError as e:
            print("--------------------------------------------------")
            print("Установка psql клиента провалилась!")
            print("--------------------------------------------------")
            logger.error("Ошибка установки клиента psql! Код: %s", e.returncode)
            logger.error("Вывод ошибки: \n %s", e)
            return

        logger.info("Установка PostgreSQL и Клиента psql завершена успешно!")
        print("--------------------------------------------------")
        print("Установка PostgreSQL и Клиента psql завершена успешно!")
        print("--------------------------------------------------")