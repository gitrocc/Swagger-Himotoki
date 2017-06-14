# -*- coding: utf-8 -*-

import sys
import os
import yaml
from jinja2 import Environment, FileSystemLoader

reserved_word_dict = {
    'self': '_self', 
}

swift_type_dict = {
    'integer': 'Int', 
    'number': 'Float', 
    'string': 'String', 
    'boolean': 'Bool', 

    'int32': 'Int', 
    'int64': 'Int64', 
    'float': 'Float', 
    'double': 'Double', 
    'byte': 'String', 
    'binary': 'String', 
    'date': 'Date', 
    'date-time': 'Date', 
    'password': 'String', 
}

def camelize(snake_str):
    while snake_str[0] == '_':
        snake_str = snake_str[1:]
    splits = snake_str.split('_')
    return splits[0] + ''.join(x.title() for x in splits[1:])

def pascalize(snake_str, prefix=''):
    prefix = prefix.title() if prefix.islower() else prefix
    snake_str = snake_str.title() if snake_str.islower() else snake_str
    return (prefix + snake_str).replace('_', '')

def swift_type(property_type, class_name_ref):
    if class_name_ref:
        return class_name_ref
    elif property_type in swift_type_dict:
        return swift_type_dict[property_type]
    return 'Any?'

def himotoki_extraction(is_required, is_array):
    if is_array:
        if is_required:
            return '<||'
        return '<||?'
    if is_required:
        return '<|'
    return '<|?'

def safe_reserved_word(keyword):
    if keyword in reserved_word_dict:
        return reserved_word_dict[keyword]
    return keyword

class DefinitionVO(object):
    class_name = ''
    properties = []
    enums = []

    def __init__(self, class_name='', properties=[], enums=[]):
        self.class_name = class_name
        self.properties = properties
        self.enums = enums

class EnumVO(object):
    enum_name = ''
    enum_type = ''
    enum_dict = {}

    def __init__(self, enum_name='', enum_type='', enum_dict=''):
        self.enum_name = enum_name
        self.enum_type = enum_type
        self.enum_dict = enum_dict

class PropertyVO(object):
    key_name = ''
    class_name_ref = None
    property_type = ''
    property_format = ''
    is_required = False
    is_array = False
    is_enum = False

    def __init__(self, key_name='', class_name_ref=None, 
            property_type='', property_format='', 
            is_required=False, is_array=False, is_enum=False):
        self.key_name = key_name
        self.class_name_ref = class_name_ref
        self.property_type = property_type
        self.property_format = property_format
        self.is_required = is_required
        self.is_array = is_array
        self.is_enum = is_enum

class SwaggerHimotoki(object):

    jinja_env = None

    yml_definitions = {}
    prefix = ''
    definitions = []

    output_dir = 'SwaggerHimotoki'

    @classmethod
    def load_args(cls, yml, prefix=''):
        try:
            yml_dict = yaml.load(yml)
            cls.yml_definitions = yml_dict['definitions']
            if prefix:
                cls.prefix = prefix.upper()
            cls.decode_definitions()
        except Exception as e:
            print e
        return cls

    @classmethod
    def decode_definitions(cls):
        for class_name in cls.yml_definitions.keys():
            class_obj = cls.yml_definitions[class_name]
            cls.decode_definition(class_name, class_obj)

    @classmethod
    def decode_definition(cls, class_name, obj, parent_class_name=''):
        if not 'properties' in obj:
            return []
        definition_class_name = cls.prefix + pascalize(class_name, prefix=parent_class_name)
        dif_properties = []
        dif_enums = []

        required_props = obj['required'] if 'required' in obj else []
        properties = obj['properties'] if 'properties' in obj else []
        for prop_key in properties.keys():
            is_required = False
            is_array = False
            is_enum = False

            keys = properties[prop_key].keys()
            prop_obj = properties[prop_key]['items'] if 'items' in keys else properties[prop_key]
            meta_keys = prop_obj.keys()

            property_type = prop_obj['type'] if 'type' in meta_keys else ''
            property_format = prop_obj['format'] if 'format' in meta_keys else property_type
            class_name_ref = cls.prefix + cls.get_ref_class_name(prop_obj['$ref']) if '$ref' in meta_keys else None

            if prop_key in required_props:
                is_required = True
            if 'items' in keys:
                is_array = True
            if 'properties' in meta_keys:
                _parent_class_name = parent_class_name if parent_class_name else class_name
                definition_vo = cls.decode_definition(prop_key, prop_obj, parent_class_name=_parent_class_name)
                class_name_ref = definition_vo.class_name
            if 'enum' in meta_keys:
                enum_vo = cls.make_enum_vo(prop_key, property_type, prop_obj['enum'])
                dif_enums.append(enum_vo)
                class_name_ref = enum_vo.enum_name
                is_enum = True

            property_vo = PropertyVO(
                key_name=prop_key, class_name_ref=class_name_ref, 
                property_type=property_type, property_format=property_format, 
                is_required=is_required, is_array=is_array, is_enum=is_enum
            )
            dif_properties.append(property_vo)

        definition_vo = DefinitionVO(class_name=definition_class_name, properties=dif_properties, enums=dif_enums)
        cls.add_definition(definition_vo)

        return definition_vo

    @classmethod
    def add_definition(cls, definition_vo):
        exist = False
        for definition in cls.definitions:
            if definition.class_name == definition_vo.class_name:
                print 'Error conflict Decodable Class Name', definition_vo.class_name
                exist = True
        if not exist:
            cls.definitions.append(definition_vo)

    @classmethod
    def get_ref_class_name(cls, ref_key):
        return ref_key.split('/')[-1]

    @classmethod
    def make_enum_vo(cls, enum_key, enum_type, enums):
        enum_name = pascalize(enum_key)
        enum_dict = {}
        for enum in enums:
            _enum = enum['value'] if type(enum) == dict else enum
            _enum_key = camelize(_enum.lower())
            enum_dict[_enum_key] = _enum
        return EnumVO(enum_name=enum_name, enum_type=enum_type, enum_dict=enum_dict)

    @classmethod
    def init_jinja_env_if_needed(cls):
        if cls.jinja_env:
            return
        current_path = os.path.abspath(os.path.dirname(__file__))
        cls.jinja_env = Environment(loader=FileSystemLoader(current_path, encoding='utf8'), autoescape=True)
        cls.jinja_env.filters['camelize'] = camelize
        cls.jinja_env.filters['pascalize'] = pascalize
        cls.jinja_env.filters['swift_type'] = swift_type
        cls.jinja_env.filters['himotoki_extraction'] = himotoki_extraction
        cls.jinja_env.filters['safe_reserved_word'] = safe_reserved_word

    @classmethod
    def get_rendered_source(cls, template_path, **args):
        cls.init_jinja_env_if_needed()
        return cls.jinja_env.get_template(template_path).render(args)

    @classmethod
    def add_file(cls, file_name, file_content):
        if not os.path.exists(cls.output_dir):
            os.mkdir(cls.output_dir)
        file_path = '%s/%s' % (cls.output_dir, file_name)
        f = open(file_path, 'w')
        f.write(file_content)
        f.close()

    @classmethod
    def export_himotoki(cls):
        for definition in cls.definitions:
            source = cls.get_rendered_source('himotoki_decodable.swift', definition=definition)
            cls.add_file(definition.class_name+'.swift', source)
