
import os
import sys
import logging
import configparser

CONFIG_FILE_PATH = "/Users/Downloads/Test_task/config.ini"
LOG_FILE_PATH = "/Users/Downloads/Test_task.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)


def parse_permissions_string(perm_str):
    try:
        return int(perm_str, 8)
    except ValueError:
        logging.error(f"Некорректный формат прав доступа '{perm_str}'. Ожидается восьмеричное число (например, '755').")
        return None


def apply_permissions_from_config(config_filepath):
    config = configparser.ConfigParser()
    overall_success = True

    if not os.path.exists(config_filepath):
        logging.critical(f"Конфигурационный файл не найден: {config_filepath}")
        return False

    try:
        config.read(config_filepath)
        logging.info(f"Конфигурационный файл '{config_filepath}' успешно прочитан.")
    except configparser.Error as e:
        logging.critical(f"Ошибка при разборе конфигурационного файла '{config_filepath}': {e}")
        return False
    except Exception as e:
        logging.critical(f"Неожиданная ошибка при чтении конфигурационного файла '{config_filepath}': {e}")
        return False

    if not config.sections():
        logging.warning("В конфигурационном файле не найдено ни одной секции.")
        return True

    for section in config.sections():
        logging.info(f"Обработка секции: [{section}]")
        try:
            path = config.get(section, 'path')
            permissions_str = config.get(section, 'permissions')

            parsed_permissions = parse_permissions_string(permissions_str)
            if parsed_permissions is None:
                overall_success = False
                continue

            try:
                os.chmod(path, parsed_permissions)
                logging.info(f"Успешно применены права '{permissions_str}' к '{path}'")
            except FileNotFoundError:
                logging.error(f"Ошибка: Файл или папка не найдены по пути '{path}'. Права не применены.")
                overall_success = False
            except PermissionError:
                logging.error(f"Ошибка доступа: Недостаточно прав для изменения прав '{path}'. Могут потребоваться права root.")
                overall_success = False
            except OSError as e:
                logging.error(f"Ошибка ОС при изменении прав для '{path}': {e}")
                overall_success = False
        except configparser.NoOptionError as e:
            logging.error(f"Ошибка конфигурации в секции '{section}': Отсутствует обязательный параметр '{e.option}'.")
            overall_success = False
        except Exception as e:
            logging.error(f"Неожиданная ошибка при обработке секции '{section}': {e}")
            overall_success = False

    return overall_success


if __name__ == "__main__":
    if len(sys.argv) > 1:
        CONFIG_FILE_PATH = sys.argv[1]
    else:
        logging.warning(f"Путь к конфигурационному файлу не указан. Используется путь по умолчанию: {CONFIG_FILE_PATH}")

    log_dir = os.path.dirname(LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
            logging.info(f"Создана директория для логов: {log_dir}")
        except OSError as e:
            print(f"Критическая ошибка: Не удалось создать директорию для логов '{log_dir}': {e}", file=sys.stderr)
            sys.exit(1)

    if apply_permissions_from_config(CONFIG_FILE_PATH):
        logging.info("Скрипт завершил работу успешно.")
        sys.exit(0)
    else:
        logging.error("Скрипт завершил работу с ошибками.")
        sys.exit(1)
