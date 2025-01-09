----------------------------------------------------
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

6. доступные команды:

# ---------------------------  Organizations  ---------------------------

- Создать организацию
        create_organization <name> <business_email> [<country>]

- Удалить организацию
        delete_organization <name>

- Показать все организации
        show_organizations [SkipMDCheck]

- Показать конкретную организацию
        show_organization <name>

# ---------------------------  User / Business User  ---------------------------

- Создать пользователя (доступ уровня Admin)
        create_user <login> <password> <first_name> <last_name> [<country>], [<language>]

- Удалить пользователя (доступ уровня Admin)
        delete_user <login>

- Показать данные пользователя (доступ уровня Admin)
        show_user <login>

- Создать бизнесс пользователя (доступ уровня Admin)
        create_business_user <login> <buisness_id> <space1> <role1>[ <spaceN> <roleN>]

- Изменить параметры бизнесс пользователя (доступ уровня Admin)
        set_business_user <login> <buisness_id> <space1> <role1>[ <spaceN> <roleN>]

- Показать бизнесс пользователя (доступ уровня Admin)
        show_business_user <login> <buisness_id>

- Логин пользователя
        login <login> <password>

- Выполнять команды через админ контроллеры
        work_as_admin

- Изменение пароля пользователя
        set_password <old_password> <new_password>

- Показ всех бизнесов (trustors) пользователя
        show_trustors

- Показ прав пользователя (trusts)
        show_rights

- Логин бизнес-пользователя
        use_business <id>

- Установить сервис для пользования
        use_service <service_path>

# ---------------------------  Access Config  ---------------------------

- Задать конфигурацию доступа
        set_access_config <key>,[ <service_path>], <baseUrl>,[ <businessId>],[ <business_email>],[ <user_email>],[ <password>],[ <api_key>]

- Удалить конфигурацию доступа
        delete_access_config <key>

- Показать все конфигурации доступа
        show_access_configs

- Показать текущую конфигурацию доступа
        show_current_access_config

- Использовать конкретную конфигурацию доступа
        use_access_config <key>

# ---------------------------  Raw Requests  ---------------------------

- Сделать raw request от лица бизнес-пользователя
        raw_request_business <url_suffix> POST|GET|PUT|DELETE|PATCH [<body_escaped_json>] [multipart]

- Сделать raw request от лица админа
        raw_request_admin <url_suffix> POST|GET|PUT|DELETE|PATCH [<body_escaped_json>] [multipart]

- Сделать произвольный raw request
        raw_request <url_suffix_ext> POST|GET|PUT|DELETE|PATCH [<body_escaped_json>] [multipart]

# ---------------------------  Script Variables  ---------------------------

- Установить значение переменной
        set_script_variable <script_variable> [<value>]

- Установить значение переменной на значение ключа из последнего response
        set_script_variable_from_response <script_variable> <key_in_last_response_json>

- Загрузить значение переменной из файла
        set_script_variable_from_file <script_variable> <file_path> [Unescaped | Escaped | DoubleEscaped]

- Загрузить значение переменной из атрибута
        set_script_variable_from_attribute <script_variable> <entity_id> <attribute_key>

- Показать значения всех переменных
        show_script_variables

# ---------------------------  EntityType Permissions / Permissions Variables  ---------------------------

- Установить переменную доступа
        set_permissions_variable <permissions_variable_name> <escaped_json>

- Создать переменную доступа
        create_permissions_variable <permissions_variable_name>

- Редактировать переменную доступа
        edit_permissions_variable <permissions_variable_name>

- Установить доступ, команда может быть применена для открытой permissions_variable или для открытой EntityType
        set_permission <permission_type> <level> [<space> <role>]

- Удалить доступ, команда может быть применена для открытой permissions_variable или для открытой EntityType
        delete_permission <permission_type> <level>

- Показать все параметры доступа, команда может быть применена для открытой permissions_variable или для открытой EntityType
        show_permissions

- Сохранить переменную доступа
        save_permissions_variable

- Откат открытой переменной доступа
        discard_permissions_variable

- Удалить переменную доступа
        delete_permissions_variable <permissions_variable_name>

- Показать все переменные доступа
        show_permissions_variables

- Установить параметры доступа к EntityType по переменной доступа
        set_permissions_from_variable <permissions_variable_name>

# ---------------------------  Businesses (Admin)  ---------------------------

- Создать новый бизнес
        create_business [<business_id>], [Clear]

- Удалить бизнес
        delete_business [<business_id>], [Force]

- Показать имеющиеся бизнесы
        show_businesses

# ---------------------------  BusinessPermissions (Admin)  ---------------------------

