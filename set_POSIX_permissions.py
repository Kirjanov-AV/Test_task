import configparser
import os
import stat
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/set_permissions.log"), 
        logging.StreamHandler(sys.stdout) 
    ]
)


def parse_permissions(perm_str):
    try:
        return int(perm_str, 8)
    except ValueError:
        logging.error(f"Некорректный формат прав: {perm_str}")
        return None

def set_permissions(config_file):
    config = configparser.ConfigParser()
    try:
        config.read(config_file)
    except Exception as e:
        logging.error(f"Ошибка при чтении конфигурационного файла: {e}")
        return False 

    success = True  

    for section in config.sections():
        try:
            path = config[section]['path']
            permissions_str = config[section]['permissions']

            permissions = parse_permissions(permissions_str)
            if permissions is None:
                success = False
                continue 

            try:
                os.chmod(path, permissions)
                logging.info(f"Права {permissions_str} установлены для {path}")
            except FileNotFoundError:
                logging.error(f"Файл или папка не найдены: {path}")
                success = False 
            except OSError as e:
                logging.error(f"Ошибка при установке прав для {path}: {e}")
                success = False 
        except KeyError as e:
            logging.error(f"Отсутствует обязательный параметр в секции {section}: {e}")
            success = False 

    return success 

if __name__ == "__main__":
    CONFIG_FILE = "/etc/set_permissions/config.ini" 
    if not os.path.exists(os.path.dirname(CONFIG_FILE)):
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE))
            logging.info(f"Создан каталог {os.path.dirname(CONFIG_FILE)}")
        except OSError as e:
            logging.error(f"Не удалось создать каталог {os.path.dirname(CONFIG_FILE)}: {e}")
            sys.exit(1) 

    status = set_permissions(CONFIG_FILE)

    if status:
        logging.info("Скрипт успешно завершен.")
        sys.exit(0) 
    else:
        logging.error("Скрипт завершен c ошибками.")
        sys.exit(1) 
