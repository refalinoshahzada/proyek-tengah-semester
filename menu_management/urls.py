from django.urls import path
from .views import admin_menu_view, add_menu, edit_menu, delete_menu,menu_items_api

app_name = 'menu_management'

urlpatterns = [
    path('admin_menu/<uuid:restaurant_id>/', admin_menu_view, name='admin_menu'),
    path('admin_menu/add/<uuid:restaurant_id>/', add_menu, name='add_menu'),
    path('admin_menu/edit/<uuid:restaurant_id>/<uuid:id>/', edit_menu, name='edit_menu'),
    path('admin_menu/delete/<uuid:restaurant_id>/<uuid:id>/', delete_menu, name='delete_menu'),
    path('api/menu_items/<uuid:restaurant_id>/', menu_items_api, name='menu_items_api'),
]
