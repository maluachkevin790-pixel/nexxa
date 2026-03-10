
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from .models import Dish


class DishModelTests(TestCase):
    """1. Model-level validation"""

    def _make_dish(self, **kwargs):
        defaults = dict(name='Tomato Soup', price=Decimal('5.99'), category='starter')
        defaults.update(kwargs)
        return Dish(**defaults)

    # ── Price validation ───────────────────────────────────────────────────
    def test_negative_price_raises(self):
        dish = self._make_dish(price=Decimal('-1.00'))
        with self.assertRaises(Exception):
            dish.save()

    def test_zero_price_raises(self):
        dish = self._make_dish(price=Decimal('0.00'))
        with self.assertRaises(Exception):
            dish.save()

    def test_positive_price_saves(self):
        dish = self._make_dish(price=Decimal('9.99'))
        dish.save()
        self.assertEqual(Dish.objects.count(), 1)

    # ── Duplicate name validation ──────────────────────────────────────────
    def test_duplicate_name_raises(self):
        Dish.objects.create(name='Burger', price=Decimal('12.00'), category='main')
        dup = self._make_dish(name='Burger')
        with self.assertRaises(Exception):
            dup.save()

    def test_case_insensitive_duplicate_raises(self):
        Dish.objects.create(name='Burger', price=Decimal('12.00'), category='main')
        dup = self._make_dish(name='burger')
        with self.assertRaises(Exception):
            dup.save()

    # ── Availability default ───────────────────────────────────────────────
    def test_availability_defaults_true(self):
        dish = self._make_dish()
        dish.save()
        self.assertTrue(dish.availability)


class DishCRUDViewTests(TestCase):
    """2. CRUD views"""

    def setUp(self):
        self.client = Client()
        self.dish = Dish.objects.create(
            name='Margherita', price=Decimal('11.50'), category='main'
        )

    # ── List ──────────────────────────────────────────────────────────────
    def test_list_view(self):
        resp = self.client.get(reverse('dish_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Margherita')

    # ── Detail ────────────────────────────────────────────────────────────
    def test_detail_view(self):
        resp = self.client.get(reverse('dish_detail', args=[self.dish.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Margherita')

    # ── Create ────────────────────────────────────────────────────────────
    def test_create_dish(self):
        resp = self.client.post(reverse('dish_create'), {
            'name': 'Caesar Salad', 'price': '8.50',
            'category': 'starter', 'availability': True,
        })
        self.assertRedirects(resp, reverse('dish_list'))
        self.assertTrue(Dish.objects.filter(name='Caesar Salad').exists())

    def test_create_rejects_negative_price(self):
        resp = self.client.post(reverse('dish_create'), {
            'name': 'Bad Dish', 'price': '-5.00',
            'category': 'main', 'availability': True,
        })
        self.assertEqual(resp.status_code, 200)          # stays on form
        self.assertFalse(Dish.objects.filter(name='Bad Dish').exists())

    def test_create_rejects_duplicate_name(self):
        resp = self.client.post(reverse('dish_create'), {
            'name': 'Margherita', 'price': '10.00',
            'category': 'main', 'availability': True,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Dish.objects.filter(name='Margherita').count(), 1)

    # ── Update ────────────────────────────────────────────────────────────
    def test_update_dish(self):
        resp = self.client.post(reverse('dish_update', args=[self.dish.pk]), {
            'name': 'Margherita', 'price': '13.00',
            'category': 'main', 'availability': True,
        })
        self.assertRedirects(resp, reverse('dish_list'))
        self.dish.refresh_from_db()
        self.assertEqual(self.dish.price, Decimal('13.00'))

    # ── Delete ────────────────────────────────────────────────────────────
    def test_delete_dish(self):
        resp = self.client.post(reverse('dish_delete', args=[self.dish.pk]))
        self.assertRedirects(resp, reverse('dish_list'))
        self.assertFalse(Dish.objects.filter(pk=self.dish.pk).exists())

    # ── Toggle availability ───────────────────────────────────────────────
    def test_toggle_availability(self):
        original = self.dish.availability          # True
        self.client.post(reverse('dish_toggle', args=[self.dish.pk]))
        self.dish.refresh_from_db()
        self.assertNotEqual(self.dish.availability, original)


class URLPatternTests(TestCase):
    """3. URL routes match spec exactly"""

    def setUp(self):
        self.dish = Dish.objects.create(
            name='Test Dish', price=Decimal('7.00'), category='side'
        )

    def test_menu_root(self):
        self.assertEqual(reverse('dish_list'), '/menu/')

    def test_add_url(self):
        self.assertEqual(reverse('dish_create'), '/menu/add/')

    def test_edit_url(self):
        self.assertEqual(
            reverse('dish_update', args=[self.dish.pk]),
            f'/menu/{self.dish.pk}/edit/'
        )

    def test_delete_url(self):
        self.assertEqual(
            reverse('dish_delete', args=[self.dish.pk]),
            f'/menu/{self.dish.pk}/delete/'
        )

# Create your tests here.
