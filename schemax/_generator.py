import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional

from d42 import schema
from jinja2 import Environment, FileSystemLoader, Template

from ._data_collector import SchemaData


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

    def _append_string(self, lst: List[str], suffix: str) -> List[str]:
        return [f'{suffix}.{item}' for item in lst]


class MainGenerator(Generator):
    __PATH_TEMPLATES = os.path.dirname(os.path.realpath(__file__)) + '/templates'
    __TEMPLATE_SCHEMAS = 'schemas.py.j2'
    __TEMPLATE_SCHEMA_DEFINITION = 'schema_definition.py.j2'
    __TEMPLATE_INTERFACES = 'interfaces.py.j2'
    __TEMPLATE_API_ROUTE = 'api_route.py.j2'
    __TEMPLATE_SCENARIO = 'scenario.py.j2'

    __DIRECTORY_SCHEMAS = 'schemas'
    __DIRECTORY_INTERFACES = 'interfaces'
    __DIRECTORY_SCENARIOS = 'scenarios'

    __FILE_API_INTERFACE = 'api.py'
    __FILE_RESPONSE_SCHEMAS = 'response_schemas.py'
    __FILE_REQUEST_SCHEMAS = 'request_schemas.py'

    def __init__(
        self, schema_data: List[SchemaData], base_url: Optional[str] = None, humanize: bool = False
    ):
        super().__init__()
        self.schema_data = schema_data
        self.__templates = Environment(loader=FileSystemLoader(self.__PATH_TEMPLATES))
        self.__templates.filters['append_str'] = self._append_string
        self.base_url = base_url
        self.humanize = humanize

    def response_schemas(self) -> None:
        self._create_package(self.__DIRECTORY_SCHEMAS)
        self._generate_by_template(
            file_path=f'{self.__DIRECTORY_SCHEMAS}/{self.__FILE_RESPONSE_SCHEMAS}',
            template_name=self.__TEMPLATE_SCHEMAS)

        with open(f'{self.__DIRECTORY_SCHEMAS}/{self.__FILE_RESPONSE_SCHEMAS}', 'a') as file:
            for data_item in self.schema_data:
                if data_item.status == 200:
                    template = self._get_template(self.__TEMPLATE_SCHEMA_DEFINITION)
                    schema_name = data_item.schema_prefix_humanized \
                        if self.humanize else data_item.schema_prefix
                    file.write(
                        template.render(
                            schema_name=f'{schema_name}' + 'ResponseSchema',
                            schema_definition=data_item.response_schema_d42
                        )
                    )

    def request_schemas(self) -> None:
        self._create_package(self.__DIRECTORY_SCHEMAS)
        self._generate_by_template(
            file_path=f'{self.__DIRECTORY_SCHEMAS}/{self.__FILE_REQUEST_SCHEMAS}',
            template_name=self.__TEMPLATE_SCHEMAS)

        with open(f'{self.__DIRECTORY_SCHEMAS}/{self.__FILE_REQUEST_SCHEMAS}', 'a') as file:
            for data_item in self.schema_data:
                if data_item.request_schema != schema.any:
                    template = self._get_template(self.__TEMPLATE_SCHEMA_DEFINITION)
                    schema_name = data_item.schema_prefix_humanized \
                        if self.humanize else data_item.schema_prefix
                    file.write(
                        template.render(
                            schema_name=f'{schema_name}' + 'RequestSchema',
                            schema_definition=data_item.request_schema_d42
                        )
                    )

    def interfaces(self) -> None:
        self._create_package(self.__DIRECTORY_INTERFACES)
        self._generate_by_template(
            file_path=f'{self.__DIRECTORY_INTERFACES}/{self.__FILE_API_INTERFACE}',
            template_name=self.__TEMPLATE_INTERFACES,
            base_url=self.base_url
        )

        with open(f'{self.__DIRECTORY_INTERFACES}/{self.__FILE_API_INTERFACE}', 'a') as file:
            for data_item in self.schema_data:
                if data_item.status == 200:
                    template = self._get_template(self.__TEMPLATE_API_ROUTE)
                    file.write(
                        template.render(
                            interface_method=(
                                data_item.interface_method_humanized.lower()
                                if self.humanize
                                else data_item.interface_method
                            ),
                            http_method=data_item.http_method.upper(),
                            path=data_item.path,
                            args=data_item.args,
                            request_schema=(
                                data_item.request_schema_d42
                                if data_item.request_schema != schema.any
                                else None
                            )
                        )
                    )

    def scenarios(self) -> None:
        self._create_package(self.__DIRECTORY_SCENARIOS)
        for data_item in self.schema_data:
            self._generate_by_template(
                file_path=f'{self.__DIRECTORY_SCENARIOS}/{data_item.interface_method}.py',
                template_name=self.__TEMPLATE_SCENARIO,
                subject=data_item.interface_method.split('_'),
                interface_method=(
                    data_item.interface_method_humanized.lower()
                    if self.humanize
                    else data_item.interface_method
                ),
                args=data_item.args,
                response_schema=data_item.schema_prefix + 'ResponseSchema',
                request_schema=(
                    data_item.schema_prefix + 'RequestSchema'
                    if data_item.request_schema != schema.any
                    else None
                )
            )

    def all(self) -> None:
        self.request_schemas()
        self.response_schemas()
        self.interfaces()
        self.scenarios()

    def _get_template(self, template_name: str) -> Template:
        return self.__templates.get_template(name=template_name)
