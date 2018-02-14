# coding: utf-8
from jinja2 import Environment, PackageLoader, select_autoescape

from inftybot import config


def create_template_environment():
    extensions = config.JINJA_EXTENSIONS or tuple()

    return Environment(
        loader=PackageLoader('inftybot', 'templates'),
        autoescape=select_autoescape(['html', 'md']),
        extensions=extensions
    )


template_environment = create_template_environment()


def render_template(template_name, context):
    template = template_environment.get_template(template_name)
    return template.render(**context)
