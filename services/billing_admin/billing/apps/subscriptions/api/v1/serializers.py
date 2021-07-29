from rest_framework import serializers

from billing.apps.subscriptions.models import Tariff, Product


class TariffSerializer(serializers.ModelSerializer):
    discount = serializers.SerializerMethodField()

    def get_discount(self, obj):
        if obj.discount:
            return obj.discount.value
        return ''

    class Meta:
        model = Tariff
        fields = ['id', 'price', 'period', 'discount']


class ProductSerializer(serializers.ModelSerializer):
    tariffs = TariffSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'access_type', 'tariffs']
