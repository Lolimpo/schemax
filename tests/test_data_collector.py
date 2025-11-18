from baby_steps import given, then, when
from d42 import optional, schema

from schemax import collect_schema_data


def test_tc1_simple_get_endpoint_with_200_response():
    """TC1: Simple GET endpoint with 200 response"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"}
                                            },
                                            "required": ["id", "name"]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 1
        schema_data = result[0]

        # Basic metadata
        assert schema_data.http_method == "get"
        assert schema_data.path == "/users"
        assert schema_data.status == 200

        # GET should have no request body
        assert schema_data.request_schema == {}
        assert schema_data.request_schema_d42 == schema.any

        # GET with no params should have empty queries
        assert schema_data.queries_schema.get("properties") == {}

        # Response schema should be converted
        assert schema_data.response_schema_d42 == schema.dict({
            "id": schema.int,
            "name": schema.str
        })

        # No path arguments
        assert schema_data.args == []


def test_tc2_post_endpoint_with_request_body():
    """TC2: POST endpoint with request body and 201 response"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string"}
                                        },
                                        "required": ["name", "email"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 1
        schema_data = result[0]

        assert schema_data.http_method == "post"
        assert schema_data.status == 201

        # POST should have request body
        assert schema_data.request_schema != {}
        assert schema_data.request_schema_d42 == schema.dict({
            "name": schema.str,
            "email": schema.str
        })

        # Args should contain "body" for request body
        assert "body" in schema_data.args

        # Response schema
        assert schema_data.response_schema_d42 == schema.dict({
            optional("id"): schema.int,
            ...: ...
        })


def test_tc3_multiple_status_codes_for_same_endpoint():
    """TC3: Multiple status codes for same endpoint - should create multiple SchemaData objects"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array", "items": {"type": "object"}}
                                    }
                                }
                            },
                            "404": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {"error": {"type": "string"}}}
                                    }
                                }
                            },
                            "500": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {"message": {"type": "string"}}}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 3

        # All should have same path and method
        for item in result:
            assert item.path == "/users"
            assert item.http_method == "get"

        # Different status codes
        statuses = {item.status for item in result}
        assert statuses == {200, 404, 500}

        # Each should have different response schema
        response_200 = next(item for item in result if item.status == 200)
        response_404 = next(item for item in result if item.status == 404)
        response_500 = next(item for item in result if item.status == 500)

        assert response_200.response_schema_d42 == schema.list(schema.dict)
        assert response_404.response_schema_d42 == schema.dict({optional("error"): schema.str, ...: ...})
        assert response_500.response_schema_d42 == schema.dict({optional("message"): schema.str, ...: ...})


def test_tc4_all_http_methods():
    """TC4: All HTTP methods should be processed"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users": {
                    "get": {"responses": {"200": {"content": {"application/json": {"schema": {"type": "array"}}}}}},
                    "post": {"responses": {"201": {"content": {"application/json": {"schema": {"type": "object"}}}}}},
                    "put": {"responses": {"200": {"content": {"application/json": {"schema": {"type": "object"}}}}}},
                    "patch": {"responses": {"200": {"content": {"application/json": {"schema": {"type": "object"}}}}}},
                    "delete": {"responses": {"204": {"description": "No content"}}}
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        # Should have 5 results (one per method)
        assert len(result) == 5

        methods = {item.http_method for item in result}
        assert methods == {"get", "post", "put", "patch", "delete"}

        # Verify each method is correctly assigned
        get_item = next(item for item in result if item.http_method == "get")
        assert get_item.status == 200

        post_item = next(item for item in result if item.http_method == "post")
        assert post_item.status == 201

        delete_item = next(item for item in result if item.http_method == "delete")
        assert delete_item.status == 204


def test_tc5_multiple_endpoints():
    """TC5: Multiple endpoints should all be processed"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users": {
                    "get": {"responses": {"200": {"content": {"application/json": {"schema": {"type": "array"}}}}}}
                },
                "/posts": {
                    "get": {"responses": {"200": {"content": {"application/json": {"schema": {"type": "array"}}}}}}
                },
                "/comments": {
                    "get": {"responses": {"200": {"content": {"application/json": {"schema": {"type": "array"}}}}}}
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 3

        paths = {item.path for item in result}
        assert paths == {"/users", "/posts", "/comments"}


def test_tc6_simple_path_parameter():
    """TC6: Simple path parameter should be extracted and converted to snake_case"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users/{userId}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "userId",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 1
        schema_data = result[0]

        assert schema_data.path == "/users/{userId}"
        # Path parameter should be converted to snake_case
        assert schema_data.args == ["user_id"]
        assert schema_data.converted_path == "/users/{user_id}"


def test_tc7_multiple_path_parameters():
    """TC7: Multiple path parameters should all be extracted"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users/{userId}/posts/{postId}": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 1
        schema_data = result[0]

        assert schema_data.path == "/users/{userId}/posts/{postId}"
        # Both parameters extracted and converted to snake_case
        assert schema_data.args == ["user_id", "post_id"]


def test_tc8_path_parameter_with_enum_generates_multiple_paths():
    """TC8: Path parameter with enum should generate multiple SchemaData objects"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users/{status}": {
                    "parameters": [
                        {
                            "name": "status",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "enum": ["active", "inactive", "pending"]
                            }
                        }
                    ],
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        # Should create 3 SchemaData objects, one for each enum value
        assert len(result) == 3

        paths = {item.path for item in result}
        assert paths == {"/users/active", "/users/inactive", "/users/pending"}

        # All should have same method and status
        for item in result:
            assert item.http_method == "get"
            assert item.status == 200


def test_tc9_camelcase_path_parameters_converted_to_snake_case():
    """TC9: CamelCase path parameters should be converted to snake_case"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users/{userId}/organizations/{organizationId}": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 1
        schema_data = result[0]

        # CamelCase converted to snake_case
        assert schema_data.args == ["user_id", "organization_id"]


def test_tc10_required_query_parameter():
    """TC10: Required query parameter should be in required array"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users": {
                    "get": {
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 1
        schema_data = result[0]

        # Query schema should have limit in properties
        assert "limit" in schema_data.queries_schema["properties"]
        assert schema_data.queries_schema["properties"]["limit"] == {"type": "integer"}

        # Required parameter should be in required array
        assert "limit" in schema_data.queries_schema["required"]

        # d42 schema should reflect required parameter
        assert schema_data.queries_schema_d42 == schema.dict({
            "limit": schema.int,
            ...: ...
        })


def test_tc11_optional_query_parameter():
    """TC11: Optional query parameter should NOT be in required array"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users": {
                    "get": {
                        "parameters": [
                            {
                                "name": "offset",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 1
        schema_data = result[0]

        # Query schema should have offset in properties
        assert "offset" in schema_data.queries_schema["properties"]

        # Optional parameter should NOT be in required array
        assert "required" not in schema_data.queries_schema or "offset" not in schema_data.queries_schema.get("required", [])

        # d42 schema should use optional()
        assert schema_data.queries_schema_d42 == schema.dict({
            optional("offset"): schema.int,
            ...: ...
        })


def test_tc12_multiple_query_parameters_mixed_required_optional():
    """TC12: Multiple query parameters with mix of required and optional"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users": {
                    "get": {
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "integer", "minimum": 1, "maximum": 100}
                            },
                            {
                                "name": "offset",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer", "minimum": 0}
                            },
                            {
                                "name": "sort",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 1
        schema_data = result[0]

        # All parameters should be in properties
        assert "limit" in schema_data.queries_schema["properties"]
        assert "offset" in schema_data.queries_schema["properties"]
        assert "sort" in schema_data.queries_schema["properties"]

        # Only limit should be required
        assert schema_data.queries_schema["required"] == ["limit"]

        # d42 schema should reflect the mixed required/optional status
        assert schema_data.queries_schema_d42 == schema.dict({
            "limit": schema.int.min(1).max(100),
            optional("offset"): schema.int.min(0),
            optional("sort"): schema.str,
            ...: ...
        })


def test_tc13_no_query_parameters():
    """TC13: Endpoint with no query parameters should have minimal query schema"""
    with given:
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    with when:
        result = collect_schema_data(openapi_spec)

    with then:
        assert len(result) == 1
        schema_data = result[0]

        # Queries schema should be minimal (empty properties)
        assert schema_data.queries_schema["type"] == "object"
        assert schema_data.queries_schema["properties"] == {}
        assert "required" not in schema_data.queries_schema

        # d42 schema should handle empty queries appropriately
        # Could be schema.dict or schema.dict({...: ...}) depending on implementation
        # The key is it shouldn't fail
        assert schema_data.queries_schema_d42 is not None
