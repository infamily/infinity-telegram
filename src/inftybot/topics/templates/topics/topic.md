{% load langsplit_tags %}

{% if object.categories_names %}
`Categories:` {{object.categories_names|join:','}}
{% endif %}

`{{object.get_type_display}}:` *{{object.title|select_language}}*

{{object.body|select_language}}

*URL:* {{object.url}}
_Reply to this message to post a comment on Infinity._