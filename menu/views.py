
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django import forms
from .models import Dish
import decimal
# Create your views here.


# ── List ──────────────────────────────────────────────────────────────────
def dish_list(request):
    """List all dishes with optional category filter."""
    category_filter = request.GET.get('category', '')
    dishes = Dish.objects.all()
    if category_filter:
        dishes = dishes.filter(category=category_filter)

    context = {
        'dishes': dishes,
        'categories': Dish.CATEGORY_CHOICES,
        'selected_category': category_filter,
        'total': Dish.objects.count(),
        'available_count': Dish.objects.filter(availability=True).count(),
    }
    return render(request, 'menu/menu_list.html', context)


# ── Detail ────────────────────────────────────────────────────────────────
def dish_detail(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    return render(request, 'menu/dish_detail.html', {'dish': dish})


# ── Create ────────────────────────────────────────────────────────────────
def dish_create(request):
    if request.method == 'POST':
        form = DishForm(request.POST)
        if form.is_valid():
            dish = form.save()
            messages.success(request, f'✅ "{dish.name}" has been added to the menu!')
            return redirect('dish_list')
        else:
            messages.error(request, '⚠️ Please fix the errors below.')
    else:
        form = DishForm()

    return render(request, 'menu/dish_form.html', {'form': form, 'action': 'Add'})


# ── Update ────────────────────────────────────────────────────────────────
def dish_update(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if request.method == 'POST':
        form = DishForm(request.POST, instance=dish)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ "{dish.name}" has been updated.')
            return redirect('dish_list')
        else:
            messages.error(request, '⚠️ Please fix the errors below.')
    else:
        form = DishForm(instance=dish)

    return render(request, 'menu/dish_form.html', {
        'form': form,
        'action': 'Update',
        'dish': dish,
    })


# ── Delete ────────────────────────────────────────────────────────────────
def dish_delete(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if request.method == 'POST':
        name = dish.name
        dish.delete()
        messages.success(request, f'🗑️ "{name}" has been removed from the menu.')
        return redirect('dish_list')
    return render(request, 'menu/dish_confirm_delete.html', {'dish': dish})


# ── Availability Toggle (quick POST action from list view) ─────────────────
def dish_toggle_availability(request, pk):
    if request.method == 'POST':
        dish = get_object_or_404(Dish, pk=pk)
        dish.availability = not dish.availability
        dish.save()
        status = 'available' if dish.availability else 'unavailable'
        messages.success(request, f'🔄 "{dish.name}" is now {status}.')
    return redirect('dish_list')


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'price', 'category', 'availability']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= decimal.Decimal('0'):
            raise forms.ValidationError('Price must be greater than $0.00.')
        return price

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        qs = Dish.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'A dish named "{name}" already exists.')
        return name

def dish_confirm_delete(request):
    return render(request, 'dish_confirm_delete.html')

def dish_form(request):
    return render(request, 'dish_form.html')
def menu_list(request):
    return render(request, 'menu_list.html')

