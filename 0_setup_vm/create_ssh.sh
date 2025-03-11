#!/bin/bash

# Проверяем аргументы
if [ "$#" -ne 5 ]; then
    echo "Использование: $0 <IP-адрес> <пользователь> <пароль пользователя> <пароль root> <путь до публичного SSH-ключа>"
    exit 1
fi

# Проверяем, установлен ли sshpass
if ! command -v sshpass &> /dev/null; then
    echo "Ошибка: sshpass не установлен!"
    echo "Установите его командой:"
    echo "  sudo apt install sshpass   # Для Debian/Ubuntu"
    echo "  sudo yum install sshpass   # Для RHEL/CentOS"
    exit 1
fi

IP="$1"
USER="$2"
USER_PASS="$3"
ROOT_PASS="$4"
SSH_KEY="$5"

# Проверяем, существует ли публичный ключ
if [ ! -f "$SSH_KEY" ]; then
    echo "Ошибка: Файл SSH-ключа '$SSH_KEY' не найден!"
    exit 1
fi

echo "Копируем SSH-ключ '$SSH_KEY' на сервер..."
ssh-keyscan -H "$IP" >> ~/.ssh/known_hosts

# Копируем SSH-ключ во временную папку на сервер
sshpass -p "$USER_PASS" scp "$SSH_KEY" "$USER@$IP:/tmp/authorized_keys"

# Проверяем, является ли система Debian
sshpass -p "$USER_PASS" ssh "$USER@$IP" <<EOF
    if grep -q "ID=debian" /etc/os-release; then
        echo "Обнаружена Debian, устанавливаем sudo..."
        echo "$ROOT_PASS" | su -c "apt install -y sudo"
    fi
EOF

# Подключаемся и выполняем команды от root
sshpass -p "$USER_PASS" ssh "$USER@$IP" <<EOF
    echo "$ROOT_PASS" | su -c "mkdir -p /root/.ssh && chmod 700 /root/.ssh"

    echo "$ROOT_PASS" | su -c "mv /tmp/authorized_keys /root/.ssh/authorized_keys"

    echo "$ROOT_PASS" | su -c "chmod 600 /root/.ssh/authorized_keys"
    echo "$ROOT_PASS" | su -c "chown root:root /root/.ssh/authorized_keys"

    # Разрешаем вход только по SSH-ключу
    echo "$ROOT_PASS" | su -c "sed -i 's/^#PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config"
    echo "$ROOT_PASS" | su -c "systemctl restart sshd"

    echo ""
    echo -e "\e[32mНастройка завершена! Теперь root может заходить по SSH-ключу.\e[0m"
EOF

# Проверяем, является ли система Debian
if grep -q "ID=debian" /etc/os-release; then
    echo "Обнаружена Debian, устанавливаем sudo..."
    apt install -y sudo
fi


