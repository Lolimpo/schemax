import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, Template


class Generator(ABC):
    @abstractmethod
    def _get_template(self, template_name: str) -> Template:
        pass

    def _create_dir(self, dir_name: str) -> None:
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

    def _create_package(self, dir_name: str) -> None:
        self._create_dir(dir_name=dir_name)
        init_file_path = f'{dir_name}/__init__.py'
        if not os.path.exists(init_file_path):
            Path(init_file_path).touch()

    def _generate_by_template(self, file_path: str, template_name: str, **kwargs: Any) -> None:
        if not os.path.exists(file_path):
            template = self._get_template(template_name=template_name)
            with open(file_path, 'w') as file:
                file.write(template.render(**kwargs))


class MainGenerator(Generator):
    __PATH_TEMPLATES = os.path.dirname(os.path.realpath(__file__)) + '/templates'
    __TEMPLATE_SCHEMAS = 'schemas.py.j2'
    __TEMPLATE_SCHEMA_DEFINITION = 'schema_definition.py.j2'
    __TEMPLATE_INTERFACES = 'interfaces.py.j2'
    __TEMPLATE_API_ROUTE = 'api_route.py.j2'

    __DIRECTORY_SCHEMAS = 'schemas'
    __DIRECTORY_INTERFACES = 'interfaces'

    __FILE_API_INTERFACE = 'api.py'
    __FILE_RESPONSE_SCHEMAS = 'response_schemas.py'
    __FILE_REQUEST_SCHEMAS = 'request_schemas.py'

    def __init__(self, schema_data: List[Dict[str, Any]]):
        super().__init__()
        self.schema_data = schema_data
        self.__templates = Environment(loader=FileSystemLoader(self.__PATH_TEMPLATES))

    def response_schemas(self) -> None:
        self._create_package(self.__DIRECTORY_SCHEMAS)
        self._generate_by_template(
            file_path=f'{self.__DIRECTORY_SCHEMAS}/{self.__FILE_RESPONSE_SCHEMAS}',
            template_name=self.__TEMPLATE_SCHEMAS)

        with open(f'{self.__DIRECTORY_SCHEMAS}/{self.__FILE_RESPONSE_SCHEMAS}', 'a') as file:
            for data_item in self.schema_data:
                template = self._get_template(self.__TEMPLATE_SCHEMA_DEFINITION)
                file.write(
                    template.render(
                        schema_name=f'{data_item["interface_method"]}' + "ResponseSchema",
                        schema_definition=data_item["response_schema"]
                    )
                )

    def request_schemas(self) -> None:
        self._create_package(self.__DIRECTORY_SCHEMAS)
        self._generate_by_template(
            file_path=f'{self.__DIRECTORY_SCHEMAS}/{self.__FILE_REQUEST_SCHEMAS}',
            template_name=self.__TEMPLATE_SCHEMAS)

        with open(f'{self.__DIRECTORY_SCHEMAS}/{self.__FILE_REQUEST_SCHEMAS}', 'a') as file:
            for data_item in self.schema_data:
                if data_item["request_schema"] != "schema.any":
                    template = self._get_template(self.__TEMPLATE_SCHEMA_DEFINITION)
                    file.write(
                        template.render(
                            schema_name=f'{data_item["interface_method"]}' + "RequestSchema",
                            schema_definition=data_item["request_schema"]
                        )
                    )

    def interfaces(self) -> None:
        self._create_package(self.__DIRECTORY_INTERFACES)
        self._generate_by_template(
            file_path=f"{self.__DIRECTORY_INTERFACES}/{self.__FILE_API_INTERFACE}",
            template_name=self.__TEMPLATE_INTERFACES
        )

        with open(f"{self.__DIRECTORY_INTERFACES}/{self.__FILE_API_INTERFACE}", "a") as file:
            for data_item in self.schema_data:
                template = self._get_template(self.__TEMPLATE_API_ROUTE)
                file.write(
                    template.render(
                        interface_method=data_item["interface_method"],
                        http_method=data_item["http_method"].upper(),
                        path=data_item["path"],
                        args=data_item["args"]
                    )
                )

    def all(self) -> None:
        self.request_schemas()
        self.response_schemas()
        self.interfaces()

    def _get_template(self, template_name: str) -> Template:
        return self.__templates.get_template(name=template_name)
