from django.contrib import admin
from django.utils.html import format_html
from .models import Dog, DogImage, Breed, Testimonial, SiteConfig


# ──────────────────────────────────────────
# BREED ADMIN
# ──────────────────────────────────────────
@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ['name', 'dog_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def dog_count(self, obj):
        return obj.dogs.count()
    dog_count.short_description = 'Dogs Listed'


# ──────────────────────────────────────────
# DOG ADMIN
# ──────────────────────────────────────────
class DogImageInline(admin.TabularInline):
    model = DogImage
    extra = 3
    fields = ['image', 'is_primary', 'alt_text', 'sort_order']


@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    list_display = [
        'thumbnail', 'name', 'breed', 'gender', 'age',
        'formatted_price', 'location', 'status', 'created_at'
    ]
    list_filter = ['status', 'breed', 'gender', 'is_kci_registered']
    list_editable = ['status']
    search_fields = ['name', 'breed__name', 'location', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['sold_at', 'created_at', 'updated_at']
    inlines = [DogImageInline]

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'breed', 'age', 'gender', 'color')
        }),
        ('Pricing & Location', {
            'fields': ('price', 'location')
        }),
        ('Details', {
            'fields': (
                'description', 'vaccination_status',
                'is_kci_registered', 'weight', 'microchipped'
            )
        }),
        ('Status', {
            'fields': ('status', 'sold_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_sold', 'mark_available', 'mark_reserved']

    def thumbnail(self, obj):
        img = obj.primary_image
        if img and img.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius: 8px; object-fit: cover;" />',
                img.image.url
            )
        return '📷 No photo'
    thumbnail.short_description = 'Photo'

    def formatted_price(self, obj):
        return f'₹{obj.price:,.0f}'
    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price'

    @admin.action(description='🔴 Mark as SOLD')
    def mark_sold(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='sold', sold_at=timezone.now())
        self.message_user(request, f'{queryset.count()} dog(s) marked as sold.')

    @admin.action(description='🟢 Mark as AVAILABLE')
    def mark_available(self, request, queryset):
        queryset.update(status='available', sold_at=None)
        self.message_user(request, f'{queryset.count()} dog(s) marked as available.')

    @admin.action(description='🟡 Mark as RESERVED')
    def mark_reserved(self, request, queryset):
        queryset.update(status='reserved')
        self.message_user(request, f'{queryset.count()} dog(s) marked as reserved.')


# ──────────────────────────────────────────
# TESTIMONIAL ADMIN
# ──────────────────────────────────────────
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'city', 'rating', 'dog_breed', 'is_active', 'created_at']
    list_filter = ['is_active', 'rating']
    list_editable = ['is_active']
    search_fields = ['customer_name', 'review']


# ──────────────────────────────────────────
# SITE CONFIG ADMIN (Singleton)
# ──────────────────────────────────────────
@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Branding', {
            'fields': ('site_name', 'tagline')
        }),
        ('Contact Info', {
            'fields': ('admin_whatsapp', 'admin_phone', 'admin_email', 'address')
        }),
        ('Hero Section', {
            'fields': ('hero_image', 'hero_title', 'hero_subtitle')
        }),
        ('Pop-up Modal', {
            'fields': ('popup_enabled', 'popup_title', 'popup_message', 'popup_delay_seconds'),
            'description': 'The "Hellow hooman!" pop-up that appears after a delay'
        }),
        ('Trust Elements', {
            'fields': ('total_happy_families', 'years_in_business', 'total_breeds_available')
        }),
        ('Auto-Cleanup', {
            'fields': ('auto_delete_sold_days',),
            'description': 'Sold dogs and their photos are auto-deleted after this many days'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('About Us', {
            'fields': ('about_us',),
        }),
    )

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