- Установка прав доступа для бизнеса
        set_business_permissions <type> <space> <role> [<secondFactorRequired>]

- Удаление прав доступа для бизнеса
        delete_business_permissions <id>

- Показ всех прав доступа для бизнеса
        show_business_permissions

# ---------------------------  Schema  ---------------------------

- Импорт схемы
        import_schema <schema_path> [SkipSystemItems]

# ---------------------------  Attributes  ---------------------------

- Создание атрибута
        create_attribute <key>

- Редактирование атрибута
        edit_attribute <key>

- Установка нового имени атрибута
        set_attribute_key <key>

- Установка нового Label (отображаемого имени) атрибута
        set_attribute_label [<label>] [locale]

        допустимые типы локалей:
        en_us, zh_cn, fr_fr, de_de, nl_nl, pl_pl, ru_ru

- Установка типа данных атрибута
        set_attribute_type <type>

- Установка флагов атрибута
        set_attribute_flags [IsFixed]

- Установка фиксированных значений атрибута
        set_attribute_fixed_values "<value1>", "<value2>", "<value3>", ...

- Установка фиксированных значений атрибута и их показываемые значения
        set_attribute_fixed_display_values "<value1>" "<display_value1>", "<value2>" "<display_value2>", "<value3>" "<display_value2>", ...

- Установка валидатора атрибута
        set_attribute_validator <key> <type> <parameter> <error_message>

        допустимые типы валидаторов:
        RegexValidator, NumberLowerValidator, NumberLowerOrEqualsValidator, NumberGreaterValidator, NumberGreaterOrEqualsValidator,
        AddressAcceptableCountriesValidator, AddressRequiredFieldsValidator, ObjectSchemaValidator, DateTimeLowerValidator,
        DateTimeLowerOrEqualsValidator, DateTimeGreaterValidator, DateTimeGreaterOrEqualsValidator, TimeSpanLowerValidator,
        TimeSpanLowerOrEqualsValidator, TimeSpanGreaterValidator, TimeSpanGreaterOrEqualsValidator, StringMaxLengthValidator,
        StringMinLengthValidator, StringInvalidCharactersValidator, AttachmentMaxFileSizeInBytesValidator,
        AttachmentAvailableMimeTypesValidator, HtmlSecurityValidator

- Удаление валидатора атрибута
        delete_attribute_validator <key>

- Показ всех валидаторов атрибута
        show_attribute_validators

- Сохранить открытый атрибут
        save_attribute

- Откат открытого атрибута
        discard_attribute

- Удаление атрибута
        delete_attribute <key>

- Показ всех атрибутов
        show_attributes

# ---------------------------  EntityTypes  ---------------------------

- Создание нового типа сущности
        create_entity_type <key>

- Редактирование типа сущности
        edit_entity_type <key>

- Установка родителя для типа сущности
        set_entity_type_parent <parentKey>

- Установка машины состояний для типа сущности
        set_entity_type_state_machine <stateMachineKey>

- Установка флагов типа сущности
        set_entity_type_flags [IsAbstract], [IsSearchable], [IsUnique], [IsDraftAllowed]

- Установка нового Label (отображаемого имени) типа сущности
        set_entity_type_label [<label>]

- Добавить атрибут к типу сущности
        add_attribute <key>, [IsFullTextSearch], [IsMandatory], [IsUnique], [IsDraftMandatory], [IsReadonly], [IsComputed], [IsEncrypted]

- Установить дефолтное значение атрибута
        set_attribute_default_value <key> [<default_value>], [OnCreate], [OnUpdate]

- Удалить атрибут у типа сущности
        remove_attribute <key>

- Задать вычисляемое значение атрибута
        edit_computed_value <key>

- Задать переменную для вычисляемого атрибута по другому атрибуту этой сущности или сущности, на которую ссылается эта.
        set_variable_attribute <variable_key>, [<to_reference_key>], <attribute_key>[, SetDefault | Error | Ignore]

- Задать переменную для вычисляемого атрибута по атрибуту другой сущности, ссылающейся на эту
        set_variable_attribute_from <variable_key>, <from_reference_key>, <attribute_key>[, SetDefault | Error | Ignore]

- Установить дефолтное значение переменной вычисляемого атрибута
        set_variable_default_value <variable_key> [<default_value>]

- Задать для вычисляемого атрибута переменную, связанную с workflow
        set_variable_workflow <variable_key>, <workflow_key>

- Удалить переменную для вычисляемого атрибута
        delete_variable <variable_key>

- Показать все переменные для вычисляемого атрибута
        show_variables

- Задать выражение для вычисляемого атрибута
        set_expression "<expression>" [Expression|Script]  # Expression by default

