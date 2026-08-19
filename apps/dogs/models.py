from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField
from decimal import Decimal


class Breed(models.Model):
    """Dog breeds — Labrador, German Shepherd, Beagle, etc."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        db_table = 'breeds'
        ordering = ['name']
        verbose_name = 'Breed'
        verbose_name_plural = 'Breeds'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Dog(models.Model):
    """Each dog listed for sale."""

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    STATUS_CHOICES = (
        ('available', '🟢 Available'),
        ('reserved', '🟡 Reserved'),
        ('sold', '🔴 Sold'),
    )

    # ── Basic Info ──
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    breed = models.ForeignKey(
        Breed, on_delete=models.PROTECT, related_name='dogs'
    )
    age = models.CharField(max_length=50, help_text='e.g., "3 months", "1.5 years"')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    color = models.CharField(max_length=50, help_text='e.g., "Golden", "Black & Tan"')

    # ── Pricing & Location ──
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    location = models.CharField(max_length=255, help_text='e.g., "Mumbai, Maharashtra"')

    # ── Details ──
    description = models.TextField(
        help_text='Health info, temperament, parent details, etc.'
    )
    vaccination_status = models.CharField(
        max_length=255, blank=True,
        help_text='e.g., "1st dose done", "Fully vaccinated"'
    )
    is_kci_registered = models.BooleanField(
        default=False, verbose_name='KCI Registered'
    )
    weight = models.CharField(max_length=30, blank=True, help_text='e.g., "5 kg"')
    microchipped = models.BooleanField(default=False)

    # ── Status ──
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='available'
    )
    sold_at = models.DateTimeField(null=True, blank=True, editable=False)

    # ── Timestamps ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dogs'
        ordering = ['-created_at']
        verbose_name = 'Dog'
        verbose_name_plural = 'Dogs'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['breed']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.breed}")
            slug = base_slug
            counter = 1
            while Dog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Track when dog is sold
        if self.status == 'sold' and not self.sold_at:
            self.sold_at = timezone.now()

        # Reset sold_at if admin changes back to available
        if self.status != 'sold':
            self.sold_at = None

        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.status == 'available'

    @property
    def primary_image(self):
        """Get the main display photo."""
        img = self.images.filter(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img

    def __str__(self):
        return f"{self.name} ({self.breed}) — {self.get_status_display()}"


class DogImage(models.Model):
    """Multiple photos per dog. Stored on Cloudinary."""

    dog = models.ForeignKey(
        Dog, on_delete=models.CASCADE, related_name='images'
    )
    image = CloudinaryField(
        'image',
        folder='dogs/',
        transformation={'quality': 'auto', 'fetch_format': 'auto'},
    )
    alt_text = models.CharField(
        max_length=255, blank=True,
        help_text='Describe the photo for accessibility'
    )
    is_primary = models.BooleanField(
        default=False, help_text='Main display photo'
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'dog_images'
        ordering = ['sort_order', '-is_primary']
        verbose_name = 'Dog Photo'
        verbose_name_plural = 'Dog Photos'

    def __str__(self):
        return f"Photo of {self.dog.name} ({'Primary' if self.is_primary else 'Extra'})"


class Testimonial(models.Model):
    """Customer reviews displayed on homepage carousel."""

    customer_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    review = models.TextField()
    rating = models.PositiveIntegerField(
        default=5,
        help_text='Rating from 1 to 5',
        validators=[MinValueValidator(1)],
    )
    photo = CloudinaryField(
        'image', blank=True, null=True,
        folder='testimonials/',
        help_text='Optional photo of customer with their dog'
    )
    dog_breed = models.CharField(
        max_length=100, blank=True,
        help_text='Breed they purchased'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'testimonials'
        ordering = ['-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f"{self.customer_name} — ⭐{self.rating}"


class SiteConfig(models.Model):
    """
    Singleton configuration — only 1 row ever exists.
    Admin edits this to change site-wide settings without touching code.
    """

    # ── Branding ──
    site_name = models.CharField(max_length=100, default='PuppyFarm')
    tagline = models.CharField(max_length=255, default='Find Your Perfect Pup')

    # ── Contact ──
    admin_whatsapp = models.CharField(
        max_length=20, help_text='Country code + number, no + or spaces. e.g., 919876543210'
    )
    admin_phone = models.CharField(
        max_length=20, help_text='Display format. e.g., +91 98765 43210'
    )
    admin_email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    # ── Hero Section ──
    hero_image = CloudinaryField(
        'image', blank=True, null=True, folder='site/'
    )
    hero_title = models.CharField(max_length=255, default='Find Your Perfect Pup 🐶')
    hero_subtitle = models.CharField(
        max_length=500, blank=True,
        default='Healthy, vaccinated puppies from trusted breeders'
    )

    # ── Pop-up Modal ──
    popup_enabled = models.BooleanField(default=True)
    popup_title = models.CharField(max_length=100, default='Hellow hooman! 🐶')
    popup_message = models.CharField(
        max_length=255,
        default='Looking for a furry friend? Chat with us now!'
    )
    popup_delay_seconds = models.PositiveIntegerField(
        default=5, help_text='Seconds before pop-up appears'
    )

    # ── Trust Elements ──
    total_happy_families = models.PositiveIntegerField(default=100)
    years_in_business = models.PositiveIntegerField(default=5)
    total_breeds_available = models.PositiveIntegerField(default=20)

    # ── Cleanup Settings ──
    auto_delete_sold_days = models.PositiveIntegerField(
        default=3,
        help_text='Days after marking sold before auto-deleting dog and photos'
    )

    # ── SEO ──
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    # ── About Us ──
    about_us = models.TextField(blank=True)

    class Meta:
        db_table = 'site_config'
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton — always use pk=1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Site Configuration'
