from django.urls import path
from django.views.generic import TemplateView

from product.views.product import CreateProductView, create_product, edit_product, products
from product.views.variant import VariantView, VariantCreateView, VariantEditView

app_name = "product"

urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),
    
    
    path('edit/<int:id>/', edit_product, name='edit.product'),
    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('api/create/', create_product, name="api.create.product"),
    # path('list/', TemplateView.as_view(template_name='products/list.html', extra_context={
    #     'product': True
    # }), name='list.product'),
    path('list/', products, name="list.product"),
]
