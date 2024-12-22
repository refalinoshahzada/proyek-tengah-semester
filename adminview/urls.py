from django.urls import path
from .views import (
    admin_restaurant_view,
    edit_restaurant,
    delete_restaurant,
    add_restaurant,          # Django web form
    add_restaurant_json,     # Flutter JSON endpoint
    admin_menu_view,
    add_menu,
    edit_menu,
    delete_menu,
    restaurant_count,
    edit_restaurant_json,
    delete_restaurant_json
)

app_name = 'adminview'

urlpatterns = [
    # Django web form endpoints
    path('', admin_restaurant_view, name='admin_restaurant'),
    path('add/', add_restaurant, name='add_restaurant'),        # Django form
    path('edit/<str:uuid>/', edit_restaurant, name='edit_restaurant'),
    path('delete/<str:uuid>/', delete_restaurant, name='delete_restaurant'),
    
    # Flutter JSON endpoints
    path('add-json/', add_restaurant_json, name='add_restaurant_json'),  # Flutter
    path('edit-json/<str:uuid>/', edit_restaurant_json, name='edit_restaurant_json'),
    path('delete-json/<str:uuid>/', delete_restaurant_json, name='delete_restaurant_json'),
    
    # Other endpoints remain the same
    path('admin_menu/<uuid:restaurant_id>/', admin_menu_view, name='admin_menu'),
    path('admin_menu/add/<uuid:restaurant_id>/', add_menu, name='add_menu'),
    path('admin_menu/edit/<uuid:restaurant_id>/<uuid:id>/', edit_menu, name='edit_menu'),
    path('admin_menu/delete/<uuid:restaurant_id>/<uuid:id>/', delete_menu, name='delete_menu'),
    path('restaurant-count/', restaurant_count, name='restaurant_count'),
]
