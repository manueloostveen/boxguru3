from django import template
from boxguru.settings import TEXT_FILES_ROOT

register = template.Library()

@register.filter
def print_file_content(f):
    file = open(f, 'r')
    try:
        return file.read()
    except IOError:
        return ''


@register.filter
def print_file_content2(f):
    file = open(f, 'r')
    try:
        return file.read()
    except IOError:
        return ''

@register.filter
def print_text_file(filename):
    file = open(TEXT_FILES_ROOT + '/' + filename, 'r')
    try:
        return file.read()
    except IOError:
        return ''