from django.urls import include, path
from main.views import *

app_name = 'main'

urlpatterns = [
    path('', homepage, name='homepage'),
    path('favorites/toggle/<uuid:restaurant_id>/', toggle_favorite, name='toggle_favorite'),  # Perbaikan URL pattern untuk UUID
    path('login', login_user, name='login'),
    path('register', register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('restaurant/',restaurant_list,name='restaurant'),
    path('restaurant/<uuid:restaurant_id>/', product_detail, name='product_detail'),
    path('json/', show_json, name='show_json'),
    path('restaurantdetail/<uuid:restaurant_id>/', product_detail, name='product_detail'),
    path('auth/', include('authentication.urls')),
]
