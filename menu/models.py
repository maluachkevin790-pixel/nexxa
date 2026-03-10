from django.db import models
from django.db import models
from django.core.exceptions import ValidationError


class Dish(models.Model):
    CATEGORY_CHOICES = [
        ('starter', 'Starter'),
        ('main', 'Main'),
        ('dessert', 'Dessert'),
        ('beverage', 'Beverage'),
        ('side', 'Side'),
    ]

    name         = models.CharField(max_length=100, unique=True)   # DB-level uniqueness
    price        = models.DecimalField(max_digits=6, decimal_places=2)
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='main')
    availability = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = 'Dishes'

    def __str__(self):
        return f"{self.name} (${self.price})"

    # ── Model-level validation ──────────────────────────────────────────────
    def clean(self):
        # 1. Price must be positive
        if self.price is not None and self.price <= 0:
            raise ValidationError({'price': 'Price must be a positive number.'})

        # 2. Prevent duplicate names (case-insensitive), excluding self on update
        qs = Dish.objects.filter(name__iexact=self.name)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({'name': f'A dish named "{self.name}" already exists.'})

    def save(self, *args, **kwargs):
        self.full_clean()          # always run clean() before saving
        super().save(*args, **kwargs)


# Create your models here.
