import json
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import generic

from product.models import Product, ProductVariant, ProductVariantPrice, Variant
from django.db.models import Q
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from itertools import groupby
from operator import itemgetter

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
    
@csrf_exempt
def create_product(request):
    # {"title":"Iphone","sku":"iphone-14-pro","description":"Iphone excellent","product_image":[],
    # "product_variant":[{"option":2,"tags":["Purple","red"]}],
    # "product_variant_prices":[{"title":"Purple/","price":"1000","stock":"2"},
    # {"title":"red/","price":"1010","stock":"4"}]}
    data = json.loads(request.body)
    print(data)
    product_data = {
            "title": data.get("title", None),
            "sku": data.get("sku", None),
            "description": data.get("description", None),
    }
    product = Product.objects.create(**product_data)
        
    product_variant_data = data.get("product_variant", None)

    variant_dict = {}
    for variant in product_variant_data:
        for tag in variant.get("tags"):
            variant_data = {
                "product": product,
                "variant_title": tag,
                "variant": Variant.objects.filter(id=variant.get("option")).first()
            }
            
            product_variant = ProductVariant.objects.create(**variant_data)
            variant_dict[tag] = product_variant

    product_variant_prices_data = data.get("product_variant_prices", None)

    for product_variant_price in product_variant_prices_data:
        variants = product_variant_price.get("title", None).split("/")
        product_variant_price_data = {
            "price": product_variant_price.get("price", None),
            "stock": product_variant_price.get("stock", None),
            "product": product
        }
        try:
           product_variant_price_data["product_variant_one"]: variant_dict[variants[0]]
        except:
            product_variant_price_data["product_variant_one"] = None
        try:
            product_variant_price_data["product_variant_two"]= variant_dict[variants[1]]
        except:
            product_variant_price_data["product_variant_two"] = None
        
        try:
            product_variant_price_data["product_variant_three"]= variant_dict[variants[2]]
        except:
            product_variant_price_data["product_variant_three"] = None

        ProductVariantPrice.objects.create(**product_variant_price_data)
    
    return redirect(reverse('product:list.product'))


@csrf_exempt
def edit_product(request, id):
    product = Product.objects.get(id=id)
    if request.method == "POST":
        
        data = json.loads(request.body)
        print(data)

        
        product.title = data.get("title", None)
        product.sku = data.get("sku", None)
        product.description = data.get("description", None)
        
        product.save()
        
    variants_stock = []
    variants_price = []
    # {"title":"Purple/","price":"1000","stock":"2"}
    variant_prices = product.productvariantprice_set.all()
    variants_price_obj = []
    try:
        for variant_price in variant_prices:
            variants_price.append({"title": "{}/{}/{}".format(
                variant_price.product_variant_one.variant_title,
                variant_price.product_variant_two.variant_title,
                variant_price.product_variant_three.variant_title), "price": variant_price.price, "stock":variant_price.stock })
    except:
        pass
    variants = []
    # for var in p_variants:
        # "product_variant":[{"option":2,"tags":["Purple","red"]}]
    p_variants = product.productvariant_set.all().order_by('variant')

    for v, group in groupby(p_variants, lambda x: x.variant):
        variants.append({"option": v.id, "tags": [x.variant_title for x in list(group)] })

    print(variants)
    # variants = Variant.objects.filter(active=True).values('id', 'title')
    # print(variants)
    context = {
        "product": {"id": product.id, "title": product.title, "sku": product.sku, "description": product.description},
        "variants_price": variants_price,
        "variants": variants
    }

    print(variants_price)
    return render(request, 'products/edit.html', context)





def products(request):
    if request.method == "GET":
        title = request.GET.get('title', "")
        price_from = request.GET.get('price_from', "")
        price_to = request.GET.get('price_to', "")
        date = request.GET.get('date', "")
        variant = request.GET.get('variant', "")

        query = Q()
        if title:
            query &= Q(title__contains=title)
       
        if price_from:

                query &= Q(productvariantprice__price__gte=float(price_from))
            
        if price_to:
            query &= Q(productvariantprice__price__lte=float(price_to))
        if date:
            # date = datetime.strptime(date, '%Y-%m-%d').time()

            query &= Q(created_at__date=date)
        if variant:
            query &= Q(productvariant__variant_title=variant)



        products_list = Product.objects.filter(query).order_by('created_at').distinct()
        variants = ProductVariant.objects.order_by('variant_title').values_list('variant_title', flat=True).distinct()
        # application_list = ProductVariantPrice.objects.filter(query).prefetch_related('transaction', 'seat', 'call_for_application', 'user')
        # application_list = Application.objects.filter(query)
        page = request.GET.get('page', 1)
        paginator = Paginator(products_list, 5) #list 5 item every page
       
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)


    return render(request, 'products/list.html', {"products": products, "variants": variants, "filters": {"variant": "black", "price_from": price_from, "price_to": price_to, "variant": variant, "title": title, "date": date}} )
