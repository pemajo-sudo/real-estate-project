from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("properties/", views.property_list, name="property_list"),
    path("properties/<int:pk>/", views.property_detail, name="property_detail"),
    path("properties/add/", views.property_create, name="property_create"),
    path("properties/<int:pk>/edit/", views.property_update, name="property_update"),
    path("properties/<int:pk>/delete/", views.property_delete, name="property_delete"),
]