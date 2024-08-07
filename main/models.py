from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from profanityfilter import ProfanityFilter

profanity_filter = ProfanityFilter()


class Review(models.Model):
    '''
    Модель коментаря з данними:
        User: юзер
        Content: контент
        stars: сколько звезд поставив
        created_at: час коли написав 
        is_admin: адмін юзер чи ні
        likes: скыльки у нього лайків 
        liked: поточний юзер лайкнув чи ні
        reply_to: кому відповід тільки якщо це відповідль на коментар
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    stars = models.IntegerField(
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='liked_reviews', blank=True)
    liked = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')


    def save(self, *args, **kwargs):
        '''Зацензурює погані слова'''
        self.content = profanity_filter.censor(self.content)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''Удаляет все связанные данные с комментарием'''
        self.replies.all().delete()
        self.likes.clear()
        super().delete(*args, **kwargs)


class Pizza(models.Model):
    """
    pizza
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    
    def __str__(self):
        return self.name
    

class Cart(models.Model):
    """
    модель кошику
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Order(models.Model):
    """
    Модель для заказа
    """
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    house_number = models.CharField(max_length=20)
    apartment_number = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=100)
    delivery_time = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Order {self.id} by {self.name}'

class CartItem(models.Model):
    """
    модель для предметів в кошику
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.pizza.price * self.quantity
        super().save(*args, **kwargs)