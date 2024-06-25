from django import template

register = template.Library()


@register.filter
# Join all the tags of a paper instance together in template
def join_tags(paper, delimiter=", "):
    return delimiter.join(tag.name for tag in paper.tags.all())


@register.filter
# Get paper title of workflow, especially from workflow instructions for new uploads
def get_title(workflow):
    if paper := workflow.paper:
        return paper.title
    # "instructions" is something like "paper: <title>"
    instructions = workflow.instructions
    return instructions[7:]
