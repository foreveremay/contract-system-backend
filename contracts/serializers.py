from rest_framework import serializers
from .models import Contract, Client, CostItem, Category

# 【修正】將 CostItemSerializer 的定義，移到 ContractSerializer 前面
class CostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostItem
        fields = ['id', 'description', 'amount']

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
    # 現在當程式讀到這一行時，已經知道 CostItemSerializer 是什麼了
    cost_items = CostItemSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'name', 'contract_number',
            'type', 'status', 'amount',
            'start_date', 'end_date', 'is_stamped',
            'client', 'client_name',
            'category', 'category_name',
            'parent_contract',
            'cost_items',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'client': {'required': True},
            'category': {'required': False, 'allow_null': True},
            'parent_contract': {'required': False, 'allow_null': True},
            'start_date': {'required': False, 'allow_null': True},
            'end_date': {'required': False, 'allow_null': True},
        }

class ProfitMarginSerializer(serializers.Serializer):
    profit_a = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_b = serializers.DecimalField(max_digits=12, decimal_places=2)
    overall_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
