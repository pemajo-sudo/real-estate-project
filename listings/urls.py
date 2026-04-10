from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sell/", views.sell_property, name="sell"),
    path("about/", views.about, name="about"),
    path("agents/", views.find_agent, name="find_agent"),
    path("register/", views.register, name="register"),
    path("inquiries/", views.view_inquiries, name="view_inquiries"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    path("dashboard/", views.dashboard_view, name="dashboard"),

    path("properties/", views.property_list, name="property_list"),
    path("properties/<int:pk>/", views.property_detail, name="property_detail"),
    path("properties/<int:pk>/inquiry/", views.send_inquiry, name="send_inquiry"),
    path("properties/<int:pk>/schedule-visit/", views.schedule_visit, name="schedule_visit"),
    path("properties/<int:pk>/compare/add/", views.add_to_compare, name="add_to_compare"),
    path("properties/<int:pk>/compare/remove/", views.remove_from_compare, name="remove_from_compare"),
    path("properties/<int:pk>/wishlist/add/", views.add_to_wishlist, name="add_to_wishlist"),
    path("properties/<int:pk>/wishlist/remove/", views.remove_from_wishlist, name="remove_from_wishlist"),
    path("compare/", views.compare_properties, name="compare_properties"),
    path("properties/add/", views.property_create, name="property_create"),
    path("properties/<int:pk>/edit/", views.property_update, name="property_update"),
    path("properties/<int:pk>/delete/", views.property_delete, name="property_delete"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
]