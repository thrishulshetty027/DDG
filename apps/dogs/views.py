import urllib.parse
from django.shortcuts import render, get_object_or_404
from .models import Dog, Breed, Testimonial, SiteConfig


def home_page(request):
    """Landing page — hero + dog grid + trust section + testimonials."""

    # Get filter parameters
    breed_filter = request.GET.get('breed', '')
    gender_filter = request.GET.get('gender', '')
    sort_by = request.GET.get('sort', 'newest')

    # Base queryset — only available & reserved dogs
    dogs = Dog.objects.filter(
        status__in=['available', 'reserved']
    ).select_related('breed').prefetch_related('images')

    # Apply filters
    if breed_filter:
        dogs = dogs.filter(breed__slug=breed_filter)
    if gender_filter:
        dogs = dogs.filter(gender=gender_filter)

    # Apply sorting
    if sort_by == 'price_low':
        dogs = dogs.order_by('price')
    elif sort_by == 'price_high':
        dogs = dogs.order_by('-price')
    else:  # newest
        dogs = dogs.order_by('-created_at')

    # Get all breeds for filter dropdown
    breeds = Breed.objects.all()

    # Active testimonials
    testimonials = Testimonial.objects.filter(is_active=True)[:10]

    # Site config
    config = SiteConfig.load()

    context = {
        'dogs': dogs,
        'breeds': breeds,
        'testimonials': testimonials,
        'config': config,
        'current_breed': breed_filter,
        'current_gender': gender_filter,
        'current_sort': sort_by,
    }
    return render(request, 'home.html', context)


def dog_detail(request, slug):
    """Single dog page with all details + WhatsApp button."""

    dog = get_object_or_404(
        Dog.objects.select_related('breed').prefetch_related('images'),
        slug=slug,
        status__in=['available', 'reserved']
    )

    config = SiteConfig.load()

    # Build WhatsApp message
    whatsapp_message = (
        f"Hi, I'm interested in *{dog.name}* ({dog.breed.name})\n"
        f"Price: ₹{dog.price:,.0f}\n"
        f"Age: {dog.age}\n"
        f"Gender: {dog.get_gender_display()}\n"
        f"Location: {dog.location}\n"
        f"Link: {request.build_absolute_uri()}"
    )
    whatsapp_url = (
        f"https://wa.me/{config.admin_whatsapp}"
        f"?text={urllib.parse.quote(whatsapp_message)}"
    )

    # Related dogs (same breed, excluding current)
    related_dogs = Dog.objects.filter(
        breed=dog.breed, status='available'
    ).exclude(pk=dog.pk).prefetch_related('images')[:4]

    context = {
        'dog': dog,
        'config': config,
        'whatsapp_url': whatsapp_url,
        'related_dogs': related_dogs,
    }
    return render(request, 'dogs/detail.html', context)
