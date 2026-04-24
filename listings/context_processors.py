from listings.models import UserProfile


def seller_permissions(request):
    user = getattr(request, "user", None)
    can_post = False
    if user and user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.can_post_property:
            can_post = True
        else:
            from listings.models import SellLead
            can_post = SellLead.objects.filter(user=user, status=SellLead.STATUS_APPROVED, is_used=False).exists()
    return {"user_can_post_property": can_post}
