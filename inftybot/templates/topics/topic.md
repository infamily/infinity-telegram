{% if categories_str %}
`Categories:` {{categories_str|split(',')|strip(' ')|exclude('')|join(', ')}}
{%- endif %}

`{{type_str}}:` *{{title}}*

{{body}}

*URL:* {{url}}
_Reply to this message to post a comment on Infinity._