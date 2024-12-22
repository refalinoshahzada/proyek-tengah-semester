from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from main.models import Restaurant
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import ModelForm
from django.shortcuts import render, get_object_or_404
from menu_management.models import MenuItem, Restaurant
from django.shortcuts import render
from menu_management.views import admin_menu_view, add_menu, edit_menu, delete_menu,menu_api,add_menu_api,edit_menu_api,delete_menu_api
from main.models import *
from django.views.decorators.csrf import csrf_exempt
import json


class RestaurantForm(ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'location', 'average_price', 'rating']



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

@staff_member_required(login_url='main:login')
def edit_restaurant(request, uuid):
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

@staff_member_required(login_url='main:login')
def delete_restaurant(request, uuid):
    restaurant = get_object_or_404(Restaurant, id=uuid)
    restaurant.delete()
    return redirect('adminview:admin_restaurant')

@csrf_exempt
def add_restaurant_json(request):
    print("Request method:", request.method)  # Log metode HTTP
    print("Request body:", request.body) 
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

            # Create the restaurant
            restaurant = Restaurant.objects.create(
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