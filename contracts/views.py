from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Contract, Client, Category, CostItem, Payment, Invoice
from .serializers import (
    ContractSerializer, ClientSerializer, CategorySerializer,
    CostItemSerializer, PaymentSerializer, InvoiceSerializer,
    ProfitMarginSerializer, SettlementDataSerializer, ContractSettlementSerializer
)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CostItemViewSet(viewsets.ModelViewSet):
    queryset = CostItem.objects.all()
    serializer_class = CostItemSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all().order_by('-created_at')
    serializer_class = ContractSerializer

    @action(detail=True, methods=['get'], url_path='settlement-data')
    def settlement_data(self, request, pk=None):
        contract_a = self.get_object()
        if contract_a.type != 'A':
            return Response({'error': 'Only Type A contracts can be settled.'}, status=status.HTTP_400_BAD_REQUEST)
        contracts_b = contract_a.sub_contracts.all()
        costs_a = contract_a.cost_items.all()
        b_contract_ids = contracts_b.values_list('id', flat=True)
        costs_b = CostItem.objects.filter(contract__id__in=b_contract_ids)
        serializer = SettlementDataSerializer(instance={
            'contract_a': contract_a,
            'contracts_b': contracts_b,
            'costs_a': costs_a,
            'costs_b': costs_b,
        })
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='settle')
    def settle(self, request, pk=None):
        contract = self.get_object()
        serializer = ContractSettlementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            contract.bonus_total_amount = data['bonus_total_amount']
            contract.bonus_split_a = data['bonus_split_a']
            contract.bonus_split_b = data['bonus_split_b']
            contract.status = Contract.ContractStatus.SETTLED
            contract.save()
            return Response(ContractSerializer(contract).data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        contract = self.get_object()
        if contract.type != 'A':
            return Response({'error': 'Analysis is only available for Type A contracts.'}, status=status.HTTP_400_BAD_REQUEST)
        margin_data = contract.calculate_profit_margins()
        if margin_data is None:
             return Response({'error': 'Failed to calculate margins.'}, status=500)
        serializer = ProfitMarginSerializer(data=margin_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)