from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from .models import Review
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from main.models import Restaurant
from django.http import JsonResponse
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
@login_required
def add_review_ajax(request, restaurant_name):
    restaurant = get_object_or_404(Restaurant, name=restaurant_name)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.restaurant_name = restaurant.name
            review.save()
            
            # Respond with the new review data
            response_data = {
                'reviewer': review.user.username,
                'comment': review.comment,
                'rating': review.rating,
            }
            return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid form'}, status=400)

@csrf_exempt
def edit_review(request, id):
    # Mendapatkan review berdasarkan id
    review = get_object_or_404(Review, pk=id)

    # Set review sebagai instance dari form
    form = ReviewForm(request.POST or None, instance=review)

    if form.is_valid() and request.method == "POST":
        form.save()
        # Redirect ke halaman review restoran setelah perubahan disimpan
        return HttpResponseRedirect(reverse('restaurant_review', kwargs={'name': review.restaurant_name}))

    context = {
        'form': form,
        'restaurant_name': review.restaurant_name  # Mengirimkan nama restoran ke template
    }
    return render(request, "edit_review.html", context)

@csrf_exempt
def delete_review(request, id):
    # Mendapatkan review berdasarkan id
    review = get_object_or_404(Review, pk=id)

    # Hapus review
    review.delete()

    # Redirect ke halaman review restoran setelah review dihapus
    return HttpResponseRedirect(reverse('review:restaurant_review', kwargs={'name': review.restaurant_name}))




@csrf_exempt
def restaurant_review(request, name):
    # Mendapatkan restoran berdasarkan nama
    restaurant = get_object_or_404(Restaurant, name=name)

    # Mendapatkan semua review untuk restoran ini dari database
    user_reviews = Review.objects.filter(restaurant_name=name)
    menu_items = restaurant.menu_items.all()

    form = ReviewForm
    context = {
        'restaurant': restaurant,
        'reviews': user_reviews, # Semua review dari database
        'menu_items' : menu_items,
        'form': form
    }
    return render(request, 'restaurant_review.html', context)

@csrf_exempt
def edit_review_ajax(request):
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        review = get_object_or_404(Review, id=review_id, user=request.user)
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment')
        review.save()
        return JsonResponse({
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'username': review.user.username, 
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

def show_json(request):
    data = Review.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

@csrf_exempt
def create_review_flutter(request):
    if request.method == 'POST':
        try:
            # Debug print
            print(f"Received data: {request.POST}")
            
            # Buat review baru
            new_review = Review.objects.create(
                user=request.user,
                restaurant_name=request.POST.get('restaurant_name'),
                rating=int(request.POST.get('rating')),
                comment=request.POST.get('comment')
            )
            
            new_review.save()
            
            return JsonResponse({
                "status": "success",
                "message": "Review berhasil ditambahkan!"
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)
            
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=401)

# Untuk mendapatkan review berdasarkan nama restoran
@csrf_exempt
@login_required
def get_restaurant_reviews(request, restaurant_name):
    if request.method == 'GET':
        try:
            reviews = Review.objects.filter(restaurant_name=restaurant_name)
            # Gunakan custom serializer untuk menyertakan username
            review_data = []
            for review in reviews:
                review_dict = {
                    "model": "review.review",
                    "pk": review.pk,
                    "fields": {
                        "user": review.user.username,  # Ambil username alih-alih user ID
                        "restaurant_name": review.restaurant_name,
                        "rating": review.rating,
                        "comment": review.comment,
                        "created_at": review.created_at.isoformat()
                    }
                }
                review_data.append(review_dict)
            return JsonResponse(review_data, safe=False)
        except Exception as e:
            print(f"Debug - Error: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)

@csrf_exempt
def get_username(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "username": request.user.username,
            "status": "success"
        })
    return JsonResponse({
        "status": "error",
        "message": "User not authenticated"
    }, status=401)

@csrf_exempt
def edit_review_flutter(request, review_id):
    if request.method == 'POST':
        try:
            review = Review.objects.get(pk=review_id)
            if review.user == request.user:
                rating = request.POST.get('rating')  # Gunakan request.POST alih-alih json.loads
                comment = request.POST.get('comment')
                
                review.rating = int(rating)
                review.comment = comment
                review.save()
                
                return JsonResponse({
                    "status": "success",
                    "message": "Review berhasil diperbarui"
                })
            return JsonResponse({
                "status": "error",
                "message": "Anda tidak memiliki izin untuk mengedit review ini"
            }, status=403)
        except Review.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Review tidak ditemukan"
            }, status=404)
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=400)

@csrf_exempt
def delete_review_flutter(request, review_id):
    if request.method == 'POST':  # Ganti DELETE menjadi POST
        try:
            review = Review.objects.get(pk=review_id)
            if review.user == request.user:
                review.delete()
                return JsonResponse({
                    "status": "success",
                    "message": "Review berhasil dihapus"
                })
            return JsonResponse({
                "status": "error",
                "message": "Anda tidak memiliki izin untuk menghapus review ini"
            }, status=403)
        except Review.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Review tidak ditemukan"
            }, status=404)
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=400)

