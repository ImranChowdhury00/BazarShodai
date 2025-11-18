import datetime
import random
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from sslcommerz_python_api import SSLCSession

from carts.models import Cart, CartItem
from carts.utils import get_session_key
from products.models import Product

from .models import Order, OrderProduct, Payment

from .utils import send_order_confirmation_email


def place_order(request):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        cart = get_object_or_404(Cart, session_key=get_session_key(request))

    cart_products = CartItem.objects.filter(cart=cart).select_related("product")

    if cart_products.count() == 0:
        return redirect("home")

    quantity = 0
    total = 0
    for cart_product in cart_products:
        total += cart_product.product.price * cart_product.quantity
        quantity += cart_product.quantity

    if request.method == "POST":
        payment_option = request.POST.get("payment_method")  # cash / sslcommercez

        # try:
        current_date = datetime.datetime.now()
        order_number = current_date.strftime("%Y%m%d%H%M%S") + str(
            random.randint(1000,9999)
        )  
        
        if request.user.is_authenticated:
            current_user = request.user

            order = Order.objects.create(
                user=current_user,
                mobile=current_user.mobile,
                address_line_1=current_user.address_line_1,
                address_line_2=current_user.address_line_2,
                country=current_user.country,
                city=current_user.city,
                order_note=request.POST.get("order_note", ""),
                order_total=total,
                status="Pending",
                order_number=order_number,
            )
        else:
            order = Order.objects.create(
                user= None,
                mobile = request.POST.get('mobile'),
                address_line_1 = request.POST.get('address_1'),
                order_note=request.POST.get("order_note", ""),
                country = request.POST.get('country'),
                city = request.POST.get('city'),
                status="Pending",
                order_number=order_number,
                order_total=total,
            )

        request.session['latest_order_number'] = order.order_number

        for cart_item in cart_products:
            OrderProduct.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                product_price=cart_item.product.price,
            )


            product = Product.objects.get(id=cart_item.product.id)
            if product.stock >= cart_item.quantity:
                product.stock -= cart_item.quantity
                product.save()

        # if request.user.is_authenticated:
        #     send_order_confirmation_email(current_user, order)

        if payment_option == "cash":
            cart_products.delete()
            return redirect("order_complete")
        elif payment_option == "sslcommerz":
            return redirect("payment")

        # except Exception as e:
        #     return HttpResponse("Error occurred: " + str(e))

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_products,
        "grand_total": total + settings.DELIVERY_CHARGE,
    }

    return render(request, "orders/checkout.html", context=context)


def payment(request):
    mypayment = SSLCSession(
        sslc_is_sandbox=True,
        sslc_store_id=settings.SSLCOMMERZ_STORE_ID,
        sslc_store_pass=settings.SSLCOMMERZ_STORE_PASS,
    )

    status_url = request.build_absolute_uri("payment_status")
    print("status url :",status_url)
    mypayment.set_urls(
        success_url=status_url,
        fail_url=status_url,
        cancel_url=status_url,
        ipn_url=status_url,
    )

    user = request.user
    order = Order.objects.filter(user=user, status="Pending").last()

    mypayment.set_product_integration(
        total_amount=Decimal(order.order_total),
        currency="BDT",
        product_category="clothing",
        product_name="demo-product",
        num_of_item=2,
        shipping_method="YES",
        product_profile="None",
    )

    mypayment.set_customer_info(
        name=user.first_name,
        email=user.email,
        address1=order.address_line_1,
        address2=order.address_line_2,
        city=order.city,
        postcode='1207',
        country=order.country,
        phone=order.mobile,
    )

    mypayment.set_shipping_info(
        shipping_to=user.first_name,
        address=order.address_line_2,
        city=order.city,
        postcode='1207',
        country=order.country,
    )

    response_data = mypayment.init_payment()
    print("response data : ",response_data)
    # if response_data["status"] == "FAILED":
    #     order.status = "Failed"
    #     # TODO: restock product
    #     order.save()

    return redirect(response_data["GatewayPageURL"])


@csrf_exempt
def payment_status(request):
    if request.method == "POST":
        payment_data = request.POST
        if payment_data["status"] == "VALID":
            val_id = payment_data["val_id"]
            tran_id = payment_data["tran_id"]

            order = Order.objects.filter(user=request.user).last()

            payment = Payment.objects.create(
                user=request.user,
                payment_id=val_id,
                payment_method="SSLCommerz",
                amount_paid=order.order_total,
                status="Completed",
            )

            order.status = "Completed"
            order.payment = payment
            order.save()

            # CartItems will be automatically deleted
            Cart.objects.filter(user=request.user).delete()

            context = {
                "order": order,
                "transaction_id": tran_id,
            }
            return render(request, "orders/order-success.html", context)

        else:
            return render(request, "orders/payment-failed.html")
        
def order_complete(request):
    cash = True
    order = None
    order_number = request.session.get('latest_order_number')
    if order_number:
        order = get_object_or_404(Order, order_number=order_number)

        if 'latest_order_number' in request.session:
            del request.session['latest_order_number']
    if not order:
        return redirect('home')
    # if request.user.is_authenticated:
    #     order = Order.objects.filter(user= request.user).last()
    # else:
    #     order = Order.objects.filter()
    return render(request, 'orders/status.html', {'cash':cash,'order':order})