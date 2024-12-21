from django.urls import path
from .views import (
    admin_restaurant_view, edit_restaurant, delete_restaurant, add_restaurant,
    admin_menu_view, add_menu, edit_menu, delete_menu,
    add_restaurant_json, restaurant_count,
    menu_api, add_menu_api, edit_menu_api, delete_menu_api
)

app_name = 'adminview'

urlpatterns = [
    # --- Bagian "adminview" untuk Web Form (opsional dipertahankan) ---
    path('', admin_restaurant_view, name='admin_restaurant'),
    path('edit/<str:uuid>/', edit_restaurant, name='edit_restaurant'),
    path('delete/<str:uuid>/', delete_restaurant, name='delete_restaurant'),
    path('add/', add_restaurant, name='add_restaurant'),
    path('admin_menu/<uuid:restaurant_id>/', admin_menu_view, name='admin_menu'),
    path('admin_menu/add/<uuid:restaurant_id>/', add_menu, name='add_menu'),
    path('admin_menu/edit/<uuid:restaurant_id>/<uuid:id>/', edit_menu, name='edit_menu'),
    path('admin_menu/delete/<uuid:restaurant_id>/<uuid:id>/', delete_menu, name='delete_menu'),

    # --- Bagian Admin Restaurant JSON (opsional) ---
    path('json/', add_restaurant_json, name='add_restaurant'),
    path('restaurant-count/', restaurant_count, name='restaurant_count'),

    # --- Bagian API JSON untuk Menu Items ---
    path('api/menu_items/<uuid:restaurant_id>/', menu_api, name='list_menu_api'),
    path('api/menu_items/add/<uuid:restaurant_id>/', add_menu_api, name='add_menu_api'),
    path('api/menu_items/edit/<uuid:restaurant_id>/<uuid:menu_item_id>/', edit_menu_api, name='edit_menu_api'),
    path('api/menu_items/delete/<uuid:restaurant_id>/<uuid:menu_item_id>/', delete_menu_api, name='delete_menu_api'),
]
