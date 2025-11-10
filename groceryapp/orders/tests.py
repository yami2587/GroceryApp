from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from .models import PromoCode

User = get_user_model()
#demo test for promo code during checkout by gpt
class CheckoutPromoTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='pass')
        self.prod = Product.objects.create(name='Milk', category='dairy', price=100, stock=10)
        self.promo = PromoCode.objects.create(code='SAVE10', discount_percent=10, active=True)

    def test_promo_validation(self):
        resp = self.client.get(reverse('promo-validate') + '?code=SAVE10')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['valid'])
        self.assertEqual(resp.json()['discount_percent'], 10)

    def test_checkout_with_promo(self):
        self.client.login(username='u1', password='pass')
        # add cart
        self.client.post(reverse('cart-add-ui'), {'product_id': self.prod.id, 'quantity': 2})
        # checkout with promo
        resp = self.client.post(reverse('checkout-page'), {'promo_code': 'SAVE10'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        # order created, stock reduced
        p = Product.objects.get(pk=self.prod.id)
        self.assertEqual(p.stock, 8)  # 10 - 2
