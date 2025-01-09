import json
import os
import datetime
from cli_rest_api_client import RestAPIClient
from colorama import init, Fore, Style

init()
label_key = "__label__"
supported_label_locales = ['en_us', 'zh_cn', 'fr_fr', 'de_de', 'nl_nl', 'pl_pl', 'ru_ru']
# соответсвие команд и методов для работы через __call_method
methods = {
    'create_organization': ['_create_organization', 'Organizations'],
    'delete_organization': ['_delete_organization', 'Organizations'],
    'show_organizations': ['_show_organizations', 'Organizations'],
    'show_organization': ['_show_organization', 'Organizations'],
    'create_user': ['_create_user', 'User / Business User'],
    'delete_user': ['_delete_user', 'User / Business User'],
    'show_user': ['_show_user', 'User / Business User'],
    'create_business_user': ['_create_business_user', 'User / Business User'],
    'set_business_user': ['_set_business_user', 'User / Business User'],
    'show_business_user': ['_show_business_user', 'User / Business User'],
    'login': ['_login', 'User / Business User'],
    'work_as_admin': ['_work_as_admin', 'User / Business User'],
    'set_password': ['_set_password', 'User / Business User'],
    'show_trustors': ['_show_trustors', 'User / Business User'],
    'show_rights': ['_show_rights', 'User / Business User'],
    'use_business': ['_use_business', 'User / Business User'],
    'use_service': ['_use_service', 'User / Business User'],
    'set_access_config': ['_set_access_config', 'Access Config'],
    'delete_access_config': ['_delete_access_config', 'Access Config'],
    'show_access_configs': ['_show_access_configs', 'Access Config'],
    'show_current_access_config': ['_show_current_access_config', 'Access Config'],
    'use_access_config': ['_use_access_config', 'Access Config'],
    'raw_request_business': ['_raw_request_business', 'Raw Requests'],
    'raw_request_admin': ['_raw_request_admin', 'Raw Requests'],
    'raw_request': ['_raw_request', 'Raw Requests'],
    'set_script_variable': ['_set_script_variable', 'Script Variables'],
    'set_script_variable_from_response': ['_set_script_variable_from_response', 'Script Variables'],
    'set_script_variable_from_file': ['_set_script_variable_from_file', 'Script Variables'],
    'set_script_variable_from_attribute': ['_set_script_variable_from_attribute', 'Script Variables'],
    'show_script_variables': ['_show_script_variables', 'Script Variables'],
    'set_permissions_variable': ['_set_permissions_variable', 'EntityType Permissions / Permissions Variables'],
    'create_permissions_variable': ['_create_permissions_variable', 'EntityType Permissions / Permissions Variables'],
    'edit_permissions_variable': ['_edit_permissions_variable', 'EntityType Permissions / Permissions Variables'],
    'set_permission': ['_set_permission', 'EntityType Permissions / Permissions Variables'],
    'delete_permission': ['_delete_permission', 'EntityType Permissions / Permissions Variables'],
    'show_permissions': ['_show_permissions', 'EntityType Permissions / Permissions Variables'],
    'save_permissions_variable': ['_save_permissions_variable', 'EntityType Permissions / Permissions Variables'],
    'discard_permissions_variable': ['_discard_permissions_variable', 'EntityType Permissions / Permissions Variables'],
    'delete_permissions_variable': ['_delete_permissions_variable', 'EntityType Permissions / Permissions Variables'],
    'show_permissions_variables': ['_show_permissions_variables', 'EntityType Permissions / Permissions Variables'],
    'set_permissions_from_variable': ['_set_permissions_from_variable', 'EntityType Permissions / Permissions Variables'],
    'create_business': ['_create_business', 'Businesses (Admin)'],
    'delete_business': ['_delete_business', 'Businesses (Admin)'],
    'show_businesses': ['_show_businesses', 'Businesses (Admin)'],
    'set_business_permissions': ['_set_business_permissions', 'BusinessPermissions (Admin)'],
    'delete_business_permissions': ['_delete_business_permissions', 'BusinessPermissions (Admin)'],
    'show_business_permissions': ['_show_business_permissions', 'BusinessPermissions (Admin)'],
    'import_schema': ['_import_schema', 'Schema'],
    'create_attribute': ['_create_attribute', 'Attributes'],
    'edit_attribute': ['_edit_attribute', 'Attributes'],
    'set_attribute_key': ['_set_attribute_key', 'Attributes'],
    'set_attribute_label': ['_set_attribute_label', 'Attributes'],
    'set_attribute_type': ['_set_attribute_type', 'Attributes'],
    'set_attribute_flags': ['_set_attribute_flags', 'Attributes'],
    'set_attribute_fixed_values': ['_set_attribute_fixed_values', 'Attributes'],
    'set_attribute_fixed_display_values': ['_set_attribute_fixed_display_values', 'Attributes'],
    'set_attribute_validator': ['_set_attribute_validator', 'Attributes'],
    'delete_attribute_validator': ['_delete_attribute_validator', 'Attributes'],
    'show_attribute_validators': ['_show_attribute_validators', 'Attributes'],
    'save_attribute': ['_save_attribute', 'Attributes'],
    'discard_attribute': ['_discard_attribute', 'Attributes'],
    'delete_attribute': ['_delete_attribute', 'Attributes'],
    'show_attributes': ['_show_attributes', 'Attributes'],
    'create_entity_type': ['_create_entity_type', 'EntityTypes'],
    'edit_entity_type': ['_edit_entity_type', 'EntityTypes'],
    'set_entity_type_parent': ['_set_entity_type_parent', 'EntityTypes'],
    'set_entity_type_state_machine': ['_set_entity_type_state_machine', 'EntityTypes'],
    'set_entity_type_flags': ['_set_entity_type_flags', 'EntityTypes'],
    'set_entity_type_label': ['_set_entity_type_label', 'EntityTypes'],
    'add_attribute': ['_add_attribute', 'EntityTypes'],
    'set_attribute_default_value': ['_set_attribute_default_value', 'EntityTypes'],
    'remove_attribute': ['_remove_attribute', 'EntityTypes'],
    'edit_computed_value': ['_edit_computed_value', 'EntityTypes'],
    'set_variable_attribute': ['_set_variable_attribute', 'EntityTypes'],
    'set_variable_attribute_from': ['_set_variable_attribute_from', 'EntityTypes'],
    'set_variable_default_value': ['_set_variable_default_value', 'EntityTypes'],
    'set_variable_workflow': ['_set_variable_workflow', 'EntityTypes'],
    'delete_variable': ['_delete_variable', 'EntityTypes'],
    'show_variables': ['_show_variables', 'EntityTypes'],
    'set_expression': ['_set_expression', 'EntityTypes'],
    'set_computed_value_flags': ['_set_computed_value_flags', 'EntityTypes'],
    'close_computed_value': ['_close_computed_value', 'EntityTypes'],
    'discard_computed_value': ['_discard_computed_value', 'EntityTypes'],
    'show_computed_values': ['_show_computed_values', 'EntityTypes'],
    'add_reference_to': ['_add_reference_to', 'EntityTypes'],
    'add_reference_from': ['_add_reference_from', 'EntityTypes'],
    'remove_reference_to': ['_remove_reference_to', 'EntityTypes'],
    'remove_reference_from': ['_remove_reference_from', 'EntityTypes'],
    'save_entity_type': ['_save_entity_type', 'EntityTypes'],
    'discard_entity_type': ['_discard_entity_type', 'EntityTypes'],
    'delete_entity_type': ['_delete_entity_type', 'EntityTypes'],
    'show_entity_types': ['_show_entity_types', 'EntityTypes'],
    'edit_reference': ['_edit_reference', 'References'],
    'set_reference_to_key': ['_set_reference_to_key', 'References'],
    'set_reference_from_key': ['_set_reference_from_key', 'References'],
    'set_reference_flags': ['_set_reference_flags', 'References'],
    'set_reference_type': ['_set_reference_type', 'References'],
    'save_reference': ['_save_reference', 'References'],
    'discard_reference': ['_discard_reference', 'References'],
    'delete_reference': ['_delete_reference', 'References'],
    'show_references': ['_show_references', 'References'],
    'create_entity': ['_create_entity', 'Entities'],
    'edit_entity': ['_edit_entity', 'Entities'],
    'set_entity_attribute_value': ['_set_entity_attribute_value', 'Entities'],
    'add_entity_reference_to': ['_add_entity_reference_to', 'Entities'],
    'remove_entity_reference_to': ['_remove_entity_reference_to', 'Entities'],
    'save_entity': ['_save_entity', 'Entities'],
    'discard_entity': ['_discard_entity', 'Entities'],
    'delete_entity': ['_delete_entity', 'Entities'],
    'show_entities': ['_show_entities', 'Entities'],
    'add_entity_state_category': ['_add_entity_state_category', 'State Categories / State Machine'],
    'delete_entity_state_category': ['_delete_entity_state_category', 'State Categories / State Machine'],
    'show_entity_state_categories': ['_show_entity_state_categories', 'State Categories / State Machine'],
    'create_state_machine': ['_create_state_machine', 'State Categories / State Machine'],
    'edit_state_machine': ['_edit_state_machine', 'State Categories / State Machine'],
    'add_sm_state': ['_add_sm_state', 'State Categories / State Machine'],
    'set_sm_state': ['_set_sm_state', 'State Categories / State Machine'],
    'delete_sm_state': ['_delete_sm_state', 'State Categories / State Machine'],
    'show_sm_states': ['_show_sm_states', 'State Categories / State Machine'],
    'add_sm_transition': ['_add_sm_transition', 'State Categories / State Machine'],
    'delete_sm_transitions': ['_delete_sm_transitions', 'State Categories / State Machine'],
    'show_sm_transitions': ['_show_sm_transitions', 'State Categories / State Machine'],
    'save_state_machine': ['_save_state_machine', 'State Categories / State Machine'],
    'discard_state_machine': ['_discard_state_machine', 'State Categories / State Machine'],
    'delete_state_machine': ['_delete_state_machine', 'State Categories / State Machine'],
    'show_state_machines': ['_show_state_machines', 'State Categories / State Machine'],
    'help': ['_help', ''],
    'use_legacy_searcher': ['_use_legacy_searcher', ''],
    'set_output_file': ['init_output_script', ''],
    'set_log': ['_set_log', ''],
    'generate_readme': ['_generate_readme', ''],
    'ignore_object_existence_error': ['_ignore_object_existence_error', '']
}
# список команд, которые могут выполнятся без <service_path>
do_not_validate_commands = ('help',
                            'use_legacy_searcher',
                            'set_output_file',
                            'set_log',
                            'create_organization',
                            'delete_organization',
                            'show_organization',
                            'show_organizations',
                            'create_user',
                            'delete_user',
                            'show_user',
                            'create_business_user',
                            'set_business_user',
                            'show_business_user',
                            'login',
                            'work_as_admin',
                            'set_password',
                            'show_trustors',
                            'show_rights',
                            'use_business',
                            'use_service',
                            'set_access_config',
                            'delete_access_config',
                            'show_access_configs',
                            'show_current_access_config',
                            'use_access_config',
                            'raw_request',
                            'set_script_variable',
                            'set_script_variable_from_response',
                            'set_script_variable_from_file',
                            'show_script_variables',
                            'set_permissions_variable',
                            'create_permissions_variable',
                            'edit_permissions_variable',
                            'set_permission',
                            'delete_permission',
                            'show_permissions',
                            'save_permissions_variable',
                            'discard_permissions_variable',
                            'delete_permissions_variable',
                            'show_permissions_variables',
                            'generate_readme',
                            'ignore_object_existence_error'
                            )


