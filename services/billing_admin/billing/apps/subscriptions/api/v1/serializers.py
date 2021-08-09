from django.conf import settings
from rest_framework import serializers

from billing.apps.subscriptions.models import Tariff, Product, Discount, Subscription


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


class SubscriptionSerializer(serializers.ModelSerializer):
    tariff = TariffDetailSerializer()
    discount = DiscountDetailSerializer()
    status_display = serializers.SerializerMethodField()

    def get_status_display(self, obj):
        task_status = obj.payment_task_status

        if not task_status:
            return obj.get_status_display()

        if task_status == 'FAILURE':
            return "При оплате произошла ошибка"
        elif task_status in ['PENDING', 'STARTED', 'RETRY']:
            return "Ожидание оплаты"

        return obj.get_status_display()

    class Meta:
        model = Subscription
        fields = ['id', 'expiration_date', 'status', 'status_display', 'tariff', 'discount']


class PaymentSerializer(serializers.Serializer):
    tariff_id = serializers.UUIDField(label='id тарифа')
    payment_system = serializers.ChoiceField(
        label='название платежной системы',
        choices=[settings.YOOMONEY, settings.STRIPE]
    )
