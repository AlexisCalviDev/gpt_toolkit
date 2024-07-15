class JSONSchemaBuilder:
    TYPE_STRING = "string"
    TYPE_INTEGER = "integer"
    TYPE_NUMBER = "number"
    TYPE_BOOLEAN = "boolean"
    TYPE_OBJECT = "object"
    TYPE_ARRAY = "array"

    @staticmethod
    def create_schema(structure):
        def build_schema(item):
            if isinstance(item, dict):
                return {
                    "type": JSONSchemaBuilder.TYPE_OBJECT,
                    "properties": {k: build_schema(v) for k, v in item.items()}
                }
            elif isinstance(item, list):
                return {
                    "type": JSONSchemaBuilder.TYPE_ARRAY,
                    "items": build_schema(item[0]) if item else {}
                }
            elif isinstance(item, str):
                return {"type": JSONSchemaBuilder.TYPE_STRING, "description": item}
            elif isinstance(item, int):
                return {"type": JSONSchemaBuilder.TYPE_INTEGER}
            elif isinstance(item, float):
                return {"type": JSONSchemaBuilder.TYPE_NUMBER}
            elif isinstance(item, bool):
                return {"type": JSONSchemaBuilder.TYPE_BOOLEAN}
            else:
                return {"type": JSONSchemaBuilder.TYPE_STRING}

        return build_schema(structure)
