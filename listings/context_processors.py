from listings.models import UserProfile


def seller_permissions(request):
    user = getattr(request, "user", None)
    can_post = False
    if user and user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        can_post = profile.can_post_property
    return {"user_can_post_property": can_post}
