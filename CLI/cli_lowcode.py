import cmd
import os
from cli_core import CLICore
from getpass_asterisk.getpass_asterisk import getpass_asterisk

label_key = "__label__"


class EntitiesCLI(cmd.Cmd):
    prompt = 'cli-lowcode> '

    def __init__(self):
        super().__init__()
        self.history_back = []  # back stack для объектов (Entity, EntityType)
        self.history_forward = []  # forward stack для объектов (Entity, EntityType)
        self.current_object = None
        self.cli_core = CLICore()
        self.cli_core.init_output_script('script_output.txt')

        # лог - скрипт
        self.script_file = 'script_output.txt'
        with open(self.script_file, 'w') as file:
            file.write('')

    def print_with_press_any_key(self, text):
        print(f"----------------------------------")
        print(text)
        print(f"----------------------------------")
        print()
        input("<Нажмите любую клавишу для продолжения> ")
        print()

    def show_entity_type_to_create(self, entity_type, references_to, references_from):
        print()
        print(f"-----------------Создаваемый/редактируемый тип Entity-----------------")
        print(f"Имя типа Entity: {entity_type['key']}")
        if 'parentKey' in entity_type:
            print(f"Родитель: {entity_type['parentKey']}")
        if 'stateMachineKey' in entity_type:
            print(f"Машина состояний: {entity_type['stateMachineKey']}")
        if 'flags' in entity_type:
            print(f"Флаги: {entity_type['flags']}")
        if 'attributes' in entity_type and len(entity_type['attributes']) > 0:
            print(f"Атрибуты:")
            for attribute in entity_type['attributes']:
                print(f"    {attribute['key']} {('(' + attribute['flags'] + ')') if 'flags' in attribute else ''}")
        if len(references_to) > 0:
            print(f"Ссылки на другие типы (referencedTo):")
            for reference in references_to:
                print(f"    {reference['toEntityTypeKey']}, {reference['type']} {('(' + reference['flags'] + ')') if reference['flags'] != 'None' else ''}")
        if len(references_from) > 0:
            print(f"Ссылки других типов на этот (referencedFrom):")
            for reference in references_from:
                print(f"    {reference['fromEntityTypeKey']}, {reference['type']} {('(' + reference['flags'] + ')') if reference['flags'] != 'None' else ''}")
        print(f"--------------------------------------------------------")

    def show_reference(self, reference):
        print()
        print(f"-----------------Редактируемая ссылка-----------------")
        if 'fromEntityTypeKey' in reference:
            print(f"fromEntityTypeKey: {reference['fromEntityTypeKey']}")
        if 'toEntityTypeKey' in reference:
            print(f"toEntityTypeKey: {reference['toEntityTypeKey']}")
        if 'fromReferenceKey' in reference:
            print(f"fromReferenceKey: {reference['fromReferenceKey']}")
        if 'toReferenceKey' in reference:
            print(f"toReferenceKey: {reference['toReferenceKey']}")
        if 'flags' in reference:
            print(f"flags: {reference['flags']}")
        if 'type' in reference:
            print(f"type: {reference['type']}")
        print(f"------------------------------------------------------")

    def get_entity_type_id(self, entity_type):
        response = self.cli_core.rest_api_client.get_entity_types(f"Key={entity_type}")

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        if len(response.json()) == 0:
            print(f"Entity тип {entity_type} отсутствует")
            return

        return response.json()[0]['id']

    def add_references_to(self):
        print()
        print(f"Доступные типы Entities:")
        print(f"----------------------------------")
        self.cli_core.do_command(f"show_entity_types")

        to_entity_type_key = input(f"Укажите тип Entity для ссылки: ").strip()

        if self.get_entity_type_id(to_entity_type_key) is None:  # такого типа нет
            print()
            print(f"Такого типа не существует")
            print()
            return

        reference_type = input(f"Укажите тип ссылки (OneToOne | OneToMany | ManyToOne | ManyToMany): ").strip()
        self.cli_core.do_command(f"add_reference_to {to_entity_type_key} {reference_type}")
        return

    def remove_references_to(self, references_to):
        if len(references_to) > 0:
            print()
            print(f"Ссылки на другие типы (referencedTo):")
            print(f"----------------------------------")
            for reference in references_to:
                print(f"{reference['toEntityTypeKey']}, {reference['type']}")
            print()
        else:
            print()
            print(f"Ссылки на другие типы отсутсвуют")
            print()
            return

        to_reference_key = input(f"Укажите убираемую ссылку: ").strip()

        # проверка имеется ли указанная ссылка
        reference_exist = False
        for reference in references_to:
            if reference['toEntityTypeKey'] == to_reference_key:
                reference_exist = True
                break
        if not reference_exist:
            print()
            print(f"Такой ссылки нет")
            print()
            return

        self.cli_core.do_command(f"remove_reference_to {to_reference_key}")
        return

    def add_references_from(self):
        print()
        print(f"Доступные типы Entities:")
        print(f"----------------------------------")
        self.cli_core.do_command(f"show_entity_types")
        print()
        from_entity_type_key = input(f"Укажите тип Entity, которая должна ссылаться на эту Entity: ").strip()

        if self.get_entity_type_id(from_entity_type_key) is None:  # такого типа нет
            print()
            print(f"Такого типа не существует")
            print()
            return

        reference_type = input(f"Укажите тип ссылки (OneToOne | OneToMany | ManyToOne | ManyToMany): ").strip()
        self.cli_core.do_command(f"add_reference_from {from_entity_type_key} {reference_type}")
        return

    def remove_references_from(self, references_from):
        if len(references_from) > 0:
            print()
            print(f"Ссылки других типов на этот (referencedFrom):")
            print(f"----------------------------------")
            for reference in references_from:
                print(f"{reference['fromEntityTypeKey']}, {reference['type']}")
            print()
        else:
            print()
            print(f"Ссылки других типов на этот отсутсвуют")
            print()
            return

        from_reference_key = input(f"Укажите убираемую ссылку: ").strip()

        # проверка имеется ли указанная ссылка
        reference_exist = False
        for reference in references_from:
            if reference['fromEntityTypeKey'] == from_reference_key:
                reference_exist = True
                break
        if not reference_exist:
            print()
            print(f"Такой ссылки нет")
            print()
            return

        self.cli_core.do_command(f"remove_reference_from {from_reference_key}")
        return

    def set_entity_type_parent(self):
        if 'parentKey' in self.cli_core.opened_entity_type:
            print(f"Текущий родитель: {self.cli_core.opened_entity_type['parentKey']}")

        self.cli_core.do_command(f"show_entity_types")
        entity_type_key = input(f"Укажите тип Entity родителя (или пустая строка для удаления родителя): ").strip()

        if entity_type_key in ('', None):
            # убрать родителя
            self.cli_core.do_command(f"set_entity_type_parent")
        else:
            # проставить родителя
            if self.get_entity_type_id(entity_type_key) is None:
                # такого типа нет
                print()
                print(f"Такого типа не существует")
                print()
                return
            self.cli_core.do_command(f"set_entity_type_parent {entity_type_key}")
        return

    def set_entity_type_state_machine(self):
        if 'stateMachineKey' in self.cli_core.opened_entity_type:
            self.print_with_press_any_key(f"Машина состояний у этого типа Entity уже имеется. Машину состояний нельзя менять.")
            return

        self.cli_core.do_command(f"show_state_machines")
        state_machine_key = input(f"Укажите машину состояний: ").strip()

        if state_machine_key in ('', None):
            self.print_with_press_any_key(f"Машина состояний не указана")
        else:
            # проставить state_machine
            self.cli_core.do_command(f"set_entity_type_state_machine {state_machine_key}")
        return

    def set_entity_type_flags(self):
        if 'flags' in self.cli_core.opened_entity_type:
            print(f"Текущие флаги: {self.cli_core.opened_entity_type['flags']}")
            print()
        entity_type_flags = input(f"Укажите флаги для этого типа Entity (IsAbstract, IsSearchable, IsUnique, IsDraftAllowed или пустая строка для удаления флагов): ").strip()

        if entity_type_flags in ('', None):
            # убрать флаги
            self.cli_core.do_command(f"set_entity_type_flags")
        else:
            # проставить флаги
            self.cli_core.do_command(f"set_entity_type_flags {entity_type_flags}")
        return

    def show_attribute_details(self, attribute):
        print()
        print(f"Атрибут {attribute['key']}")
        print(f"----------------------------------")
        print(f"Id: {attribute['id']}")
        print(f"Type: {attribute['type']}")
        print(f"Flags: {attribute['flags']}")
        if 'properties' in attribute:
            for prop in attribute['properties']:
                if prop['key'].lower() == label_key:
                    print(f"Label: {prop['value']}")
        print(f"----------------------------------")

    def add_attribute(self, attributes):
        if not self.cli_core.do_command(f"show_attributes"):
            return

        attribute_key = input("Введите имя атрибута: ").strip()

        # проверка не был ли атрибут уже добавлен
        if len(attributes) > 0:
            for attribute in attributes:
                if attribute['key'] == attribute_key:
                    print(f"Атрибут {attribute_key} уже добавлен")
                    return

        # проверка существует ли атрибут
        response = self.cli_core.rest_api_client.get_attributes(f"Key={attribute_key}")

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        if len(response.json()) > 0:
            # атрибут существует
            print(f"Атрибут {attribute_key} существует, будет добавлен")
            attribute_type = response.json()[0]['type']

        else:
            # атрибут не существует, надо создать
            attribute_type = input(f"Атрибут {attribute_key} не существует, введите его тип для создания\n"
                                   f"(GUID | Boolean | Number | Object | String | Text | DateTime | Address | TimeSpan | Attachment): ").strip()

            if not self.cli_core.do_command(f"create_attribute {attribute_key}"):
                return
            if not self.cli_core.do_command(f"set_attribute_type {attribute_type}"):
                return
            if not self.cli_core.do_command(f"save_attribute"):
                return

        if attribute_type in ("String", "Text"):
            attribute_flags = "IsFullTextSearch"
            print(f"Будет установлен для этого атрибута флаг: {attribute_flags}")
        else:
            attribute_flags = ""
            print(f"Для этого атрибута не будут установлены флаги")

        yes = input(f"Хотите редактировать флаги? ([Y]es): ").strip()
        if yes.lower() in ('y', 'yes'):
            attribute_flags = input(
                f"Укажите флаги для этого атрибута (IsFullTextSearch, IsMandatory, IsUnique, IsDraftMandatory, IsReadonly, IsImmutable, IsEncrypted или пустая строка для удаления флагов): ").strip()

        self.cli_core.do_command(f"add_attribute {attribute_key} {attribute_flags}")
        return

    def remove_attribute(self, attributes):
        if len(attributes) > 0:
            print()
            print(f"Доступные атрибуты:")
            print(f"----------------------------------")
            for attribute in attributes:
                print(f"{attribute['key']} {'(' + attribute['id'] + ')' if 'id' in attribute else ''}")
            print()
        else:
            print()
            print(f"Атрибуты отсутсвуют")
            print()
            return

        attribute_key = input("Введите имя убираемого атрибута: ").strip()

        # проверка имеется ли указанный атрибут
        attribute_exist = False
        for attribute in attributes:
            if attribute['key'] == attribute_key:
                attribute_exist = True
                break
        if not attribute_exist:
            print()
            print(f"Такого атрибута нет")
            print()
            return

        self.cli_core.do_command(f"remove_attribute {attribute_key}")
        return

    def set_attribute_fixed_values(self):
        if ("IsFixed" in self.cli_core.opened_attribute["flags"]) and ("values" in self.cli_core.opened_attribute):
            print()
            print(
                f"Текущие возможные значения для IsFixed атрибута:")
            print(f"----------------------------------")
            if len(self.cli_core.opened_attribute["values"]) > 0:
                for value in self.cli_core.opened_attribute["values"]:
                    print(f"{value['locales'][0]['value']}")
            else:
                print("Значения отсутвуют")

        if self.cli_core.do_command(f"set_attribute_flags IsFixed"):
            print()
            print(f"Введите возможные фиксированные значения атрибута (как минимум одно) в формате:")
            print(f"    \"value 1\", value2, \"value 3\", ...")
            attribute_fixed_values = input(f"Если значение содержит пробелы, то заключайте значение в двойные кавычки: ")

            self.cli_core.do_command(f"set_attribute_fixed_values {attribute_fixed_values}")

    def show_current_object(self, show_with_schema=False):
        if self.current_object is None:
            print(f"Не выбрано никакого объекта, используйте select_entity или select_entity_type")
        else:
            attributes = {}
            references_existence = {}
            references = []

            if self.current_object['id'] is not None:
                # выбранный объект - Entity
                # запрос схемы и первоначальное заполнение attributes и references
                if show_with_schema:
                    data = {
                        "locale": "none",
                        "entityTypesByKeys": [self.current_object["type"]],
                        "entityTypesOptions": {
                            "includeReferencedToByKeys": ["*"],
                            "includeAttributesByKeys": ["*"],
                        },
                        "attributesOptions": {
                            "includeValues": True
                        }
                    }

                    response = self.cli_core.rest_api_client.get_entity_type_schema(data)

                    if response.status_code != 200:
                        print(f"Response text: {response.text}")
                        return

                    entity_schema = response.json()
                    entity_type_schema = entity_schema["entityTypes"][0]

                    if "attributes" in entity_type_schema:
                        for attribute in entity_type_schema["attributes"]:
                            if attribute['key'] != "__NAME":
                                attributes[attribute['key']] = None

                    if "referencedTo" in entity_type_schema:
                        for reference in entity_type_schema["referencedTo"]:
                            references_existence[reference['key']] = False
                else:
                    entity_type_schema = None

                # заполнение attributes и references реальными данными entity
                parameters = f"Id={self.current_object['id']}&WithAttributeValues=true&WithReferencedTo=true"
                response = self.cli_core.rest_api_client.get_entities(parameters)

                if response.status_code == 200:
                    entity = response.json()[0]
                    if 'attributeValues' in entity:
                        attribute_name = next(((lambda x: x)(attributeValue)
                                               for attributeValue in entity["attributeValues"]
                                               if attributeValue["attributeKey"] == "__NAME"), None)
                    else:
                        attribute_name = None

                    if attribute_name is None:
                        entity_name = None
                    else:
                        entity_name = attribute_name['valueLocales'][0]['value']

                    if 'stateKey' in entity:
                        state_key = entity['stateKey']
                    else:
                        state_key = None

                    if 'isDraft' in entity:
                        is_draft = entity['isDraft']
                    else:
                        is_draft = None

                else:
                    print(f"Response text: {response.text}")
                    return

                # заполнение значений атрибутов
                if 'attributeValues' in entity:
                    for attributeValue in entity['attributeValues']:
                        if attributeValue["attributeKey"] != "__NAME":
                            attributes[attributeValue['attributeKey']] = attributeValue['valueLocales'][0]['value']

                # заполнение ссылок referencedTo
                if 'referencedTo' in entity:
                    for reference in entity['referencedTo']:
                        if show_with_schema:
                            reference_flags = next(((lambda x: x)(ref['flags'])
                                                    for ref in entity_type_schema["referencedTo"]
                                                    if ref["key"] == reference['key']), None)
                        else:
                            reference_flags = 'None'

                        references.append(f"{reference['key']}{' (' + reference_flags + ')' if reference_flags != 'None' else ''}: {reference['entityId']} ({reference['entityTypeKey']})")
                        references_existence[reference['key']] = True

                print(f"-------------------------------------------")
                print(f"Selected object - Entity:")
                print(f"    EntityId: {self.current_object['id']}")
                if entity_name is not None:
                    print(f"    __NAME: {entity_name}")
                print(f"    Type: {self.current_object['type']}")
                if state_key is not None:
                    print(f"    StateMachine: {state_key}")
                if is_draft is not None:
                    print(f"    isDraft: {is_draft}")

                # Вывод значений атрибутов
                if attributes:
                    print(f"Атрибуты:")
                    for key, value in attributes.items():
                        if show_with_schema:
                            attribute_flags = next(((lambda x: x)(attribute['flags'])
                                                    for attribute in entity_type_schema["attributes"]
                                                    if attribute["key"] == key), None)
                        else:
                            attribute_flags = 'None'
                        print(f"    {key}{' (' + attribute_flags + ')' if attribute_flags != 'None' else ''}: {value}")

                # Вывод ссылок referencedTo
                if references_existence:
                    print(f"Ссылки referencedTo:")
                    for reference in references:
                        print(f"    {reference}")
                    for key, value in references_existence.items():
                        if not value:
                            if show_with_schema:
                                reference_flags = next(((lambda x: x)(ref['flags'])
                                                        for ref in entity_type_schema["referencedTo"]
                                                        if ref["key"] == key), None)
                            else:
                                reference_flags = 'None'
                            print(f"    {key}{' (' + reference_flags + ')' if reference_flags != 'None' else ''}: None")

                print(f"-------------------------------------------")

            else:
                # выбранный объект - EntityType
                print(f"-------------------------------------------")
                print(f"Selected object - EntityType: {self.current_object['type']}")
                print(f"-------------------------------------------")

    """do_ methods"""
    """ Users/BusinessUsers """

    def do_login(self, parameter=None):
        """Логин пользователя"""
        args = self.cli_core.parse_args(parameter)

        login = args[0] if len(args) > 0 else None
        password = args[1] if len(args) > 1 else None

        if not login:
            login = input("Введите Ваш логин: ").strip()

        if password is None:
            if self.cli_core.is_pycharm_terminal():
                password = input("Введите пароль: ")
            else:
                password = getpass_asterisk("Введите пароль: ")

        if not self.cli_core.do_command(f"login {login} \"{password}\""):
            return

        yes = input(f"Хотите работать под бизнес-пользователем? ([Y]es): ").strip()
        if yes.lower() not in ('y', 'yes'):
            return

        if not self.cli_core.do_command(f"show_trustors"):
            return

        business_id = input(f"Введите business_id: ").strip()
        self.cli_core.do_command(f"use_business {business_id}")
        return

    def do_set_password(self, parameter=None):
        """изменение пароля пользователя"""
        args = self.cli_core.parse_args(parameter)

        old_password = args[0] if len(args) > 0 else None
        new_password = args[1] if len(args) > 1 else None

        if old_password is None:
            if self.cli_core.is_pycharm_terminal():
                old_password = input("Введите старый пароль: ")
            else:
                old_password = getpass_asterisk("Введите старый пароль: ")

        if new_password is None:
            if self.cli_core.is_pycharm_terminal():
                new_password = input("Введите новый пароль: ")
            else:
                new_password = getpass_asterisk("Введите новый пароль: ")

        self.cli_core.do_command(f"set_password \"{old_password}\" \"{new_password}\"")
        return

    """Attributes"""

    def do_show_attributes(self, fake_arg):
        """Показать имеющиеся атрибуты."""
        self.cli_core.do_command(f"show_attributes")

    def do_edit_attribute(self, attribute_key=None):
        """Редактирование атрибута."""

        if attribute_key in (None, ''):
            self.cli_core.do_command(f"show_attributes")
            attribute_key = input("Укажите имя атрибута для редактирования: ").strip()

        if not self.cli_core.do_command(f"edit_attribute {attribute_key}"):
            return

        while True:
            self.show_attribute_details(self.cli_core.opened_attribute)
            # Показать меню выбора
            print()
            print("Выберите действие:")
            print("1. Переименовать")
            print("2. Установить отображаемое имя (Label)")
            print("3. Установить тип данных")
            print("4. Редактировать флаги")
            print("5. Установить фиксированные значения")
            print()
            print("s. Сохранить атрибут и выйти из редактирования")
            print("d. Выход из редактирования без сохранения")
            print()

            choice = input("Введите номер выбранного действия: ").strip()

            if choice == '1':
                # Переименовать
                attribute_key = input("Задайте новое имя (key) атрибута: ").strip()

                if self.cli_core.get_attribute_id(attribute_key, False) is not None:
                    print()
                    print(f"\033[31mАтрибут {attribute_key} уже существует\033[0m")
                else:
                    self.cli_core.do_command(f"set_attribute_key {attribute_key}")

            elif choice == '2':
                # Установить отображаемое имя
                attribute_label = input("Задайте отображаемое имя (Label): ")
                self.cli_core.do_command(f"set_attribute_label \"{attribute_label}\"")

            elif choice == '3':
                # Установить тип данных
                attribute_type = input(f"Введите новый тип данных\n"
                                       f"(GUID | Boolean | Number | Object | String | Text | DateTime | Address | TimeSpan | Attachment): ").strip()
                self.cli_core.do_command(f"set_attribute_type {attribute_type}")

            elif choice == '4':
                # Установить флаги
                if 'flags' in self.cli_core.opened_attribute:
                    print(f"Текущие флаги: {self.cli_core.opened_attribute['flags']}")
                    print()
                attribute_flags = input(
                    f"Укажите флаги для этого атрибута (IsFixed или пустая строка для удаления флагов): ").strip()

                if attribute_flags in ('', None):
                    # убрать флаги
                    self.cli_core.do_command(f"set_attribute_flags")
                else:
                    # проставить флаги
                    self.cli_core.do_command(f"set_attribute_flags {attribute_flags}")

            elif choice == '5':
                # Установить фиксированные значения
                self.set_attribute_fixed_values()

            elif choice == 's':
                # Сохранить и выйти
                if self.cli_core.do_command(f"save_attribute"):
                    print()
                    print(f"Атрибут сохранён")
                    print()
                break

            elif choice == 'd':
                # Выход без сохранения
                self.cli_core.do_command(f"discard_attribute")
                break

            else:
                print("Неверный ввод, пожалуйста, введите число от 1 до 5, 's' или 'd'.")

    def do_delete_attribute(self, attribute_key=None):
        """Удалить атрибут."""

        if attribute_key in (None, ''):
            self.cli_core.do_command(f"show_attributes")
            attribute_key = input("Укажите имя атрибута для удаления: ").strip()

        attribute_id = self.cli_core.get_attribute_id(attribute_key)

        if attribute_id is not None:
            self.cli_core.do_command(f"delete_attribute {attribute_key}")
            print(f"Атрибут {attribute_key} удалён")
            print()
        else:
            print(f"Удаление отменено")
            print()

    """Entity Types"""

    def do_create_entity_type(self, entity_type_key=None):
        """Создать новый тип Entity."""
        if entity_type_key in (None, ''):
            entity_type_key = input(
                f"Задайте имя нового типа Entity: ").strip()

        if not self.cli_core.do_command(f"create_entity_type {entity_type_key}"):
            return

        if not self.cli_core.do_command(f"set_entity_type_flags isSearchable"):
            return

        while True:
            references_to = []
            references_from = []
            for reference in self.cli_core.opened_entity_type_references:
                if ('to_delete' not in reference) or (not reference['to_delete']):
                    if reference['fromEntityTypeKey'] == self.cli_core.opened_entity_type['key']:
                        references_to.append(reference)
                    if reference['toEntityTypeKey'] == self.cli_core.opened_entity_type['key']:
                        references_from.append(reference)
            self.show_entity_type_to_create(self.cli_core.opened_entity_type, references_to, references_from)

            # Показать меню выбора
            print()
            print("Выберите действие:")
            print("1. Добавить атрибуты")
            print("2. Убрать атрибуты")
            print()
            print("3. Добавить ссылки на другие типы Entity (referencedTo)")
            print("4. Убрать ссылки на другие типы Entity (referencedTo)")
            print("5. Добавить ссылки на этот тип Entity (referencedFrom)")
            print("6. Убрать ссылки на этот тип Entity (referencedFrom)")
            print()
            print("7. Редактировать родителя")
            print("8. Установить машину состояний")
            print("9. Редактировать флаги")
            print()
            print("s. Сохранить тип и выйти из создания типа Entity")
            print("d. Выход из создания типа Entity без сохранения")
            print()

            choice = input("Введите номер выбранного действия: ").strip()

            if choice == '1':
                # Добавление атрибутов
                attributes = []
                if 'attributes' in self.cli_core.opened_entity_type:
                    attributes = self.cli_core.opened_entity_type['attributes']
                self.add_attribute(attributes)

            elif choice == '2':
                # Удаление атрибутов
                attributes = []
                if 'attributes' in self.cli_core.opened_entity_type:
                    attributes = self.cli_core.opened_entity_type['attributes']
                self.remove_attribute(attributes)

            elif choice == '3':
                # Добавление referencedTo ссылок
                self.add_references_to()

            elif choice == '4':
                # Убрать referencedTo ссылку
                self.remove_references_to(references_to)

            elif choice == '5':
                # Добавление referencedFrom ссылок
                self.add_references_from()

            elif choice == '6':
                # Убрать referencedFrom ссылку
                self.remove_references_from(references_from)

            elif choice == '7':
                # Редактировать родителя
                self.set_entity_type_parent()

            elif choice == '8':
                # Установить машину состояний
                self.set_entity_type_state_machine()

            elif choice == '9':
                # Редактировать флаги
                self.set_entity_type_flags()

            elif choice == 's':
                # Сохранить и выйти
                self.cli_core.do_command(f"save_entity_type")
                break

            elif choice == 'd':
                # Выход без сохранения
                self.cli_core.do_command(f"discard_entity_type")
                break

            else:
                print("Неверный ввод, пожалуйста, введите число от 1 до 9, 's' или 'd'.")

    def do_select_entity_type(self, entity_type_key=None):
        """Выбрать Entity Type."""
        if entity_type_key in ("", None):
            self.cli_core.do_command(f"show_entity_types")
            entity_type_key = input(f"Не указан никакой тип Entity (команда select_entity_type <entity_type_key>), задайте тип Entity: ").strip()

        if self.current_object is not None:
            self.history_back.append(self.current_object.copy())
        self.history_forward.clear()
        self.current_object = {"id": None, "type": entity_type_key}
        self.show_current_object()

    def do_edit_entity_type(self, entity_type_key=None):
        """Редактировать тип Entity."""
        if entity_type_key not in ("", None):
            self.do_select_entity_type(entity_type_key)
        else:
            if (self.current_object is None) or (self.current_object['type'] in ("", None)):
                self.cli_core.do_command(f"show_entity_types")
                entity_type_key = input(f"Не указан никакой тип Entity (команда select_entity <entity_id>, select_entity_type <entity_type_key> или edit_entity_type <entity_type_key>), "
                                        f"задайте тип Entity: ").strip()
                self.do_select_entity_type(entity_type_key)
            else:
                if self.current_object['id'] in ("", None):
                    # выбранный объект - EntityType
                    self.show_current_object(True)
                else:
                    # выбранный объект - Entity, надо выбрать его тип
                    self.do_select_entity_type(self.current_object['type'])
                entity_type_key = self.current_object['type']

        if not self.cli_core.do_command(f"edit_entity_type {entity_type_key}"):
            return

        while True:
            references_to = []
            references_from = []
            for reference in self.cli_core.opened_entity_type_references:
                if ('to_delete' not in reference) or (not reference['to_delete']):
                    if reference['fromEntityTypeKey'] == self.cli_core.opened_entity_type['key']:
                        references_to.append(reference)
                    if reference['toEntityTypeKey'] == self.cli_core.opened_entity_type['key']:
                        references_from.append(reference)
            self.show_entity_type_to_create(self.cli_core.opened_entity_type, references_to, references_from)

            # Показать меню выбора
            print()
            print("Выберите действие:")
            print("1. Добавить атрибуты")
            print("2. Убрать атрибуты")
            print()
            print("3. Добавить ссылки на другие типы Entity (referencedTo)")
            print("4. Убрать ссылки на другие типы Entity (referencedTo)")
            print("5. Добавить ссылки на этот тип Entity (referencedFrom)")
            print("6. Убрать ссылки на этот тип Entity (referencedFrom)")
            print()
            print("7. Редактировать родителя")
            print("8. Редактировать флаги")
            print()
            print("s. Сохранить тип и выйти из редактирования типа Entity")
            print("d. Выход из редактирования типа Entity без сохранения")
            print()

            choice = input("Введите номер выбранного действия: ").strip()

            if choice == '1':
                # Добавление атрибутов
                attributes = []
                if 'attributes' in self.cli_core.opened_entity_type:
                    attributes = self.cli_core.opened_entity_type['attributes']
                self.add_attribute(attributes)

            elif choice == '2':
                # Удаление атрибутов
                attributes = []
                if 'attributes' in self.cli_core.opened_entity_type:
                    attributes = self.cli_core.opened_entity_type['attributes']
                self.remove_attribute(attributes)

            elif choice == '3':
                # Добавление referencedTo ссылок
                self.add_references_to()

            elif choice == '4':
                # Убрать referencedTo ссылку
                self.remove_references_to(references_to)

            elif choice == '5':
                # Добавление referencedFrom ссылок
                self.add_references_from()

            elif choice == '6':
                # Убрать referencedFrom ссылку
                self.remove_references_from(references_from)

            elif choice == '7':
                # Редактировать родителя
                self.set_entity_type_parent()

            elif choice == '8':
                # Редактировать флаги
                self.set_entity_type_flags()

            elif choice == 's':
                # Сохранить и выйти
                self.cli_core.do_command(f"save_entity_type")
                break

            elif choice == 'd':
                # Выход без сохранения
                self.cli_core.do_command(f"discard_entity_type")
                break

            else:
                print("Неверный ввод, пожалуйста, введите число от 1 до 8, 's' или 'd'.")

    def do_delete_entity_type(self, entity_type=None):
        """Удалить заданный тип Entity."""
        if entity_type in (None, ''):
            if self.current_object is not None:
                entity_type = self.current_object['type']
            else:
                print(
                    f"Никакой тип Entity не выбран. Используйте select_entity_type или укажите тип в параметре delete_entity_type <entity_type>")
                return

        yes = input(f"Подтвердите удаление Entity типа {entity_type} ([Y]es): ").strip()
        if yes.lower() in ('y', 'yes'):
            self.cli_core.do_command(f"delete_entity_type {entity_type}")
        else:
            print(f"Удаление отменено")

    def do_show_entity_types(self, fake_arg):
        """Показать типы Entity."""
        self.cli_core.do_command(f"show_entity_types")

    """Entities"""

    def do_show_entities(self, entity_type=None):
        """Показать Entities заданного типа."""
        if entity_type in (None, ''):
            if (self.current_object is not None) and self.current_object['type']:
                entity_type = self.current_object['type']
                self.cli_core.do_command(f"show_entities {entity_type}")
            else:
                self.cli_core.do_command(f"show_entities")
        else:
            self.cli_core.do_command(f"show_entities {entity_type}")

    def do_select_entity(self, entity_id=None, show_with_schema=False):
        """Выбрать Entity."""
        if entity_id in ("", None):
            self.do_show_entities()
            entity_id = input(f"Не указан никакой Entity (команда select_entity <entity_id>), задайте Entity: ").strip()

        parameters = f"Id={entity_id}"
        response = self.cli_core.rest_api_client.get_entities(parameters)

        if response.status_code == 200:
            if self.current_object is not None:
                self.history_back.append(self.current_object.copy())
            self.history_forward.clear()
            self.current_object = {"id": entity_id, "type": response.json()[0]['entityTypeKey']}

            self.show_current_object(show_with_schema)

        else:
            print(f"Response text: {response.text}")

    def do_show_referenced_entities(self, entity_id=None):
        """Показать связанные Entities."""
        if entity_id in (None, ''):
            if self.current_object is None or self.current_object["id"] is None:
                print(f"Не выбрана никакая Entity, используйте select_entity <entity_id> или укажите entity в параметре show_referenced_entities <entity_id>")
                return
            else:
                entity_id = self.current_object["id"]

        parameters = f"Id={entity_id}&WithReferencedTo=true"
        response = self.cli_core.rest_api_client.get_entities(parameters)

        if response.status_code == 200:
            print(f"Response: {response.json()}")

            if 'referencedTo' in response.json()[0]:
                referenced_to_entities = response.json()[0]['referencedTo']
                for referenced_to_entity in referenced_to_entities:
                    print(f"{referenced_to_entity['entityTypeKey']}: {referenced_to_entity['entityId']}")
            else:
                print(f"Связанные entities (referencedTo) отсутствуют.")

        else:
            print(f"Response text: {response.text}")
            return

    def do_edit_entity(self, entity_id=None):
        """Редактирование Entity."""
        if entity_id not in ("", None):
            self.do_select_entity(entity_id, True)
        else:
            if (self.current_object is None) or (self.current_object['id'] in ("", None)):
                self.do_show_entities()
                entity_id = input(f"Не выбран никакой Entity (команда select_entity <entity_id> или edit_entity <entity_id>), задайте Entity: ").strip()
                self.do_select_entity(entity_id, True)
            else:
                self.show_current_object(True)

        # открытие Entity
        if not self.cli_core.do_command(f"edit_entity {self.current_object['id']}"):
            self.cli_core.do_command(f"discard_entity")
            return

        # получение схемы
        data = {
            "locale": "none",
            "entityTypesByKeys": [self.current_object["type"]],
            "entityTypesOptions": {
                "includeReferencedToByKeys": ["*"],
                "includeAttributesByKeys": ["*"],
            },
            "attributesOptions": {
                "includeValues": True
            }
        }
        response = self.cli_core.rest_api_client.get_entity_type_schema(data)

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        entity_schema = response.json()
        entity_type = entity_schema["entityTypes"][0]

        while True:
            # Показать меню выбора
            print()
            print("Выберите действие:")
            print("1. Редактировать атрибуты")
            print("2. Добавление referencedTo ссылки")
            print("3. Удаление referencedTo ссылки")
            print()
            print("s. Сохранить entity и выйти из редактирования")
            print("d. Выход из редактирования без сохранения Entity")
            print()

            choice = input("Введите номер выбранного действия: ").strip()

            if choice == '1':
                # Редактировать атрибуты
                if "attributes" not in entity_type:
                    print("Нет доступных атрибутов для редактирования.")
                else:
                    attribute_key = input("Введите имя атрибута: ").strip()

                    attribute3 = next(((lambda x: x)(attribute2) for attribute2 in entity_schema["attributes"] if
                                       attribute2["key"].lower() == attribute_key.lower()), None)
                    attribute_type = attribute3["type"]

                    if "IsFixed" in attribute3["flags"]:
                        print(
                            f"Возможные значения для IsFixed атрибута {attribute_key} ({attribute_type}):")
                        for value in attribute3["values"]:
                            print(f"{value['locales'][0]['value']}")

                    attribute_value = input(f"Введите новое значение для атрибута {attribute_key} ({attribute_type}): ")
                    if not self.cli_core.do_command(f"set_entity_attribute_value {attribute_key} \"{attribute_value}\""):
                        self.cli_core.do_command(f"discard_entity")
                        return

            elif choice == '2':
                # Добавление ссылки
                if 'referencedTo' not in entity_type:
                    print("Нет доступных ссылок для добавления.")
                else:
                    reference_key = input("Введите имя ссылки: ").strip()

                    reference3 = next(((lambda x: x)(reference2)
                                       for reference2 in entity_type["referencedTo"]
                                       if reference2["entityTypeKey"].lower() == reference_key.lower()), None)

                    print(f"Возможные значения для ссылки {reference_key}:")
                    for acceptableEntityType in reference3["acceptableEntityType"]:
                        data = {
                            "entitiesOptions": {
                                "includeAttributeValuesByAttributeKeys": ["*"],
                                "includeEntityWorkflowStatesByWorkflowKeys": ["*"],
                                "includeReferences": False
                            },
                            "entitiesByEntityTypeKeys": [acceptableEntityType["key"]],
                            "locale": "none"
                        }
                        response = self.cli_core.rest_api_client.get_entities_vector(data)
                        if response.status_code != 200:
                            print(f"Response text: {response.text}")
                            return

                        entities = response.json()
                        for entity in entities:
                            if 'attributeValues' in entity:
                                attribute_name = next(((lambda x: x)(attributeValue)
                                                       for attributeValue in entity["attributeValues"]
                                                       if attributeValue["attributeKey"] == "__NAME"), None)
                            else:
                                attribute_name = None
                            print(
                                f"{acceptableEntityType['key']}, id: {entity['id']}{', __NAME: ' + attribute_name['valueLocales'][0]['value'] if attribute_name else ''}")

                    reference_value = input(f"Введите ссылку {reference_key}: ").strip()
                    if not self.cli_core.do_command(f"add_entity_reference_to {reference_key} {reference_value}"):
                        self.cli_core.do_command(f"discard_entity")
                        return

            elif choice == '3':
                # Удаление ссылки
                reference_key = input("Введите имя ссылки: ").strip()
                reference_value = input(f"Введите ссылку {reference_key} для удаления: ").strip()

                if not self.cli_core.do_command(f"remove_entity_reference_to {reference_key} {reference_value}"):
                    self.cli_core.do_command(f"discard_entity")
                    return

            elif choice == 's':
                if 'isDraft' in self.cli_core.opened_entity and self.cli_core.opened_entity['isDraft']:
                    yes = input(
                        f"Эта сущность - черновик. Хотите опубликовать? ([Y]es): ").strip()
                    if yes.lower() in ('y', 'yes'):
                        drafted_state = "Published"
                    else:
                        drafted_state = ""
                else:
                    drafted_state = ""

                # Сохранение entity
                if not self.cli_core.do_command(f"save_entity {drafted_state}"):
                    self.cli_core.do_command(f"discard_entity")
                    return

                self.show_current_object(False)
                break

            elif choice == 'd':
                # Выход из редактирования
                self.cli_core.do_command(f"discard_entity")
                break

            else:
                print("Неверный ввод, пожалуйста, введите число от 1 до 3, 's' или 'd'.")

    def do_create_entity(self, entity_type_key=None):
        """Создать новую Entity."""

        if entity_type_key not in ("", None):
            self.do_select_entity_type(entity_type_key)
        else:
            if (self.current_object is None) or (self.current_object["type"] in ("", None)):
                self.cli_core.do_command(f"show_entity_types")
                entity_type_key = input(f"Не выбран никакой тип Entity (команды select_entity <entity_id>, select_entity_type <entity_type> или create_entity <entity_type>), "
                                        f"задайте тип Entity: ").strip()
                self.do_select_entity_type(entity_type_key)
            else:
                self.show_current_object()

        data = {
            "locale": "none",
            "entityTypesByKeys": [self.current_object["type"]],
            "entityTypesOptions": {
                "includeReferencedToByKeys": ["*"],
                "includeAttributesByKeys": ["*"],
            },
            "attributesOptions": {
                "includeValues": True
            }
        }
        response = self.cli_core.rest_api_client.get_entity_type_schema(data)

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        entity_schema = response.json()

        if len(entity_schema["entityTypes"]) == 0:
            print(f"Схема для типа {self.current_object['type']} пустая. Проверьте права для получения схемы")
            return

        # Создание новой сущности
        if not self.cli_core.do_command(f"create_entity {self.current_object['type']}"):
            self.cli_core.do_command(f"discard_entity")
            return

        entity_type = entity_schema["entityTypes"][0]

        # Логика черновика
        is_draft = False
        if ('flags' in entity_type) and ('IsDraftAllowed' in entity_type['flags']):
            yes = input(f"Для сущности этого типа возможно создать черновик. Создать как черновик? ([Y]es): ").strip()
            if yes.lower() in ('y', 'yes'):
                is_draft = True

        # Задание атрибутов
        if "attributes" in entity_type:
            for attribute in entity_type["attributes"]:
                if ((not is_draft and "IsMandatory" in attribute["flags"]) or (is_draft and "IsDraftMandatory" in attribute["flags"])) \
                        and ("IsComputed" not in attribute["flags"]) and ("defaultValues" not in attribute):
                    attribute3 = next(((lambda x: x)(attribute2) for attribute2 in entity_schema["attributes"] if
                                       attribute2["key"].lower() == attribute['key'].lower()), None)
                    attribute_type = attribute3["type"]

                    if "IsFixed" in attribute3["flags"]:
                        print(
                            f"Возможные значения для обязательного IsFixed атрибута {attribute['key']} ({attribute_type}):")
                        for value in attribute3["values"]:
                            print(f"{value['locales'][0]['value']}")

                    value = input(
                        f"Введите значение для обязательного атрибута {attribute['key']} ({attribute_type}): ")
                    if not self.cli_core.do_command(f"set_entity_attribute_value {attribute['key']} \"{value}\""):
                        self.cli_core.do_command(f"discard_entity")
                        return

        # Задание референсов
        if "referencedTo" in entity_type:
            for reference in entity_type["referencedTo"]:
                if (not is_draft and "IsRequired" in reference["flags"]) or (is_draft and "IsDraftMandatory" in reference["flags"]):
                    print(f"Возможные значения для обязательной ссылки {reference['entityTypeKey']}")
                    for acceptableEntityType in reference["acceptableEntityType"]:
                        data = {
                            "entitiesOptions": {
                                "includeAttributeValuesByAttributeKeys": ["*"],
                                "includeEntityWorkflowStatesByWorkflowKeys": ["*"],
                                "includeReferences": False
                            },
                            "entitiesByEntityTypeKeys": [acceptableEntityType["key"]],
                            "locale": "none"
                        }
                        response = self.cli_core.rest_api_client.get_entities_vector(data)
                        if response.status_code != 200:
                            print(f"Response text: {response.text}")
                            return

                        entities = response.json()
                        for entity in entities:
                            if 'attributeValues' in entity:
                                attribute_name = next(
                                    ((lambda x: x)(attributeValue) for attributeValue in entity["attributeValues"] if
                                     attributeValue["attributeKey"] == "__NAME"), None)
                            else:
                                attribute_name = None
                            print(
                                f"{acceptableEntityType['key']}, id: {entity['id']}{', __NAME: ' + attribute_name['valueLocales'][0]['value'] if attribute_name else ''}")

                    value = input(f"Введите значение для обязательной ссылки {reference['entityTypeKey']}: ").strip()
                    if not self.cli_core.do_command(f"add_entity_reference_to {reference['key']} {value}"):
                        self.cli_core.do_command(f"discard_entity")
                        return

        if is_draft:
            drafted_state = "Drafted"
        else:
            drafted_state = ""

        if not self.cli_core.do_command(f"save_entity {drafted_state}"):
            self.cli_core.do_command(f"discard_entity")
            return

    def do_delete_entity(self, entity_id=None):
        """Удалить заданный тип Entity."""
        if entity_id in ("", None):
            if (self.current_object is None) or (self.current_object['id'] in ("", None)):
                self.do_show_entities()
                entity_id = input(f"Не указан никакой Entity (команда select_entity <entity_id> или delete_entity <entity_id>), задайте Entity: ").strip()
            else:
                self.show_current_object(True)
                entity_id = self.current_object['id']

        yes = input(f"Подтвердите удаление Entity {entity_id} ([Y]es): ").strip()
        if yes.lower() in ('y', 'yes'):
            self.cli_core.do_command(f"delete_entity {entity_id}")
        else:
            print(f"Удаление отменено")

    """References"""

    def do_show_references(self, fake_arg):
        """Показать все ссылки."""
        self.cli_core.do_command(f"show_references")

    def do_edit_reference(self, parameter=None):
        """Редактировать ссылку"""
        args = self.cli_core.parse_args(parameter)
        if len(args) < 2:
            if not self.cli_core.do_command(f"show_references"):
                return
            print()
            print(f"Ссылка не указана (команда edit_reference <fromEntityTypeKey> <toKey>)")
            print()
            from_entity_type = input(f"Введите <fromEntityTypeKey>): ").strip()
            to_reference_key = input(f"Введите <toKey>): ").strip()
        else:
            from_entity_type = args[0]
            to_reference_key = args[1]

        if not self.cli_core.do_command(f"edit_reference {from_entity_type} {to_reference_key}"):
            return

        while True:
            self.show_reference(self.cli_core.opened_reference)

            # Показать меню выбора
            print()
            print("Выберите действие:")
            print("1. Редактировать ключ toReferenceKey")
            print("2. Редактировать ключ fromReferenceKey")
            print("3. Редактировать флаги")
            print("4. Редактировать тип ссылки")
            print()
            print("s. Сохранить ссылку и выйти из редактирования")
            print("d. Выход из редактирования без сохранения")
            print()

            choice = input("Введите номер выбранного действия: ").strip()

            if choice == '1':
                # Редактировать ключ toReferenceKey
                to_reference_key = input("Введите новый toReferenceKey: ").strip()
                self.cli_core.do_command(f"set_reference_to_key {to_reference_key}")

            elif choice == '2':
                # Редактировать ключ fromReferenceKey
                from_reference_key = input("Введите новый fromReferenceKey: ").strip()
                self.cli_core.do_command(f"set_reference_from_key {from_reference_key}")

            elif choice == '3':
                # Редактировать флаги
                reference_flags = input("Задайте флаги этой ссылки (IsDeleteCascade, IsRequired, IsDraftMandatory или пустая строка для удаления флагов): ").strip()
                self.cli_core.do_command(f"set_reference_flags {reference_flags}")

            elif choice == '4':
                # Редактировать тип ссылки
                reference_type = input(f"Укажите тип ссылки (OneToOne | OneToMany | ManyToOne | ManyToMany): ").strip()
                self.cli_core.do_command(f"set_reference_type {reference_type}")

            elif choice == 's':
                # Сохранить ссылку и выйти из редактирования
                self.cli_core.do_command(f"save_reference")
                break

            elif choice == 'd':
                # Выход без сохранения
                self.cli_core.do_command(f"discard_reference")
                break

            else:
                print("Неверный ввод, пожалуйста, введите число от 1 до 4, 's' или 'd'.")

    def do_delete_reference(self, parameter=None):
        """Удаление ссылки"""
        args = self.cli_core.parse_args(parameter)
        if len(args) < 2:
            if not self.cli_core.do_command(f"show_references"):
                return
            print()
            print(f"Ссылка не указана (команда delete_reference <fromEntityTypeKey> <toKey>)")
            print()
            from_entity_type = input(f"Введите <fromEntityTypeKey>): ").strip()
            to_reference_key = input(f"Введите <toKey>): ").strip()
        else:
            from_entity_type = args[0]
            to_reference_key = args[1]

        response = self.cli_core.rest_api_client.get_references(
            from_entity_type_key=from_entity_type,
            to_references_keys=[to_reference_key])

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        references = response.json()
        if not references:
            print(f"Сслыка сущности с параметрами fromEntityTypeKey: {from_entity_type} и toKey: {to_reference_key} не найдена")
            return

        self.show_reference(references[0])
        yes = input(f"Подтвердите удаление этой ссылки ([Y]es): ").strip()
        if yes.lower() in ('y', 'yes'):
            self.cli_core.do_command(f"delete_reference {from_entity_type} {to_reference_key}")
        else:
            print(f"Удаление отменено")

    """Others"""

    def do_show_selected_object(self, fake_arg):
        """Показать текущий выбранный объект."""
        self.show_current_object()

    def do_back(self, fake_arg):
        """Вернуться к предыдущему объекту, который был выбран ранее."""
        if len(self.history_back) > 0:
            previous_entity = self.history_back.pop()
            self.history_forward.append(self.current_object)
            self.current_object = previous_entity

            self.show_current_object()
        else:
            print("Нет истории перемещений назад.")

    def do_forward(self, fake_arg):
        """Вернуться к следующему объекту, который был выбран ранее."""
        if len(self.history_forward) > 0:
            next_entity = self.history_forward.pop()
            self.history_back.append(self.current_object)
            self.current_object = next_entity

            self.show_current_object()
        else:
            print("Нет истории перемещений вперед.")

    def do_scripts(self, fake_arg):
        """Режим ввода скриптов"""
        while True:
            command = input("lowcode_cli.scripts> ")
            if command.lower() == 'exit':
                break
            else:
                self.cli_core.do_command(command.strip())

    def do_set_output_file(self, parameter=None):
        """Задание выходного скрипт-файла"""
        if parameter in (None, ''):
            print()
            print(f"выходной скрипт-файл не указан (команда set_output_file <file>)")
            print()
            output_script = input("Введите выходной скрипт-файл: ").strip()
        else:
            args = self.cli_core.parse_args(parameter)
            if len(args) > 0:
                output_script = args[0]
            else:
                output_script = ''

        if os.path.exists(output_script):
            print()
            print(f"Файл {output_script} существует.")
            inp = input(f"Хотите перезаписать его ([R]ewrite) или продолжить ([C]ontinue)? ").strip()
            print()
            if inp.lower() == 'r':
                self.cli_core.do_command(f"set_output_file \"{output_script}\"")
            elif inp.lower() == 'c':
                self.cli_core.do_command(f"set_output_file \"{output_script}\" continue")
            else:
                print()
                print(f"Отмена инициализации выходного скрипт-файла")
                print()
        else:
            self.cli_core.do_command(f"set_output_file \"{output_script}\"")

    def do_exit(self, fake_arg):
        """Выйти из CLI."""
        print("Выход из CLI.")
        return True

    def do_help(self, args):
        """Выводит список доступных команд и их описание."""
        cmd.Cmd.do_help(self, args)

    def complete(self, text, state):
        """Подсказка с возможными командами."""
        commands = [name[3:] for name in dir(self) if name.startswith("do_")]
        options = [i for i in commands if i.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None


if __name__ == '__main__':
    EntitiesCLI().cmdloop()
