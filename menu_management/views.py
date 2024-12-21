from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from main.models import Restaurant, MenuItem, Category
from .forms import MenuItemForm
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.csrf import csrf_exempt

ALLOWED_CATEGORIES = [
    "gudeg", "oseng", "bakpia", "sate", "sego gurih",
    "wedang", "lontong", "rujak cingur", "mangut lele", "ayam", "lainnya"
]

@csrf_exempt
def handle_categories(menu_item, category_names):
    menu_item.categories.clear()  # Clear existing associations
    for name in category_names:
        name = name.strip().lower()
        if name in ALLOWED_CATEGORIES:
            category, _ = Category.objects.get_or_create(name=name.title())
            menu_item.categories.add(category)



@csrf_exempt
def menu_items_api(request, restaurant_id):
    print(f"Request method: {request.method}")  # Debug
    print(f"Request received for restaurant_id: {restaurant_id}")  # Debug
    if request.method == 'GET':
        try:
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
            print(f"Menu items: {data}")  # Debug
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"Error: {e}")  # Debug
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)



@csrf_exempt
@user_passes_test(lambda u: u.is_staff, login_url='main:login')
def admin_menu_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = restaurant.menu_items.all()
    return render(request, 'menu_management/admin_menu.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
    })

@csrf_exempt
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

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Menu item added successfully!',
                    'redirect_url': reverse('menu_management:admin_menu', args=[restaurant_id])
                })

            return redirect('menu_management:admin_menu', restaurant_id=restaurant.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Form validation failed.',
                    'errors': form.errors
                })
    else:
        form = MenuItemForm()
    return render(request, 'menu_management/add_menu.html', {
        'form': form,
        'restaurant': restaurant,
        'allowed_categories': ALLOWED_CATEGORIES,
    })

@csrf_exempt
@user_passes_test(lambda u: u.is_staff, login_url='main:login')
def edit_menu(request, restaurant_id, id):
    menu_item = get_object_or_404(MenuItem, id=id, restaurant__id=restaurant_id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=menu_item)
        if form.is_valid():
            updated_item = form.save(commit=False)
            updated_item.restaurant = menu_item.restaurant
            updated_item.save()

            category_names = request.POST.getlist('categories')
            handle_categories(updated_item, category_names)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Menu item updated successfully!',
                    'redirect_url': reverse('menu_management:admin_menu', args=[restaurant_id])
                })

            return redirect('menu_management:admin_menu', restaurant_id=restaurant_id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Form validation failed.',
                    'errors': form.errors
                })
    else:
        form = MenuItemForm(instance=menu_item)
        selected_categories = list(menu_item.categories.values_list('name', flat=True))

    return render(request, 'menu_management/edit_menu.html', {
        'form': form,
        'restaurant': menu_item.restaurant,
        'menu_item': menu_item,
        'selected_categories': selected_categories,
    })

@csrf_exempt
@user_passes_test(lambda u: u.is_staff, login_url='main:login')
def delete_menu(request, restaurant_id, id):
    menu_item = get_object_or_404(MenuItem, id=id, restaurant__id=restaurant_id)
    menu_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Menu item deleted successfully!',
            'redirect_url': reverse('menu_management:admin_menu', args=[restaurant_id])
        })

    return redirect('menu_management:admin_menu', restaurant_id=restaurant_id)

@csrf_exempt
def add_menu_api(request, restaurant_id):
    # Debug: Log request method dan isi body request
    print(f"Request method: {request.method}")  
    print(f"Request received for restaurant ID: {restaurant_id}")  
    print(f"Request body: {request.body}")  

    if request.method == 'POST':
        try:
            # Parse JSON data dari request body
            data = json.loads(request.body)
            print(f"Parsed JSON: {data}")  

            # Validasi input
            name = data.get('name')
            categories = data.get('categories', [])

            if not name or not categories:
                print("Invalid input: Missing name or categories.")  # Debug
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid input fields.',
                }, status=400)

            # Periksa apakah restoran valid
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
            print(f"Restaurant found: {restaurant.name}")  

            # Buat MenuItem baru
            menu_item = MenuItem.objects.create(name=name, restaurant=restaurant)
            print(f"MenuItem created: {menu_item}")  

            # Tambahkan kategori ke MenuItem
            for category_name in categories:
                category, _ = Category.objects.get_or_create(name=category_name.title())
                menu_item.categories.add(category)
                print(f"Added category: {category.name}")  

            # Respon sukses
            return JsonResponse({
                'status': 'success',
                'message': 'Menu item added successfully!',
            })

        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debug: Tangkap error
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)
    else:
        print("Invalid request method.")  # Debug
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.',
        }, status=405)