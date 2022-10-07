from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from api.permissions import IsClient, IsSeller
from api.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order
from yaml import load as load_yaml, Loader
import pprint

# Create your views here.

from rest_framework.views import APIView


class CustomAPIView(APIView):
    def get_permissions(self):
        # Instances and returns the dict of permissions that the view requires.
        return {key: [permission() for permission in permissions] for key, permissions in self.permission_classes.items()}

    def check_permissions(self, request):
        # Gets the request method and the permissions dict, and checks the permissions defined in the key matching
        # the method.
        method = request.method.lower()
        for permission in self.get_permissions()[method]:
            if not permission.has_permission(request, self):
                self.permission_denied(
                    request, message=getattr(permission, 'message', None)
                )

class UpdateShop(CustomAPIView):
    permission_classes = {'post': [IsSeller, permissions.IsAuthenticated]}

    def post(self, request):
        with open("../../data/shop1.yaml") as stream:
            try:
                data = load_yaml(stream, Loader=Loader)
                shop_data = data['shop']
                categories = data['categories']
                goods = data['goods']
                shop, _ = Shop.objects.get_or_create(name=shop_data['shop'])
                for category_data in categories:
                    category, _ = Category.objects.get_or_create(id=category_data['id'], name=category_data['name'])
                    category.shops.add(shop.id)
                    category.save()
                for good in goods:
                    product, _ = Product.objects.get_or_create(id=good['id'], name=good['name'], category_id=good['category'])
                    product_info = ProductInfo.objects.create(
                        product=product.id,
                        shop=shop.id,
                        model=good['model'],
                        price=good['price'],
                        price_rrc=good['price_rrc'],
                        quantity=good['quantity'])
                    for name, value in good['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(
                            product_info=product_info.id,
                            parameter=parameter_object.id,
                            value=value)
            except yaml.YAMLError as exc:
                return Response({'status':'Error', 'message': exc})
        return Response({'status':'OK'})

class BasketView(CustomAPIView):

    permission_classes = {[permissions.IsAuthenticated, isClient]}

    def get(self, request, *args, *kwargs):
        basket = Order.objects.filter(user_id=request.user.id, state='basket')
