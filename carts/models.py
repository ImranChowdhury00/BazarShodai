from django.db import models
from products.models import Product, TimeStampedModel
from accounts.models import CustomUser


class Cart(TimeStampedModel):
    session_key = models.CharField(max_length=250, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name="carts")

    def __str__(self):
        if self.user:
            return f"Cart for User : {self.user.first_name}"
        else:
            return f"Anonymous Cart : {self.session_key}"


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name="cart_products")
    product = models.ForeignKey(Product, null=True,on_delete=models.DO_NOTHING, related_name="cart_products")
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, null=True)
    quantity = models.PositiveSmallIntegerField(default=0)

    def sub_total(self):
        return self.product.discount_price * self.quantity

    def __str__(self):
        return f"CartItem: {self.product.name}"