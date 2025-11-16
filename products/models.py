from django.db import models
from django.utils.text import slugify
from accounts.models import CustomUser
from django.db.models import Avg, Count


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    category_name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank= True)
    category_img = models.ImageField(upload_to="categories")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.category_name
    
    
class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank= True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default = 0.00)

    stock = models.PositiveIntegerField()
    available = models.BooleanField(default= True)
    unit= models.CharField(max_length=100 ,null=True, blank=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        base_slug = slugify(self.name)

        if not self.pk or self.slug != base_slug:
            unique_slug = base_slug
            counter = 1
        
            while Product.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1
    
            self.slug = unique_slug
        super().save(*args, **kwargs)

    @property
    def discount_price(self):
        return self.price * (1 - self.discount_percentage / 100)
      
    def average_review(self):
        reviews = Review.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        self.rating = avg
        return avg

    def count_review(self):
        reviews = Review.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/images")

    def __str__(self):
        return f"Image for {self.product.name}"
    
    
class Review(TimeStampedModel):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name="reviews", on_delete=models.CASCADE)

    rating = models.FloatField()
    review = models.TextField()

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Review by {self.user.first_name} for {self.product.name}"