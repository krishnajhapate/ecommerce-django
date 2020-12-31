from django.shortcuts import render,get_object_or_404,redirect,reverse
from .models import Item,OrderItem,Order,Address,Payment,Coupon,Refund
from django.views.generic import ListView,DetailView,View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from .forms import CheckoutForm,CouponForm,RefundForm
import stripe
import random
import string
stripe.api_key = settings.STRIPE_TEST_KEY

# Create your views here.
def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase+string.digits,k=20))


class HomeView(ListView):
    model =Item
    template_name='home.html'
    paginate_by=8

class ItemDetailView(DetailView):
    model = Item
    template_name = 'products.html'

def home(request):
    context ={
        'items':Item.objects.all()
    }
    return render(request,'home.html',context)

class OrderSummaryView(LoginRequiredMixin,View):
    def get(self,*args, **kwargs):
        items = Item.objects.order_by('?')[:4]
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            context = {
                'objects':order,
                'items':items,
            }
            return render(self.request,'order_summary.html',context)
        except ObjectDoesNotExist:
            context = {
                'items':items,
            }
            messages.error(self.request,'You do not have an active order')
            return render(self.request,'order_summary.html',context)
        

@login_required
def add_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item,created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        )
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request,"This item quantity was updated.")
            return redirect("core:order-summary")

        else:
            order.items.add(order_item)
            order_item.quantity +=1
            order_item.save()
            messages.info(request,"This item was added to your cart.")
            return redirect("core:order-summary")

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
    return redirect("core:order-summary")

@login_required
def add_single_item_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item,created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        )
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request,"This item quantity was updated.")
            return redirect("core:order-summary")

        else:
            order.items.add(order_item)
            messages.info(request,"This item was added to your cart.")
            return redirect("core:order-summary")

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
    return redirect("core:order-summary")

@login_required
def remove_from_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item,created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        )
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.quantity =0
            order_item.save()
            order.items.remove(order_item)
            messages.info(request,"This item was removed from your cart.")
            return redirect("core:product",slug=slug)

        else:
            # add a message saying the user doesn't have an order
            messages.info(request,"This item was not in your cart.")
            return redirect("core:product",slug=slug)

        
    else:
         # add a message saying the user doesn't have an order
        messages.info(request,"You don not have an active order.")
        return redirect("core:product",slug=slug)
    return redirect("core:product",slug=slug)   

@login_required
def remove_single_item_from_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item,created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        )
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity ==0:
                order.items.remove(order_item)
            else:
                order_item.quantity -=1
                order_item.save()
                if order_item.quantity == 0:
                    order.items.remove(order_item)
            order_item.save()
            messages.info(request,"This item was updated.")
            return redirect("core:order-summary")

        else:
            # add a message saying the user doesn't have an order
            messages.info(request,"This item was not in your cart.")
            return redirect("core:order-summary")

        
    else:
         # add a message saying the user doesn't have an order
        messages.info(request,"You don not have an active order.")
        return redirect("core:order-summary")
    return redirect("core:order-summary")   

class CheckoutView(LoginRequiredMixin,View):
    def get(self,*args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            if order: 
                print(order)
                pass
            else:
                order=None
                messages.warning(self.request,"Your cart is empty to further checkout")
                return redirect("/")
            # form 
            form  = CheckoutForm()
            order = Order.objects.get(user=self.request.user,ordered=False)
            context={
                    'form':form,
                    "order":order,
                    'couponform':CouponForm(),
                    'DISPLAY_COUPON_FORM':True
                }
            return render(self.request,'checkout.html',context)
        except ObjectDoesNotExist:
            messages.error(self.request,"You dont have an active order")
            return redirect("core:checkout")

    def post(self,*args, **kwargs):
        form = CheckoutForm(self.request.POST or None) 
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            if form.is_valid():
                street_address= form.cleaned_data.get('street_address')
                apartment_address= form.cleaned_data.get('apartment_address')
                country= form.cleaned_data.get('country')
                zip= form.cleaned_data.get('zip')
                # TODO add functionality to these fields
                # same_billing_address= form.cleaned_data.get('same_billing_address')
                # save_info= form.cleaned_data.get('save_info')
                payment_option= form.cleaned_data.get('payment_option')
                billing_address = Address(
                    user=self.request.user ,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    countries=country,
                    zip=zip,
                    address_type='B'
                )
                billing_address.save()
                order.billing_address=billing_address
                order.save()
                if payment_option=="S":
                    return redirect("core:payment",payment_option="stripe")
                elif payment_option=="P":
                    return redirect("core:payment",payment_option="paypal")
                else:
                    messages.error(self.request,"Invalid payment options selected")
                    return redirect("core:checkout")
            return redirect('core:order-summary')
        except ObjectDoesNotExist:
            messages.warning(self.request,"Failed to checkout")
            return redirect("core:checkout")
        return redirect("core:checkout")
            
class PaymentView(View):
    def get(self,*args, **kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False)
        
        if order.billing_address:
            context = { 
                "order":order,
                "couponform":CouponForm(),
                'DISPLAY_COUPON_FORM':True
            }
            return render(self.request,"payment.html",context)
        else:
            messages.error(self.request,"You have not added billing address")
            return redirect("core:checkout")

    def post(self,*args, **kwargs):
        order =Order.objects.get(user=self.request.user,ordered=False)
        token = self.request.POST.get('stripeToken')
        amount  = int(order.get_total()*100)
        try:
            charge=stripe.Charge.create(
                amount=amount,
                currency="inr",
                source=token,
            )
            # create the payment

            payment = Payment()
            payment.stripe_charge_id= charge['id']
            print("chargeid",charge['id'])
            payment.user =self.request.user
            payment.amount =order.get_total()
            payment.save()

            # assign the payment to the order
            order_items =  Order.objects.all()
            order_items.update(ordered=True)
            for  item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request,"Your order was successful")
            return redirect('core:home')

        # Use Stripe's library to make requests...
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error',{})
            messages.error(self.request,f"{err.get('message')}")   
            return redirect('core:home')


        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request,f"RateLimitError")   
            return redirect('core:home')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request,f"Invalid Parameters")   
            return redirect('core:home')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request,f"Not authenticated.")   
            return redirect('core:home')

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request,f"Network Error")   
            return redirect('core:home')

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request,f"Something went wrong.You were not charged please try again later.")   
            return redirect('core:home')

        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request,f"A serious error occured.We have been notified")   
            return redirect('core:home')

def product(request):
    return render(request,'products.html')
    
def get_coupon(request,code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.error(request,"This coupon does not exist")
        return redirect("core:checkout")

class RequestRefundView(View):
    def get(self,*args, **kwargs):
        form = RefundForm()
        context={
            'form':form
        }
        return render(self.request,'request_refund.html',context)
    def post(self,*args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')

            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested =True
                order.save()

                # store the refund
                refund =Refund()
                refund.order =order
                refund.reason =message
                refund.email = email
                refund.save()
                messages.info(self.request,"Your request recieved")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request,"This order does not exists")
                return redirect("core:request-refund")



class AddCouponView(LoginRequiredMixin,View):
    def post(self,*args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user,ordered=False)
                order.coupon = get_coupon(self.request,code)
                order.save()
                messages.success(self.request,f"Coupon code '{order.coupon}' applied successfully")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.error(self.request,"You dont have an active order")
                return redirect("core:checkout")