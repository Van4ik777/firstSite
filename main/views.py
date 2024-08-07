import json
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from .forms import RegisterUserForm
from .utils import DataMixin
from django.contrib.auth import logout
from .forms import ReviewForm
from django.shortcuts import redirect, get_object_or_404
from .models import Review, Cart, CartItem, Order
from .forms import OrderForm
from .models import Pizza
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


# словник для зберігання піц у когшику
cart_items = []

'''ТУТ ПО НАЗВАМ УСЕ ЗРОЗУМІЛО'''
def add_like(request, review_id):
    # додавання лайку до коментаря 
    if request.method == 'POST' and request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_id)

        if request.user in review.likes.all():
            review.likes.remove(request.user)
        else:
            review.likes.add(request.user)
        return redirect('pizza_1')
    else:
        return redirect('pizza_1')


def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.method == 'POST':
        review.delete()
    return redirect('pizza_1')


def add_review_1(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        print(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            reply_to_id = request.POST.get('reply_to')
            if reply_to_id:
                parent_review = get_object_or_404(Review, pk=reply_to_id)
                review.reply_to = parent_review
            review.save()
            return redirect('pizza_1')
    else:
        return redirect('pizza_1')

    return redirect('pizza_1')


def profile(request):
    return render(request, 'main/profile.html')


def logout_user(request):
    logout(request)
    return redirect('main')


def register(request):
    return render(request, 'main/register.html')
@login_required
@require_POST
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pizza_id = data.get('pizza_id')
        quantity = data.get('quantity', 1)
        pizza = get_object_or_404(Pizza, id=pizza_id)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, pizza=pizza)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({'message': 'Товар успешно добавлен в корзину.'})
    else:
        return JsonResponse({'message': 'Метод запроса не поддерживается.'}, status=405)

@login_required
@require_POST
def increase_quantity(request):
    if request.method == 'POST':
        pizza_id = request.POST.get('pizza_id')
        pizza = get_object_or_404(Pizza, id=pizza_id)
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            cart_item, created = CartItem.objects.get_or_create(cart=cart, pizza=pizza)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
                return redirect('cart')
            else:
                return redirect('cart')
        else:
            return JsonResponse({'message': 'Корзина не найдена для данного пользователя.'}, status=404)
    else:
        return JsonResponse({'message': 'Метод запроса не поддерживается.'}, status=405)

@login_required
@require_POST
def decrease_quantity(request):
    if request.method == 'POST':
        pizza_id = request.POST.get('pizza_id')
        pizza = get_object_or_404(Pizza, id=pizza_id)
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            cart_item = CartItem.objects.filter(cart=cart, pizza=pizza).first()
            if cart_item:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                    return redirect('cart')

                else:
                    cart_item.delete()
                    return redirect('cart')

            else:
                return JsonResponse({'message': 'Товар не найден в корзине.'}, status=404)
        else:
            return JsonResponse({'message': 'Корзина не найдена для данного пользователя.'}, status=404)
    else:
        return JsonResponse({'message': 'Метод запроса не поддерживается.'}, status=405)


def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_items = cart.cartitem_set.all()
        for item in cart_items:
            if item.quantity < 1:
                item.delete()
        return render(request, 'main/cart.html')
    return render(request, 'main/cart.html')



def cart(request):
    """ІДЕАЛЬНО"""

    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.pizza.price * item.quantity for item in cart_items)
    else:
        cart_items = []
        total_price = 0

    return render(request, 'main/cart.html', {"cart": cart_items, "total_price": total_price})



def main(request):
    pizzas = Pizza.objects.all()
    return render(request, 'main/main.html', {'pizzas' : pizzas})


def pizza_1(request):
    """коментарі """
    pizzas = Pizza.objects.all()
    form = ReviewForm()
    reviews = Review.objects.all().order_by('-stars')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('pizza_1')
    
    return render(request, 'main/pizza_1.html', {'form': form, 'reviews': reviews,'pizzas' : pizzas})


def pizza_2(request):
    return render(request, 'main/pizza_2.html')


def pizza_3(request):
    return render(request, 'main/pizza_3.html')


class RegisterUser(DataMixin, CreateView):
    """
    Коласс регистрации пользователя 
    """
    form_class = RegisterUserForm
    template_name = "main/register.html"
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        user = User.objects.get(username=username)
        auth_login(self.request, user)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Register")
        return dict(list(context.items()) + list(c_def.items()))

def login(request):
    '''логін юзера'''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('main')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

@login_required
def checkout(request):
    """ИДЕАЛЬНОЕ ОФОРМЛЕННЯ заказу"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            city = form.cleaned_data['city']
            house_number = form.cleaned_data['house_number']
            apartment_number = form.cleaned_data['apartment_number']
            payment_method = form.cleaned_data['payment_method']
            delivery_time = form.cleaned_data['delivery_time']
            
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart_items = CartItem.objects.filter(cart=cart)
                total_price = sum(item.pizza.price * item.quantity for item in cart_items)
                
                order = Order.objects.create(
                    name=name,
                    phone=phone,
                    city=city,
                    house_number=house_number,
                    apartment_number=apartment_number,
                    payment_method=payment_method,
                    delivery_time=delivery_time,
                    total_price=total_price
                )
                print("")
                print(f'####################Order:{order.id}#########################')
                print("Order Details:")
                print(f"--------Name: {order.name}")
                print(f"--------Phone: {order.phone}")
                print(f"--------City: {order.city}")
                print(f"--------House Number: {order.house_number}")
                print(f"--------Apartment Number: {order.apartment_number}")
                print(f"--------Payment Method: {order.payment_method}")
                print(f"--------Delivery Time: {order.delivery_time}")
                print(f"--------Total Price: {order.total_price}")
                print("--------Ordered Pizzas:")
                for item in cart_items:
                    print(f"----------------Pizza: {item.pizza.name}, Quantity: {item.quantity}")
                print('###################################################')
                print("")
                print("")

                cart_items.delete()
                
                return redirect('order_success')
            else:
                return JsonResponse({'message': 'Корзина не найдена для данного пользователя.'}, status=404)
    else:
        form = OrderForm()

    return render(request, 'main/checkout.html', {'form': form})



def order_success(request):
    #оплата пройшла успішно)
    return render(request, 'main/order_success.html')