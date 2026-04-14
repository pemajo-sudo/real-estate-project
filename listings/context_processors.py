from listings.models import UserProfile


def seller_permissions(request):
    user = getattr(request, "user", None)
    can_post = False
    if user and user.is_authenticated:
        has_approved_lead = user.sell_leads.filter(status="Approved").exists()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.can_post_property != has_approved_lead:
            profile.can_post_property = has_approved_lead
            profile.save(update_fields=["can_post_property"])
        can_post = has_approved_lead
    return {"user_can_post_property": can_post}
