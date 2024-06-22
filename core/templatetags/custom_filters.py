from django import template

register = template.Library()


@register.filter
# Join all the tags of a paper instance together in template
def join_tags(paper, delimiter=", "):
    return delimiter.join(tag.name for tag in paper.tags.all())
