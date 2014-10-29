from django import template
from django.forms import CheckboxSelectMultiple, ClearableFileInput, RadioSelect
from django.conf import settings
from wagtail.wagtailcore.models import Page

register = template.Library()


@register.assignment_tag(takes_context=False)
def get_menu_pages():  
    try:          
        menuitems = Page.objects.filter(live=True, show_in_menus=True).values('title', 'slug', 'url_path')  
    except:
        menuitems = []


    return { 'menuitems': menuitems }