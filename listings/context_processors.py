from listings.models import UserProfile


def seller_permissions(request):
    user = getattr(request, "user", None)
    can_post = False
    if user and user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.can_post_property:
            can_post = True
        else:
            from listings.models import Property
            approved_leads_count = user.sell_leads.filter(status="Approved").count()
            properties_count = Property.objects.filter(owner=user).count()
            can_post = properties_count < approved_leads_count
    return {"user_can_post_property": can_post}
