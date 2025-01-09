import requests
import json
import uuid
import math
import datetime

default_password = "Qwerty123"


class RestAPIClient:
    def __init__(self):
        super().__init__()

        # default access_config
        self.access_config = {}

        self.last_response = None

        self.api_key = ""
        self.headers_standard = {
            "Content-Type": "application/json"
        }

        self.log_path = ""
        self.debug_log = False

    def __do_request(self, request_type, url, headers=None, data=None, files=None):

        response = None

        i = 0
        while i < 2:
            i += 1

            if self.debug_log:
                self.__print_and_log('')
                self.__print_and_log(f"---------------Request-------------------")
                self.__print_and_log(f"{request_type.upper()} {url}")
                self.__print_and_log(f"data = {data}")

            if request_type.lower() == 'post':
                response = requests.post(url, headers=headers, data=data, files=files)
            elif request_type.lower() == 'get':
                response = requests.get(url, headers=headers, data=data, files=files)
            elif request_type.lower() == 'put':
                response = requests.put(url, headers=headers, data=data, files=files)
            elif request_type.lower() == 'delete':
                response = requests.delete(url, headers=headers, data=data, files=files)
            elif request_type.lower() == 'patch':
                response = requests.patch(url, headers=headers, data=data, files=files)
            else:
                break

            if self.debug_log:
                self.__print_and_log(f"---------------Response------------------")
                self.__print_and_log(f"{response.text}")
                self.__print_and_log(f"-----------------------------------------")

            if response.status_code == 401 and i == 1:
                self.refresh_api_key()
                if headers:
                    if 'Authorization' in headers:
                        headers['Authorization'] = f"Bearer {self.api_key}"
            else:
                break

        return response

    def __print_and_log(self, string):
        if self.log_path not in (None, ''):
            with open(self.log_path, 'a', encoding="utf-8") as file:
                file.write(f"{datetime.datetime.now()}: " + string + f"\n")
        print(string)

    def get_user_token(self, base_url, user_email, password=None):
        # Get UserToken
        url = f"{base_url}/api/business/registry/v2/tokens"

        headers = {
            "Content-Type": "application/json",
        }

        if password is None:
            password = default_password

        data = {
            "login": user_email,
            "password": password
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Обработка ответа
        if response.status_code == 200:
            response_data = response.json()

            self.__print_and_log('')
            self.__print_and_log("UserToken: ")
            self.__print_and_log('---------------------------------------')
            self.__print_and_log(response_data['accessToken'])
            self.__print_and_log('')

            return response_data['accessToken']
        else:
            self.__print_and_log(f"Ошибка: {response.status_code}")
            self.__print_and_log(response.text)
            return None

    def get_business_user_token(self, base_url, business_email, business_id, password=None, with_context=True, get_user_token=True):

        if get_user_token:
            # Get UserToken
            user_token = self.get_user_token(base_url, business_email, password)

            if not user_token:
                return None
        else:
            user_token = self.api_key

            # Get BusinessUserToken
        url = f"{base_url}/api/business/registry/v2/tokens/trust"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {user_token}"  # Если требуется аутентификация
        }

        data = {
            "trustorId": business_id
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()

        # Обработка ответа
        if response.status_code == 200:
            self.__print_and_log('')
            self.__print_and_log("BusinessUserToken: ")
            self.__print_and_log('---------------------------------------')
            self.__print_and_log(response_data['accessToken'])
            self.__print_and_log('')
            business_user_token = response_data['accessToken']
        else:
            self.__print_and_log(f"Ошибка: {response.status_code}")
            self.__print_and_log(response.text)
            return None

        if with_context:
            # Get BusinessUserToken with context
            url = f"{base_url}/api/business/registry/{business_id}/v2/tokens/context"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {business_user_token}"
            }

            response = requests.post(url, headers=headers)
            response_data = response.json()

            # Обработка ответа
            if response.status_code == 200:
                self.__print_and_log("BusinessUserToken with context: ")
                self.__print_and_log('---------------------------------------')
                self.__print_and_log(response_data['accessToken'])
                self.__print_and_log('')
                return response_data['accessToken']
            else:
                self.__print_and_log(f"Ошибка: {response.status_code}")
                self.__print_and_log(response.text)
                return None
        else:
            return business_user_token

    def use_access_config(self, key):
        # загружаем access_configs из файла
        with open("access_configs.json") as input_file:
            try:
                access_configs = json.load(input_file)
            except json.decoder.JSONDecodeError as e:
                self.__print_and_log(f"Ошибка загрузки JSON access_configs.json:\n{e}")
                return False

        for access_config in access_configs:
            if access_config['key'].lower() == key.lower():
                self.access_config = access_config
                if 'baseUrl' not in self.access_config:
                    self.access_config['baseUrl'] = ''
                if 'service_path' not in self.access_config:
                    self.access_config['service_path'] = ''
                if 'businessId' not in self.access_config:
                    self.access_config['businessId'] = ''
                self.update_api_key()
                return True

        return False

    def refresh_api_key(self):
        if 'baseUrl' in self.access_config and self.access_config['baseUrl']:
            if 'password' in self.access_config:
                password = self.access_config['password']
            else:
                password = None
            if 'user_email' in self.access_config and self.access_config['user_email']:
                self.api_key = self.get_user_token(self.access_config['baseUrl'], self.access_config['user_email'], password)
            else:
                if 'business_email' in self.access_config and self.access_config['business_email'] and \
                        'businessId' in self.access_config and self.access_config['businessId']:
                    self.api_key = self.get_business_user_token(self.access_config['baseUrl'],
                                                                self.access_config['business_email'],
                                                                self.access_config['businessId'], password)
                else:
                    return

            self.access_config['api_key'] = self.api_key

            """
            # загружаем access_configs из файла
            with open("access_configs.json") as input_file:
                try:
                    access_configs = json.load(input_file)
                except json.decoder.JSONDecodeError as e:
                    self.__print_and_log(f"Ошибка загрузки JSON access_configs.json:\n{e}")
                    return

            new_access_configs = []
            for access_config in access_configs:
                if access_config['key'].lower() != self.access_config['key'].lower():
                    new_access_configs.append(access_config)
            new_access_configs.append(self.access_config)

            # записываем access_configs в файл
            with open("access_configs.json", "w") as outfile:
                json.dump(new_access_configs, outfile)            
            """

    def update_api_key(self):
        if 'api_key' in self.access_config and self.access_config['api_key']:
            self.api_key = self.access_config['api_key']
        else:
            self.refresh_api_key()

        self.headers_standard = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def put_tennant_settings(self, data):
        url = f"{self.access_config['baseUrl']}/api/admin/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/tenantSettings"

        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def reindex(self, parameters):
        url = f"{self.access_config['baseUrl']}/api/business/searcher/{self.access_config['businessId']}v0/index/reindex"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('post', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def raw_request_business(self, url_suffix, request_type, body, multipart, access_level='business'):
        url_suffix_ext = f"api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/{url_suffix}"
        return self.raw_request(url_suffix_ext, request_type, body, multipart)

    def raw_request(self, url_suffix_ext, request_type, body, multipart):
        url = f"{self.access_config['baseUrl']}/{url_suffix_ext}"

        if body is None:
            data = None
        else:
            data = json.dumps(body)

        if multipart:
            boundary = str(uuid.uuid4())  # Генерация уникального значения для границы
            headers_multipart = {
                "Authorization": f"Bearer {self.api_key}",  # Если требуется аутентификация
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            }
            form_data = f"--{boundary}\r\nContent-Disposition: form-data; name=\"Json\"\r\n\r\n{json.dumps(body)}\r\n--{boundary}--\r\n"
            headers = headers_multipart
            data = form_data.encode("utf-8")
        else:
            headers = self.headers_standard

        if request_type.lower() == 'post':
            response = self.__do_request('post', url, headers=headers, data=data)
        elif request_type.lower() == 'get':
            response = self.__do_request('get', url, headers=headers, data=data)
        elif request_type.lower() == 'put':
            response = self.__do_request('put', url, headers=headers, data=data)
        elif request_type.lower() == 'delete':
            response = self.__do_request('delete', url, headers=headers, data=data)
        elif request_type.lower() == 'patch':
            response = self.__do_request('patch', url, headers=headers, data=data)
        else:
            response = None

        self.last_response = response
        return response

    """ Organizations """

    def create_organization(self, data):
        url = f"{self.access_config['baseUrl']}/api/v0/registry/admin/organizations"

        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_organizations(self, parameters):
        url = f"{self.access_config['baseUrl']}/api/v0/registry/admin/organizations"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def delete_organization(self, organization_id):
        url = f"{self.access_config['baseUrl']}/api/v0/registry/admin/organizations/{organization_id}"

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    """ Users/BusinessUsers """

    def create_user(self, data):
        url = f"{self.access_config['baseUrl']}/api/v0/registry/admin/users"

        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_user(self, parameters):
        url = f"{self.access_config['baseUrl']}/api/v0/registry/admin/user"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def delete_user(self, user_id):
        url = f"{self.access_config['baseUrl']}/api/v0/registry/admin/users/{user_id}"

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def create_trusts(self, data):
        url = f"{self.access_config['baseUrl']}/api/v0/registry/admin/trusts"

        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_trustees(self, parameters):
        url = f"{self.access_config['baseUrl']}/api/v0/registry/trusts/trustees"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def set_password(self, data):
        url = f"{self.access_config['baseUrl']}/api/v0/registry/users/password"

        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    """ Schema """

    def import_schema(self, schema_path, parameters="", access_level='business'):
        # в случае протухания токена повторный запрос в __do_request не будет успешным
        # из-за закрытия open(schema_path, 'rb') в files
        # поэтому для проверки и актуализации токена нужен какой-то простой бизнесс запрос, например, get_entity_types
        self.get_entity_types()

        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/schema/import"
        if len(parameters) != 0:
            url += f"?{parameters}"

        headers_multipart = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": f"application/problem+json"
        }
        files = {
            'inputFile': ('schema.json;type=application/json', open(schema_path, 'rb'))
        }

        response = self.__do_request('post', url, headers=headers_multipart, files=files)

        self.last_response = response
        return response

    """ Businesses (Admin)"""

    def create_business(self, data, parameters=''):
        url = f"{self.access_config['baseUrl']}/api/admin/{self.access_config['service_path']}/v0/businesses"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_businesses(self, parameters=''):
        url = f"{self.access_config['baseUrl']}/api/admin/{self.access_config['service_path']}/v0/businesses"
        if len(parameters) != 0:
            url += f"?{parameters}"

        # response = self.__do_request('get', url, headers=self.headers_standard)
        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def delete_business(self, ids, parameters=''):
        url = f"{self.access_config['baseUrl']}/api/admin/{self.access_config['service_path']}/v0/businesses"

        query_prefix = '?'
        for businessId in ids:
            url += f"{query_prefix}id={businessId}"
            if query_prefix == '?':
                query_prefix = '&'

        if len(parameters) != 0:
            url += f"{query_prefix}{parameters}"

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def delete_business_searcher(self, business_id):
        # костыль для обхода https://jira.paragon-software.com/browse/MSOR-2213
        url = f"{self.access_config['baseUrl']}/api/admin/{self.access_config['service_path']}/v0/businesses/{business_id}"

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    """ BusinessPermissions (Admin)"""

    def create_business_permissions(self, data):
        url = f"{self.access_config['baseUrl']}/api/admin/{self.access_config['service_path']}/v0/businesses/{self.access_config['businessId']}/permissions"

        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_business_permissions(self):
        url = f"{self.access_config['baseUrl']}/api/admin/{self.access_config['service_path']}/v0/businesses/{self.access_config['businessId']}/permissions"

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def put_business_permissions(self, data):
        url = f"{self.access_config['baseUrl']}/api/admin/{self.access_config['service_path']}/v0/businesses/{self.access_config['businessId']}/permissions"

        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def delete_business_permissions(self, ids):
        url = f"{self.access_config['baseUrl']}/api/admin/{self.access_config['service_path']}/v0/businesses/{self.access_config['businessId']}/permissions"
        query_prefix = '?'
        for permissions_id in ids:
            url += f"{query_prefix}id={permissions_id}"
            if query_prefix == '?':
                query_prefix = '&'

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    """ Entity State Categories """

    def create_entity_state_categories(self, data):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityStateCategories"
        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_entity_state_categories(self, parameters=''):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityStateCategories"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def delete_entity_state_categories(self, ids):
        if not ids:
            self.last_response = ""
            return

        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityStateCategories"
        query_prefix = '?'
        for state_machines_id in ids:
            url += f"{query_prefix}id={state_machines_id}"
            if query_prefix == '?':
                query_prefix = '&'

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    """ State Machines """

    def create_state_machines(self, data):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityStateMachines"
        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def put_state_machines(self, data):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityStateMachines"
        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_state_machines(self, parameters=''):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityStateMachines"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def delete_state_machines(self, ids):
        if not ids:
            self.last_response = ""
            return

        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityStateMachines"
        query_prefix = '?'
        for state_machines_id in ids:
            url += f"{query_prefix}id={state_machines_id}"
            if query_prefix == '?':
                query_prefix = '&'

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    """ References """

    def create_reference(self, data, access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypeReferences"
        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_references(self,
                       from_references_keys=None,
                       to_references_keys=None,
                       from_entity_type_key=None,
                       access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypeReferences"

        query_prefix = '?'
        if from_references_keys is not None:
            for from_reference in from_references_keys:
                url += f"{query_prefix}fromReferenceKey={from_reference}"
                if query_prefix == '?':
                    query_prefix = '&'

        if to_references_keys is not None:
            for to_reference in to_references_keys:
                url += f"{query_prefix}toReferenceKey={to_reference}"
                if query_prefix == '?':
                    query_prefix = '&'

        if from_entity_type_key is not None:
            url += f"{query_prefix}fromEntityTypeKey={from_entity_type_key}"

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def put_references(self, data, access_level='business'):
        if not data:
            self.last_response = ""
            return

        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypeReferences"

        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def delete_references(self, ids, access_level='business'):
        if not ids:
            self.last_response = ""
            return

        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypeReferences"
        query_prefix = '?'
        for referenceId in ids:
            url += f"{query_prefix}id={referenceId}"
            if query_prefix == '?':
                query_prefix = '&'

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    """ Entity Types """

    def create_entity_type(self, data, access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypes"
        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_entity_types(self, parameters='', access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypes"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def put_entity_type(self, data, access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypes"
        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def delete_entity_type(self, entity_type_id, access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypes?id={entity_type_id}"
        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def get_entity_type_schema(self, data):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities/query/schema"
        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    """ Permissions """

    def create_entity_type_permissions(self, entity_type_id, data, access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypes/{entity_type_id}/permissions"
        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_entity_type_permissions(self, entity_type_id, parameters='', access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypes/{entity_type_id}/permissions"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def put_entity_type_permissions(self, entity_type_id, data, access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypes/{entity_type_id}/permissions"

        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def delete_entity_type_permissions(self, entity_type_id, ids, access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entityTypes/{entity_type_id}/permissions"
        query_prefix = '?'
        for id in ids:
            url += f'{query_prefix}id={id}'
            if query_prefix == '?':
                query_prefix = '&'

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    """ Attributes """

    def create_attribute(self, data):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/attributes"
        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_attributes(self, parameters):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/attributes?{parameters}"
        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def put_attributes(self, data):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/attributes"
        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def delete_attribute(self, attribute_id):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/attributes?id={attribute_id}"
        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    """ Entities """

    def create_entity(self, new_entity_data, parameters="", access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities?{parameters}"
        boundary = str(uuid.uuid4())  # Генерация уникального значения для границы
        headers_multipart = {
            "Authorization": f"Bearer {self.api_key}",  # Если требуется аутентификация
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }

        form_data = f"--{boundary}\r\nContent-Disposition: form-data; name=\"Json\"\r\n\r\n{json.dumps(new_entity_data)}\r\n--{boundary}--\r\n"
        response = self.__do_request('post', url, headers=headers_multipart, data=form_data.encode("utf-8"))

        self.last_response = response
        return response

    def put_entities_state_transit(self, data):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities/stateTransit"
        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def put_entities_workflow_transit(self, data):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities/workflows/transit"
        response = self.__do_request('put', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_entities_vector(self, data, skip_entities=0, access_level='business'):
        url = f"{self.access_config['baseUrl']}/api/{access_level}/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities/query/vector?Skip={skip_entities}"
        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_all_entities_vector(self, vector_data, vector_count_data):
        # общее количество Entities
        response = self.get_entities_vector_count(vector_count_data)
        if response.status_code != 200:
            self.last_response = response
            return response

        count = int(response.text)
        iterations = math.ceil(count / 100)

        entities = []

        for i in range(iterations):
            skip_entities = i * 100
            response = self.get_entities_vector(vector_data, skip_entities)

            if response.status_code != 200:
                self.last_response = response
                return response

            entities.extend(response.json())

        self.last_response = entities
        return entities  # в случае успеха возвращается json со всеми entities, status_code отсутствует

    def get_entities_vector_count(self, data):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities/query/vector/count"
        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response

    def get_entities(self, parameters=None):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities"

        if (parameters is not None) and (len(parameters) != 0):
            url += f'?{parameters}'

        response = self.__do_request('get', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def put_entities(self, data, parameters=""):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities?{parameters}"
        boundary = str(uuid.uuid4())  # Генерация уникального значения для границы
        headers_multipart = {
            "Authorization": f"Bearer {self.api_key}",  # Если требуется аутентификация
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
        form_data = f"--{boundary}\r\nContent-Disposition: form-data; name=\"Json\"\r\n\r\n{json.dumps(data)}\r\n--{boundary}--\r\n"
        response = self.__do_request('put', url, headers=headers_multipart, data=form_data.encode("utf-8"))

        self.last_response = response
        return response

    def delete_entity(self, ids):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities"

        query_prefix = '?'
        for entity_id in ids:
            url += f'{query_prefix}id={entity_id}'
            if query_prefix == '?':
                query_prefix = '&'

        response = self.__do_request('delete', url, headers=self.headers_standard)

        self.last_response = response
        return response

    def create_entities_task(self, data, parameters):
        url = f"{self.access_config['baseUrl']}/api/business/{self.access_config['service_path']}/{self.access_config['businessId']}/v0/entities/task"
        if len(parameters) != 0:
            url += f"?{parameters}"

        response = self.__do_request('post', url, headers=self.headers_standard, data=json.dumps(data))

        self.last_response = response
        return response