class CLICore:
    """ Класс для работы с LowCode CLI """

    def __init__(self):
        super().__init__()

        self.opened_entity = {}
        self.opened_entity_type = {}
        self.opened_attribute = {}
        self.opened_entity_type_references = []
        self.opened_reference = {}
        self.opened_state_machine = {}
        self.opened_computed_attribute = {}
        self.opened_permissions = {}
        self.opened_entity_type_permissions = []
        self.opened_permissions_variable = {}

        self.rest_api_client = RestAPIClient()

        # use default access_config
        self.rest_api_client.use_access_config('default')

        self.output_script = ""
        self.log_path = ""
        self._set_log('log.txt')
        self.script_variables = {}
        self.permissions_variables = {
            "default": [
                {
                    'level': 'Business',
                    'type': 'CreateEntity'
                },
                {
                    'level': 'Business',
                    'type': 'ReadEntity'
                },
                {
                    'level': 'Business',
                    'type': 'UpdateEntity'
                },
                {
                    'level': 'Business',
                    'type': 'DeleteEntity'
                },
                {
                    'level': 'Business',
                    'type': 'QuerySchema'
                },
                {
                    'level': 'Business',
                    'type': 'QueryVector'
                }
            ]

        }
        self.legacy_searcher = False
        self.rewrite_all_permissions = False
        self.access_level = 'business'
        self.ignore_object_existence_error = False

    def __validate_flags(self, flags, valid_values):
        for flag in flags:
            if flag.lower() not in valid_values:
                return False

        return True

    def __remove_none_from_array(self, flags):
        if flags is not None:
            new_flags = []
            for flag in flags:
                if flag is not None:
                    new_flags.append(flag)
            return new_flags
        else:
            return None

    def __insert_script_variable_value(self, arg):

        if arg is not None:
            for key, value in self.script_variables.items():
                arg = arg.replace('{{' + key + '}}', str(value))

        return arg

    def __escape_string(self, string):
        string = string.encode('unicode_escape').decode()
        string = string.replace('"', '\\"')
        # string = string.replace("'", "\\'")
        return string

    def __unescape_json(self, escaped_string):
        """Преобразование экранированной строки в JSON"""
        prefix_error = "__unescape_json error:"

        unescaped_string = escaped_string.encode().decode('unicode-escape')
        try:
            unescaped_json = json.loads(unescaped_string)
        except json.decoder.JSONDecodeError as e:
            self.print_error(prefix_error, f"Ошибка загрузки JSON {unescaped_string}:\n{e}")
            return None

        return unescaped_json

    def __validate_access_config(self):
        prefix_error = "Ошибка параметров вызова: "
        if ('baseUrl' not in self.rest_api_client.access_config) or (not self.rest_api_client.access_config['baseUrl']):
            self.print_error(prefix_error, f"Отсутвует baseUrl в access_config")
            return False
        if ('service_path' not in self.rest_api_client.access_config) or (not self.rest_api_client.access_config['service_path']):
            self.print_error(prefix_error, f"Отсутвует service_path в access_config, используйте команду \'use_service <service_path>\'")
            return False
        return True

    def __validate_business_organization_entity_type(self, business_id):
        prefix_error = "__check_business_organization_entity_type error"

        current_access_config = self.rest_api_client.access_config
        self.rest_api_client.access_config['service_path'] = 'registry/masterdata'
        self.rest_api_client.access_config['businessId'] = business_id
        response = self.rest_api_client.get_entity_types(access_level='admin')
        self.rest_api_client.access_config = current_access_config

        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        entity_types = response.json()
        is_business_organization_entity_type = False
        if len(entity_types) > 0:
            for entity_type in entity_types:
                if entity_type['key'].upper() == 'BUSINESS_ORGANIZATION':
                    is_business_organization_entity_type = True
                    break
        else:
            self.print_error(prefix_error, f"Entity types для {business_id} в MD отсутствуют")
            return False

        return is_business_organization_entity_type

    def __print_and_log(self, string):
        self.write_to_file(self.log_path, f"{datetime.datetime.now()}: {string}")
        print(string)

    def __init_file_to_write(self, file_path, cont=False):
        """Инициализация файла для записи в него"""
        prefix_error = "__init_file_to_write error:"

        try:
            if cont:
                with open(file_path, 'a') as file:
                    file.write('')
            else:
                with open(file_path, 'w') as file:
                    file.write('')
            return True
        except FileNotFoundError:
            self.print_error(prefix_error, f"Проблема инициализации файла {file_path}")
            return False

    def __call_method(self, args):
        prefix_error = "Ошибка выполнения:"
        if args[0].lower() in methods:

            # проверка возможности выполнения команды
            if args[0].lower() not in do_not_validate_commands:
                if not self.__validate_access_config():
                    return False

            method_name = methods[args[0].lower()][0]
            method_args = tuple(args[1:])

            if hasattr(self, method_name):
                method = getattr(self, method_name, None)
                if callable(method):
                    result = method(*method_args)
                    if result:
                        self.print_success('---Ok---')
                    return result

                else:
                    self.print_error(prefix_error, f"Метод с именем '{method_name}' не является вызываемым.")
                    return False
            else:
                self.print_error(prefix_error, f"Метод с именем '{method_name}' не найден в классе.")
                return False

        else:
            self.print_error(prefix_error, f"Неизвестная команда: {args[0]}")
            return False

    def is_pycharm_terminal(self):
        return "PYCHARM_HOSTED" in os.environ

    def parse_args(self, raw_arg):
        """ Метод обработки аргументов """
        args = []

        # 0: starting search; 1: non quote delimiter; 2: quote delimiter;
        state = 0
        i = 0  # следующий индекс строки
        from_pos = 0  # с какой позиции извлекаем получаем подстроку

        # цикл по кажому символу входной команды
        while i < len(raw_arg):
            ch = raw_arg[i]
            if state == 0:  # Начальный режим
                if ch == '"' and (i == 0 or raw_arg[i - 1] != "\\"):
                    # Аргумент команды заключен в кавычки. Значит аргумент может быть как строка с пробелами так и с запятой
                    # Сабстрока начинается со следующего после кавычек символа
                    from_pos = i + 1
                    state = 2
                elif ch > ' ':
                    # В данный режим мы попадаем, когда ожидаем непосредственно саму команду. Запятая не является частью команды
                    if ch == ',':
                        if len(args) == 1:
                            # первая запятая не может отделяет первый и второй аргумент, это значит второй аргумент - None
                            args.append(None)
                        from_pos = i + 1
                    else:
                        from_pos = i
                    state = 1
            elif state == 1:
                # Обработка разделителя команд: пробел или запятая
                if ch <= ' ' or ch == ',':
                    state = 0
                    arg = raw_arg[from_pos:i].strip()
                    if ch == ',':
                        args.append(arg if len(arg) > 0 else None)

                        # для обработи случая create_attribute ,,Test --> ['create_attribute', None, 'Test']
                        # для обработи случая create_attribute Test, --> ['create_attribute', 'Test', None]
                        continue
                    elif len(arg) > 0:
                        args.append(arg)
                elif ch == '"' and (i == 0 or raw_arg[i - 1] != "\\"):
                    # Если после разделитля ',' встречаются двойные кавычки
                    from_pos = i + 1
                    state = 2
            elif state == 2:
                if ch == '"' and (i == 0 or raw_arg[i - 1] != "\\"):
                    # Обрабатываем закрывающие кавычки -- конец команды
                    state = 0
                    arg = raw_arg[from_pos:i]
                    args.append(arg if len(arg) > 0 else None)

            i += 1

        if state == 1:
            arg = raw_arg[from_pos:i]
            args.append(arg if len(arg) > 0 else None)

        return args

    def write_to_file(self, file_path, string):
        """Запись в файл"""
        if file_path not in (None, ''):
            with open(file_path, 'a', encoding="utf-8") as file:
                file.write(string + f"\n")

    def print_error(self, prefix_error, error_text):
        """Вывод ошибки"""
        self.__print_and_log('')
        self.__print_and_log(f"{prefix_error}")
        self.__print_and_log(f"----------------------------------")
        print(Fore.RED + f"{error_text}" + Style.RESET_ALL)
        self.write_to_file(self.log_path, f"{datetime.datetime.now()}: {error_text}")
        self.__print_and_log('')

    def print_success(self, text):
        """ Вывод успешного результата """
        print(Fore.GREEN + f"{text}" + Style.RESET_ALL)
        self.write_to_file(self.log_path, f"{datetime.datetime.now()}: {text}")
        self.__print_and_log('')

    def do_command(self, command):
        """Исполнение команды"""
        self.write_to_file(self.output_script, command)
        self.write_to_file(self.log_path, f"{datetime.datetime.now()}: {command}")

        args = self.parse_args(command)

        # замена указаний переменной {{variable}} её значением
        if len(args) > 0:
            new_args = []
            for arg in args:
                new_args.append(self.__insert_script_variable_value(arg))
            args = new_args
        else:
            # пустая строка
            return True

        return self.__call_method(args)

    """ Organizations """

    def _create_organization(self, *args):
        """Создать организацию
        create_organization <name> <business_email> [<country>]"""
        prefix_error = "_create_organization error:"

        name = args[0] if len(args) > 0 else None
        business_email = args[1] if len(args) > 1 else None
        country = args[2] if len(args) > 2 else "US"

        if not name:
            self.print_error(prefix_error, f"Отсутствует name")
            return False

        if not business_email:
            self.print_error(prefix_error, f"Отсутствует business_email")
            return False

        # создание организации в registry
        data = {
            "email": business_email,
            "name": name,
            "country": country,
        }

        response = self.rest_api_client.create_organization(data)

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        business_id = response.json()['id']
        self.print_success(f"Организация {name} в registry создана, business_id: {business_id}")

        # создание бизнеса в registry
        current_access_config = self.rest_api_client.access_config
        self.rest_api_client.access_config['service_path'] = 'registry'
        result = self._create_business(business_id, '')
        self.rest_api_client.access_config = current_access_config

        if not result:
            return False

        self.print_success(f"Бизнес {business_id} в registry создан")

        # создание бизнеса в MD
        current_access_config = self.rest_api_client.access_config
        self.rest_api_client.access_config['service_path'] = 'registry/masterdata'
        result = self._create_business(business_id, '')
        self.rest_api_client.access_config = current_access_config

        if not result:
            return False

        self.print_success(f"Бизнес {business_id} в MD создан")

        # создание организации в MD
        data = [
            {
                "attributeValues": [
                    {
                        "attributeKey": "NAME",
                        "valueLocales": [{"value": name}]
                    },
                    {
                        "attributeKey": "REGISTRY_ID",
                        "valueLocales": [{"value": business_id}]

                    }
                ],
                "entityTypeKey": "BUSINESS_ORGANIZATION"
            }
        ]

        current_access_config = self.rest_api_client.access_config
        self.rest_api_client.access_config['service_path'] = 'registry/masterdata'
        self.rest_api_client.access_config['businessId'] = business_id
        response = self.rest_api_client.create_entity(data, "", 'admin')
        self.rest_api_client.access_config = current_access_config

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        self.print_success(f"BUSINESS_ORGANIZATION для {business_id} в MD создана")

        return True

    def _delete_organization(self, *args):
        """Удалить организацию
        delete_organization <name>"""
        prefix_error = "_delete_organization error:"

        name = args[0] if len(args) > 0 else None

        if not name:
            self.print_error(prefix_error, f"Отсутствует name")
            return False

        # получение организации из registry
        response = self.rest_api_client.get_organizations(f"Name={name}")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        organizations = response.json()

        if len(organizations) > 0:
            business_id = organizations[0]['id']

            # удаление организации из registry
            response = self.rest_api_client.delete_organization(f"{business_id}")

            if response.status_code != 204:
                self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                return False

            self.print_success(f"Организация {name} ({business_id}) в registry удалена")

            # удаление бизнеса из registry
            current_access_config = self.rest_api_client.access_config
            self.rest_api_client.access_config['service_path'] = 'registry'
            result = self._delete_business(business_id, 'Force')
            self.rest_api_client.access_config = current_access_config

            if not result:
                return False

            self.print_success(f"Бизнес {business_id} в registry удалён")

            # удаление бизнеса из MD
            current_access_config = self.rest_api_client.access_config
            self.rest_api_client.access_config['service_path'] = 'registry/masterdata'
            result = self._delete_business(business_id, 'Force')
            self.rest_api_client.access_config = current_access_config

            if not result:
                return False

            self.print_success(f"Бизнес {business_id} в MD удалён")

        else:
            self.__print_and_log(f"Организация отсутствует")
        self.__print_and_log('')

        return True

    def _show_organization(self, *args):
        """Показать конкретную организацию
        show_organization <name>"""
        prefix_error = "_show_organization error:"

        name = args[0] if len(args) > 0 else None

        if not name:
            self.print_error(prefix_error, f"Отсутствует name")
            return False

        # получение организации из registry
        response = self.rest_api_client.get_organizations(f"Name={name}")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        organizations = response.json()

        if len(organizations) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"{organizations[0]['name']} ({organizations[0]['id']}):")
            self.__print_and_log(f"----------------------------------")
            self.__print_and_log(f"        business_email: {organizations[0]['email']}")
            self.__print_and_log(f"        country: {organizations[0]['country']}")
        else:
            self.__print_and_log(f"Организация отсутствует")
        self.__print_and_log('')

        return True

    def _show_organizations(self, *args):
        """Показать все организации
        show_organizations [SkipMDCheck]"""
        prefix_error = "_show_organizations error:"

        SkipMDCheck = args[0] if len(args) > 0 else ""

        if SkipMDCheck.lower() == 'skipmdcheck':
            SkipMDCheck = True
        else:
            SkipMDCheck = False

        i = 0
        organizations = []
        while True:
            # получение организации из registry
            response = self.rest_api_client.get_organizations(f"Skip={i}")

            if response.status_code != 200:
                self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                return False

            if len(response.json()) == 0:
                break

            organizations.extend(response.json())
            i += 100

        if len(organizations) > 0:

            self.__print_and_log('')
            self.__print_and_log(f"Доступные организации: ")
            self.__print_and_log(f"----------------------------------")
            for organization in organizations:
                business_id = organization['id']

                if not SkipMDCheck and self.__validate_business_organization_entity_type(business_id):
                    # получение организаций из MD
                    data = {
                        "entitiesOptions": {
                            "includeAttributeValuesByAttributeKeys": ["*"],
                            "includeEntityWorkflowStatesByWorkflowKeys": ["*"],
                            "includeReferences": False
                        },
                        "entitiesByEntityTypeKeys": ['BUSINESS_ORGANIZATION'],
                        "locale": "none",
                        "entitiesByAttributeValues": [
                            {
                                "attributeKey": "REGISTRY_ID",
                                "operator": "Equals",
                                "value": business_id
                            }
                        ]
                    }

                    current_access_config = self.rest_api_client.access_config
                    self.rest_api_client.access_config['service_path'] = 'registry/masterdata'
                    self.rest_api_client.access_config['businessId'] = business_id
                    response = self.rest_api_client.get_entities_vector(data, 0, 'admin')
                    self.rest_api_client.access_config = current_access_config

                    if response.status_code != 200:
                        self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                        return False

                    if len(response.json()) > 0:
                        is_org_in_md = True
                    else:
                        is_org_in_md = False
                else:
                    is_org_in_md = False

                self.__print_and_log(f"{organization['name']} ({business_id}):")
                self.__print_and_log(f"        business_email: {organization['email']}")
                self.__print_and_log(f"        country: {organization['country']}")
                if not SkipMDCheck:
                    self.__print_and_log(f"        наличие в MD: {is_org_in_md}")
        else:
            self.__print_and_log(f"Организации отсутствуют")
        self.__print_and_log('')

        return True

    """ Users/BusinessUsers """

    def _create_user(self, *args):
        """Создать пользователя (доступ уровня Admin)
        create_user <login> <password> <first_name> <last_name> [<country>], [<language>]"""
        prefix_error = "_create_user error:"

        login = args[0] if len(args) > 0 else None
        password = args[1] if len(args) > 1 else None
        first_name = args[2] if len(args) > 2 else None
        last_name = args[3] if len(args) > 3 else None
        country = args[4] if len(args) > 4 else "US"
        language = args[5] if len(args) > 5 else "EN_US"

        if not login:
            self.print_error(prefix_error, f"Отсутствует login")
            return False

        if not password:
            self.print_error(prefix_error, f"Отсутствует password")
            return False

        if not first_name:
            self.print_error(prefix_error, f"Отсутствует first_name")
            return False

        if not last_name:
            self.print_error(prefix_error, f"Отсутствует last_name")
            return False

        if not country:
            self.print_error(prefix_error, f"Отсутствует country")
            return False

        if not language:
            self.print_error(prefix_error, f"Отсутствует language")
            return False

        data = {
            "email": login,
            "password": password,
            "firstName": first_name,
            "lastName": last_name,
            "language": language,
            "country": country,
            "privacyPolicyAccepted": True,
            "startingStatus": "NonObjected"
        }

        response = self.rest_api_client.create_user(data)

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        return True

    def _delete_user(self, *args):
        """Удалить пользователя (доступ уровня Admin)
        delete_user <login>"""
        prefix_error = "_delete_user error:"

        login = args[0] if len(args) > 0 else None

        if not login:
            self.print_error(prefix_error, f"Отсутствует login")
            return False

        # получение данных пользователя
        response = self.rest_api_client.get_user(f"LoginOrEmail={login}")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        if 'id' in response.json():
            user_id = response.json()['id']

            # удаление пользователя
            response = self.rest_api_client.delete_user(f"{user_id}")

            if response.status_code != 204:
                self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                return False

        else:
            self.print_error(prefix_error, f"Пользователь {login} отсутствует")
            return False

        return True

    def _show_user(self, *args):
        """Показать данные пользователя (доступ уровня Admin)
        show_user <login>"""
        prefix_error = "show_user error:"

        login = args[0] if len(args) > 0 else None

        if not login:
            self.print_error(prefix_error, f"Отсутствует login")
            return False

        # получение данных пользователя
        response = self.rest_api_client.get_user(f"LoginOrEmail={login}")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        user = response.json()

        self.__print_and_log('')
        self.__print_and_log(f"Данные пользователя: ")
        self.__print_and_log(f"----------------------------------")
        self.__print_and_log(f"email: {user['email']}")
        self.__print_and_log(f"id: {user['id']}")
        self.__print_and_log(f"firstName: {user['firstName']}")
        self.__print_and_log(f"lastName: {user['lastName']}")
        self.__print_and_log(f"language: {user['language']}")
        self.__print_and_log(f"country: {user['country']}")

        return True

    def _create_business_user(self, *args):
        """Создать бизнесс пользователя (доступ уровня Admin)
        create_business_user <login> <buisness_id> <space1> <role1>[ <spaceN> <roleN>]"""
        prefix_error = "create_business_user error:"

        login = args[0] if len(args) > 0 else None
        business_id = args[1] if len(args) > 1 else None
        scopes = []
        i = 2
        while len(args) > (i + 1):
            scopes.append(
                {
                    "space": args[i],
                    "role": args[i + 1]
                }
            )
            i += 2

        if not login:
            self.print_error(prefix_error, f"Отсутствует login")
            return False

        if not business_id:
            self.print_error(prefix_error, f"Отсутствует business_id")
            return False

        if len(scopes) < 1:
            self.print_error(prefix_error, f"Отсутствует, как минимум, одна пара <space> <role>")
            return False

        # получение данных пользователя
        response = self.rest_api_client.get_user(f"LoginOrEmail={login}")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        user_id = response.json()['id']
        first_name = response.json()['firstName']
        last_name = response.json()['lastName']

        # создание трастов
        data = {
            "trustorId": business_id,
            "trusteeId": user_id,
            "trustRights": scopes
        }

        response = self.rest_api_client.create_trusts(data)

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        # получение business_org_id из masterdata
        data = {
            "entitiesOptions": {
                "includeAttributeValuesByAttributeKeys": ["*"],
                "includeEntityWorkflowStatesByWorkflowKeys": ["*"],
                "includeReferences": False
            },
            "entitiesByEntityTypeKeys": ['BUSINESS_ORGANIZATION'],
            "locale": "none",
            "entitiesByAttributeValues": [
                {
                    "attributeKey": "REGISTRY_ID",
                    "operator": "Equals",
                    "value": business_id
                }
            ]
        }

        current_access_config = self.rest_api_client.access_config
        self.rest_api_client.access_config['service_path'] = 'registry/masterdata'
        self.rest_api_client.access_config['businessId'] = business_id
        response = self.rest_api_client.get_entities_vector(data, 0, 'admin')
        self.rest_api_client.access_config = current_access_config

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        if len(response.json()) > 0:
            business_org_id = response.json()[0]['id']
        else:
            self.print_error(prefix_error, f"BUSINESS_ORGANIZATION в MD не найдена! Бизнес контакт в MD не создан.")
            return False

        # создание business_contact в MD
        data = [
            {
                "attributeValues": [
                    {
                        "attributeKey": "FIRST_NAME",
                        "valueLocales": [{"value": first_name}]
                    },
                    {
                        "attributeKey": "REGISTRY_ID",
                        "valueLocales": [{"value": user_id}]

                    },
                    {
                        "attributeKey": "LAST_NAME",
                        "valueLocales": [{"value": last_name}]

                    },
                    {
                        "attributeKey": "PERSONAL_EMAIL",
                        "valueLocales": [{"value": login}]
                    }
                ],
                "referencedTo": [
                    {
                        "entityId": business_org_id,
                        "key": "BUSINESS"
                    }
                ],
                "entityTypeKey": "BUSINESS_CONTACT"
            }
        ]

        current_access_config = self.rest_api_client.access_config
        self.rest_api_client.access_config['service_path'] = 'registry/masterdata'
        self.rest_api_client.access_config['businessId'] = business_id
        response = self.rest_api_client.create_entity(data, "", 'admin')
        self.rest_api_client.access_config = current_access_config

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        return True

    def _set_business_user(self, *args):
        """Изменить параметры бизнесс пользователя (доступ уровня Admin)
        set_business_user <login> <buisness_id> <space1> <role1>[ <spaceN> <roleN>]"""
        prefix_error = "set_business_user error:"

        login = args[0] if len(args) > 0 else None
        business_id = args[1] if len(args) > 1 else None
        scopes = []
        i = 2
        while len(args) > (i + 1):
            scopes.append(
                {
                    "space": args[i],
                    "role": args[i + 1]
                }
            )
            i += 2

        if not login:
            self.print_error(prefix_error, f"Отсутствует login")
            return False

        if not business_id:
            self.print_error(prefix_error, f"Отсутствует business_id")
            return False

        if len(scopes) < 1:
            self.print_error(prefix_error, f"Отсутствует, как минимум, одна пара <space> <role>")
            return False

        # получение данных пользователя
        response = self.rest_api_client.get_user(f"LoginOrEmail={login}")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        user_id = response.json()['id']

        # создание трастов
        data = {
            "trustorId": business_id,
            "trusteeId": user_id,
            "trustRights": scopes
        }

        response = self.rest_api_client.create_trusts(data)

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        return True

    def _show_business_user(self, *args):
        """Показать бизнесс пользователя (доступ уровня Admin)
        show_business_user <login> <buisness_id>"""
        prefix_error = "show_business_user error:"

        login = args[0] if len(args) > 0 else None
        business_id = args[1] if len(args) > 1 else None

        if not login:
            self.print_error(prefix_error, f"Отсутствует login")
            return False

        if not business_id:
            self.print_error(prefix_error, f"Отсутствует business_id")
            return False

        # получение данных пользователя
        response = self.rest_api_client.get_user(f"LoginOrEmail={login}")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        user_id = response.json()['id']

        # получение BUSINESS_CONTACT из masterdata
        data = {
            "entitiesOptions": {
                "includeAttributeValuesByAttributeKeys": ["*"],
                "includeEntityWorkflowStatesByWorkflowKeys": ["*"],
                "includeReferences": False
            },
            "entitiesByEntityTypeKeys": ['BUSINESS_CONTACT'],
            "locale": "none",
            "entitiesByAttributeValues": [
                {
                    "attributeKey": "REGISTRY_ID",
                    "operator": "Equals",
                    "value": user_id
                }
            ]
        }

        current_access_config = self.rest_api_client.access_config
        self.rest_api_client.access_config['service_path'] = 'registry/masterdata'
        self.rest_api_client.access_config['businessId'] = business_id
        response = self.rest_api_client.get_entities_vector(data, 0, 'admin')
        self.rest_api_client.access_config = current_access_config

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        business_contacts = response.json()

        if len(business_contacts) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Данные бизнес-контакта: ")
            self.__print_and_log(f"----------------------------------")
            for attribute_value in business_contacts[0]['attributeValues']:
                self.__print_and_log(f"{attribute_value['attributeKey']}: {attribute_value['valueLocales'][0]['value']}")
        else:
            self.__print_and_log(f"Бизнес-контакт отсутвует в Masterdata")
        self.__print_and_log('')

        return True

    def _login(self, *args):
        """Логин пользователя
        login <login> <password>"""
        prefix_error = "login error:"

        login = args[0] if len(args) > 0 else None
        password = args[1] if len(args) > 1 else None

        if not login:
            self.print_error(prefix_error, f"Отсутствует login")
            return False

        if password is None:
            self.print_error(prefix_error, f"Отсутствует пароль")
            return False

        response = self.rest_api_client.get_user_token(self.rest_api_client.access_config['baseUrl'], login, password)
        # в случае успешного выполнения - возвращяется токен
        if not response:
            self.print_error(prefix_error, f"Токен не получен")
            return False

        self.rest_api_client.access_config['api_key'] = response
        self.rest_api_client.update_api_key()
        self.rest_api_client.access_config['user_email'] = login
        self.rest_api_client.access_config['password'] = password

        return True

    def _work_as_admin(self, *args):
        """Выполнять команды через админ контроллеры
        work_as_admin"""
        self.access_level = 'admin'
        return True

    def _set_password(self, *args):
        """Изменение пароля пользователя
        set_password <old_password> <new_password>"""
        prefix_error = "set_password error:"

        old_password = args[0] if len(args) > 0 else None
        new_password = args[1] if len(args) > 1 else None

        if old_password is None:
            self.print_error(prefix_error, f"Отсутствует старый пароль")
            return False

        if new_password is None:
            self.print_error(prefix_error, f"Отсутствует новый пароль")
            return False

        data = {
            "currentPassword": old_password,
            "newPassword": new_password
        }

        response = self.rest_api_client.set_password(data)

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        return True

    def _show_trustors(self, *args):
        """Показ всех бизнесов (trustors) пользователя
        show_trustors"""
        prefix_error = "show_trustors error:"

        response = self.rest_api_client.get_trustees('WithDetails=true')

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        trustors = response.json()

        if len(trustors) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные бизнесы: ")
            self.__print_and_log(f"----------------------------------")
            for trustor in trustors:
                self.__print_and_log(f"{trustor['trustor']['name']}: {trustor['trustorId']}")
        else:
            self.__print_and_log(f"Доступные бизнесы отсутствуют")
        self.__print_and_log('')

        return True

    def _show_rights(self, *args):
        """Показ прав пользователя (trusts)
        show_rights"""
        prefix_error = "show_rights error:"

        response = self.rest_api_client.get_trustees('WithDetails=true')

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        trustors = response.json()

        if len(trustors) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Имеющиеся права: ")
            self.__print_and_log(f"----------------------------------")
            for trustor in trustors:
                self.__print_and_log(f"{trustor['trustor']['name']} ({trustor['trustorId']}):")
                if 'trustRights' in trustor and len(trustor['trustRights']) > 0:
                    for trust_right in trustor['trustRights']:
                        self.__print_and_log(f"      {trust_right['space']}: {trust_right['role']}")
                else:
                    self.__print_and_log(f"Права для этого бизнеса отсутствуют")

        else:
            self.__print_and_log(f"Доступные бизнесы отсутствуют")
        self.__print_and_log('')

        return True

    def _use_business(self, *args):
        """Логин бизнес-пользователя
        use_business <id>"""
        prefix_error = "use_business error:"

        business_id = args[0] if len(args) > 0 else None

        if not business_id:
            self.print_error(prefix_error, f"Отсутствует business_id")
            return False

        response = self.rest_api_client.get_business_user_token(self.rest_api_client.access_config['baseUrl'], None, business_id, password=None, with_context=True, get_user_token=False)

        if hasattr(response, 'status_code'):
            self.print_error(prefix_error, f"Бизнес-токен с контекстом не получен")
            return False

        self.access_level = 'business'

        self.rest_api_client.access_config['api_key'] = response
        self.rest_api_client.update_api_key()
        self.rest_api_client.access_config['businessId'] = business_id
        self.rest_api_client.access_config['business_email'] = self.rest_api_client.access_config['user_email']
        del self.rest_api_client.access_config['user_email']

        return True

    def _use_service(self, *args):
        """Установить сервис для пользования
        use_service <service_path>"""
        prefix_error = "use_service error:"

        service_path = args[0] if len(args) > 0 else None

        if not service_path:
            self.print_error(prefix_error, f"Отсутствует service_path")
            return False

        self.rest_api_client.access_config['service_path'] = service_path

        return True

    """ Access Configs """

    def _set_access_config(self, *args):
        """Задать конфигурацию доступа
        set_access_config <key>,[ <service_path>], <baseUrl>,[ <businessId>],[ <business_email>],[ <user_email>],[ <password>],[ <api_key>]"""
        prefix_error = "_set_access_config error:"

        key = args[0] if len(args) > 0 else None
        service_path = args[1] if len(args) > 1 else None
        base_url = args[2] if len(args) > 2 else None
        business_id = args[3] if len(args) > 3 else None
        business_email = args[4] if len(args) > 4 else None
        user_email = args[5] if len(args) > 5 else None
        password = args[6] if len(args) > 6 else None
        api_key = args[7] if len(args) > 7 else None

        if not key:
            self.print_error(prefix_error, f"Отсутствует key")
            return False

        if not base_url:
            self.print_error(prefix_error, f"Отсутствует base_url")
            return False

        # загружаем access_configs из файла
        with open("access_configs.json") as input_file:
            try:
                access_configs = json.load(input_file)
            except json.decoder.JSONDecodeError as e:
                self.print_error(prefix_error, f"Ошибка загрузки JSON access_configs.json:\n{e}")
                return False

        new_access_config = {
            "key": key,
            "baseUrl": base_url
        }
        if service_path:
            new_access_config['service_path'] = service_path
        if business_id:
            new_access_config['businessId'] = business_id
        if business_email:
            new_access_config['business_email'] = business_email
        if user_email:
            new_access_config['user_email'] = user_email
        if password:
            new_access_config['password'] = password
        if api_key:
            new_access_config['api_key'] = api_key

        new_access_configs = []
        for access_config in access_configs:
            if access_config['key'].lower() != key.lower():
                new_access_configs.append(access_config)

        new_access_configs.append(new_access_config)

        # записываем new_access_configs в файл
        with open("access_configs.json", "w") as outfile:
            json.dump(new_access_configs, outfile)

        return True

    def _delete_access_config(self, *args):
        """Удалить конфигурацию доступа
        delete_access_config <key>"""
        prefix_error = "_delete_access_config error:"

        key = args[0] if len(args) > 0 else None

        if not key:
            self.print_error(prefix_error, f"Отсутствует key")
            return False

        # загружаем access_configs из файла
        with open("access_configs.json") as input_file:
            try:
                access_configs = json.load(input_file)
            except json.decoder.JSONDecodeError as e:
                self.print_error(prefix_error, f"Ошибка загрузки JSON access_configs.json:\n{e}")
                return False

        access_config_exists = False
        new_access_configs = []
        for access_config in access_configs:
            if access_config['key'].lower() == key.lower():
                access_config_exists = True
            else:
                new_access_configs.append(access_config)

        if not access_config_exists:
            self.print_error(prefix_error, f"Access Config {key} не найден")
            return False

        # записываем access_configs в файл
        with open("access_configs.json", "w") as outfile:
            json.dump(new_access_configs, outfile)

        return True

    def _show_access_configs(self, *args):
        """Показать все конфигурации доступа
        show_access_configs"""
        prefix_error = "_show_access_configs error:"

        # загружаем access_configs из файла
        with open("access_configs.json") as input_file:
            try:
                access_configs = json.load(input_file)
            except json.decoder.JSONDecodeError as e:
                self.print_error(prefix_error, f"Ошибка загрузки JSON access_configs.json:\n{e}")
                return False

        if len(access_configs) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные конфигурации доступа:")
            self.__print_and_log(f"----------------------------------")
            for access_config in access_configs:
                self.__print_and_log(f"{access_config['key']}:")
                if 'service_path' in access_config:
                    self.__print_and_log(f"    service_path = {access_config['service_path']}")
                self.__print_and_log(f"    baseUrl = {access_config['baseUrl']}")
                if 'businessId' in access_config:
                    self.__print_and_log(f"    businessId = {access_config['businessId']}")
                if 'business_email' in access_config:
                    self.__print_and_log(f"    business_email = {access_config['business_email']}")
                if 'user_email' in access_config:
                    self.__print_and_log(f"    user_email = {access_config['user_email']}")
                if 'password' in access_config:
                    self.__print_and_log(f"    password = {access_config['password']}")
                if 'api_key' in access_config:
                    self.__print_and_log(f"    api_key = {access_config['api_key']}")

        else:
            self.__print_and_log(f"Конфигурации доступа отсутствуют")

        self.__print_and_log('')
        return True

    def _show_current_access_config(self, *args):
        """Показать текущую конфигурацию доступа
        show_current_access_config"""
        prefix_error = "_show_current_access_config error:"

        current_access = self.rest_api_client.access_config

        # загружаем access_configs из файла
        with open("access_configs.json") as input_file:
            try:
                access_configs = json.load(input_file)
            except json.decoder.JSONDecodeError as e:
                self.print_error(prefix_error, f"Ошибка загрузки JSON access_configs.json:\n{e}")
                return False

        current_access_config = {}
        if len(access_configs) > 0:
            for access_config in access_configs:
                if current_access['key'].lower() == access_config['key'].lower():
                    current_access_config = access_config
                    break

        if 'service_path' not in current_access_config or not current_access_config['service_path']:
            current_access_config['service_path'] = 'None'
        if 'businessId' not in current_access_config or not current_access_config['businessId']:
            current_access_config['businessId'] = 'None'
        if 'business_email' not in current_access_config or not current_access_config['business_email']:
            current_access_config['business_email'] = 'None'
        if 'user_email' not in current_access_config or not current_access_config['user_email']:
            current_access_config['user_email'] = 'None'
        if 'password' not in current_access_config or not current_access_config['password']:
            current_access_config['password'] = 'None'
        if 'api_key' not in current_access_config or not current_access_config['api_key']:
            current_access_config['api_key'] = 'None'

        if 'service_path' not in current_access or not current_access['service_path']:
            current_access['service_path'] = 'None'
        if 'businessId' not in current_access or not current_access['businessId']:
            current_access['businessId'] = 'None'
        if 'business_email' not in current_access or not current_access['business_email']:
            current_access['business_email'] = 'None'
        if 'user_email' not in current_access or not current_access['user_email']:
            current_access['user_email'] = 'None'
        if 'password' not in current_access or not current_access['password']:
            current_access['password'] = 'None'
        if 'api_key' not in current_access or not current_access['api_key']:
            current_access['api_key'] = 'None'

        self.__print_and_log('')
        self.__print_and_log(f"Текущая конфигурация доступа {access_config['key']}:")
        self.__print_and_log(f"----------------------------------")
        self.__print_and_log(f"    service_path = {current_access_config['service_path']}"
                             f"{' (Текущее значение: ' + current_access['service_path'] + ')' if current_access['service_path'] != current_access_config['service_path'] else ''}")
        self.__print_and_log(f"    baseUrl = {access_config['baseUrl']}")
        self.__print_and_log(f"    businessId = {current_access_config['businessId']}"
                             f"{' (Текущее значение: ' + current_access['businessId'] + ')' if current_access['businessId'] != current_access_config['businessId'] else ''}")
        self.__print_and_log(f"    business_email = {current_access_config['business_email']}"
                             f"{' (Текущее значение: ' + current_access['business_email'] + ')' if current_access['business_email'] != current_access_config['business_email'] else ''}")
        self.__print_and_log(f"    user_email = {current_access_config['user_email']}"
                             f"{' (Текущее значение: ' + current_access['user_email'] + ')' if current_access['user_email'] != current_access_config['user_email'] else ''}")
        self.__print_and_log(f"    password = {current_access_config['password']}"
                             f"{' (Текущее значение: ' + current_access['password'] + ')' if current_access['password'] != current_access_config['password'] else ''}")
        self.__print_and_log(f"    api_key = {current_access_config['api_key']}"
                             f"{' (Текущее значение: ' + current_access['api_key'] + ')' if current_access['api_key'] != current_access_config['api_key'] else ''}")

        self.__print_and_log('')
        return True

    def _use_access_config(self, *args):
        """Использовать конкретную конфигурацию доступа
        use_access_config <key>"""
        prefix_error = "_use_access_config error:"

        key = args[0] if len(args) > 0 else None

        if not key:
            self.print_error(prefix_error, f"Отсутствует key")
            return False

        if not self.rest_api_client.use_access_config(key):
            self.print_error(prefix_error, f"Access Config {key} не найден")
            return False

        return True

    """ Raw Requests """

    def _raw_request_business(self, *args):
        """Сделать raw request от лица бизнес-пользователя
        raw_request_business <url_suffix> POST|GET|PUT|DELETE|PATCH [<body_escaped_json>] [multipart]"""
        url_suffix = args[0] if len(args) > 0 else None
        request_type = args[1] if len(args) > 1 else None
        body = args[2] if len(args) > 2 else None
        multipart = True if len(args) > 3 and args[3] is not None and args[3].lower() == 'multipart' else False
        access_level = args[4] if len(args) > 4 else 'business'

        prefix_error = f"_raw_request_{access_level} error:"

        if not url_suffix:
            self.print_error(prefix_error, f"Отсутствует url_suffix")
            return False

        if not request_type:
            self.print_error(prefix_error, f"Отсутствует request_type ( POST | GET | PUT | DELETE | PATCH)")
            return False
        else:
            if not self.__validate_flags([request_type], ['post', 'get', 'put', 'delete', 'patch']):
                self.print_error(prefix_error,
                                 f"Неверный request_type. Возможные значения: POST, GET, PUT, DELETE, PATCH")
                return False

        if body:
            unescaped_body = self.__unescape_json(body)
            if unescaped_body is None:
                return False
        else:
            unescaped_body = None

        response = self.rest_api_client.raw_request_business(url_suffix, request_type, unescaped_body, multipart, access_level)

        if response.status_code != 200 and response.status_code != 204:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        self.__print_and_log("------------------------------------------")
        self.__print_and_log(f"Status Code: {response.status_code}")
        self.__print_and_log(f"Response: {response.text}")
        self.__print_and_log('')

        return True

    def _raw_request_admin(self, *args):
        """Сделать raw request от лица админа
        raw_request_admin <url_suffix> POST|GET|PUT|DELETE|PATCH [<body_escaped_json>] [multipart]"""

        url_suffix = args[0] if len(args) > 0 else None
        request_type = args[1] if len(args) > 1 else None
        body = args[2] if len(args) > 2 else None
        multipart = args[3] if len(args) > 3 else None

        return self._raw_request_business(url_suffix, request_type, body, multipart, 'admin')

    def _raw_request(self, *args):
        """Сделать произвольный raw request
        raw_request <url_suffix_ext> POST|GET|PUT|DELETE|PATCH [<body_escaped_json>] [multipart]"""
        prefix_error = f"_raw_request error:"

        url_suffix_ext = args[0] if len(args) > 0 else None
        request_type = args[1] if len(args) > 1 else None
        body = args[2] if len(args) > 2 else None
        multipart = True if len(args) > 3 and args[3] is not None and args[3].lower() == 'multipart' else False

        if not url_suffix_ext:
            self.print_error(prefix_error, f"Отсутствует url_suffix_ext")
            return False

        if not request_type:
            self.print_error(prefix_error, f"Отсутствует request_type ( POST | GET | PUT | DELETE | PATCH)")
            return False
        else:
            if not self.__validate_flags([request_type], ['post', 'get', 'put', 'delete', 'patch']):
                self.print_error(prefix_error,
                                 f"Неверный request_type. Возможные значения: POST, GET, PUT, DELETE, PATCH")
                return False

        if body:
            unescaped_body = self.__unescape_json(body)
            if unescaped_body is None:
                return False
        else:
            unescaped_body = None

        response = self.rest_api_client.raw_request(url_suffix_ext, request_type, unescaped_body, multipart)

        if response.status_code != 200 and response.status_code != 204:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        self.__print_and_log("------------------------------------------")
        self.__print_and_log(f"Status Code: {response.status_code}")
        self.__print_and_log(f"Response: {response.text}")
        self.__print_and_log('')

        return True

    """ Script Variables """

    def _set_script_variable(self, *args):
        """Установить значение переменной
        set_script_variable <script_variable> [<value>]"""
        prefix_error = "set_script_variable error:"

        script_variable = args[0] if len(args) > 0 else None
        value = args[1] if len(args) > 1 else ""

        if not script_variable:
            self.print_error(prefix_error, f"Отсутствует script_variable")
            return False

        if value is None:
            value = ""

        self.script_variables[script_variable] = value

        return True

    def _set_script_variable_from_response(self, *args):
        """Установить значение переменной на значение ключа из последнего response
        set_script_variable_from_response <script_variable> <key_in_last_response_json>"""
        prefix_error = "set_script_variable_from_response error:"

        script_variable = args[0] if len(args) > 0 else None
        key = args[1] if len(args) > 1 else None

        if not script_variable:
            self.print_error(prefix_error, f"Отсутствует script_variable")
            return False

        if not key:
            self.print_error(prefix_error, f"Отсутствует key_in_last_response_json")
            return False

        if hasattr(self.rest_api_client.last_response, 'status_code'):
            response_json = self.rest_api_client.last_response.json()
        else:
            # для случаев, когда response - это уже JSON (get_all_entities_vector)
            response_json = self.rest_api_client.last_response

        if isinstance(response_json, list):
            if len(response_json) > 0:
                response_item = response_json[0]
            else:
                response_item = {}
        else:
            response_item = response_json

        if key in response_item:
            value = response_item[key]
            self.__print_and_log(f"{key}:{value}")
            self.script_variables[script_variable] = value
        else:
            self.print_error(prefix_error, f"Отсутствует {key} в response_item = {response_item}")
            return False

        return True

    def _set_script_variable_from_file(self, *args):
        """Загрузить значение переменной из файла
        set_script_variable_from_file <script_variable> <file_path> [Unescaped | Escaped | DoubleEscaped]"""
        prefix_error = "set_script_variable_from_file error:"

        script_variable = args[0] if len(args) > 0 else None
        file_path = args[1] if len(args) > 1 else None
        escape_flag = args[2] if len(args) > 2 else "Escaped"

        if not script_variable:
            self.print_error(prefix_error, f"Отсутствует script_variable")
            return False

        if not file_path:
            self.print_error(prefix_error, f"Отсутствует file_path")
            return False

        if not self.__validate_flags([escape_flag], ['unescaped', 'escaped', 'doubleescaped']):
            self.print_error(prefix_error,
                             f"Неверный escape_flag. Возможные значения: Unescaped, Escaped, DoubleEscaped. "
                             f"В случае отсутвия флага - применяется Escaped")
            return False

        with open(file_path, 'r', encoding="utf-8-sig") as file:
            value = file.read()

        value = self.__insert_script_variable_value(value)

        if escape_flag.lower() == 'unescaped':
            self.script_variables[script_variable] = value
        elif escape_flag.lower() == 'escaped':
            value_escaped = self.__escape_string(value)
            self.script_variables[script_variable] = value_escaped
        elif escape_flag.lower() == 'doubleescaped':
            value_escaped = self.__escape_string(value)
            value_double_escaped = self.__escape_string(value_escaped)
            self.script_variables[script_variable] = value_double_escaped

        return True

    def _set_script_variable_from_attribute(self, *args):
        """Загрузить значение переменной из атрибута
        set_script_variable_from_attribute <script_variable> <entity_id> <attribute_key>"""
        prefix_error = "_set_script_variable_from_attribute error:"

        script_variable = args[0] if len(args) > 0 else None
        entity_id = args[1] if len(args) > 1 else None
        attribute_key = args[2] if len(args) > 2 else None

        if not script_variable:
            self.print_error(prefix_error, f"Отсутствует script_variable")
            return False

        if not entity_id:
            self.print_error(prefix_error, 'Не указан id сущности')
            return False

        if not attribute_key:
            self.print_error(prefix_error, 'Не указан attribute_key')
            return False

        response = self.rest_api_client.get_entities(f'id={entity_id}&WithAttributeValues=true')
        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        entities = response.json()
        if len(entities) == 0:
            self.print_error(prefix_error, f'Сущность с id = {entity_id} не найдена')
            return False

        entity = entities[0]
        is_found = False
        if 'attributeValues' in entity:
            for attr_value in entity['attributeValues']:
                if attr_value['attributeKey'].lower() == attribute_key.lower():
                    if attr_value['valueLocales']:
                        value = attr_value['valueLocales'][0]['value']
                        is_found = True
                    break

        if is_found:
            return self._set_script_variable(script_variable, value)
        else:
            self.print_error(prefix_error, f'Значение атрибута {attribute_key} отсутствует у сущности {entity_id}')
            return False

    def _show_script_variables(self, *args):
        """Показать значения всех переменных
        show_script_variables"""

        if self.script_variables != {}:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные переменные скрипта:")
            self.__print_and_log(f"----------------------------------")
            for key, value in self.script_variables.items():
                self.__print_and_log(f"{key}: {value}")
        else:
            self.__print_and_log(f"Переменные скрипта отсутствуют")

        self.__print_and_log('')
        return True

    """ Permissions Variables/ EntityType Permissions"""

    def _set_permissions_variable(self, *args):
        """Установить переменную доступа
        set_permissions_variable <permissions_variable_name> <escaped_json>"""
        prefix_error = "_set_permissions_variable error:"

        permissions_variable = args[0] if len(args) > 0 else None
        escaped_json = args[1] if len(args) > 1 else None

        if not permissions_variable:
            self.print_error(prefix_error, f"Отсутствует permissions_variable_name")
            return False
        if not escaped_json:
            self.print_error(prefix_error, f"Отсутствует escaped_json")
            return False

        unescaped_json = self.__unescape_json(escaped_json)
        if unescaped_json is None:
            return False

        self.permissions_variables[permissions_variable] = unescaped_json

        return True

    def _create_permissions_variable(self, *args):
        """Создать переменную доступа
        create_permissions_variable <permissions_variable_name>"""
        prefix_error = "_create_permissions_variable error:"

        permissions_variable = args[0] if len(args) > 0 else None

        if not permissions_variable:
            self.print_error(prefix_error, f"Отсутствует permissions_variable_name")
            return False

        if permissions_variable in self.permissions_variables:
            if self.ignore_object_existence_error:
                self.__print_and_log('Применена опция ignore_object_existence_error. Используется edit_permissions_variable')
                return self._edit_permissions_variable(permissions_variable)
            self.print_error(prefix_error, f"Переменная доступа {permissions_variable} уже существует")
            return False

        if self.opened_permissions_variable != {}:
            self.print_error(prefix_error, f"Уже имеется открытая переменная доступа, используйте save_permissions_variable или discard_permissions_variable, чтобы закрыть её")
            return False

        self.opened_permissions_variable = {
            "Name": permissions_variable,
            "Value": []
        }

        return True

    def _edit_permissions_variable(self, *args):
        """Редактировать переменную доступа
        edit_permissions_variable <permissions_variable_name>"""
        prefix_error = "_edit_permissions_variable error:"

        permissions_variable = args[0] if len(args) > 0 else None

        if not permissions_variable:
            self.print_error(prefix_error, f"Отсутствует permissions_variable_name")
            return False

        if permissions_variable not in self.permissions_variables:
            self.print_error(prefix_error, f"Переменной доступа {permissions_variable} не существует. Используйте команду create_permissions_variable")
            return False

        self.opened_permissions_variable = {
            "Name": permissions_variable,
            "Value": self.permissions_variables[permissions_variable]
        }

        return True

    def _set_permission(self, *args):
        """Установить доступ, команда может быть применена для открытой permissions_variable или для открытой EntityType
        set_permission <permission_type> <level> [<space> <role>]"""
        prefix_error = "_set_permission error:"

        permission_type = args[0] if len(args) > 0 else None
        level = args[1] if len(args) > 1 else None
        space = args[2] if len(args) > 2 else None
        role = args[3] if len(args) > 3 else None

        if not permission_type:
            self.print_error(prefix_error, f"Отсутствует permission_type")
            return False

        if not level:
            self.print_error(prefix_error, f"Отсутствует level")
            return False

        if self.opened_permissions_variable != {} and self.opened_permissions != {}:
            self.print_error(prefix_error, f"Имеется открытая переменная доступа {self.opened_permissions_variable['Name']} "
                                           f"и одновременно открыто редактирование EntityType {self.opened_permissions['Name']}. "
                                           f"Требуется что-то из этого закрыть (save_permissions_variable, discard_permissions_variable, save_entity_type, discard_entity_type).")
            return False

        if self.opened_permissions_variable == {} and self.opened_permissions == {}:
            self.print_error(prefix_error, f"Отсутвует открытая переменная доступа или открытая EntityType "
                                           f"(create_permissions_variable, edit_permissions_variable, create_entity_type, edit_entity_type)")
            return False

        new_value = []
        if self.opened_permissions_variable != {}:
            permissions = self.opened_permissions_variable['Value']
        else:
            permissions = self.opened_permissions['Value']

        is_found = False
        for value in permissions:
            if value['type'] == permission_type and value['level'] == level:
                is_found = True
                if space:
                    value['space'] = space
                elif 'space' in value:
                    del value['space']
                if role:
                    value['role'] = role
                elif 'role' in value:
                    del value['space']
            new_value.append(value)

        if not is_found:
            permission = {
                "type": permission_type,
                "level": level
            }
            if space:
                permission['space'] = space
            if role:
                permission['role'] = role
            new_value.append(permission)

        if self.opened_permissions_variable != {}:
            self.opened_permissions_variable['Value'] = new_value
        else:
            self.opened_permissions['Value'] = new_value

        return True

    def _delete_permission(self, *args):
        """Удалить доступ, команда может быть применена для открытой permissions_variable или для открытой EntityType
        delete_permission <permission_type> <level>"""
        prefix_error = "_delete_permission error:"

        permission_type = args[0] if len(args) > 0 else None
        level = args[1] if len(args) > 1 else None

        if not permission_type:
            self.print_error(prefix_error, f"Отсутствует permission_type")
            return False

        if not level:
            self.print_error(prefix_error, f"Отсутствует level")
            return False

        if self.opened_permissions_variable != {} and self.opened_permissions != {}:
            self.print_error(prefix_error, f"Имеется открытая переменная доступа {self.opened_permissions_variable['Name']} "
                                           f"и одновременно открыто редактирование EntityType {self.opened_permissions['Name']}. "
                                           f"Требуется что-то из этого закрыть (save_permissions_variable, discard_permissions_variable, save_entity_type, discard_entity_type).")
            return False

        if self.opened_permissions_variable == {} and self.opened_permissions == {}:
            self.print_error(prefix_error, f"Отсутвует открытая переменная доступа или открытая EntityType "
                                           f"(create_permissions_variable, edit_permissions_variable, create_entity_type, edit_entity_type)")
            return False

        new_value = []
        if self.opened_permissions_variable != {}:
            permissions = self.opened_permissions_variable['Value']
        else:
            permissions = self.opened_permissions['Value']

        for value in permissions:
            if value['type'] != permission_type or value['level'] != level:
                new_value.append(value)

        if self.opened_permissions_variable != {}:
            self.opened_permissions_variable['Value'] = new_value
        else:
            self.opened_permissions['Value'] = new_value

        return True

    def _show_permissions(self, *args):
        """Показать все параметры доступа, команда может быть применена для открытой permissions_variable или для открытой EntityType
        show_permissions"""
        prefix_error = "_show_permissions error:"

        if self.opened_permissions_variable != {} and self.opened_permissions != {}:
            self.print_error(prefix_error, f"Имеется открытая переменная доступа {self.opened_permissions_variable['Name']} "
                                           f"и одновременно открыто редактирование EntityType {self.opened_permissions['Name']}. "
                                           f"Требуется что-то из этого закрыть (save_permissions_variable, discard_permissions_variable, save_entity_type, discard_entity_type).")
            return False

        if self.opened_permissions_variable == {} and self.opened_permissions == {}:
            self.print_error(prefix_error, f"Отсутвует открытая переменная доступа или открытая EntityType "
                                           f"(create_permissions_variable, edit_permissions_variable, create_entity_type, edit_entity_type)")
            return False

        if self.opened_permissions_variable != {}:
            opened_permissions = self.opened_permissions_variable
        else:
            opened_permissions = self.opened_permissions

        if len(opened_permissions['Value']) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Параметры доступа {opened_permissions['Name']}: ")
            self.__print_and_log(f"----------------------------------")
            for permission in opened_permissions['Value']:
                self.__print_and_log(f"{permission['type']}:")
                self.__print_and_log(f"        level: {permission['level']}")
                if 'space' in permission:
                    self.__print_and_log(f"        space: {permission['space']}")
                if 'role' in permission:
                    self.__print_and_log(f"        role: {permission['role']}")
        else:
            self.__print_and_log(f"Параметры доступа отсутствуют")
        self.__print_and_log('')

        return True

    def _save_permissions_variable(self, *args):
        """Сохранить переменную доступа
        save_permissions_variable"""
        prefix_error = "_save_permissions_variable error:"

        if self.opened_permissions_variable == {}:
            self.print_error(prefix_error, f"Отсутствует открытая permissions_variable, используйте create_permissions_variable или edit_permissions_variable")
            return False

        self.permissions_variables[self.opened_permissions_variable['Name']] = self.opened_permissions_variable['Value']

        self.opened_permissions_variable = {}
        return True

    def _discard_permissions_variable(self, *args):
        """Откат открытой переменной доступа
        discard_permissions_variable"""
        self.opened_permissions_variable = {}
        return True

    def _delete_permissions_variable(self, *args):
        """Удалить переменную доступа
        delete_permissions_variable <permissions_variable_name>"""
        prefix_error = "_delete_permissions_variable error:"

        permissions_variable = args[0] if len(args) > 0 else None

        if not permissions_variable:
            self.print_error(prefix_error, f"Отсутствует permissions_variable_name")
            return False

        if permissions_variable in self.permissions_variables:
            del self.permissions_variables[permissions_variable]

        return True

    def _show_permissions_variables(self, *args):
        """Показать все переменные доступа
        show_permissions_variables"""

        if len(self.permissions_variables) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные переменные доступа: ")
            self.__print_and_log(f"----------------------------------")
            for name, value in self.permissions_variables.items():
                self.__print_and_log(f"{name}:")
                if len(value) > 0:
                    for permission in value:
                        self.__print_and_log(f"        {permission['type']}: {permission['level'] + ' '}"
                                             f"{permission['space'] + ' ' if 'space' in permission else ''}"
                                             f"{permission['role'] + ' ' if 'role' in permission else ''}")
                else:
                    self.__print_and_log(f"        пусто")
        else:
            self.__print_and_log(f"Переменные доступа отсутствуют")
        self.__print_and_log('')

        return True

    def _set_permissions_from_variable(self, *args):
        """Установить параметры доступа к EntityType по переменной доступа
        set_permissions_from_variable <permissions_variable_name>"""
        prefix_error = "_set_permissions_from_variable error:"

        permissions_variable_name = args[0] if len(args) > 0 else None

        if not permissions_variable_name:
            self.print_error(prefix_error, f"Отсутствует permissions_variable_name")
            return False

        if permissions_variable_name not in self.permissions_variables:
            self.print_error(prefix_error, f"Отсутствует переменная доступа {permissions_variable_name}. "
                                           f"Используйте create_permissions_variable, чтобы создать её.")
            return False

        if self.opened_permissions == {}:
            self.print_error(prefix_error, f"Отсутствует открытая EntityType. Используйте create_entity_type или edit_entity_type")
            return False

        self.opened_permissions['Value'] = self.permissions_variables[permissions_variable_name]
        # зачистка возможных id для профилактики
        for permission in self.opened_permissions['Value']:
            if 'id' in permission:
                del permission['id']
        # флаг для перезаписывания всех permissions
        self.rewrite_all_permissions = True

        return True

    """ Businesses (Admin)"""

    def _create_business(self, *args):
        """Создать новый бизнес
        create_business [<business_id>], [Clear]"""
        prefix_error = "create_business error:"

        business_id = args[0] if len(args) > 0 else None
        clear_flag = args[1] if len(args) > 1 else ""

        if not business_id:
            business_id = self.rest_api_client.access_config['businessId']

        if clear_flag.lower() == 'clear':
            parameters = 'ignoreDefaultSchema=true'
        else:
            parameters = 'ignoreDefaultSchema=false'

        # костыль для обхода https://jira.paragon-software.com/browse/MSOR-2213
        if self.legacy_searcher and self.rest_api_client.access_config['service_path'].lower() == 'searcher':
            data = {
                "id": business_id
            }
        else:
            data = [
                {
                    "id": business_id
                }
            ]

        response = self.rest_api_client.create_business(data, parameters)

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        return True

    def _delete_business(self, *args):
        """Удалить бизнес
        delete_business [<business_id>], [Force]"""
        prefix_error = "delete_business error:"

        business_id = args[0] if len(args) > 0 else None
        force_flag = args[1] if len(args) > 1 else ""

        if not business_id:
            business_id = self.rest_api_client.access_config['businessId']

        if force_flag.lower() == 'force':
            parameters = 'force=true'
        else:
            parameters = 'force=false'

        # костыль для обхода https://jira.paragon-software.com/browse/MSOR-2213
        if self.legacy_searcher and self.rest_api_client.access_config['service_path'].lower() == 'searcher':
            response = self.rest_api_client.delete_business_searcher(business_id)
        else:
            response = self.rest_api_client.delete_business([business_id], parameters)

        if response.status_code != 204:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        return True

    def _show_businesses(self, *args):
        """Показать имеющиеся бизнесы
        show_businesses"""
        prefix_error = "show_businesses error:"

        response = self.rest_api_client.get_businesses("")
        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False
        businesses = response.json()
        if len(businesses) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные бизнесы:")
            self.__print_and_log(f"----------------------------------")
            for business in businesses:
                # костыль для обхода https://jira.paragon-software.com/browse/MSOR-2213
                if self.legacy_searcher and self.rest_api_client.access_config['service_path'].lower() == 'searcher':
                    self.__print_and_log(f"id: {business['id']}{' (current)' if business['id'] == self.rest_api_client.access_config['businessId'] else ''} ")
                else:
                    self.__print_and_log(
                        f"id: {business['id']}, isDeleted: {business['isDeleted']}{' (current)' if business['id'] == self.rest_api_client.access_config['businessId'] else ''} ")
            self.__print_and_log('')
        else:
            self.__print_and_log(f"Бизнесы отсутствуют")
        return True

    """ BusinessPermissions (Admin)"""

    def _set_business_permissions(self, *args):
        """Установка прав доступа для бизнеса
        set_business_permissions <type> <space> <role> [<secondFactorRequired>]"""
        prefix_error = "set_business_permissions error:"

        permissions_type = args[0] if len(args) > 0 else None
        space = args[1] if len(args) > 1 else None
        role = args[2] if len(args) > 2 else None
        second_factor_required = args[3] if len(args) > 3 else None

        if not permissions_type:
            self.print_error(prefix_error, "type не указан")
            return False

        if not space:
            self.print_error(prefix_error, "space не указан")
            return False

        if not role:
            self.print_error(prefix_error, "role не указана")
            return False

        # получение текущих business permissions
        response = self.rest_api_client.get_business_permissions()
        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False
        business_permissions = response.json()

        new_business_permissions = {}

        for business_permission in business_permissions:
            if business_permission['type'].lower() == permissions_type.lower():
                new_business_permissions = business_permission

        data = [
            {
                "type": permissions_type,
                "space": space,
                "role": role,
            }
        ]
        if second_factor_required:
            data[0]['secondFactorRequired'] = second_factor_required

        if 'id' in new_business_permissions:
            data[0]['id'] = new_business_permissions['id']
            response = self.rest_api_client.put_business_permissions(data)
        else:
            response = self.rest_api_client.create_business_permissions(data)

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        self.print_success(f"id: {response.json()[0]['id']}")

        return True

    def _delete_business_permissions(self, *args):
        """Удаление прав доступа для бизнеса
        delete_business_permissions <id>"""
        prefix_error = "delete_business_permissions error:"

        permissions_id = args[0] if len(args) > 0 else None

        if not permissions_id:
            self.print_error(prefix_error, "id не указан")
            return False

        response = self.rest_api_client.delete_business_permissions([permissions_id])
        if response.status_code != 204:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        return True

    def _show_business_permissions(self, *args):
        """Показ всех прав доступа для бизнеса
        show_business_permissions"""
        prefix_error = "show_business_permissions error:"

        response = self.rest_api_client.get_business_permissions()
        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False
        business_permissions = response.json()
        if len(business_permissions) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные права доступа для бизнеса:")
            self.__print_and_log(f"----------------------------------")
            for business_permission in business_permissions:
                self.__print_and_log(f"{business_permission['id']}:")
                self.__print_and_log(f"      type: {business_permission['type']}")
                self.__print_and_log(f"      space: {business_permission['space']}")
                self.__print_and_log(f"      role: {business_permission['role']}")
                self.__print_and_log(f"      secondFactorRequired: {business_permission['secondFactorRequired']}")
        else:
            self.__print_and_log(f"Доступные права доступа для бизнеса отсутствуют")
        self.__print_and_log('')

        return True

    """ Schema"""

    def _import_schema(self, *args):
        """Импорт схемы
        import_schema <schema_path> [SkipSystemItems]"""
        prefix_error = "import_schema error:"

        schema_path = args[0] if len(args) > 0 else None
        skip_system_items = args[1] if len(args) > 1 else None

        if not schema_path:
            self.print_error(prefix_error, "schema_path не указан")
            return False

        if not skip_system_items:
            parameters = "SkipSystemItems=false"
        elif skip_system_items.lower() == 'skipsystemitems':
            parameters = "SkipSystemItems=true"
        else:
            self.print_error(prefix_error, "неверный флаг, должен быть SkipSystemItems для игнорирования импорта системных объектов")
            return False

        response = self.rest_api_client.import_schema(schema_path, parameters)
        if response.status_code != 204:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        return True

    """ Attributes """

    def get_attribute_id(self, attribute_key, warning=True):
        response = self.rest_api_client.get_attributes(f"Key={attribute_key}")

        if response.status_code != 200:
            self.__print_and_log(f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return

        if len(response.json()) == 0:
            if warning:
                self.__print_and_log(f"Атрибут {attribute_key} отсутствует")
            return

        return response.json()[0]['id']

    def _create_attribute(self, *args):
        """Создание атрибута
        create_attribute <key>"""
        prefix_error = "create_attribute error:"

        attribute_key = args[0] if len(args) > 0 else None

        if attribute_key in (None, ''):
            self.print_error(prefix_error, "attribute_key не указан")
            return False

        response = self.rest_api_client.get_attributes(f"Key={attribute_key}")
        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        if len(response.json()) > 0:
            # атрибут существует
            if self.ignore_object_existence_error:
                self.__print_and_log('Применена опция ignore_object_existence_error. Используется edit_attribute')
                return self._edit_attribute(attribute_key)

            self.print_error(prefix_error, f"Атрибут {attribute_key} уже существует")
            return False
        else:
            # атрибута не существует
            self.opened_attribute = {
                "key": attribute_key,
                "flags": "None",
                "type": "String"
            }
            return True

    def _edit_attribute(self, *args):
        """Редактирование атрибута
        edit_attribute <key>"""
        prefix_error = "edit_attribute error:"

        attribute_key = args[0] if len(args) > 0 else None

        if attribute_key in (None, ''):
            self.print_error(prefix_error, f"attribute_key не указан")
            return False

        response = self.rest_api_client.get_attributes(f"Key={attribute_key}&WithProperties=true&WithValidators=true")
        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        if len(response.json()) > 0:
            # атрибут существует
            self.opened_attribute = response.json()[0]
            return True
        else:
            # атрибута не существует
            self.print_error(prefix_error, f"Атрибута {attribute_key} не существует")
            return False

    def _set_attribute_key(self, *args):
        """Установка нового имени атрибута
        set_attribute_key <key>"""
        prefix_error = "set_attribute_key error:"

        attribute_key = args[0] if len(args) > 0 else None

        if attribute_key in (None, ''):
            self.print_error(prefix_error, f"attribute_key не указан")
            return False

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False
        else:
            # есть открытый атрибут
            self.opened_attribute['key'] = attribute_key
            return True

    def _set_attribute_label(self, *args):
        """Установка нового Label (отображаемого имени) атрибута
        set_attribute_label [<label>]"""
        prefix_error = "set_attribute_label error:"

        attribute_label = args[0] if len(args) > 0 else None
        label_locale = args[1].lower() if len(args) > 1 else None

        if label_locale and label_locale not in supported_label_locales:
            self.print_error(prefix_error,
                             f"Поддерживаемые локали {supported_label_locales}")
            return False

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False

        # есть открытый атрибут

        if attribute_label in (None, ""):
            # очищение label
            if 'properties' in self.opened_attribute:
                new_properties = [prop for prop in self.opened_attribute['properties'] if
                                  prop["key"] != label_key.upper()]
                if len(new_properties) > 0:
                    self.opened_attribute['properties'] = new_properties
                else:
                    del self.opened_attribute['properties']
            return True

        if 'properties' not in self.opened_attribute:
            # нет properties
            self.opened_attribute['properties'] = [
                {
                    "key": label_key.upper(),
                    "value": attribute_label,
                    "locale": label_locale
                }
            ]
        else:
            # есть properties
            prop_found = False
            for prop in self.opened_attribute['properties']:
                if prop['key'].lower() == label_key:
                    locale_exists = 'locale' in prop and prop['locale']
                    if (locale_exists and prop['locale'].lower() == label_locale) or (not locale_exists and not label_locale):
                        prop['value'] = attribute_label
                        if locale_exists:
                            prop['locale'] = label_locale
                        prop_found = True
                        break

            if not prop_found:
                # есть properties, но отсутствует label
                self.opened_attribute['properties'].append({
                    "key": label_key.upper(),
                    "value": attribute_label,
                    "locale": label_locale
                })

        return True

    def _set_attribute_type(self, *args):
        """Установка типа данных атрибута
        set_attribute_type <type>"""
        prefix_error = "set_attribute_type error:"

        attribute_type = args[0] if len(args) > 0 else None

        if attribute_type in (None, ''):
            self.print_error(prefix_error, f"attribute_type не указан")
            return False

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False
        else:
            # есть открытый атрибут
            self.opened_attribute['type'] = attribute_type
            return True

    def _set_attribute_flags(self, *args):
        """Установка флагов атрибута
        set_attribute_flags [IsFixed]"""
        prefix_error = "set_attribute_flags error:"

        attribute_flags = args[0] if len(args) > 0 else None

        if attribute_flags in (None, ''):
            # сброс всех флагов
            attribute_flags = "None"

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False
        else:
            # есть открытый атрибут
            self.opened_attribute['flags'] = attribute_flags

            # в случае отсутвия IsFixed - обнуление values
            if attribute_flags.find("IsFixed") < 0:
                if 'values' in self.opened_attribute:
                    del self.opened_attribute['values']

            return True

    def _set_attribute_fixed_values(self, *args):
        """Установка фиксированных значений атрибута
        set_attribute_fixed_values "<value1>", "<value2>", "<value3>", ..."""
        prefix_error = "set_attribute_fixed_values error:"

        attribute_fixed_values = args[0:] if len(args) > 0 else None

        if attribute_fixed_values is None:
            self.print_error(prefix_error, f"Укажите как минимум одно фиксированное значение")
            return False

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False
        else:
            # есть открытый атрибут
            self.opened_attribute['values'] = []
            for fixed_value in attribute_fixed_values:
                self.opened_attribute['values'].append({"locales": [{"value": fixed_value}]})
            return True

    def _set_attribute_fixed_display_values(self, *args):
        """Установка фиксированных значений атрибута и их показываемые значения
        set_attribute_fixed_display_values "<value1>" "<display_value1>", "<value2>" "<display_value2>", "<value3>" "<display_value2>", ..."""
        prefix_error = "_set_attribute_fixed_display_values error:"

        if len(args) > 1:
            attribute_fixed_values = []
            i = 0
            while len(args) > (i + 1):
                attribute_fixed_values.append(
                    {
                        "value": args[i],
                        "display": args[i + 1]
                    }
                )
                i += 2
        else:
            attribute_fixed_values = None

        if attribute_fixed_values is None:
            self.print_error(prefix_error, f"Укажите как минимум одну пару: фиксированное значение и его отображение")
            return False

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False
        else:
            # есть открытый атрибут
            self.opened_attribute['values'] = []
            for fixed_value in attribute_fixed_values:
                self.opened_attribute['values'].append({"locales": [fixed_value]})
            return True

    def _set_attribute_validator(self, *args):
        """Установка валидатора атрибута
        set_attribute_validator <key> <type> <parameter> <error_message>

        допустимые типы валидаторов:
        RegexValidator, NumberLowerValidator, NumberLowerOrEqualsValidator, NumberGreaterValidator, NumberGreaterOrEqualsValidator,
        AddressAcceptableCountriesValidator, AddressRequiredFieldsValidator, ObjectSchemaValidator, DateTimeLowerValidator,
        DateTimeLowerOrEqualsValidator, DateTimeGreaterValidator, DateTimeGreaterOrEqualsValidator, TimeSpanLowerValidator,
        TimeSpanLowerOrEqualsValidator, TimeSpanGreaterValidator, TimeSpanGreaterOrEqualsValidator, StringMaxLengthValidator,
        StringMinLengthValidator, StringInvalidCharactersValidator, AttachmentMaxFileSizeInBytesValidator,
        AttachmentAvailableMimeTypesValidator, HtmlSecurityValidator"""
        prefix_error = "set_attribute_validator error:"

        key = args[0] if len(args) > 0 else None
        validator_type = args[1] if len(args) > 1 else None
        if len(args) > 2:
            if validator_type.lower() == 'HtmlSecurityValidator'.lower():
                parameter = self.__unescape_json(args[2])
            else:
                parameter = args[2].encode().decode('unicode-escape')
        else:
            parameter = None

        error_message = args[3] if len(args) > 3 else None

        if not key:
            self.print_error(prefix_error, f"key не задан")
            return False

        if not validator_type:
            self.print_error(prefix_error, f"validator_type не задан")
            return False

        if not parameter:
            self.print_error(prefix_error, f"parameter не задан")
            return False

        if not error_message:
            self.print_error(prefix_error, f"error_message не задан")
            return False

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False

        new_validators = []
        if 'validators' in self.opened_attribute:
            for validator in self.opened_attribute['validators']:
                if validator['key'].lower() != key.lower():
                    new_validators.append(validator)

        new_validators.append(
            {
                "key":  key,
                "type": validator_type,
                "config": {
                    "parameter": parameter
                },
                "properties": [
                    {
                        "key": "ERROR_MESSAGE",
                        "value": error_message
                    }
                ]
            }
        )
        self.opened_attribute['validators'] = new_validators

        return True

    def _delete_attribute_validator(self, *args):
        """Удаление валидатора атрибута
        delete_attribute_validator <key>"""
        prefix_error = "delete_attribute_validator error:"

        key = args[0] if len(args) > 0 else None

        if not key:
            self.print_error(prefix_error, f"key не задан")
            return False

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False

        new_validators = []
        if 'validators' in self.opened_attribute:
            for validator in self.opened_attribute['validators']:
                if validator['key'].lower() != key.lower():
                    new_validators.append(validator)

        if len(new_validators) > 0:
            self.opened_attribute['validators'] = new_validators
        elif 'validators' in self.opened_attribute:
            del self.opened_attribute['validators']

        return True

    def _show_attribute_validators(self, *args):
        """Показ всех валидаторов атрибута
        show_attribute_validators"""
        prefix_error = "show_attribute_validators error:"

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False

        if 'validators' in self.opened_attribute and len(self.opened_attribute['validators']) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Валидаторы атрибута:")
            self.__print_and_log(f"----------------------------------")
            for validator in self.opened_attribute['validators']:
                self.__print_and_log(f"{validator['key']}:")
                self.__print_and_log(f"        type: {validator['type']}")
                self.__print_and_log(f"        parameter: {validator['config']['parameter']}")
                if 'properties' in validator:
                    error_message_property = next(((lambda x: x)(property_item)
                                               for property_item in validator["properties"]
                                               if property_item["key"].lower() == 'ERROR_MESSAGE'.lower()), None)
                else:
                    error_message_property = None
                if error_message_property:
                    self.__print_and_log(f"        error message: {error_message_property['value']}")
            self.__print_and_log('')
        else:
            self.__print_and_log(f"Валидаторы отсутствуют")

        return True

    def _save_attribute(self, *args):
        """Сохранить открытый атрибут
        save_attribute"""
        prefix_error = "save_attribute error:"

        if self.opened_attribute == {}:
            # нет открытого атрибута
            self.print_error(prefix_error,
                             f"Нет открытого атрибута. Используйте предварительно команды create_attribute <key> или edit_attribute <key>")
            return False

        # проверка надо создавать или обновлять
        if 'id' in self.opened_attribute:
            # атрибут существует
            response = self.rest_api_client.put_attributes([self.opened_attribute])
        else:
            # атрибута не существует
            response = self.rest_api_client.create_attribute([self.opened_attribute])

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        # успешно сохранён атрибут
        self.opened_attribute = {}
        return True

    def _discard_attribute(self, *args):
        """Откат открытого атрибута
        discard_attribute"""
        self.opened_attribute = {}
        return True

    def _delete_attribute(self, *args):
        """Удаление атрибута
        delete_attribute <key>"""
        prefix_error = "delete_attribute error:"

        attribute_key = args[0] if len(args) > 0 else None

        if attribute_key in (None, ''):
            self.print_error(prefix_error, "attribute_key не указан")
            return False

        attribute_id = self.get_attribute_id(attribute_key, False)

        if attribute_id is not None:
            response = self.rest_api_client.delete_attribute(attribute_id)
            if response.status_code != 204:
                self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                return False
            return True
        else:
            self.print_error(prefix_error, f"Атрибут {attribute_key} не найден")
            return False

    def _show_attributes(self, *args):
        """Показ всех атрибутов
        show_attributes"""
        prefix_error = "show_attributes error:"

        response = self.rest_api_client.get_attributes("")
        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False
        attributes = response.json()
        if len(attributes) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные атрибуты:")
            self.__print_and_log(f"----------------------------------")
            for attribute in attributes:
                self.__print_and_log(f"{attribute['key']} ({attribute['id']}): {attribute['type']}")
            self.__print_and_log('')
        else:
            self.__print_and_log(f"Атрибуты отсутствуют")
        return True

    """ Entity Types """

    def __set_variable_attribute(self, variable_key, to_reference_key, from_reference_key, attribute_key, attribute_not_found_behavior):
        """Универсальный внутренний метод для задания переменной вычисляемого атрибута"""
        prefix_error = "set_variable_attribute error:"

        if not variable_key:
            self.print_error(prefix_error, f"Отсутствует variable_key")
            return False

        if not attribute_key:
            self.print_error(prefix_error, f"Отсутствует attribute_key, откуда брать значение")
            return False

        if attribute_not_found_behavior in (None, ''):
            attribute_not_found_behavior = 'SetDefault'

        if self.opened_computed_attribute == {}:
            # нет открытого computed_value
            self.print_error(prefix_error,
                             f"Нет открытого вычисляемого значения. Используйте предварительно команду edit_computed_value <key>")
            return False

        new_variables = []
        if self.opened_computed_attribute['computedValues'][0]['variables'] is not None:
            for variable in self.opened_computed_attribute['computedValues'][0]['variables']:
                if variable['variableKey'].lower() != variable_key.lower():
                    new_variables.append(variable)

        if to_reference_key in (None, ""):
            if from_reference_key in (None, ""):
                new_variables.append(
                    {
                        "attributeKey": attribute_key,
                        "attributeNotFoundBehavior": attribute_not_found_behavior,
                        "variableKey": variable_key.upper(),
                        "type": "Attribute"
                    }
                )
            else:
                new_variables.append(
                    {
                        "attributeKey": attribute_key,
                        "attributeNotFoundBehavior": attribute_not_found_behavior,
                        "fromReferenceKey": from_reference_key,
                        "variableKey": variable_key.upper(),
                        "type": "Attribute"
                    }
                )
        else:
            new_variables.append(
                {
                    "attributeKey": attribute_key,
                    "attributeNotFoundBehavior": attribute_not_found_behavior,
                    "toReferenceKey": to_reference_key,
                    "variableKey": variable_key.upper(),
                    "type": "Attribute"
                }
            )
        self.opened_computed_attribute['computedValues'][0]['variables'] = new_variables

        return True

    def _create_entity_type(self, *args):
        """Создание нового типа сущности
        create_entity_type <key>"""
        prefix_error = "create_entity_type error:"

        entity_type_key = args[0] if len(args) > 0 else None

        if not entity_type_key:
            self.print_error(prefix_error, "entity_type_key не указан")
            return False

        response = self.rest_api_client.get_entity_types(f"Key={entity_type_key}", access_level=self.access_level)
        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        if len(response.json()) > 0:
            # entity_type существует
            if self.ignore_object_existence_error:
                self.__print_and_log('Применена опция ignore_object_existence_error. Используется edit_entity_type')
                return self._edit_entity_type(entity_type_key)

            self.print_error(prefix_error, f"Тип сущности {entity_type_key} уже существует")
            return False
        else:
            # entity_type не существует
            self.opened_entity_type = {
                "key": entity_type_key,
                "flags": "isSearchable",
                "attributes": []
            }
            self.opened_entity_type_permissions = []
            self.opened_permissions = {
                "Name": entity_type_key,
                "Value": self.permissions_variables['default']
            }
            return True

    def _edit_entity_type(self, *args):
        """Редактирование типа сущности
        edit_entity_type <key>"""
        prefix_error = "edit_entity_type error:"

        entity_type_key = args[0] if len(args) > 0 else None

        if not entity_type_key:
            self.print_error(prefix_error, f"entity_type_key не указан")
            return False

        response = self.rest_api_client.get_entity_types(
            f"Key={entity_type_key}&WithProperties=true&WithAttributes=true&WithReferencedFrom=true&WithReferencedTo=true",
            access_level=self.access_level
        )

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        if len(response.json()) > 0:
            # entity_type существует
            self.opened_entity_type = response.json()[0]

            if 'attributes' not in self.opened_entity_type:
                self.opened_entity_type['attributes'] = []

            entity_type_references = {}
            if ('referencedTo' in self.opened_entity_type) and self.opened_entity_type['referencedTo']:
                response = self.rest_api_client.get_references(
                    to_references_keys=[to_reference['key'] for to_reference in self.opened_entity_type['referencedTo']],
                    access_level=self.access_level
                )

                if response.status_code != 200:
                    self.print_error(prefix_error, response.text)
                    self.opened_entity_type = {}
                    return False

                for item in response.json():
                    if item['id'] in entity_type_references:
                        continue
                    entity_type_references[item['id']] = item

            if ('referencedFrom' in self.opened_entity_type) and self.opened_entity_type['referencedFrom']:
                response = self.rest_api_client.get_references(
                    from_references_keys=[from_reference['key'] for from_reference in self.opened_entity_type['referencedFrom']],
                    access_level=self.access_level
                )

                if response.status_code != 200:
                    self.print_error(prefix_error, response.text)
                    self.opened_entity_type = {}
                    return False

                for item in response.json():
                    if item['id'] in entity_type_references:
                        continue
                    entity_type_references[item['id']] = item

            self.opened_entity_type_references = [reference for key, reference in entity_type_references.items()]

            # получение entity_type_permissions
            response = self.rest_api_client.get_entity_type_permissions(
                self.opened_entity_type['id'],
                'WithAttributeValueConditions=true',
                access_level=self.access_level
            )
            if response.status_code != 200:
                self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                return False

            self.opened_entity_type_permissions = response.json()
            self.opened_permissions['Name'] = entity_type_key
            self.opened_permissions['Value'] = self.opened_entity_type_permissions

            return True
        else:
            # entity_type не существует
            self.print_error(prefix_error, f"Типа сущности {entity_type_key} не существует")
            return False

    def _set_entity_type_parent(self, *args):
        """Установка родителя для типа сущности
        set_entity_type_parent <parentKey>"""
        prefix_error = "set_entity_type_parent error:"

        parent_key = args[0] if len(args) > 0 else None

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False
        else:
            # есть открытый entity type
            if parent_key in ('', None):
                self.__print_and_log(f"Родитель не указан, родитель будет отсутвовать")
                if 'parentKey' in self.opened_entity_type:
                    del self.opened_entity_type['parentKey']
            else:
                self.opened_entity_type['parentKey'] = parent_key
            return True

    def _set_entity_type_state_machine(self, *args):
        """Установка машины состояний для типа сущности
        set_entity_type_state_machine <stateMachineKey>"""
        prefix_error = "set_entity_type_state_machine error:"

        state_machine_key = args[0] if len(args) > 0 else None

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False
        else:
            # есть открытый entity type
            if 'stateMachineKey' in self.opened_entity_type:
                self.print_error(prefix_error,
                                 f"Машина состояний у этого типа Entity уже имеется. Машину состояний нельзя менять.")
                return False

            if state_machine_key in ('', None):
                self.print_error(prefix_error, f"Укажите ключ машины состояний")
                return False
            else:
                self.opened_entity_type['stateMachineKey'] = state_machine_key
                return True

    def _set_entity_type_flags(self, *args):
        """Установка флагов типа сущности
        set_entity_type_flags [IsAbstract], [IsSearchable], [IsUnique], [IsDraftAllowed]"""
        prefix_error = "set_entity_type_flags error:"

        flags = args[0:] if len(args) > 0 else None

        # удаление None элемента из массива
        flags = self.__remove_none_from_array(flags)

        if flags and (not self.__validate_flags(flags, ['isabstract', 'issearchable', 'isunique', 'isdraftallowed'])):
            self.print_error(prefix_error,
                             f"Неверный флаг для entity type. Возможные значения: IsAbstract, IsSearchable, IsUnique, IsDraftAllowed")
            return False

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False
        else:
            # есть открытый entity type
            self.opened_entity_type['flags'] = ','.join(flags) if (flags is not None) and (len(flags) > 0) else "None"
            return True

    def _set_entity_type_label(self, *args):
        """Установка нового Label (отображаемого имени) типа сущности
        set_entity_type_label [<label>]"""
        prefix_error = "set_entity_type_label error:"

        label = args[0] if len(args) > 0 else None

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False

        if not label:
            # очищение label
            if 'properties' in self.opened_entity_type:
                new_properties = [prop for prop in self.opened_entity_type['properties'] if
                                  prop["key"] != label_key.upper()]
                if len(new_properties) > 0:
                    self.opened_entity_type['properties'] = new_properties
                else:
                    del self.opened_entity_type['properties']
            return True

        if 'properties' not in self.opened_entity_type:
            # нет properties
            self.opened_entity_type['properties'] = [
                {
                    "key": label_key.upper(),
                    "value": label
                }
            ]
        else:
            # есть properties
            prop_found = False
            for prop in self.opened_entity_type['properties']:
                if prop['key'].lower() == label_key:
                    prop['value'] = label
                    prop_found = True
                    break
            if not prop_found:
                # есть properties, но отсутствует label
                self.opened_entity_type['properties'].append({
                    "key": label_key.upper(),
                    "value": label
                })

        return True

    def _add_attribute(self, *args):
        """Добавить атрибут к типу сущности
        add_attribute <key>, [IsFullTextSearch], [IsMandatory], [IsUnique], [IsDraftMandatory], [IsReadonly], [IsComputed], [IsEncrypted]"""
        prefix_error = "add_attribute error:"

        key = args[0] if len(args) > 0 else None
        flags = args[1:] if len(args) > 1 else None

        if not key:
            self.print_error(prefix_error, f"Укажите ключ атрибута")
            return False

        # удаление None элемента из массива
        flags = self.__remove_none_from_array(flags)

        if flags is not None:
            if not self.__validate_flags(flags, ['isfulltextsearch',
                                                 'ismandatory',
                                                 'isunique',
                                                 'isdraftmandatory',
                                                 'isreadonly',
                                                 'iscomputed',
                                                 'isimmutable',
                                                 'ismultivalue',
                                                 'isencrypted']):
                self.print_error(prefix_error,
                                 f"Неверный флаг для атрибута entity type. Возможные значения: IsFullTextSearch, IsMandatory, IsUnique, IsDraftMandatory, IsReadonly, IsComputed, IsImmutable, IsMultiValue, IsEncrypted")
                return False

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False
        else:
            # есть открытый entity type
            if self.opened_entity_type['attributes'] is None:
                self.opened_entity_type['attributes'] = [{
                    'key': key,
                    'flags': ','.join(flags) if (flags is not None) and (len(flags) > 0) else 'None'
                }]
            else:
                for attribute in self.opened_entity_type['attributes']:
                    if attribute['key'].lower() == key.lower():
                        self.print_error(prefix_error, f"Атрибут {key} уже добавлен ранее")
                        return False

                self.opened_entity_type['attributes'].append({
                    'key': key,
                    'flags': ','.join(flags) if (flags is not None) and (len(flags) > 0) else 'None'
                })
            return True

    def _set_attribute_default_value(self, *args):
        """Установить дефолтное значение атрибута
        set_attribute_default_value <key> [<default_value>], [OnCreate], [OnUpdate]"""
        prefix_error = "set_attribute_default_value error:"

        key = args[0] if len(args) > 0 else None
        default_value = args[1] if len(args) > 1 else None
        flags = args[2:] if len(args) > 2 else None

        if not key:
            self.print_error(prefix_error, f"Укажите ключ атрибута")
            return False

        # удаление None элемента из массива
        flags = self.__remove_none_from_array(flags)

        if flags is not None:
            if not self.__validate_flags(flags, ['oncreate', 'onupdate']):
                self.print_error(prefix_error,
                                 f"Неверный флаг дефолтного значения атрибута. Возможные значения: OnCreate, OnUpdate")
                return False

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False
        else:
            # есть открытый entity type
            is_attribute_found = False
            new_attributes = []
            if self.opened_entity_type['attributes'] is not None:
                for attribute in self.opened_entity_type['attributes']:
                    if attribute['key'].lower() == key.lower():
                        if not default_value:
                            if 'defaultValues' in attribute:
                                del attribute['defaultValues']
                            if 'defaultValueTriggerFlags' in attribute:
                                del attribute['defaultValueTriggerFlags']
                        else:
                            attribute['defaultValues'] = [
                                {
                                    "locales": [
                                        {
                                            "value": default_value
                                        }
                                    ]
                                }
                            ]
                            attribute['defaultValueTriggerFlags'] = ','.join(flags) if (flags is not None) and (len(flags) > 0) else 'None'
                        is_attribute_found = True
                    new_attributes.append(attribute)

            if is_attribute_found:
                self.opened_entity_type['attributes'] = new_attributes
                return True
            else:
                self.print_error(prefix_error,
                                 f"Тип сущности {self.opened_entity_type['key']} не содержит атрибут {key}")
                return False

    def _remove_attribute(self, *args):
        """Удалить атрибут у типа сущности
        remove_attribute <key>"""
        prefix_error = "remove_attribute error:"

        key = args[0] if len(args) > 0 else None

        if not key:
            self.print_error(prefix_error, f"Укажите ключ атрибута")
            return False

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False
        else:
            # есть открытый entity type

            self.opened_entity_type['attributes'] = [
                attribute
                for attribute in self.opened_entity_type['attributes']
                if attribute['key'].lower() != key.lower()
            ]
            return True

    def _edit_computed_value(self, *args):
        """Задать вычисляемое значение атрибута
        edit_computed_value <key>"""
        prefix_error = "edit_computed_value error:"

        key = args[0] if len(args) > 0 else None

        if not key:
            self.print_error(prefix_error, f"Отсутствует ключ вычисляемого атрибута")
            return False

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False

        computed_attribute = next(((lambda x: x)(attribute)
                                   for attribute in self.opened_entity_type["attributes"]
                                   if attribute["key"].lower() == key.lower()), None)

        if not computed_attribute:
            self.print_error(prefix_error,
                             f"Атрибут {key} не найден")
            return False

        if 'IsComputed' not in computed_attribute['flags']:
            self.print_error(prefix_error,
                             f"Атрибут {key} не вычисляемый, установите флаг IsComputed")
            return False

        self.opened_computed_attribute = computed_attribute
        if 'computedValueTriggerFlags' not in self.opened_computed_attribute:
            self.opened_computed_attribute['computedValueTriggerFlags'] = "OnCreate, OnUpdate, OnVariableChanged"
        if 'computedValues' not in self.opened_computed_attribute:
            self.opened_computed_attribute['computedValues'] = [
                {
                    "expression": "",
                    "expressionType": "Expression",
                    "variables": None
                }
            ]

        return True

    def _set_variable_attribute(self, *args):
        """Задать переменную для вычисляемого атрибута по другому атрибуту этой сущности или сущности, на которую ссылается эта.
        set_variable_attribute <variable_key>, [<to_reference_key>], <attribute_key>[, SetDefault | Error | Ignore]"""

        variable_key = args[0] if len(args) > 0 else None
        to_reference_key = args[1] if len(args) > 1 else None
        attribute_key = args[2] if len(args) > 2 else None
        attribute_not_found_behavior = args[3] if len(args) > 3 else None

        return self.__set_variable_attribute(variable_key, to_reference_key, None, attribute_key, attribute_not_found_behavior)

    def _set_variable_attribute_from(self, *args):
        """Задать переменную для вычисляемого атрибута по атрибуту другой сущности, ссылающейся на эту
        set_variable_attribute_from <variable_key>, <from_reference_key>, <attribute_key>[, SetDefault | Error | Ignore]"""

        variable_key = args[0] if len(args) > 0 else None
        from_reference_key = args[1] if len(args) > 1 else None
        attribute_key = args[2] if len(args) > 2 else None
        attribute_not_found_behavior = args[3] if len(args) > 3 else None

        return self.__set_variable_attribute(variable_key, None, from_reference_key, attribute_key, attribute_not_found_behavior)

    def _set_variable_default_value(self, *args):
        """Установить дефолтное значение переменной вычисляемого атрибута
        set_variable_default_value <variable_key> [<default_value>]"""
        prefix_error = "set_variable_default_value error:"

        variable_key = args[0] if len(args) > 0 else None
        default_value = args[1] if len(args) > 1 else None

        if not variable_key:
            self.print_error(prefix_error, f"Отсутствует variable_key")
            return False

        if self.opened_computed_attribute == {}:
            # нет открытого computed_value
            self.print_error(prefix_error,
                             f"Нет открытого вычисляемого значения. Используйте предварительно команду edit_computed_value <key>")
            return False

        # есть открытый computed_value
        is_variable_found = False
        new_variables = []
        if ('computedValues' in self.opened_computed_attribute) and ('variables' in self.opened_computed_attribute['computedValues'][0]):
            for variable in self.opened_computed_attribute['computedValues'][0]['variables']:
                if variable['variableKey'].lower() == variable_key.lower():
                    if not default_value and 'defaultValues' in variable:
                        del variable['defaultValues']
                    else:
                        variable['defaultValues'] = [default_value]
                    is_variable_found = True
                new_variables.append(variable)

        if is_variable_found:
            self.opened_computed_attribute['computedValues'][0]['variables'] = new_variables
            return True
        else:
            self.print_error(prefix_error,
                             f"Вычисляемое значение {self.opened_computed_attribute['key']} не содержит переменную {variable_key}")
            return False

    def _set_variable_workflow(self, *args):
        """Задать для вычисляемого атрибута переменную, связанную с workflow
        set_variable_workflow <variable_key>, <workflow_key>"""
        prefix_error = "set_variable_workflow error:"

        variable_key = args[0] if len(args) > 0 else None
        workflow_key = args[1] if len(args) > 1 else None

        if not variable_key:
            self.print_error(prefix_error, f"Отсутствует variable_key")
            return False

        if not workflow_key:
            self.print_error(prefix_error, f"Отсутствует workflow_key")
            return False

        if self.opened_computed_attribute == {}:
            # нет открытого computed_value
            self.print_error(prefix_error,
                             f"Нет открытого вычисляемого значения. Используйте предварительно команду edit_computed_value <key>")
            return False

        new_variables = []
        for variable in self.opened_computed_attribute['computedValues'][0]['variables']:
            if variable['variableKey'].lower() != variable_key.lower():
                new_variables.append(variable)

        new_variables.append(
            {
                "workflowKey": workflow_key,
                "variableKey": variable_key.upper(),
                "type": "Workflow"
            }
        )

        self.opened_computed_attribute['computedValues'][0]['variables'] = new_variables

        return True

    def _delete_variable(self, *args):
        """Удалить переменную для вычисляемого атрибута
        delete_variable <variable_key>"""
        prefix_error = "delete_variable error:"

        variable_key = args[0] if len(args) > 0 else None

        if not variable_key:
            self.print_error(prefix_error, f"Отсутствует variable_key")
            return False

        if self.opened_computed_attribute == {}:
            # нет открытого computed_value
            self.print_error(prefix_error,
                             f"Нет открытого вычисляемого значения. Используйте предварительно команду edit_computed_value <key>")
            return False

        new_variables = []
        for variable in self.opened_computed_attribute['computedValues'][0]['variables']:
            if variable['variableKey'].lower() != variable_key.lower():
                new_variables.append(variable)

        self.opened_computed_attribute['computedValues'][0]['variables'] = new_variables

        return True

    def _show_variables(self, *args):
        """Показать все переменные для вычисляемого атрибута
        show_variables"""
        prefix_error = "show_variables error:"

        if self.opened_computed_attribute == {}:
            # нет открытого computed_value
            self.print_error(prefix_error,
                             f"Нет открытого вычисляемого значения. Используйте предварительно команду edit_computed_value <key>")
            return False

        if len(self.opened_computed_attribute['computedValues'][0]['variables']) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные переменные:")
            self.__print_and_log(f"----------------------------------")
            for variable in self.opened_computed_attribute['computedValues'][0]['variables']:
                self.__print_and_log(
                    f"variableKey: {variable['variableKey']}, type: {variable['type']}{', attributeKey: ' + variable['attributeKey'] if 'attributeKey' in variable else ''}{', toReferenceKey: ' + variable['toReferenceKey'] if 'toReferenceKey' in variable else ''}{', attributeNotFoundBehavior: ' + variable['attributeNotFoundBehavior'] if 'attributeNotFoundBehavior' in variable else ''}{', workflowKey: ' + variable['workflowKey'] if 'workflowKey' in variable else ''}")
            self.__print_and_log('')
        else:
            self.__print_and_log(f"Переменные отсутствуют")

        return True

    def _set_expression(self, *args):
        """Задать выражение для вычисляемого атрибута
        set_expression "<expression>" [Expression|Script]  # Expression by default"""
        prefix_error = "set_expression error:"

        expression = args[0] if len(args) > 0 else None
        expression_type = args[1] if len(args) > 1 else "Expression"

        if not expression:
            self.print_error(prefix_error, f"Отсутствует expression")
            return False

        if not expression_type:
            expression_type = "Expression"

        if self.opened_computed_attribute == {}:
            # нет открытого computed_value
            self.print_error(prefix_error,
                             f"Нет открытого вычисляемого значения. Используйте предварительно команду edit_computed_value <key>")
            return False

        self.opened_computed_attribute['computedValues'][0]['expression'] = expression.encode().decode('unicode-escape')
        self.opened_computed_attribute['computedValues'][0]['expressionType'] = expression_type

        return True

    def _set_computed_value_flags(self, *args):
        """Задать флаги для вычисляемого атрибута
        set_computed_value_flags [OnCreate], [OnUpdate], [OnVariableChanged]"""
        prefix_error = "set_computed_value_flags error:"

        flags = args[0:] if len(args) > 0 else []

        # удаление None элемента из массива
        flags = self.__remove_none_from_array(flags)

        if flags and (not self.__validate_flags(flags, ['oncreate', 'onupdate', 'onvariablechanged'])):
            self.print_error(prefix_error,
                             f'Неверный флаг для вычисляемого атрибута. Возможные значения: OnCreate, OnUpdate, OnVariableChanged')
            return False

        if self.opened_computed_attribute == {}:
            # нет открытого computed_value
            self.print_error(prefix_error,
                             f"Нет открытого вычисляемого значения. Используйте предварительно команду edit_computed_value <key>")
            return False

        self.opened_computed_attribute['computedValueTriggerFlags'] = ','.join(flags) if (flags is not None) and (len(flags) > 0) else "None"

        return True

    def _close_computed_value(self, *args):
        """Применить изменения и закрыть вычисляемый атрибут
        close_computed_value"""
        prefix_error = "close_computed_value error:"

        if self.opened_computed_attribute == {}:
            # нет открытого computed_value
            self.print_error(prefix_error,
                             f"Нет открытого вычисляемого значения. Используйте предварительно команду edit_computed_value <key>")
            return False

        new_attributes = []
        for attribute in self.opened_entity_type['attributes']:
            if attribute['key'].lower() != self.opened_computed_attribute['key'].lower():
                new_attributes.append(attribute)

        new_attributes.append(self.opened_computed_attribute)
        self.opened_entity_type['attributes'] = new_attributes
        self.opened_computed_attribute = {}

        return True

    def _discard_computed_value(self, *args):
        """Отменить изменения вычисляемого атрибута
        discard_computed_value"""

        self.opened_computed_attribute = {}
        return True

    def _show_computed_values(self, *args):
        """Показать все вычисляемые атрибуты
        show_computed_values"""
        prefix_error = "show_computed_values error:"

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False

        if len(self.opened_entity_type['attributes']) > 0:
            show_first_computed_attribute = True  # признак показа первого вычислямого атрибута (типа Expression)
            for attribute in self.opened_entity_type['attributes']:
                if ('IsComputed' in attribute['flags']) and \
                        (('computedValues' in attribute and 'expression' == attribute['computedValues'][0]['expressionType'].lower()) or ('computedValues' not in attribute)):
                    if show_first_computed_attribute:
                        self.__print_and_log('')
                        self.__print_and_log(f"Доступные вычисляемые атрибуты (типа Expression):")
                        self.__print_and_log(f"----------------------------------")
                        show_first_computed_attribute = False
                    self.__print_and_log(
                        f"key: {attribute['key']}, flags: {attribute['flags']}{', computedValueTriggerFlags: ' + attribute['computedValueTriggerFlags'] if 'computedValueTriggerFlags' in attribute else ''}{', expression: ' + attribute['computedValues'][0]['expression'] if 'computedValues' in attribute else ''}")
            if show_first_computed_attribute:  # никакие вычисляемые атрибуты не были показаны
                self.__print_and_log(f"Вычисляемые атрибуты (типа Expression) отсутствуют")
        else:
            self.__print_and_log(f"Атрибуты отсутствуют")

        self.__print_and_log('')

        return True

    def _add_reference_to(self, *args):
        """Добавление ссылки на другой тип сущности
        add_reference_to <entity_type>, <reference_type>[, <toReferenceKey>, <fromReferenceKey>]"""
        prefix_error = "add_reference_to error:"

        entity_type_key = args[0] if len(args) > 0 else None
        reference_type = args[1] if len(args) > 1 else None
        to_reference_key = args[2] if len(args) > 2 else None
        from_reference_key = args[3] if len(args) > 3 else None

        if not entity_type_key:
            self.print_error(prefix_error,
                             f"Укажите ключ существующего типа, на который должен ссылать текущий тип")
            return False

        if not reference_type:
            self.print_error(prefix_error,
                             f"Укажите тип ссылки")
            return False

        if reference_type.lower() not in ['manytomany', 'onetomany', 'manytoone', 'onetoone']:
            self.print_error(prefix_error,
                             f"Неверный тип ссылки {reference_type}. Возможные значения: ManyToMany, OneToMany, ManyToOne, OneToOne")
            return False

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False

        if not from_reference_key:
            from_reference_key = f"{self.opened_entity_type['key']}"

        if not to_reference_key:
            to_reference_key = f"{entity_type_key}"

        reference = {
            'fromEntityTypeKey': self.opened_entity_type['key'],
            'toEntityTypeKey': entity_type_key,
            'fromReferenceKey': from_reference_key,
            'toReferenceKey': to_reference_key,
            'type': reference_type,
            'flags': 'None'
        }

        if self.opened_entity_type_references is None:
            self.opened_entity_type_references = [reference]
        else:
            self.opened_entity_type_references.append(reference)
        return True

    def _add_reference_from(self, *args):
        """Добавление ссылки другого типа сущности на этот
        add_reference_from <entity_type>, <reference_type>[, <toReferenceKey>, <fromReferenceKey>]"""
        prefix_error = "add_reference_from error:"

        entity_type_key = args[0] if len(args) > 0 else None
        reference_type = args[1] if len(args) > 1 else None
        to_reference_key = args[2] if len(args) > 2 else None
        from_reference_key = args[3] if len(args) > 3 else None

        if not entity_type_key:
            self.print_error(prefix_error,
                             f"Укажите ключ существующего типа, который должен ссылаться на текущий тип")
            return False

        if not reference_type:
            self.print_error(prefix_error,
                             f"Укажите тип ссылки")
            return False

        if reference_type.lower() not in ['manytomany', 'onetomany', 'manytoone', 'onetoone']:
            self.print_error(prefix_error,
                             f"Неверный тип ссылки {reference_type}. Возможные значения: ManyToMany, OneToMany, ManyToOne, OneToOne")
            return False

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False

        if not from_reference_key:
            from_reference_key = f"{entity_type_key}"

        if not to_reference_key:
            to_reference_key = f"{self.opened_entity_type['key']}"

        reference = {
            'fromEntityTypeKey': entity_type_key,
            'toEntityTypeKey': self.opened_entity_type['key'],
            'fromReferenceKey': from_reference_key,
            'toReferenceKey': to_reference_key,
            'type': reference_type,
            'flags': 'None'
        }

        if self.opened_entity_type_references is None:
            self.opened_entity_type_references = [reference]
        else:
            self.opened_entity_type_references.append(reference)
        return True

    def _remove_reference_to(self, *args):
        """Удаление ссылки на другой тип сущности
        remove_reference_to <toReferenceKey>"""
        prefix_error = "remove_reference_to error:"

        to_reference_key = args[0] if len(args) > 0 else None

        if not to_reference_key:
            self.print_error(prefix_error,
                             f"Укажите ссылку, которую необходимо удалить")
            return False

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False

        for reference in self.opened_entity_type_references:
            if reference['toReferenceKey'].lower() == to_reference_key.lower():
                reference['to_delete'] = True

        return True

    def _remove_reference_from(self, *args):
        """Удаление ссылки другого типа сущности на этот
        remove_reference_from <fromReferenceKey>"""
        prefix_error = "remove_reference_from error:"

        from_reference_key = args[0] if len(args) > 0 else None

        if not from_reference_key:
            self.print_error(prefix_error,
                             f"Укажите ссылку, которую необходимо удалить")
            return False

        if self.opened_entity_type == {}:
            # нет открытого entity type
            self.print_error(prefix_error,
                             f"Нет открытого entity type. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False

        for reference in self.opened_entity_type_references:
            if reference['fromReferenceKey'].lower() == from_reference_key.lower():
                reference['to_delete'] = True

        return True

    def _save_entity_type(self, *args):
        """Сохранить открытый тип сущности
        save_entity_type"""
        prefix_error = "save_entity_type error:"

        if self.opened_entity_type == {}:
            # нет открытого entity_type
            self.print_error(prefix_error,
                             f"Нет открытого типа сущности. Используйте предварительно команды create_entity_type <key> или edit_entity_type <key>")
            return False

        # удаление пустого массива attributes
        if "attributes" in self.opened_entity_type:
            if not self.opened_entity_type["attributes"]:
                del self.opened_entity_type["attributes"]

        # удаление ключа для дефолтного значения атрибута, если есть
        if "attributes" in self.opened_entity_type:
            new_attributes = []
            for attribute in self.opened_entity_type['attributes']:
                if 'defaultValues' in attribute:
                    for default_value in attribute['defaultValues']:
                        if 'key' in default_value:
                            del default_value['key']
                new_attributes.append(attribute)
            self.opened_entity_type['attributes'] = new_attributes

        entity_type_creation_mode = False
        # проверка надо создавать или обновлять
        if 'id' in self.opened_entity_type:
            # entity_type существует
            response = self.rest_api_client.put_entity_type([self.opened_entity_type], access_level=self.access_level)
        else:
            # entity_type не существует
            entity_type_creation_mode = True
            response = self.rest_api_client.create_entity_type([self.opened_entity_type], access_level=self.access_level)

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        created_entity_type_id = response.json()[0]['id']

        references_created = not self.opened_entity_type_references
        if self.opened_entity_type_references:
            while True:
                references_to_create = []
                references_to_update = []
                references_to_delete = []

                for reference in self.opened_entity_type_references:
                    if 'id' in reference:
                        if 'to_delete' in reference:
                            references_to_delete.append(reference)
                        else:
                            references_to_update.append(reference)
                    else:
                        if 'to_delete' not in reference:
                            references_to_create.append(reference)

                if references_to_create:
                    response = self.rest_api_client.create_reference(references_to_create, access_level=self.access_level)
                    if response.status_code != 200:
                        self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                        break

                if references_to_update:
                    response = self.rest_api_client.put_references(references_to_update, access_level=self.access_level)
                    if response.status_code != 200:
                        self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                        break

                if references_to_delete:
                    response = self.rest_api_client.delete_references([ref['id'] for ref in references_to_delete], access_level=self.access_level)
                    if response.status_code != 204:
                        self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                        break

                references_created = True
                break

        if (not references_created) and entity_type_creation_mode:
            response = self.rest_api_client.delete_entity_type(created_entity_type_id, access_level=self.access_level)
            if response.status_code != 204:
                self.print_error(prefix_error, 'Не удается удалить ранее созданный тип сущности')
                return False

        if entity_type_creation_mode:
            # добавляем permission
            response = self.rest_api_client.create_entity_type_permissions(created_entity_type_id,
                                                                           self.opened_permissions['Value'],
                                                                           access_level=self.access_level)
            if response.status_code != 200:
                self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                return False
        else:
            # получаем списки изменённых permissions
            update_permissions = []
            create_permissions = []
            delete_permissions = []
            for permission in self.opened_permissions['Value']:
                if 'id' in permission:
                    # обновление permission
                    update_permissions.append(permission)
                else:
                    # создание нового
                    create_permissions.append(permission)

            # что удалить
            for old_permission in self.opened_entity_type_permissions:
                if 'id' in old_permission:
                    if self.rewrite_all_permissions:
                        delete_permissions.append(old_permission['id'])
                    else:
                        is_found = False
                        for permission in self.opened_permissions['Value']:
                            if permission['type'] == old_permission['type'] and permission['level'] == old_permission['level']:
                                is_found = True
                                break
                        if not is_found:
                            delete_permissions.append(old_permission['id'])

            if len(delete_permissions) > 0:
                # удаление permissions
                response = self.rest_api_client.delete_entity_type_permissions(created_entity_type_id, delete_permissions, access_level=self.access_level)
                if response.status_code != 204:
                    self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                    return False

            if len(update_permissions) > 0:
                # обновление permissions
                response = self.rest_api_client.put_entity_type_permissions(created_entity_type_id, update_permissions, access_level=self.access_level)
                if response.status_code != 200:
                    self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                    return False

            if len(create_permissions) > 0:
                # создание новых permissions
                response = self.rest_api_client.create_entity_type_permissions(created_entity_type_id, create_permissions, access_level=self.access_level)

                if response.status_code != 200:
                    self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
                    return False

        self.print_success(f'{self.opened_entity_type["key"]}: {created_entity_type_id}')

        # успешно сохранён entity_type
        self.opened_entity_type = {}
        self.opened_entity_type_references = []
        self.opened_entity_type_permissions = []
        self.opened_permissions = {}
        self.rewrite_all_permissions = False  # этот флаг взводится только командой set_permissions_from_variable

        return True

    def _discard_entity_type(self, *args):
        """Отмена изменений открытого типа сущности
        discard_entity_type"""
        self.opened_entity_type = {}
        self.opened_entity_type_references = []
        self.opened_entity_type_permissions = []
        self.opened_permissions = {}

        return True

    def _delete_entity_type(self, *args):
        """Удалить тип сущности
        delete_entity_type <key>"""
        prefix_error = "delete_entity_type error:"

        key = args[0] if len(args) > 0 else None

        if not key:
            self.print_error(prefix_error,
                             f"Укажите ключ существующего entity type")
            return False

        response = self.rest_api_client.get_entity_types(f"key={key}", access_level=self.access_level)
        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        entity_types = response.json()
        if len(entity_types) != 1:
            self.print_error(prefix_error, f"Не удалось найти тип {key}. Текущее кол-во {len(entity_types)}")
            return False

        response = self.rest_api_client.delete_entity_type(entity_types[0]['id'], access_level=self.access_level)
        if response.status_code != 204:
            self.print_error(prefix_error, response.text)
            return False

        return True

    def _show_entity_types(self, *args):
        """Показать все имеющиеся типы сущностей
        show_entity_types
        """
        prefix_error = "show_entity_types error:"

        response = self.rest_api_client.get_entity_types(access_level=self.access_level)
        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        entity_types = response.json()
        if len(entity_types) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные entity types:")
            self.__print_and_log(f"----------------------------------")
            for entity_type in entity_types:
                self.__print_and_log(f"{entity_type['key']}"
                                     f"{' (' + entity_type['flags'] + ')' if entity_type['flags'] != 'None' else ''}"
                                     f": {entity_type['id']}"
                                     f"{', parent: ' + entity_type['parentKey'] if 'parentKey' in entity_type else ''}")
            self.__print_and_log('')
        else:
            self.__print_and_log(f"Entity types отсутствуют")

        return True

    """ References """

    def _edit_reference(self, *args):
        """Редактирование ссылки сущностей
        edit_reference <from_entity_type> <toReferenceKey>"""
        prefix_error = "edit_reference error:"

        from_entity_type = args[0] if len(args) > 0 else None
        to_reference_key = args[1] if len(args) > 1 else None

        if not from_entity_type:
            self.print_error(prefix_error, "Укажите from_entity_type")
            return False

        if not to_reference_key:
            self.print_error(prefix_error, "Укажите to_reference_key")
            return False

        response = self.rest_api_client.get_references(
            from_entity_type_key=from_entity_type,
            to_references_keys=[to_reference_key],
            access_level=self.access_level)

        if response.status_code != 200:
            self.print_error(prefix_error, response.text)

        references = response.json()
        if not references:
            self.print_error(prefix_error,
                             f"Сслыка сущности с параметрами: from_entity_type - {from_entity_type}, to_reference_key - {to_reference_key}, - не найдена")
            return False

        self.opened_reference = references[0]

        return True

    def _set_reference_to_key(self, *args):
        """Поменять имя ссылки на другую сущность
        set_reference_to_key <toReferenceKey>"""
        prefix_error = "set_reference_to_key error:"

        to_reference_key = args[0] if len(args) > 0 else None

        if not to_reference_key:
            self.print_error(prefix_error, "Укажите to_reference_key")
            return False

        if self.opened_reference == {}:
            self.print_error(prefix_error, 'Текущая ссылка не выбрана. Воспользуйтесь вначала командой edit_reference')
            return False

        self.opened_reference['toReferenceKey'] = to_reference_key
        return True

    def _set_reference_from_key(self, *args):
        """Поменять имя ссылки от другой сущности
        set_reference_from_key <fromReferenceKey>"""
        prefix_error = "set_reference_from_key error:"

        from_reference_key = args[0] if len(args) > 0 else None

        if not from_reference_key:
            self.print_error(prefix_error, "Укажите from_reference_key")
            return False

        if self.opened_reference == {}:
            self.print_error(prefix_error, 'Текущая ссылка не выбрана. Воспользуйтесь вначала командой edit_reference')
            return False

        self.opened_reference['fromReferenceKey'] = from_reference_key
        return True

    def _set_reference_flags(self, *args):
        """Поменять флаги ссылки сущностей
        set_reference_flags [IsDeleteCascade], [IsRequired], [IsDraftMandatory]"""
        prefix_error = "set_reference_flags error:"

        flags = args[0:] if len(args) > 0 else []

        # удаление None элемента из массива
        flags = self.__remove_none_from_array(flags)

        if flags and (not self.__validate_flags(flags, ['isrequired', 'isdeletecascade', 'isdraftmandatory'])):
            self.print_error(prefix_error, f'Неверный флаг для ссылки. Возможные значения: IsRequired, IsDeleteCascade, IsDraftMandatory')
            return False

        if self.opened_reference == {}:
            self.print_error(prefix_error, 'Текущая ссылка не выбрана. Воспользуйтесь вначала командой edit_reference')
            return False

        self.opened_reference['flags'] = ','.join(flags) if (flags is not None) and (len(flags) > 0) else "None"
        return True

    def _set_reference_type(self, *args):
        """Поменять тип ссылки сущностей
        set_reference_type <type>"""
        prefix_error = "set_reference_type error:"

        reference_type = args[0] if len(args) > 0 else None

        if not reference_type:
            self.print_error(prefix_error, 'Тип ссылки не задан')
            return False

        if self.opened_reference == {}:
            self.print_error(prefix_error, 'Текущая ссылка не выбрана. Воспользуйтесь вначала командой edit_reference')
            return False

        self.opened_reference['type'] = reference_type
        return True

    def _save_reference(self, *args):
        """Сохранить изменения ссылки сущностей
        save_reference"""
        prefix_error = "save_reference error:"

        if self.opened_reference == {}:
            self.print_error(prefix_error, 'Текущая ссылка не выбрана. Воспользуйтесь вначала командой edit_reference')
            return False

        response = self.rest_api_client.put_references([self.opened_reference], access_level=self.access_level)
        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        return True

    def _discard_reference(self, *args):
        """Отменить изменения ссылки сущностей
        discard_reference"""
        self.opened_reference = {}
        return True

    def _delete_reference(self, *args):
        """Удалить существующую ссылку сущностей
        delete_reference <from_entity_type>, <toReferenceKey>"""
        prefix_error = "delete_reference error:"

        from_entity_type = args[0] if len(args) > 0 else None
        to_reference_key = args[1] if len(args) > 1 else None

        if not from_entity_type:
            self.print_error(prefix_error, 'Параметр from_entity_type не задан')
            return False

        if not to_reference_key:
            self.print_error(prefix_error, 'Параметр to_reference_key не задан')
            return False

        response = self.rest_api_client.get_references(from_entity_type_key=from_entity_type,
                                                       to_references_keys=[to_reference_key],
                                                       access_level=self.access_level)
        if (response.status_code != 200) or (len(response.json()) == 0):
            self.print_error(prefix_error,
                             f'Ссылка с параметрами: from_entity_type={from_entity_type} и to_reference_key={to_reference_key}, - не найдена')
            return False

        response = self.rest_api_client.delete_references([response.json()[0]['id']], access_level=self.access_level)
        if response.status_code != 204:
            self.print_error(prefix_error,
                             f'Не удалось удалить ссылку с параметрами: from_entity_type={from_entity_type} и to_reference_key={to_reference_key}')
            return False

        return True

    def _show_references(self, *args):
        """Получить информацию о заведенных ссылках сущностей
        show_references"""
        prefix_error = "show_entity_types error:"

        response = self.rest_api_client.get_references(access_level=self.access_level)
        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        references = response.json()
        if len(references) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные ссылки:")
            self.__print_and_log(f"----------------------------------")
            for reference in references:
                self.__print_and_log(
                    f"fromEntityTypeKey: {reference['fromEntityTypeKey']}, toEntityTypeKey: {reference['toEntityTypeKey']}, fromKey: {reference['fromReferenceKey']}, toKey: {reference['toReferenceKey']}, id: {reference['id']}, flags: {reference['flags']}")
            self.__print_and_log('')
        else:
            self.__print_and_log(f"Ссылки отсутствуют")
        return True

    """ Entities """

    def _create_entity(self, *args):
        """Создание новой сущности
        create_entity <entity_type>"""
        prefix_error = "create_entity error:"

        entity_type_key = args[0] if len(args) > 0 else None

        if not entity_type_key:
            self.print_error(prefix_error, 'Не задан тип сущности')
            return False

        self.opened_entity = {
            'entityTypeKey': entity_type_key,
            'attributeValues': [],
            'referencedTo': []
        }

        return True

    def _edit_entity(self, *args):
        """Редактирование cущности
        edit_entity <entity_id>"""
        prefix_error = "edit_entity error:"

        entity_id = args[0] if len(args) > 0 else None

        if not entity_id:
            self.print_error(prefix_error, 'Не указан id сущности, которую необходимо отредактировать')
            return False

        response = self.rest_api_client.get_entities(f'id={entity_id}&WithAttributeValues=true&WithReferencedTo=true')
        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        entities = response.json()
        if not entities:
            self.print_error(prefix_error, f'Сущность с id = {entity_id} не найдена')
            return False

        self.opened_entity = entities[0]
        if 'attributeValues' in self.opened_entity:
            self.opened_entity['attributeValues'] = [
                {
                    'id': attr_value['id'],
                    'attributeKey': attr_value['attributeKey'],
                    'valueLocales': attr_value['valueLocales']
                }

                for attr_value in self.opened_entity['attributeValues']
            ]
        else:
            self.opened_entity['attributeValues'] = []

        if 'referencedTo' in self.opened_entity:
            self.opened_entity['referencedTo'] = [
                {
                    'id': reference_to['id'],
                    'entityId': reference_to['entityId'],
                    'key': reference_to['key']
                }

                for reference_to in self.opened_entity['referencedTo']
            ]
        else:
            self.opened_entity['referencedTo'] = []

        return True

    def _set_entity_attribute_value(self, *args):
        """Установка значения атрибута сущности
        set_entity_attribute_value <key> [<value>]"""
        prefix_error = "set_entity_attribute_value error:"

        key = args[0] if len(args) > 0 else None
        value = args[1] if len(args) > 1 else None

        if not key:
            self.print_error(prefix_error, 'Параметр key не задан')
            return False

        if not value:
            value = ""

        if self.opened_entity == {}:
            self.print_error(prefix_error,
                             'Текущая сущность не выбрана. Сперва воспользуйтесь методом create_entity или edit_entity')
            return False

        for attr_value in self.opened_entity['attributeValues']:
            if attr_value['attributeKey'].lower() == key.lower():
                if attr_value['valueLocales']:
                    attr_value['valueLocales'][0]['value'] = value
                else:
                    attr_value['valueLocales'].append({
                        'value': value
                    })

                return True

        if self.opened_entity['attributeValues'] is None:
            self.opened_entity['attributeValues'] = [{
                'attributeKey': key,
                'valueLocales': [{
                    'value': value
                }]
            }]
        else:
            self.opened_entity['attributeValues'].append({
                'attributeKey': key,
                'valueLocales': [{
                    'value': value
                }]
            })

        return True

    def _add_entity_reference_to(self, *args):
        """Настроить связь между сущностями
        add_entity_reference_to <toReferenceKey>, <entity_id>"""
        prefix_error = "add_entity_reference_to error:"

        to_reference_key = args[0] if len(args) > 0 else None
        entity_id = args[1] if len(args) > 1 else None

        if not to_reference_key:
            self.print_error(prefix_error, 'Не задан параметр to_reference_key')
            return False

        if not entity_id:
            self.print_error(prefix_error, 'Не задан параметр entity_id')
            return False

        if self.opened_entity == {}:
            self.print_error(prefix_error,
                             'Текущая сущность не выбрана. Сперва воспользуйтесь методом create_entity или edit_entity')
            return False

        if self.opened_entity['referencedTo'] is None:
            self.opened_entity['referencedTo'] = [{
                'key': to_reference_key,
                'entityId': entity_id
            }]
        else:
            self.opened_entity['referencedTo'].append({
                'key': to_reference_key,
                'entityId': entity_id
            })

        return True

    def _remove_entity_reference_to(self, *args):
        """Удалить связь между сущностями
        remove_entity_reference_to <toReferenceKey>, <entity_id>"""
        prefix_error = "remove_entity_reference_to error:"

        to_reference_key = args[0] if len(args) > 0 else None
        entity_id = args[1] if len(args) > 1 else None

        if not to_reference_key:
            self.print_error(prefix_error, 'Не задан параметр to_reference_key')
            return False

        if not entity_id:
            self.print_error(prefix_error, 'Не задан параметр entity_id')
            return False

        if self.opened_entity == {}:
            self.print_error(prefix_error,
                             'Нет открытой сущности. Сперва воспользуйтесь методом create_entity или edit_entity')
            return False

        self.opened_entity['referencedTo'] = [
            reference
            for reference in self.opened_entity['referencedTo']
            if (reference['key'].lower() != to_reference_key.lower()) or (reference['entityId'] != entity_id)
        ]

        return True

    def _save_entity(self, *args):
        """Сохранение изменений сущности
        save_entity [Drafted | Published]"""
        prefix_error = "save_entity error:"

        draft_state = args[0] if len(args) > 0 else None

        if self.opened_entity == {}:
            self.print_error(prefix_error,
                             'Нет открытой сущности. Сперва воспользуйтесь методом create_entity или edit_entity')
            return False

        if self.opened_entity['attributeValues']:
            # удаление текущих значений атрибутов из Entity
            attribute_values = self.opened_entity['attributeValues']
            self.opened_entity['attributeValues'] = []

            for attribute_value in attribute_values:
                if attribute_value['valueLocales'][0]['value'] != '':
                    self.opened_entity['attributeValues'].append(attribute_value)

        if not self.opened_entity['attributeValues']:
            self.opened_entity['attributeValues'] = None

        if not self.opened_entity['referencedTo']:
            self.opened_entity['referencedTo'] = None

        # обработка логики черновика
        if draft_state not in (None, ''):
            if draft_state.lower() == 'drafted':
                parameters = "isDraft=true"
            elif draft_state.lower() == 'published':
                parameters = "isDraft=false"
            else:
                self.print_error(prefix_error,
                                 'Для сущности состояние черновик или чистовик задано неправильно, используйте save_entity [Drafted | Published]')
                return False
        else:
            if 'isDraft' in self.opened_entity and self.opened_entity['isDraft']:
                parameters = "isDraft=true"
            else:
                parameters = ""

        if 'id' in self.opened_entity:
            response = self.rest_api_client.put_entities([self.opened_entity], parameters)
        else:
            response = self.rest_api_client.create_entity([self.opened_entity], parameters)

        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        self.print_success(response.json()[0]['id'])

        self.opened_entity = {}
        return True

    def _discard_entity(self, *args):
        """Отмена изменений сущности
        discard_entity"""
        self.opened_entity = {}
        return True

    def _delete_entity(self, *args):
        """Удаление сущности
        delete_entity <entity_id>"""
        prefix_error = "delete_entity error:"

        entity_id = args[0] if len(args) > 0 else None

        if (entity_id is None) or (len(entity_id) == 0):
            self.print_error(prefix_error, 'Не задан параметр entity_id')
            return False

        response = self.rest_api_client.delete_entity([entity_id])

        if response.status_code != 204:
            self.print_error(prefix_error, response.text)
            return False

        return True

    def _show_entities(self, *args):
        """Показать сущности
        show_entities [<entity_type>]"""
        prefix_error = "show_entities error:"

        entity_type_key = args[0] if len(args) > 0 else None

        if entity_type_key in (None, ''):
            response = self.rest_api_client.get_entity_types()
            if response.status_code != 200:
                self.print_error(prefix_error, response.text)
                return False

            if len(response.json()) < 1:
                self.__print_and_log(f"Нет никаких типов сущностей")
                return True

            entity_types = []
            for entity_type in response.json():
                entity_types.append(entity_type['key'])

            vector_data = {
                "entitiesOptions": {
                    "includeAttributeValuesByAttributeKeys": ["*"],
                    "includeEntityWorkflowStatesByWorkflowKeys": ["*"],
                    "includeReferences": True
                },
                "entitiesByEntityTypeKeys": entity_types,
                "locale": "none"
            }
            vector_count_data = {
                "entitiesByEntityTypeKeys": entity_types,
                "locale": "none"
            }
        else:
            vector_data = {
                "entitiesOptions": {
                    "includeAttributeValuesByAttributeKeys": ["*"],
                    "includeEntityWorkflowStatesByWorkflowKeys": ["*"],
                    "includeReferences": True
                },
                "entitiesByEntityTypeKeys": [entity_type_key],
                "locale": "none"
            }
            vector_count_data = {
                "entitiesByEntityTypeKeys": [entity_type_key],
                "locale": "none"
            }

        # получение всех Entities
        entities = self.rest_api_client.get_all_entities_vector(vector_data,
                                                                vector_count_data)  # в случае успеха возвращается json со всеми entities, status_code отсутствует

        if hasattr(entities, 'status_code'):
            self.print_error(prefix_error, entities.text)
            return False

        if len(entities) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные сущности:")
            self.__print_and_log(f"----------------------------------")
            for entity in entities:
                if 'attributeValues' in entity:
                    attribute_name = next(((lambda x: x)(attributeValue)
                                           for attributeValue in entity["attributeValues"]
                                           if attributeValue["attributeKey"] == "__NAME"), None)
                else:
                    attribute_name = None
                self.__print_and_log(
                    f"id: {entity['id']} ({entity['entityTypeKey']})"
                    f"{', __NAME: ' + attribute_name['valueLocales'][0]['value'] if attribute_name else ''}"
                    f"{', StateMachine: ' + entity['stateKey'] if 'stateKey' in entity else ''}"
                    f"{', Drafted' if ('isDraft' in entity) and (entity['isDraft']) else ''}"
                    f"{', Published' if ('isDraft' in entity) and (not entity['isDraft']) else ''}")
            self.__print_and_log('')
        else:
            self.__print_and_log(f"Сущности не созданы")

        return True

    """ Entity State Categories """

    def _add_entity_state_category(self, *args):
        """Создание новой категорий для состояний сущности
        add_entity_state_category <entity_state_category_key>"""
        prefix_error = "add_entity_state_category error:"

        entity_state_category_key = args[0] if len(args) > 0 else None

        if entity_state_category_key in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр entity_state_category_key')
            return False

        # проверка наличия категории
        response = self.rest_api_client.get_entity_state_categories(f"Key={entity_state_category_key}")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        if len(response.json()) > 0:
            # категория существует
            if self.ignore_object_existence_error:
                self.__print_and_log(f'Применена опция ignore_object_existence_error. Категория {entity_state_category_key} уже существует')
                return True

            self.print_error(prefix_error, f"Категория {entity_state_category_key} уже существует")
            return False

        data = [
            {
                'key': entity_state_category_key,
                'flags': 'None'
            }
        ]
        response = self.rest_api_client.create_entity_state_categories(data)

        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        self.print_success(response.json()[0]['id'])

        return True

    def _delete_entity_state_category(self, *args):
        """Удаление категории для состояний сущности
        delete_entity_state_category <entity_state_category_id>"""
        prefix_error = "delete_entity_state_category error:"

        entity_state_category_id = args[0] if len(args) > 0 else None

        if entity_state_category_id in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр entity_state_category_id')
            return False

        response = self.rest_api_client.delete_entity_state_categories([entity_state_category_id])

        if response.status_code != 204:
            self.print_error(prefix_error, response.text)
            return False

        return True

    def _show_entity_state_categories(self, *args):
        """Показать все категории для состояний сущности
        show_entity_state_categories"""
        prefix_error = "show_entity_state_categories error:"

        response = self.rest_api_client.get_entity_state_categories()

        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        categories = response.json()
        if len(categories) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные категории:")
            self.__print_and_log(f"----------------------------------")
            for category in categories:
                self.__print_and_log(
                    f"{category['key']} ({category['id']})")
            self.__print_and_log('')
        else:
            self.__print_and_log(f"Категории отсутствуют")

        return True

    """ State Machines """

    def _create_state_machine(self, *args):
        """Создание новой машины состояний
        create_state_machine <state_machine_key>"""
        prefix_error = "create_state_machine error:"

        state_machine_key = args[0] if len(args) > 0 else None

        if state_machine_key in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр state_machine_key')
            return False

        # проверка наличия машины состояний
        response = self.rest_api_client.get_state_machines(f"Key={state_machine_key}")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        if len(response.json()) > 0:
            # машины состояний существует
            if self.ignore_object_existence_error:
                self.__print_and_log('Применена опция ignore_object_existence_error. Используется edit_state_machine')
                return self._edit_state_machine(state_machine_key)

            self.print_error(prefix_error, f"Машина состояний {state_machine_key} уже существует")
            return False


        self.opened_state_machine = {
            'key': state_machine_key,
            'flags': 'None',
            'states': [],
            'transitions': []
        }

        return True

    def _edit_state_machine(self, *args):
        """Редактирование машины состояний
        edit_state_machine <state_machine_key>"""
        prefix_error = "edit_state_machine error:"

        state_machine_key = args[0] if len(args) > 0 else None

        if state_machine_key in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр state_machine_key')
            return False

        response = self.rest_api_client.get_state_machines(f"Key={state_machine_key}&WithStates=true&WithTransitions=true")

        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False

        if len(response.json()) == 0:
            self.print_error(prefix_error,
                             f"Машина состояний {state_machine_key} не найдена")
            return False

        self.opened_state_machine = response.json()[0]

        return True

    def _add_sm_state(self, *args):
        """Добавление состояния в машине состояний
        add_sm_state <sm_state_key> <entity_state_category_key>"""
        prefix_error = "add_sm_state error:"

        sm_state_key = args[0] if len(args) > 0 else None
        entity_state_category_key = args[1] if len(args) > 1 else None

        if sm_state_key in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр sm_state_key')
            return False

        if entity_state_category_key in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр entity_state_category_key')
            return False

        if self.opened_state_machine == {}:
            self.print_error(prefix_error,
                             'Нет открытой машины состояний. Сперва воспользуйтесь методом create_state_machine или edit_state_machine')
            return False

        state = next(((lambda x: x)(state)
                                       for state in self.opened_state_machine['states']
                                       if state["key"].lower() == sm_state_key.lower()), None)

        if state:
            # состояние уже существует
            if self.ignore_object_existence_error:
                self.__print_and_log('Применена опция ignore_object_existence_error. Используется set_sm_state')
                return self._set_sm_state(sm_state_key, entity_state_category_key)

            self.print_error(prefix_error, f"Состояние {sm_state_key} уже существует")
            return False

        self.opened_state_machine['states'].append(
            {
                'key': sm_state_key,
                'stateCategoryKey': entity_state_category_key,
                'flags': 'None'
            }
        )
        return True

    def _set_sm_state(self, *args):
        """Установить состояние в машине состояний
        set_sm_state <sm_state_key> <entity_state_category_key>"""
        prefix_error = "set_sm_state error:"

        sm_state_key = args[0] if len(args) > 0 else None
        entity_state_category_key = args[1] if len(args) > 1 else None

        if sm_state_key in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр sm_state_key')
            return False

        if entity_state_category_key in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр entity_state_category_key')
            return False

        if self.opened_state_machine == {}:
            self.print_error(prefix_error,
                             'Нет открытой машины состояний. Сперва воспользуйтесь методом create_state_machine или edit_state_machine')
            return False

        new_states = []
        is_found = False
        for state in self.opened_state_machine['states']:
            if state['key'].lower() == sm_state_key.lower():
                is_found = True
                new_states.append(
                    {
                        'key': sm_state_key,
                        'stateCategoryKey': entity_state_category_key,
                        'flags': state['flags']
                    }
                )
            else:
                new_states.append(state)

        if is_found:
            self.opened_state_machine['states'] = new_states
        else:
            self.print_error(prefix_error,
                             f"Состояние машины {sm_state_key} отсутвует. Пользуйтесь add_sm_state для его добавления")
            return False

        return True

    def _delete_sm_state(self, *args):
        """Удалить состояние в машине состояний
        delete_sm_state <sm_state_key>"""
        prefix_error = "delete_sm_state error:"

        sm_state_key = args[0] if len(args) > 0 else None

        if sm_state_key in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр sm_state_key')
            return False

        if self.opened_state_machine == {}:
            self.print_error(prefix_error,
                             'Нет открытой машины состояний. Сперва воспользуйтесь методом create_state_machine или edit_state_machine')
            return False

        new_states = []
        for state in self.opened_state_machine['states']:
            if state['key'] != sm_state_key:
                new_states.append(state)

        self.opened_state_machine['states'] = new_states

        return True

    def _show_sm_states(self, *args):
        """Показать все состояния в машине состояний
        show_sm_states"""
        prefix_error = "show_sm_state error:"

        if self.opened_state_machine == {}:
            self.print_error(prefix_error,
                             'Нет открытой машины состояний. Сперва воспользуйтесь методом create_state_machine или edit_state_machine')
            return False

        if len(self.opened_state_machine['states']) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Состояния машины состояний:")
            self.__print_and_log(f"----------------------------------")
            for state in self.opened_state_machine['states']:
                self.__print_and_log(f"{state['key']}, stateCategoryKey: {state['stateCategoryKey']}")
        else:
            self.__print_and_log(f"Состояния машины состояний отсутствуют")
        self.__print_and_log('')

        return True

    def _add_sm_transition(self, *args):
        """Добавление нового перехода состояний
        add_sm_transition [<fromStateKey>], <toStateKey>[, TransitEntity][, level1][ <space1>][ <role1>][, TransitEntity][, level2][ <space2>][ <role2>]..."""
        prefix_error = "add_sm_transitions error:"

        from_state_key = args[0] if len(args) > 0 else None
        to_state_key = args[1] if len(args) > 1 else None

        if to_state_key in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр to_state_key')
            return False

        if len(args) > 2:
            permissions = []
            i = 2
            while len(args) > (i + 1):
                type = args[i]
                level = args[i + 1]
                space = args[i + 2] if len(args) > (i + 2) else None
                role = args[i + 3] if len(args) > (i + 3) else None

                if not type:
                    type = 'TransitEntity'
                if not level:
                    self.print_error(prefix_error, 'При задании доступа, параметр level обязателен')
                    return False

                permission = {
                    "type": type,
                    "level": level
                }
                if space:
                    permission['space'] = space
                if role:
                    permission['role'] = role

                permissions.append(permission)
                i += 4
        else:
            permissions = None

        if self.opened_state_machine == {}:
            self.print_error(prefix_error,
                             'Нет открытой машины состояний. Сперва воспользуйтесь методом create_state_machine или edit_state_machine')
            return False

        if from_state_key in (None, ''):
            transition = {
                'toStateKey': to_state_key,
                'flags': 'None'
            }
        else:
            transition = {
                'fromStateKey': from_state_key,
                'toStateKey': to_state_key,
                'flags': 'None'
            }
        if permissions is not None and len(permissions) > 0:
            transition['permissions'] = permissions

        self.opened_state_machine['transitions'].append(transition)

        return True

    def _delete_sm_transitions(self, *args):
        """Удалить все переходы состояний в машине состояний
        delete_sm_transitions"""
        prefix_error = "delete_sm_transitions error:"

        if self.opened_state_machine == {}:
            self.print_error(prefix_error,
                             'Нет открытой машины состояний. Сперва воспользуйтесь методом create_state_machine или edit_state_machine')
            return False

        self.opened_state_machine['transitions'] = []

        return True

    def _show_sm_transitions(self, *args):
        """Показать переходы состояний в машине состояний
        show_sm_transitions"""
        prefix_error = "show_sm_transitions error:"

        if self.opened_state_machine == {}:
            self.print_error(prefix_error,
                             'Нет открытой машины состояний. Сперва воспользуйтесь методом create_state_machine или edit_state_machine')
            return False

        if len(self.opened_state_machine['transitions']) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Переходы состояний машины состояний:")
            self.__print_and_log(f"----------------------------------")
            for transition in self.opened_state_machine['transitions']:
                self.__print_and_log(f"fromStateKey: {transition['fromStateKey'] if 'fromStateKey' in transition else 'None'}, "
                                     f"toStateKey: {transition['toStateKey']}")
                if 'permissions' in transition and len(transition['permissions']) > 0:
                    for permission in transition['permissions']:
                        self.__print_and_log(f"Доступ {permission['type']}:")
                        self.__print_and_log(f"        level: {permission['level']}")
                        if 'space' in permission:
                            self.__print_and_log(f"        space: {permission['space']}")
                        if 'role' in permission:
                            self.__print_and_log(f"        role: {permission['role']}")

        else:
            self.__print_and_log(f"Переходы состояний машины состояний отсутствуют")
        self.__print_and_log('')

        return True

    def _save_state_machine(self, *args):
        """Сохранение машины состояний
        save_state_machine"""
        prefix_error = "save_state_machine error:"

        if self.opened_state_machine == {}:
            self.print_error(prefix_error,
                             'Нет открытой машины состояний. Сперва воспользуйтесь методом create_state_machine или edit_state_machine')
            return False

        if 'id' in self.opened_state_machine:
            response = self.rest_api_client.put_state_machines([self.opened_state_machine])
        else:
            response = self.rest_api_client.create_state_machines([self.opened_state_machine])

        if response.status_code != 200:
            self.print_error(prefix_error, response.text)
            return False

        self.print_success(response.json()[0]['id'])

        self.opened_state_machine = {}
        return True

    def _discard_state_machine(self, *args):
        """Отмена изменений машины состояний
        discard_state_machine"""
        self.opened_state_machine = {}
        return True

    def _delete_state_machine(self, *args):
        """Удаление машины состояний
        delete_state_machine <state_machine_id>"""
        prefix_error = "delete_state_machine error:"

        state_machine_id = args[0] if len(args) > 0 else None

        if state_machine_id in (None, ''):
            self.print_error(prefix_error, 'Не задан параметр state_machine_id')
            return False

        response = self.rest_api_client.delete_state_machines([state_machine_id])

        if response.status_code != 204:
            self.print_error(prefix_error, response.text)
            return False

        return True

    def _show_state_machines(self, *args):
        """Показ всех машин состояний
        show_state_machines"""
        prefix_error = "show_state_machines error:"

        response = self.rest_api_client.get_state_machines("")
        if response.status_code != 200:
            self.print_error(prefix_error, f"Status Code: {response.status_code}\nResponse text: {response.text}")
            return False
        state_machines = response.json()
        if len(state_machines) > 0:
            self.__print_and_log('')
            self.__print_and_log(f"Доступные машины состояний:")
            self.__print_and_log(f"----------------------------------")
            for state_machine in state_machines:
                self.__print_and_log(f"{state_machine['key']} ({state_machine['id']})")
        else:
            self.__print_and_log(f"Машины состояний отсутствуют")
        self.__print_and_log('')
        return True

    """ Others """

    def _help(self, *args):
        """Выводит подсказку по конкретной команде или список доступных команд
        help [<command>]"""

        prefix_error = "Ошибка выполнения:"

        if len(args) > 0:
            # вывод документацинной строки конкретной команды
            if args[0].lower() in methods:
                # вывод документацинной строки для команды
                method_name = methods[args[0].lower()][0]

                if hasattr(self, method_name):
                    method = getattr(self, method_name, None)
                    docstring = method.__doc__
                    if docstring:
                        self.__print_and_log(docstring)
                    else:
                        self.__print_and_log("Документация по команде отсутствует")
                        return False

                else:
                    self.print_error(prefix_error, f"Метод с именем '{method_name}' не найден в классе.")
                    return False
            else:
                self.print_error(prefix_error, f"Неизвестная команда: {args[0]}")
                return False

        else:
            # вывод списка команд
            command_groups = {}

            for key, value in methods.items():
                if value[1]:
                    command_group = value[1]
                else:
                    command_group = 'Others'
                if command_group not in command_groups:
                    command_groups[command_group] = []
                command_groups[command_group].append(key)

            # Количество колонок, в которые вы хотите разбить данные
            num_columns = 4

            # подсчитываем максимальное количество ширины колонок
            max_column_width = max(max(map(len, data)) for command_group, data in command_groups.items())

            for command_group, data in command_groups.items():
                self.__print_and_log('')
                separator_length = 130
                separator = ""
                caption = '  ' + command_group + '  '
                i = 0
                half_separator = (separator_length - len(caption)) // 2
                while i < half_separator:
                    separator += '-'
                    i += 1
                separator += caption
                i += len(caption)
                while i < separator_length:
                    separator += '-'
                    i += 1

                self.__print_and_log(separator)
                self.__print_and_log('')
                # Рассчитываем количество элементов в каждой колонке
                column_size = len(data) // num_columns
                remainder = len(data) % num_columns

                # Создаем список колонок
                columns = []

                start = 0
                for i in range(num_columns):
                    if i < remainder:
                        end = start + column_size + 1
                    else:
                        end = start + column_size

                    columns.append(data[start:end])
                    start = end

                # Заполняем последние строки в колонках, если есть остаток
                if remainder > 0:
                    for i in range(len(columns) - remainder):
                        columns[len(columns) - i - 1].append("")

                # Выравниваем длину каждой колонки по максимальной длине элемента
                # max_column_width = max(max(map(len, column)) for column in columns)
                formatted_columns = []

                for column in columns:
                    formatted_column = [item.ljust(max_column_width) for item in column]
                    formatted_columns.append(formatted_column)

                # Транспонируем колонки для вывода в виде колонок
                formatted_data = zip(*formatted_columns)

                for row in formatted_data:
                    self.__print_and_log("  ".join(row))

        self.__print_and_log('')
        return True

    def _use_legacy_searcher(self, *args):
        """Сервисная опция использования старого API searcher
        use_legacy_searcher"""

        flag = args[0] if len(args) > 0 else None

        if flag.lower() == 'true':
            self.legacy_searcher = True
        else:
            self.legacy_searcher = False

        return True

    def init_output_script(self, *args):
        """Инициализация генерируемого файла скрипта
        set_output_file <file> [continue]  # в batch режиме эта команда игнорируется"""
        prefix_error = "init_output_script error:"

        output_script = args[0] if len(args) > 0 else ""
        if len(args) > 1 and args[1].lower() == 'continue':
            cont = True
        else:
            cont = False

        if self.__init_file_to_write(output_script, cont):
            self.output_script = output_script
            return True
        else:
            self.output_script = ""
            self.print_error(prefix_error, f"Проблема инициализации выходного файла-скрипта {output_script}")
            return False

    def _set_log(self, *args):
        """Инициализация параметров лога
        set_log [<log_path>] [continue] [debug]"""
        prefix_error = "_set_log error:"

        log_path = args[0] if len(args) > 0 else None
        flags = args[1:] if len(args) > 1 else []

        if flags and (not self.__validate_flags(flags, ['continue', 'debug'])):
            self.print_error(prefix_error,
                             f"Неверный флаг для set_log. Возможные значения: continue, debug")
            return False

        if 'continue' in flags:
            cont = True
        else:
            cont = False

        if 'debug' in flags:
            self.rest_api_client.debug_log = True
        else:
            self.rest_api_client.debug_log = False

        if not log_path:
            self.log_path = ""
            self.rest_api_client.log_path = ""
            self.print_success('Логгирование отключено')
            return True

        try:
            if cont:
                with open(log_path, 'a') as file:
                    file.write('')
            else:
                with open(log_path, 'w') as file:
                    file.write('')
            self.log_path = log_path
            self.rest_api_client.log_path = log_path
            return True
        except FileNotFoundError:
            self.log_path = ""
            self.rest_api_client.log_path = ""
            self.print_error(prefix_error, f"Проблема инициализации лога {log_path}")
            return False

    def _generate_readme(self, *args):
        """Генерация readme файла
        generate_readme [<readme_path>]"""

        readme_path = args[0] if len(args) > 0 else 'README.txt'

        if not self.__init_file_to_write(readme_path, cont=False):
            return False

        preamble = """----------------------------------------------------
доступ к LowCode задаётся в конфигурационном файле access_configs.json и по уполчанию используется default конфигурация. См. также команды работы с Access Configs ниже
пароль бизнес-пользователя по умолчанию - Qwerty123, используется, если в конфиге неопределён.
----------------------------------------------------
для корректной работы требуется установка пакетов (pip install <package> в Python терминале), если они не были установлены:

- colorama
- requests
- getpass-asterisk
----------------------------------------------------

1. интерактивный CLI + скриптовый терминал (команда scripts) для создания дата моделей:
    cli_lowcode.py

2. дубликат команды scripts в lowcode_cli.py. скриптовый терминал для выполнения скриптов в ручном режиме. Пишется скрипт-файл.
    cli_script_terminal.py

3. исполнение скрипта-файла
    cli_script.py

   формат: python.exe cli_script.py execute script_input.txt

4. дополнительные необходимые библиотеки:
    cli_core.py
    cli_rest_api_client.py

5. команды для ввода в терминале или использования в скрипт-файле:

синтаксис команд построен на таких принципах:
 - параметры разделяются либо пробелами, либо запятыми
 - если присутвует ,, то аргумент между запятыми считается None
 - если параметр содержит пробел - заключайте в двойные кавычки - и параметр воспримется целиком между кавычками.
 - можно использовать значение переменной как {{script_variable}} в любом месте.

6. доступные команды:"""

        self.write_to_file(readme_path, preamble)
        self.__print_and_log(preamble)

        current_group = ''
        for key, value in methods.items():
            if current_group.lower() != value[1].lower():
                # вывод имени категории
                current_group = value[1]
                if not current_group:
                    current_group_to_show = 'Others'
                else:
                    current_group_to_show = current_group
                self.write_to_file(readme_path, "")
                self.__print_and_log("")
                print_string = f"# ---------------------------  {current_group_to_show}  ---------------------------"
                self.write_to_file(readme_path, print_string)
                self.__print_and_log(print_string)

            method_name = value[0].lower()
            if hasattr(self, method_name):
                method = getattr(self, method_name, None)
                docstring = method.__doc__
                if docstring:
                    self.write_to_file(readme_path, "")
                    self.__print_and_log("")
                    print_string = '- ' + docstring
                    self.write_to_file(readme_path, print_string)
                    self.__print_and_log(print_string)
                else:
                    print_string = f"{key}: Документация по команде отсутствует"
                    self.write_to_file(readme_path, print_string)
                    self.__print_and_log(print_string)

            else:
                print_string = f"Метод с именем '{method_name}' не найден в классе."
                self.write_to_file(readme_path, print_string)
                self.__print_and_log(print_string)

        return True

    def _ignore_object_existence_error(self, *args):
        """Опция игнорирования ошибок существования объектов. Если объект существует, то будет применена соответствующая команда редактирования.
                ignore_object_existence_error [False]"""

        ignore_object_existence_error = args[0] if len(args) > 0 else 'True'

        if ignore_object_existence_error.lower() == 'false':
            self.ignore_object_existence_error = False
        else:
            self.ignore_object_existence_error = True

        return True
