from django import template

from listings.models import UserProfile

register = template.Library()


@register.simple_tag
def can_post_property(user):
    if not getattr(user, "is_authenticated", False):
        return False
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile.can_post_property
