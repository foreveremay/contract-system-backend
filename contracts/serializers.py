from rest_framework import serializers
from .models import Contract, Client, CostItem, Category, Payment, Invoice

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class CostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostItem
        fields = ['id', 'contract', 'category', 'description', 'amount']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'brand_name', 'company_name', 'tax_id', 'phone', 'email']

class ContractSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.company_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    cost_items = CostItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    invoices = InvoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'name', 'contract_number',
            'type', 'status', 'amount',
            'start_date', 'end_date', 'is_stamped',
            'client', 'client_name',
            'category', 'category_name',
            'parent_contract',
            'bonus_total_amount', 'bonus_split_a', 'bonus_split_b',
            'cost_items', 'payments', 'invoices',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'client': {'required': True},
            'category': {'required': False, 'allow_null': True},
            'parent_contract': {'required': False, 'allow_null': True},
            'start_date': {'required': False, 'allow_null': True},
            'end_date': {'required': False, 'allow_null': True},
        }

# 【新】用於結算頁面一次性回傳所有資料
class SettlementDataSerializer(serializers.Serializer):
    contract_a = ContractSerializer()
    contracts_b = ContractSerializer(many=True)
    costs_a = CostItemSerializer(many=True)
    costs_b = CostItemSerializer(many=True)

# 【新】用於接收前端送來的結算資料
class ContractSettlementSerializer(serializers.Serializer):
    bonus_total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    bonus_split_a = serializers.DecimalField(max_digits=12, decimal_places=2)
    bonus_split_b = serializers.DecimalField(max_digits=12, decimal_places=2)

class ProfitMarginSerializer(serializers.Serializer):
    profit_a = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_b = serializers.DecimalField(max_digits=12, decimal_places=2)
    overall_profit = serializers.DecimalField(max_digits=12, decimal_places=2)