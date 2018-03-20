{% if object.categories_names %}
`Categories:` {{object.categories_names|join:','}}
{% endif %}

`{{object.get_type_display}}:` *{{object.title}}*

{{object.body}}

*URL:* {{object.url}}
_Reply to this message to post a comment on Infinity._