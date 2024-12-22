import datetime
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .forms import ReservationForm
from .models import Reservation
from main.models import Restaurant  # Assuming you have the Restaurant model in the 'main' app
from uuid import UUID
from django.utils import timezone
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def create_reservation(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.method == 'POST':
        print("POST request received")  # Debug: memastikan request POST terjadi
        form = ReservationForm(request.POST)
        
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.restaurant = restaurant
            reservation.save()
            return redirect('reservasi:user_reservations')
        else:
            print("Form errors:", form.errors)  # Debug: melihat kesalahan form
    else:
        print("GET request received")  # Debug: memastikan ini adalah request GET
        form = ReservationForm()

    return render(request, 'create_reservation.html', {'form': form, 'restaurant': restaurant})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)  # Ensure the user owns the reservation

    if request.method == 'POST':
        reservation.delete()  # Delete the reservation

        # Check if the request is an AJAX/JSON request (for Flutter)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({"status": "success", "message": "Reservation cancelled successfully."})

        # For web-based cancellation, redirect to the user reservations page
        return redirect('reservasi:user_reservations')

    # If the request is GET (for web confirmation), render the confirmation template
    reservation_data = {
        'id': reservation.id,
        'restaurant_name': reservation.restaurant.name,  # Assuming the restaurant model has a 'name' field
        'reservation_date': reservation.reservation_date,
        'reservation_time': reservation.reservation_time,
    }
    return render(request, 'cancel_reservation.html', {'reservation': reservation_data})  # Render confirmation template

@csrf_exempt
@login_required
def user_reservations(request):
    filter_option = request.GET.get('filter', 'all')  # Get the filter option from the request
    reservations = Reservation.objects.filter(user=request.user)

    if filter_option == 'today':
        reservations = reservations.filter(reservation_date=timezone.now().date())
    elif filter_option == 'upcoming':
        reservations = reservations.filter(reservation_date__gt=timezone.now().date())
    elif filter_option == 'due':
        reservations = reservations.filter(reservation_date__lt=timezone.now().date())

    return render(request, 'user_reservations.html', {'reservations': reservations, 'filter_option': filter_option})

@csrf_exempt
@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)  # Ensure the user owns the reservation

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()  # Save the updated reservation
            return JsonResponse({'success': True, 'message': 'Reservation updated successfully.'})  # Return success response for AJAX
        else:
            return JsonResponse({'success': False, 'errors': form.errors})  # Return errors if form is invalid

    # If the request is GET, return the reservation details for the modal
    reservation_data = {
        'id': reservation.id,
        'reservation_date': reservation.reservation_date,
        'reservation_time': reservation.reservation_time,
        'number_of_people': reservation.number_of_people,
        'special_request': reservation.special_request,
    }
    return JsonResponse({'success': True, 'reservation': reservation_data})  # Return reservation data for AJAX

@csrf_exempt
@login_required
def show_json(request):
    reservations = Reservation.objects.filter(user=request.user).select_related('restaurant')
    data = [
        {
            "model": "reservasi.reservation",
            "pk": reservation.pk,
            "fields": {
                "user": reservation.user.id,
                "restaurant": reservation.restaurant.name,  # Include the restaurant name instead of UUID
                "restaurant_image": reservation.restaurant.image,
                "reservation_date": reservation.reservation_date.strftime("%Y-%m-%d"),
                "reservation_time": reservation.reservation_time.strftime("%H:%M:%S"),
                "number_of_people": reservation.number_of_people,
                "special_request": reservation.special_request,
            },
        }
        for reservation in reservations
    ]
    return JsonResponse(data, safe=False)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date, parse_time
from django.contrib.auth.decorators import login_required
from main.models import Restaurant
from .models import Reservation
import json

