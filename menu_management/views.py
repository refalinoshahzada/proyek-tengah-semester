from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from main.models import Restaurant, MenuItem, Category
from .forms import MenuItemForm
from django.http import JsonResponse
from main.models import Restaurant, MenuItem
from django.shortcuts import get_object_or_404

ALLOWED_CATEGORIES = [
    "gudeg", "oseng", "bakpia", "sate", "sego gurih",
    "wedang", "lontong", "rujak cingur", "mangut lele", "ayam", "lainnya"
]

def handle_categories(menu_item, category_names):
    menu_item.categories.clear()  # Clear existing associations
    for name in category_names:
        name = name.strip().lower()
        if name in ALLOWED_CATEGORIES:
            category, _ = Category.objects.get_or_create(name=name.title())
            menu_item.categories.add(category)

def menu_items_api(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = restaurant.menu_items.all()
    data = [
        {
            "id": str(item.id),
            "name": item.name,
            "categories": [category.name for category in item.categories.all()]
        }
        for item in menu_items
    ]
    return JsonResponse(data, safe=False)

@user_passes_test(lambda u: u.is_staff, login_url='main:login')
def admin_menu_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = restaurant.menu_items.all()
    return render(request, 'menu_management/admin_menu.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
    })

@user_passes_test(lambda u: u.is_staff, login_url='main:login')
def add_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant
            menu_item.save()

            category_names = request.POST.getlist('categories')  
            handle_categories(menu_item, category_names)

            return redirect('adminview:admin_menu', restaurant.id)
    else:
        form = MenuItemForm()
    return render(request, 'menu_management/add_menu.html', {
        'form': form,
        'restaurant': restaurant,
        'allowed_categories': ALLOWED_CATEGORIES,  
    })

@user_passes_test(lambda u: u.is_staff, login_url='main:login')
def edit_menu(request, restaurant_id, id):
    menu_item = get_object_or_404(MenuItem, id=id, restaurant__id=restaurant_id)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=menu_item)
        if form.is_valid():
            updated_item = form.save(commit=False)
            updated_item.restaurant = menu_item.restaurant
            updated_item.save()

            # Update categories based on selected options
            category_names = request.POST.getlist('categories')
            handle_categories(updated_item, category_names)
            return redirect('menu_management:admin_menu', restaurant_id=restaurant_id)
    else:
        form = MenuItemForm(instance=menu_item)
        selected_categories = list(menu_item.categories.values_list('name', flat=True))

    return render(request, 'menu_management/edit_menu.html', {
        'form': form,
        'restaurant': menu_item.restaurant,
        'menu_item': menu_item,
        'selected_categories': selected_categories,  
    })

@user_passes_test(lambda u: u.is_staff, login_url='main:login')
def delete_menu(request, restaurant_id, id):
    menu_item = get_object_or_404(MenuItem, id=id, restaurant__id=restaurant_id)
    menu_item.delete()
    return redirect('adminview:admin_menu', restaurant_id=restaurant_id)
