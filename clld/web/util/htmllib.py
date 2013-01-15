from mako.template import Template
from markupsafe import escape, Markup


def tag(name, *children, **attrs):
    for key in attrs:
        attrs[key] = escape(attrs[key])
    cls = attrs.pop('class_', None)
    if cls:
        attrs['class'] = cls
    content = []
    for child in children:
        if isinstance(child, Markup):
            content.append(child)
        else:
            content.append(escape(child))
    content = ''.join(content)
    t = Template("""<${name} ${' '.join(key+'="'+str(val)+'"' for key, val in attrs.items())}>${content or ''}</${name}>""")
    return Markup(t.render(**locals()))
