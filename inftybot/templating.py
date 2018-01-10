# coding: utf-8
from jinja2 import Environment, PackageLoader, select_autoescape


def create_template_environment():
    return Environment(
        loader=PackageLoader('inftybot', 'templates'),
        autoescape=select_autoescape(['html', 'md'])
    )


template_environment = create_template_environment()


def render_template(template_name, context):
    template = template_environment.get_template(template_name)
    return template.render(**context)

