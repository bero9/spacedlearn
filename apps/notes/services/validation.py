class NoteValidationError(Exception):
    pass


class NoteValidator:

    SUPPORTED_TYPES = {
        "text": str,
        "number": (int, float),
        "boolean": bool,
    }

    def __init__(self, note_type):
        self.note_type = note_type

    def validate(self, fields):
        schema_fields = self.note_type.fields_schema.get("fields", [])

        errors = {}

        schema_by_name = {
            field["name"]: field
            for field in schema_fields
        }

        # 1. Check required fields
        for field_name, field_definition in schema_by_name.items():
            if field_definition.get("required", False):
                if field_name not in fields:
                    errors[field_name] = "This field is required."

        # 2. Check unknown fields
        for field_name in fields:
            if field_name not in schema_by_name:
                errors[field_name] = "Unknown field."

        # 3. Check field types
        for field_name, value in fields.items():
            if field_name not in schema_by_name:
                continue

            field_definition = schema_by_name[field_name]
            expected_type = field_definition.get("type")

            python_type = self.SUPPORTED_TYPES.get(expected_type)

            if python_type is None:
                errors[field_name] = (
                    f"Unsupported field type: {expected_type}"
                )
                continue

            if not isinstance(value, python_type):
                errors[field_name] = (
                    f"Expected type '{expected_type}'."
                )

        if errors:
            raise NoteValidationError(errors)

        return True