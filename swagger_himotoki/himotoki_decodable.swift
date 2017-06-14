//  {{ definition.class_name }}.swift

import Foundation
import Himotoki

struct {{ definition.class_name }}: Decodable {
    {%- for enum in definition.enums %}
    public enum {{ enum.enum_name }}: {{ enum.enum_type | swift_type('') }} {
        {%- for enum_key, enum_value in enum.enum_dict.items() %}
        case {{ enum_key }} = "{{ enum_value }}"
        {%- endfor %}
    }
    {%- endfor %}
    {% for property in definition.properties %}
    let {{ property.key_name | camelize }}: {% if property.is_array -%} [ {%- endif -%}
        {{  property.property_type | swift_type(property.class_name_ref) }}
        {%- if property.is_array -%} ] {%- endif %}
    {%- endfor %}

    static func decode(_ ext: Extractor) throws -> {{ definition.class_name }} {
        return try {{ definition.class_name }}(
            {%- for property in definition.properties %}
            {{ property.key_name | camelize }}: {# -#}
            {%- if property.is_enum -%} {{ property.class_name_ref }}(rawValue: {% endif -%}
            ext {{  property.is_required | himotoki_extraction(property.is_array) | safe }} "{{ property.key_name }}" {#- -#}
            {%- if property.is_enum -%} ) {%- if property.is_required -%} ! {%- endif -%} {%- endif -%}
            {%- if not loop.last -%} , {%- endif %}
            {%- endfor %}
        )
    }
}