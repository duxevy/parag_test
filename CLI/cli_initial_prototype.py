import cmd

from cli_rest_api_client import RestAPIClient

drafted_state = "Drafted_Entity"
published_state = "Published_Entity"
root_section_id = "79e41751-6263-45e3-aab0-9eb0c728ba1c"
label_key = "__label__"


class EntitiesCLI(cmd.Cmd):
    prompt = 'entities-cli> '

    def __init__(self):
        super().__init__()
        self.history_back = []  # back stack для объектов (Entity, EntityType)
        self.history_forward = []  # forward stack для объектов (Entity, EntityType)
        self.current_object = {"id": None, "type": None}
        self.rest_api_client = RestAPIClient()
        self.rest_api_client.update_api_key()

    def show_entity_type_to_create(self, entity_type, references_to, references_from):
        print()
        print(f"-----------------Создаваемый тип Entity-----------------")
        print(f"Имя типа Entity: {entity_type['key']}")
        if 'attributes' in entity_type and len(entity_type['attributes']) > 0:
            print(f"Атрибуты:")
            for attribute in entity_type['attributes']:
                print(f"    {attribute['key']}")
        if len(references_to) > 0:
            print(f"Ссылки на другие типы (referencedTo):")
            for reference in references_to:
                print(f"    {reference['toEntityTypeKey']}, {reference['type']}")
        if len(references_from) > 0:
            print(f"Ссылки других типов на этот (referencedFrom):")
            for reference in references_from:
                print(f"    {reference['fromEntityTypeKey']}, {reference['type']}")
        print(f"--------------------------------------------------------")

    def show_entity_types(self):
        response = self.rest_api_client.get_entity_types()

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        entity_types = response.json()

        if entity_types:
            print()
            for entity_type in entity_types:
                print(f"{entity_type['key']}"
                      f"{' (' + entity_type['flags'] + ')' if entity_type['flags'] != 'None' else ''}"
                      f": {entity_type['id']}"
                      f"{', parent: ' + entity_type['parentKey'] if 'parentKey' in entity_type else ''}")
            print()
        else:
            print(f"Типы Entity отсутствуют")

    def get_entity_type_id(self, entity_type):
        response = self.rest_api_client.get_entity_types(f"Key={entity_type}")

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        if len(response.json()) == 0:
            print(f"Entity тип {entity_type} отсутствует")
            return

        return response.json()[0]['id']

    def add_references_to(self, references_to):
        print()
        print(f"Доступные типы Entities:")
        self.show_entity_types()
        print()
        to_entity_type_key = input(f"Укажите тип Entity для ссылки: ")

        if self.get_entity_type_id(to_entity_type_key) is None: # такого типа нет
            return references_to

        reference_type = input(f"Укажите тип ссылки (OneToOne | OneToMany | ManyToOne | ManyToMany): ")
        references_to.append({"toEntityTypeKey": to_entity_type_key,
                              "flags": "IsDeleteCascade",
                              "type": reference_type})

        return references_to

    def add_references_from(self, references_from):
        print()
        print(f"Доступные типы Entities:")
        self.show_entity_types()
        print()
        from_entity_type_key = input(f"Укажите тип Entity, которая должна ссылаться на эту Entity: ")

        if self.get_entity_type_id(from_entity_type_key) is None: # такого типа нет
            return references_from

        reference_type = input(f"Укажите тип ссылки (OneToOne | OneToMany | ManyToOne | ManyToMany): ")
        references_from.append({"fromEntityTypeKey": from_entity_type_key,
                                "flags": "IsDeleteCascade",
                                "type": reference_type})

        return references_from

    def get_attribute_id(self, attribute_key, warning=True):
        response = self.rest_api_client.get_attributes(f"Key={attribute_key}")

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        if len(response.json()) == 0:
            if warning:
                print(f"Атрибут {attribute_key} отсутствует")
            return

        return response.json()[0]['id']

    def show_attributes(self):
        response = self.rest_api_client.get_attributes("")
        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return
        attributes = response.json()
        if len(attributes) > 0:
            print()
            print(f"Доступные атрибуты:")
            print(f"----------------------------------")
            for attribute in attributes:
                print(f"{attribute['key']} ({attribute['id']}): {attribute['type']}")
            print()
        else:
            print(f"Атрибуты отсутствуют")
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
        self.show_attributes()
        attribute_key = input("Введите имя атрибута: ")

        # проверка не был ли атрибут уже добавлен
        if len(attributes) > 0:
            for attribute in attributes:
                if attribute['key'] == attribute_key:
                    print (f"Атрибут {attribute_key} уже добавлен")
                    return attributes

        # проверка существует ли атрибут
        response = self.rest_api_client.get_attributes(f"Key={attribute_key}")

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return attributes

        if len(response.json()) > 0:
            # атрибут существует
            attribute_type = response.json()[0]['type']
            print (f"Атрибут {attribute_key} существует, добавлен")

        else:
            # атрибут не существует, надо создать
            attribute_type = input(f"Атрибут {attribute_key} не существует, введите его тип для создания\n"
                                   f"(GUID | Boolean | Number | Object | String | Text | DateTime | Address | TimeSpan | Attachment): ")
            data = [
                {
                        "key": attribute_key,
                        "flags": "None",
                        "type": attribute_type
                }
            ]
            response = self.rest_api_client.create_attribute(data)

            if response.status_code != 200:
                print(f"Response text: {response.text}")
                return attributes

        if attribute_type in ("String", "Text"):
            attribute_flags = "isFullTextSearch"
        else:
            attribute_flags = "None"

        attribute = {"key": attribute_key, "flags": attribute_flags}
        attributes.append(attribute)
        return attributes

    def create_section(self, parent_section_id, section_name):
        new_entity_data = [
            {
                "entityTypeKey": "SECTION",
                "attributeValues": [
                    {
                        "valueLocales": [{"value": section_name}],
                        "attributeKey": "__NAME"
                    }
                ],
                "referencedTo": [
                    {
                        "key": "SECTION",
                        "entityId": parent_section_id
                    }
                ]
            }
        ]

        print(f"new_entity_data: {new_entity_data}")

        # Отправка запроса на создание новой сущности
        response = self.rest_api_client.create_entity(new_entity_data)

        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Response text: {response.text}")

    def create_application(self, parent_section_id, application_name, entity_type):
        new_entity_data = [
            {
                "entityTypeKey": "APPLICATION",
                "attributeValues": [
                    {
                        "valueLocales": [{"value": application_name}],
                        "attributeKey": "__NAME"
                    },
                    {
                        "valueLocales": [{"value": entity_type}],
                        "attributeKey": "ENTITY_TYPE"
                    }
                ],
                "referencedTo": [
                    {
                        "key": "SECTION",
                        "entityId": parent_section_id
                    }
                ]
            }
        ]

        print(f"new_entity_data: {new_entity_data}")

        # Отправка запроса на создание новой сущности
        response = self.rest_api_client.create_entity(new_entity_data)

        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Response text: {response.text}")

    def show_current_object(self, show_with_schema=False):
        if self.current_object['type'] is None:
            print(f"Не выбрано никакого объекта, используйте select_entity или select_entity_type")
        else:
            attributes = {}
            references = {}

            if self.current_object['id'] is not None:

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

                    response = self.rest_api_client.get_entity_type_schema(data)

                    if response.status_code != 200:
                        print(f"Response text: {response.text}")
                        return

                    entity_schema = response.json()
                    print(f"entity_schema: {entity_schema}")

                    entity_type_schema = entity_schema["entityTypes"][0]

                    if "attributes" in entity_type_schema:
                        for attribute in entity_type_schema["attributes"]:
                            if attribute['key'] != "__NAME":
                                attributes[attribute['key']] = None

                    if "referencedTo" in entity_type_schema:
                        for reference in entity_type_schema["referencedTo"]:
                            references[reference['key']] = None

                # заполнение attributes и references реальными данными entity
                parameters = f"Id={self.current_object['id']}&WithAttributeValues=true&WithReferencedTo=true"
                response = self.rest_api_client.get_entities(parameters)

                if response.status_code == 200:
                    print(f"Response: {response.json()}")

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

                else:
                    print(f"Response text: {response.text}")
                    return
            else:
                entity_name = None
                state_key = None
                entity = {}

            # заполнение значений атрибутов
            if 'attributeValues' in entity:
                for attributeValue in entity['attributeValues']:
                    if attributeValue["attributeKey"] != "__NAME":
                        attributes[attributeValue['attributeKey']] = attributeValue['valueLocales'][0]['value']

            # заполнение ссылок referencedTo
            if 'referencedTo' in entity:
                for reference in entity['referencedTo']:
                    references[reference['key']] = f"{reference['entityId']} ({reference['entityTypeKey']})"

            print(f"-------------------------------------------")
            print(f"Selected object:")
            print(f"    EntityId: {self.current_object['id']}")
            print(f"    __NAME: {entity_name}")
            print(f"    Type: {self.current_object['type']}")
            print(f"    StateMachine: {state_key}")

            # Вывод значений атрибутов
            if attributes:
                print(f"Атрибуты:")
                for key, value in attributes.items():
                    print(f"    {key}: {value}")

            # Вывод ссылок referencedTo
            if references:
                print(f"Ссылки referencedTo:")
                for key, value in references.items():
                    print(f"    {key}: {value}")

            print(f"-------------------------------------------")

    def show_navigation_item(self, entity_id, level):
        parameters = f"Id={entity_id}&WithAttributeValues=true"
        response = self.rest_api_client.get_entities(parameters)

        if response.status_code == 200:
            entity = response.json()[0]
            attribute_name = next(((lambda x: x)(attributeValue) for attributeValue in entity["attributeValues"] if
                                   attributeValue["attributeKey"] == "__NAME"), None)

            indentation = ' ' * (level * 4)
            print(
                f"{indentation}\{attribute_name['valueLocales'][0]['value']} ({entity_id}) - {entity['entityTypeKey']}")

            # Ищем потомков
            data = {
                "entitiesOptions": {
                    "includeReferences": True
                },
                "entitiesByEntityTypeKeys": ["SECTION", "APPLICATION"],
                "entitiesByReferencedTo": [
                    {
                        "entityId": entity_id,
                        "key": "SECTION"
                    }
                ],
                "locale": "none"
            }
            response = self.rest_api_client.get_entities_vector(data)

            child_entities = response.json()
            for child_entity in child_entities:
                self.show_navigation_item(child_entity['id'], level + 1)

        else:
            print(f"Response text: {response.text}")

    def do_show_attributes(self, arg):
        """Показать имеющиеся атрибуты."""
        self.show_attributes()

    def do_edit_attribute(self, attribute_key=None):
        """Редактирование атрибута."""

        if attribute_key in (None, ''):
            self.show_attributes()
            attribute_key = input("Укажите имя атрибута для редактирования: ")

        response = self.rest_api_client.get_attributes(f"Key={attribute_key}&WithProperties=true&WithValidators=true")
        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        if len(response.json()) > 0:
            # атрибут существует
            attribute = response.json()[0]

        while True:
            self.show_attribute_details(attribute)
            # Показать меню выбора
            print()
            print("Выберите действие:")
            print("1. Переименовать")
            print("2. Установить отображаемое имя (Label)")
            print("3. Установить тип данных")
            print("4. Установить фиксированные значения")
            print("5. Сохранить атрибут и выйти из редактирования")
            print("6. Выход из редактирования без сохранения")
            print()

            choice = input("Введите номер выбранного действия: ")

            if choice == '1':
                # Переименовать
                attribute_key = input("Задайте новое имя (key) атрибута: ")
                attribute_id = self.get_attribute_id(attribute_key, False)

                if attribute_id is not None:
                    print()
                    print(f"\033[31mАтрибут {attribute_key} уже существует\033[0m")
                else:
                    attribute['key'] = attribute_key

            elif choice == '2':
                # Установить отображаемое имя
                attribute_label = input("Задайте отображаемое имя (Label): ")
                if 'properties' not in attribute:
                    # нет properties
                    attribute['properties'] = [
                        {
                            "key": label_key.upper(),
                            "value": attribute_label
                        }
                    ]
                else:
                    # есть properties
                    prop_found = False
                    for prop in attribute['properties']:
                        if prop['key'].lower() == label_key:
                            prop['value'] = attribute_label
                            prop_found = True
                            break
                    if not prop_found:
                        # есть properties, но отсутствует label
                        attribute['properties'].append({
                            "key": label_key.upper(),
                            "value": attribute_label
                        })

            elif choice == '3':
                # Установить тип данных
                attribute['type'] = input(f"Введите новый тип данных\n"
                                          f"(GUID | Boolean | Number | Object | String | Text | DateTime | Address | TimeSpan | Attachment): ")

            elif choice == '4':
                # Установить фиксированные значения
                break

            elif choice == '5':
                # Сохранить и выйти
                response = self.rest_api_client.put_attributes([attribute])

                if response.status_code != 200:
                    print(f"Response text: {response.text}")
                    return
                print()
                print(f"Атрибут сохранён")
                print()
                break

            elif choice == '6':
                # Выход без сохранения
                break

            else:
                print("Неверный ввод, пожалуйста, введите число от 1 до 6.")

        """
        else:
            # атрибут не существует
            print(f"Атрибута не существует")
            print()
        """

    def do_delete_attribute(self, attribute_key=None):
        """Удалить атрибут."""

        if attribute_key in (None, ''):
            self.show_attributes()
            attribute_key = input("Укажите имя атрибута для удаления: ")

        attribute_id = self.get_attribute_id(attribute_key)

        if attribute_id is not None:
            self.rest_api_client.delete_attribute(attribute_id)
            print(f"Атрибут {attribute_key} удалён")
            print()
        else:
            print(f"Удаление отменено")
            print()

    def do_create_entity_type(self, arg):
        """Создать новый тип Entity."""
        entity_type_key = input(
            f"Задайте имя нового типа Entity: ")

        temp_entity_type = {
            "key": entity_type_key,
            "stateMachineKey": "EntitiesStateMachine",
            "flags": "isSearchable",
            "parentKey": "BASE_ENTITY",
            "attributes": []
        }
        references_to = []
        references_from = []

        while True:
            self.show_entity_type_to_create(temp_entity_type, references_to, references_from)
            # Показать меню выбора
            print()
            print("Выберите действие:")
            print("1. Добавить атрибуты")
            print("2. Добавить ссылки на другие типы Entity (referencedTo)")
            print("3. Добавить ссылки на этот тип Entity (referencedFrom)")
            print("4. Сохранить тип и выйти из создания типа Entity")
            print("5. Выход из создания типа Entity без сохранения")
            print()

            choice = input("Введите номер выбранного действия: ")

            if choice == '1':
                # Добавление атрибутов
                temp_entity_type['attributes'] = self.add_attribute(temp_entity_type['attributes'])

            elif choice == '2':
                # Добавление referencedTo ссылок
                references_to = self.add_references_to(references_to)

            elif choice == '3':
                # Добавление referencedFrom ссылок
                references_from = self.add_references_from(references_from)

            elif choice == '4':
                # Сохранить и выйти
                # Создание нового типа Entity

                if not temp_entity_type["attributes"]:
                    del temp_entity_type["attributes"]  # удаление пустого массива attributes

                data = [temp_entity_type]
                response = self.rest_api_client.create_entity_type(data)

                if response.status_code != 200:
                    print(f"Response text: {response.text}")
                    return

                # проставление permissions
                data = [
                    {
                        "type": "CreateEntity",
                        "level": "Business"
                    },
                    {
                        "type": "ReadEntity",
                        "level": "Business"
                    },
                    {
                        "type": "UpdateEntity",
                        "level": "Business"
                    },
                    {
                        "type": "DeleteEntity",
                        "level": "Business"
                    },
                    {
                        "type": "QuerySchema",
                        "level": "Business"
                    },
                    {
                        "type": "QueryVector",
                        "level": "Business"
                    }
                ]

                self.rest_api_client.create_entity_type_permissions(response.json()[0]['id'], data)

                # Создание ссылок
                if len(references_to) > 0:
                    for reference in references_to:
                        reference['fromEntityTypeKey'] = entity_type_key
                        reference['fromReferenceKey'] = entity_type_key
                        reference['toReferenceKey'] = reference['toEntityTypeKey']
                        reference['flags'] = 'IsDeleteCascade'

                if len(references_from) > 0:
                    for reference in references_from:
                        reference['toEntityTypeKey'] = entity_type_key
                        reference['toReferenceKey'] = entity_type_key
                        reference['fromReferenceKey'] = reference['fromEntityTypeKey']
                        reference['flags'] = 'IsDeleteCascade'

                response = self.rest_api_client.create_reference(references_to + references_from)
                if response.status_code != 200:
                    print(f"Response text: {response.text}")
                    return

                break

            elif choice == '5':
                # Выход без сохранения
                break

            else:
                print("Неверный ввод, пожалуйста, введите число от 1 до 5.")

    def do_delete_entity_type(self, entity_type=None):
        """Удалить заданный тип Entity."""
        if entity_type in (None, ''):
            if self.current_object['type']:
                entity_type = self.current_object['type']
            else:
                print(
                    f"Никакой тип Entity не выбран. Используйте select_entity_type или укажите тип в параметре delete_entity_type <entity_type>")
                return

        yes = input(f"Подтвердите удаление Entity типа {entity_type} ([Y]es): ")
        if yes.lower() in ('y', 'yes'):

            # получение entity_type_id
            entity_type_id = self.get_entity_type_id(entity_type)

            if entity_type_id is None: # такого EntityType нет
                return

            response = self.rest_api_client.delete_entity_type(entity_type_id)

            if response.status_code != 204:
                print(f"Response text: {response.text}")
                return
        else:
            print(f"Удаление отменено")

    def do_show_entity_types(self, arg):
        """Показать типы Entity."""
        self.show_entity_types()

    def do_show_entities(self, entity_type=None):
        """Показать Entities заданного типа."""
        if entity_type in (None, ''):
            if self.current_object['type']:
                entity_type = self.current_object['type']
            else:
                print(
                    f"Никакой тип Entity не выбран. Используйте select_entity_type или укажите тип в параметре show_entities <entity_type>")
                return

        vector_data = {
            "entitiesOptions": {
                "includeAttributeValuesByAttributeKeys": ["*"],
                "includeEntityWorkflowStatesByWorkflowKeys": ["*"],
                "includeReferences": True
            },
            "entitiesByEntityTypeKeys": [entity_type],
            "locale": "none"
        }
        vector_count_data = {
            "entitiesByEntityTypeKeys": [entity_type],
            "locale": "none"
        }

        # получение всех Entities
        entities = self.rest_api_client.get_all_entities_vector(vector_data,
                                                                vector_count_data)  # в случае успеха возвращается json со всеми entities, status_code отсутствует

        if hasattr(entities, 'status_code'):
            print(f"Response text: {entities.text}")
            return

        for entity in entities:
            if 'attributeValues' in entity:
                attribute_name = next(((lambda x: x)(attributeValue)
                                       for attributeValue in entity["attributeValues"]
                                       if attributeValue["attributeKey"] == "__NAME"), None)
            else:
                attribute_name = None
            print(
                f"id: {entity['id']}{', __NAME: ' + attribute_name['valueLocales'][0]['value'] if attribute_name else ''}{', StateMachine: ' + entity['stateKey'] if 'stateKey' in entity else ''}")

    def do_select_entity(self, entity_id):
        """Выбрать Entity."""
        parameters = f"Id={entity_id}"
        response = self.rest_api_client.get_entities(parameters)

        if response.status_code == 200:
            print(f"Response: {response.json()}")

            if self.current_object['type'] is not None:
                self.history_back.append(self.current_object.copy())
            self.history_forward.clear()
            self.current_object = {"id": entity_id, "type": response.json()[0]['entityTypeKey']}

            self.show_current_object()

        else:
            print(f"Response text: {response.text}")

    def do_publish_entity(self, entity_id=None):
        """Опубликовать Entity."""
        if entity_id in (None, ''):
            if self.current_object["id"] is None:
                print(f"Не выбрана никакая Entity, используйте select_entity <entity_id> или укажите entity в параметре publish_entity <entity_id>")
                return
            else:
                entity_id = self.current_object["id"]

        parameters = f"Id={entity_id}"
        response = self.rest_api_client.get_entities(parameters)

        if response.status_code == 200:
            if 'stateKey' in response.json()[0]:

                if response.json()[0]['stateKey'].lower() == drafted_state.lower():
                    data = [
                        {
                            "id": entity_id,
                            "stateKey": published_state
                        }
                    ]
                    response = self.rest_api_client.put_entities_state_transit(data)
                    if response.status_code == 204:
                        print(f"Успех")
                    else:
                        print(f"Response text: {response.text}")
                else:
                    print(
                        f"Нельзя опубликовать. Для выбранной Entity {entity_id} stateKey = {response.json()[0]['stateKey']}")
            else:
                print(f"Для выбранной Entity {entity_id} отсутствует stateKey")

        else:
            print(f"Response text: {response.text}")
            return

    def do_select_entity_type(self, entity_type):
        """Выбрать Entity Type."""
        self.history_back.append(self.current_object.copy())
        self.history_forward.clear()
        self.current_object = {"id": None, "type": entity_type}
        self.show_current_object()

    def do_show_selected_object(self, arg):
        """Показать текущий выбранный объект."""
        self.show_current_object()

    def do_show_referenced_entities(self, entity_id=None):
        """Показать связанные Entities."""
        if entity_id in (None, ''):
            if self.current_object["id"] is None:
                print(f"Не выбрана никакая Entity, используйте select_entity <entity_id> или укажите entity в параметре show_referenced_entities <entity_id>")
                return
            else:
                entity_id = self.current_object["id"]

        parameters = f"Id={entity_id}&WithReferencedTo=true"
        response = self.rest_api_client.get_entities(parameters)

        if response.status_code == 200:
            print(f"Response: {response.json()}")

            if 'referencedTo' in response.json()[0]:
                referencedTo_entities = response.json()[0]['referencedTo']
                for referencedTo_entitiy in referencedTo_entities:
                    print(f"{referencedTo_entitiy['entityTypeKey']}: {referencedTo_entitiy['entityId']}")
            else:
                print(f"Связанные entities (referencedTo) отсутствуют.")

        else:
            print(f"Response text: {response.text}")
            return

    def do_edit_entity(self, arg):
        """Редактирование Entity."""
        if self.current_object['id'] is None:
            print(f"Не выбрано никакой Entity, используйте select_entity <entity_id>")
            return

        self.show_current_object(True)

        # выбранная entity
        parameters = f"Id={self.current_object['id']}&WithAttributeValues=true&WithReferencedTo=true"
        response = self.rest_api_client.get_entities(parameters)

        if response.status_code != 200:
            print(f"Response: {response.json()}")
            return

        current_entity = response.json()[0]

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
        response = self.rest_api_client.get_entity_type_schema(data)

        if response.status_code != 200:
            print(f"Response text: {response.text}")
            return

        entity_schema = response.json()
        entity_type = entity_schema["entityTypes"][0]

        # начальная инициализация словаря атрибутов
        attributes = {}
        if 'attributeValues' in current_entity:
            for attributeValue in current_entity['attributeValues']:
                attributes[attributeValue['attributeKey']] = attributeValue['valueLocales'][0]['value']

        # начальная инициализация словаря ссылок
        references = {}
        if 'referencedTo' in current_entity:
            for reference in current_entity['referencedTo']:
                references[reference['key']] = reference['entityId']

        while True:
            # Показать меню выбора
            print()
            print("Выберите действие:")
            print("1. Редактировать атрибуты")
            print("2. Редактировать ссылки")
            print("3. Сохранить entity и выйти из редактирования")
            print("4. Выход из редактирования без сохранения Entity")
            print()

            choice = input("Введите номер выбранного действия: ")

            if choice == '1':
                # Редактировать атрибуты
                if "attributes" not in entity_type:
                    print("Нет доступных атрибутов для редактирования.")
                else:
                    attribute_key = input("Введите имя атрибута: ")

                    attribute3 = next(((lambda x: x)(attribute2) for attribute2 in entity_schema["attributes"] if
                                       attribute2["key"] == attribute_key), None)
                    attribute_type = attribute3["type"]

                    if "IsFixed" in attribute3["flags"]:
                        print(
                            f"Возможные значения для IsFixed атрибута {attribute_key} ({attribute_type}):")
                        for value in attribute3["values"]:
                            print(f"{value['locales'][0]['value']}")

                    attribute_value = input(f"Введите новое значение для атрибута {attribute_key} ({attribute_type}): ")
                    attributes[attribute_key] = attribute_value

            elif choice == '2':
                # Редактировать ссылки
                if 'referencedTo' not in entity_type:
                    print("Нет доступных ссылок для редактирования.")
                else:
                    reference_key = input("Введите имя ссылки: ")

                    reference3 = next(((lambda x: x)(reference2)
                                       for reference2 in entity_type["referencedTo"]
                                       if reference2["entityTypeKey"] == reference_key), None)

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
                        response = self.rest_api_client.get_entities_vector(data)
                        if response.status_code != 200:
                            print(f"Response text: {response.text}")
                            return

                        entities = response.json()
                        for entity in entities:
                            attribute_name = next(((lambda x: x)(attributeValue)
                                                   for attributeValue in entity["attributeValues"]
                                                   if attributeValue["attributeKey"] == "__NAME"), None)
                            print(
                                f"{acceptableEntityType['key']}, id: {entity['id']}{', __NAME: ' + attribute_name['valueLocales'][0]['value'] if attribute_name else ''}")

                    reference_value = input(f"Введите новое значение ссылки {reference_key}: ")
                    references[reference_key] = reference_value

            elif choice == '3':
                # Сохранение entity

                # удаление текущих значений атрибутов из Entity
                current_entity["attributeValues"] = []

                if attributes:
                    for key, value in attributes.items():
                        if value != '':
                            new_attribute_value = {
                                "valueLocales": [{"value": value}],
                                "attributeKey": key,
                            }
                            current_entity["attributeValues"].append(new_attribute_value)

                # удаление текущих ссылок из Entity
                current_entity["referencedTo"] = []

                if references:
                    for key, value in references.items():
                        if value != '':
                            new_reference = {
                                "key": key,
                                "entityId": value
                            }
                            current_entity["referencedTo"].append(new_reference)

                # удаление пустых attributeValues и referencedTo
                if not current_entity["attributeValues"]:
                    del current_entity["attributeValues"]

                if not current_entity["referencedTo"]:
                    del current_entity["referencedTo"]

                data = [current_entity]

                response = self.rest_api_client.put_entities(data)

                if response.status_code != 200:
                    print(f"Response text: {response.text}")
                    return

                self.show_current_object(False)
                break

            elif choice == '4':
                # Выход из редактирования
                break

            else:
                print("Неверный ввод, пожалуйста, введите число от 1 до 4.")

    def do_create_entity(self, args):
        """Создать новую Entity."""

        if self.current_object["type"] in ("", None):
            print(f"Не выбран никакой тип Entity, используйте команды select_entity или select_entity_type")
        else:
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
            response = self.rest_api_client.get_entity_type_schema(data)

            if response.status_code != 200:
                print(f"Response text: {response.text}")
                return

            entity_schema = response.json()
            print(f"entity_schema: {entity_schema}")

            if len(entity_schema["entityTypes"]) == 0:
                print(f"Схема для типа {self.current_object['type']} пустая. Проверьте права для получения схемы")
                return
            # Создание новой сущности
            entity_type = entity_schema["entityTypes"][0]

            # Задание атрибутов
            attributes = {}

            if "attributes" in entity_type:
                for attribute in entity_type["attributes"]:
                    if ("IsMandatory" in attribute["flags"]) and ("IsComputed" not in attribute["flags"]) and (
                            "defaultValues" not in attribute):
                        attribute3 = next(((lambda x: x)(attribute2) for attribute2 in entity_schema["attributes"] if
                                           attribute2["key"] == attribute['key']), None)
                        attribute_type = attribute3["type"]

                        if "IsFixed" in attribute3["flags"]:
                            print(
                                f"Возможные значения для обязательного IsFixed атрибута {attribute['key']} ({attribute_type}):")
                            for value in attribute3["values"]:
                                print(f"{value['locales'][0]['value']}")

                        value = input(
                            f"Введите значение для обязательного атрибута {attribute['key']} ({attribute_type}): ")
                        attributes[attribute["key"]] = value

            # Задание референсов
            references = {}

            if "referencedTo" in entity_type:
                for reference in entity_type["referencedTo"]:
                    if "IsRequired" in reference["flags"]:
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
                            response = self.rest_api_client.get_entities_vector(data)
                            if response.status_code != 200:
                                print(f"Response text: {response.text}")
                                return

                            entities = response.json()
                            for entity in entities:
                                attribute_name = next(
                                    ((lambda x: x)(attributeValue) for attributeValue in entity["attributeValues"] if
                                     attributeValue["attributeKey"] == "__NAME"), None)
                                print(
                                    f"{acceptableEntityType['key']}, id: {entity['id']}{', __NAME: ' + attribute_name['valueLocales'][0]['value'] if attribute_name else ''}")

                        value = input(f"Введите значение для обязательной ссылки {reference['entityTypeKey']}: ")
                        references[reference["key"]] = value

            # Формирование JSON для создания новой сущности
            new_entity_data = [
                {
                    "entityTypeKey": self.current_object["type"],
                    **({"attributeValues": [
                        {
                            "valueLocales": [{"value": value}],
                            "attributeKey": key
                        } for key, value in attributes.items()
                    ]} if len(attributes) > 0 else {}),
                    **({"referencedTo": [
                        {
                            "key": key,
                            "entityId": value
                        } for key, value in references.items()
                    ]} if len(references) > 0 else {})
                }
            ]

            print(f"new_entity_data: {new_entity_data}")

            # Отправка запроса на создание новой сущности
            response = self.rest_api_client.create_entity(new_entity_data)

            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Response text: {response.text}")

    def do_create_section(self, args):
        """Создание нового раздела."""
        if (self.current_object['type'] == "SECTION") and (self.current_object['id'] is not None):
            parent_section_id = self.current_object['id']
            section_name = input(f"Введите имя нового раздела: ")

            self.create_section(parent_section_id, section_name)
        else:
            self.show_current_object()
            print(f"Выберите Entity типа SECTION")

    def do_create_application(self, args):
        """Создание нового приложения."""
        if (self.current_object['type'] == "SECTION") and (self.current_object['id'] is not None):
            parent_section_id = self.current_object['id']
            application_name = input(f"Введите имя нового приложения: ")
            entity_type = input(f"Введите тип Entity, для которого это приложение предназначено: ")
            self.create_application(parent_section_id, application_name, entity_type)
        else:
            self.show_current_object()
            print(f"Выберите Entity типа SECTION")

    def do_show_navigation_structure(self, args):
        """Показать информацию о структуре навигации."""
        print(f"----------------------------Navigation Structure--------------------------------")
        self.show_navigation_item(root_section_id, 0)
        print(f"--------------------------------------------------------------------------------")

    def do_back(self, args):
        """Вернуться к предыдущему объекту, который был выбран ранее."""
        if len(self.history_back) > 0:
            previous_entity = self.history_back.pop()
            self.history_forward.append(self.current_object)
            self.current_object = previous_entity

            self.show_current_object()
        else:
            print("Нет истории перемещений назад.")

    def do_forward(self, args):
        """Вернуться к следующему объекту, который был выбран ранее."""
        if len(self.history_forward) > 0:
            next_entity = self.history_forward.pop()
            self.history_back.append(self.current_object)
            self.current_object = next_entity

            self.show_current_object()
        else:
            print("Нет истории перемещений вперед.")

    def do_exit(self, args):
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
