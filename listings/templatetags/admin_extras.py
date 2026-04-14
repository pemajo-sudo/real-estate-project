from django import template

from listings.models import SellLead

register = template.Library()


@register.simple_tag
def sell_leads_count():
    return SellLead.objects.count()
