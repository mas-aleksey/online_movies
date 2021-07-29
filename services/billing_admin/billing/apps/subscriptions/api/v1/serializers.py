from rest_framework import serializers

from billing.apps.subscriptions.models import Tariff, Product, Discount


class DiscountDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'name', 'description', 'value']


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'access_type']


class TariffDetailSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer()
    discount = DiscountDetailSerializer()

    class Meta:
        model = Tariff
        fields = ['id', 'price', 'period', 'product', 'discount']


class TariffListSerializer(serializers.ModelSerializer):
    discount = DiscountDetailSerializer()

    class Meta:
        model = Tariff
        fields = ['id', 'price', 'period', 'discount']


class ProductSerializer(serializers.ModelSerializer):
    tariffs = TariffListSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'access_type', 'tariffs']
