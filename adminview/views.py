from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from main.models import Restaurant, Category
from django.http import JsonResponse
from django.urls import reverse
from django.forms import ModelForm
from django.views.decorators.csrf import csrf_exempt
import json

class RestaurantForm(ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'location', 'average_price', 'rating']

@csrf_exempt
@staff_member_required(login_url='main:login')
def admin_restaurant_view(request):
    restaurants = Restaurant.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    sort_option = request.GET.get('sorting')

    if category_id:
        restaurants = restaurants.filter(menu_items__categories__id=category_id).distinct()
    if sort_option == 'low_to_high':
        restaurants = restaurants.order_by('average_price')
    elif sort_option == 'high_to_low':
        restaurants = restaurants.order_by('-average_price')

    context = {
        'restaurants': restaurants,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'selected_sort': sort_option,
    }
    return render(request, 'adminview/admin_restaurant.html', context)

@csrf_exempt
@staff_member_required(login_url='main:login')
def add_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Restaurant added successfully!',
                    'redirect_url': reverse('adminview:admin_restaurant')
                })
            return redirect('adminview:admin_restaurant')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the form errors.',
                    'errors': form.errors
                })
    else:
        form = RestaurantForm()

    return render(request, 'adminview/add_restaurant.html', {'form': form})

@csrf_exempt
@staff_member_required(login_url='main:login')
def edit_restaurant(request, uuid):
    """
    Edits a Restaurant by a single UUID (restaurant.id).
    URL example: /adminview/edit/<str:uuid>/
    """
    restaurant = get_object_or_404(Restaurant, id=uuid)

    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Restaurant updated successfully!',
                    'redirect_url': reverse('adminview:admin_restaurant')
                })
            return redirect('adminview:admin_restaurant')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the form errors.',
                    'errors': form.errors
                })
    else:
        form = RestaurantForm(instance=restaurant)

    return render(request, 'adminview/edit_restaurant.html', {
        'form': form,
        'restaurant': restaurant
    })

@csrf_exempt
@staff_member_required(login_url='main:login')
def delete_restaurant(request, uuid):
    restaurant = get_object_or_404(Restaurant, id=uuid)
    restaurant.delete()
    return redirect('adminview:admin_restaurant')

@csrf_exempt
@staff_member_required(login_url='main:login')
def admin_menu_view(request, restaurant_id):
    """
    Example placeholder for menu management by RESTAURANT
    """
    return JsonResponse({'info': 'admin_menu_view placeholder'})

@csrf_exempt
@staff_member_required(login_url='main:login')
def add_menu(request, restaurant_id):
    """
    Example placeholder for add_menu
    """
    return JsonResponse({'info': 'add_menu placeholder'})

@csrf_exempt
@staff_member_required(login_url='main:login')
def edit_menu(request, restaurant_id, id):
    """
    Edits a MENU item, requiring two UUIDs: 
    /adminview/admin_menu/edit/<uuid:restaurant_id>/<uuid:id>/
    """
    return JsonResponse({'info': 'edit_menu placeholder'})

@csrf_exempt
@staff_member_required(login_url='main:login')
def delete_menu(request, restaurant_id, id):
    """
    Example placeholder for delete_menu
    """
    return JsonResponse({'info': 'delete_menu placeholder'})

@csrf_exempt
def add_restaurant_json(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            location = data.get("location")
            average_price = data.get("average_price", 0)
            rating = data.get("rating", 0)

            if not name or not location or average_price <= 0 or not (0 <= rating <= 5):
                return JsonResponse(
                    {"status": "error", "message": "Invalid input fields"},
                    status=400,
                )
            
            Restaurant.objects.create(
                name=name,
                location=location,
                average_price=average_price,
                rating=rating,
            )
            return JsonResponse(
                {"status": "success", "message": "Restaurant added successfully"}
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

@csrf_exempt
def restaurant_count(request):
    count = Restaurant.objects.count()
    return JsonResponse({'count': count})