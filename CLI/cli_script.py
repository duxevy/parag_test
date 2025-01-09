import argparse
from cli_core import CLICore

cli_core = CLICore()


def process_script_file(file_path):
    with open(file_path, 'r', encoding="utf-8-sig") as file:
        for line in file:
            command = line.strip()
            if command not in ("") and (command.find('set_output_file') == -1) and not command.startswith('#'):
                if not cli_core.do_command(command):
                    return False
        return True


# Инициализация аргументов командной строки
parser = argparse.ArgumentParser(description='LowCode скрипт-интерпретатор')
subparsers = parser.add_subparsers(dest='command', help='Команда для выполнения')

# Команда -execute
execute_script_parser = subparsers.add_parser('execute', help='Выполнение скрипт файла')
execute_script_parser.add_argument('script_name', help='Файл скрипта')

# Обработка командной строки
args = parser.parse_args()

# Вызов соответствующей функции
if args.command == 'execute':
    process_script_file(args.script_name)
else:
    print("Неизвестная команда")

    # ------------------ для запуска из PyCharm -----------------------------
    # process_script_file('script_create_business.txt')
    # -----------------------------------------------------------------------