@csrf_exempt
def create_reservation_flutter(request, restaurant_id):
    if request.method == 'POST':
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({"status": "error", "message": "User not authenticated."}, status=401)

            # Parse the request body
            data = json.loads(request.body)
            print(f"Parsed Data: {data}")  # Debug: Confirm parsed data

            # Validate and parse data
            reservation_date = parse_date(data["reservation_date"])
            reservation_time = parse_time(data["reservation_time"])
            number_of_people = int(data["number_of_people"])
            special_request = data.get("special_request", "")

            # Fetch the restaurant
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)

            # Create the reservation
            new_reservation = Reservation.objects.create(
                user=request.user,
                restaurant=restaurant,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                number_of_people=number_of_people,
                special_request=special_request
            )

            # Construct the response in the desired JSON format
            response_data = {
                "model": "reservasi.reservation",
                "pk": new_reservation.pk,
                "fields": {
                    "user": new_reservation.user.id,
                    "restaurant": str(new_reservation.restaurant.id),
                    "reservation_date": new_reservation.reservation_date.strftime("%Y-%m-%d"),
                    "reservation_time": new_reservation.reservation_time.strftime("%H:%M:%S"),
                    "number_of_people": new_reservation.number_of_people,
                    "special_request": new_reservation.special_request,
                }
            }

            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({"status": "error", "message": f"JSON Decode Error: {e}"}, status=400)
        except KeyError as e:
            return JsonResponse({"status": "error", "message": f"Missing key: {e}"}, status=400)
        except ValueError as e:
            return JsonResponse({"status": "error", "message": f"Invalid data type: {e}"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {e}"}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

@login_required
def cancel_reservation_flutter(request, reservation_id):
    if request.method == 'POST':
        try:
            # Fetch the reservation and ensure the user owns it
            reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
            
            # Delete the reservation
            reservation.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Reservasi berhasil dibatalkan!'
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'
        }, status=405)

@csrf_exempt
def edit_reservation_flutter(request, reservation_id):
    if request.method == 'POST':
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({"status": "error", "message": "User not authenticated."}, status=401)

            # Parse the request body
            data = json.loads(request.body)
            print(f"Parsed Data: {data}")  # Debug: Confirm parsed data

            # Validate and parse data
            reservation_date = parse_date(data["reservation_date"])
            reservation_time = parse_time(data["reservation_time"])
            number_of_people = int(data["number_of_people"])
            special_request = data.get("special_request", "")

            # Get the existing reservation
            reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

            # Create a form instance with the parsed data and update the reservation
            form_data = {
                'reservation_date': reservation_date,
                'reservation_time': reservation_time,
                'number_of_people': number_of_people,
                'special_request': special_request
            }

            form = ReservationForm(form_data, instance=reservation)

            if form.is_valid():
                updated_reservation = form.save()

                # Construct the response in the desired JSON format
                response_data = {
                    "status": "success",
                    "message": "Reservation updated successfully!",
                    "data": {
                        "id": updated_reservation.id,
                        "user": updated_reservation.user.id,
                        "restaurant": str(updated_reservation.restaurant.id),
                        "reservation_date": updated_reservation.reservation_date.strftime("%Y-%m-%d"),
                        "reservation_time": updated_reservation.reservation_time.strftime("%H:%M:%S"),
                        "number_of_people": updated_reservation.number_of_people,
                        "special_request": updated_reservation.special_request,
                    }
                }

                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({"status": "error", "message": "Invalid form data", "errors": form.errors}, status=400)

        except json.JSONDecodeError as e:
            return JsonResponse({"status": "error", "message": f"JSON Decode Error: {e}"}, status=400)
        except KeyError as e:
            return JsonResponse({"status": "error", "message": f"Missing key: {e}"}, status=400)
        except ValueError as e:
            return JsonResponse({"status": "error", "message": f"Invalid data type: {e}"}, status=400)
        except Exception as e:
            print(f"General Error: {e}")  # Debug print
            return JsonResponse({"status": "error", "message": f"An error occurred: {e}"}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)