- Задать флаги для вычисляемого атрибута
        set_computed_value_flags [OnCreate], [OnUpdate], [OnVariableChanged]

- Применить изменения и закрыть вычисляемый атрибут
        close_computed_value

- Отменить изменения вычисляемого атрибута
        discard_computed_value

- Показать все вычисляемые атрибуты
        show_computed_values

- Добавление ссылки на другой тип сущности
        add_reference_to <entity_type>, <reference_type>[, <toReferenceKey>, <fromReferenceKey>]

- Добавление ссылки другого типа сущности на этот
        add_reference_from <entity_type>, <reference_type>[, <toReferenceKey>, <fromReferenceKey>]

- Удаление ссылки на другой тип сущности
        remove_reference_to <toReferenceKey>

- Удаление ссылки другого типа сущности на этот
        remove_reference_from <fromReferenceKey>

- Сохранить открытый тип сущности
        save_entity_type

- Отмена изменений открытого типа сущности
        discard_entity_type

- Удалить тип сущности
        delete_entity_type <key>

- Показать все имеющиеся типы сущностей
        show_entity_types
        

# ---------------------------  References  ---------------------------

- Редактирование ссылки сущностей
        edit_reference <from_entity_type> <toReferenceKey>

- Поменять имя ссылки на другую сущность
        set_reference_to_key <toReferenceKey>

- Поменять имя ссылки от другой сущности
        set_reference_from_key <fromReferenceKey>

- Поменять флаги ссылки сущностей
        set_reference_flags [IsDeleteCascade], [IsRequired], [IsDraftMandatory]

- Поменять тип ссылки сущностей
        set_reference_type <type>

- Сохранить изменения ссылки сущностей
        save_reference

- Отменить изменения ссылки сущностей
        discard_reference

- Удалить существующую ссылку сущностей
        delete_reference <from_entity_type>, <toReferenceKey>

- Получить информацию о заведенных ссылках сущностей
        show_references

# ---------------------------  Entities  ---------------------------

- Создание новой сущности
        create_entity <entity_type>

- Редактирование cущности
        edit_entity <entity_id>

- Установка значения атрибута сущности
        set_entity_attribute_value <key> [<value>]

- Настроить связь между сущностями
        add_entity_reference_to <toReferenceKey>, <entity_id>

- Удалить связь между сущностями
        remove_entity_reference_to <toReferenceKey>, <entity_id>

- Сохранение изменений сущности
        save_entity [Drafted | Published]

- Отмена изменений сущности
        discard_entity

- Удаление сущности
        delete_entity <entity_id>

- Показать сущности
        show_entities [<entity_type>]

# ---------------------------  State Categories / State Machine  ---------------------------

- Создание новой категорий для состояний сущности
        add_entity_state_category <entity_state_category_key>

- Удаление категории для состояний сущности
        delete_entity_state_category <entity_state_category_id>

- Показать все категории для состояний сущности
        show_entity_state_categories

- Создание новой машины состояний
        create_state_machine <state_machine_key>

- Редактирование машины состояний
        edit_state_machine <state_machine_key>

- Добавление состояния в машине состояний
        add_sm_state <sm_state_key> <entity_state_category_key>

- Установить состояние в машине состояний
        set_sm_state <sm_state_key> <entity_state_category_key>

- Удалить состояние в машине состояний
        delete_sm_state <sm_state_key>

- Показать все состояния в машине состояний
        show_sm_states

- Добавление нового перехода состояний
        add_sm_transition [<fromStateKey>], <toStateKey>[, TransitEntity][, level1][ <space1>][ <role1>][, TransitEntity][, level2][ <space2>][ <role2>]...

- Удалить все переходы состояний в машине состояний
        delete_sm_transitions

- Показать переходы состояний в машине состояний
        show_sm_transitions

- Сохранение машины состояний
        save_state_machine

- Отмена изменений машины состояний
        discard_state_machine

- Удаление машины состояний
        delete_state_machine <state_machine_id>

- Показ всех машин состояний
        show_state_machines

# ---------------------------  Others  ---------------------------

- Выводит подсказку по конкретной команде или список доступных команд
        help [<command>]

- Сервисная опция использования старого API searcher
        use_legacy_searcher

- Инициализация генерируемого файла скрипта
        set_output_file <file> [continue]  # в batch режиме эта команда игнорируется

- Инициализация параметров лога
        set_log [<log_path>] [continue] [debug]

- Генерация readme файла
        generate_readme [<readme_path>]

- Опция игнорирования ошибок существования объектов. Если объект существует, то будет применена соответствующая команда редактирования.
                ignore_object_existence_error [False]
