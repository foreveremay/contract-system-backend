from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Contract, Client, Category # 引入 Category
from .serializers import ContractSerializer, ClientSerializer, ProfitMarginSerializer, CategorySerializer # 引入 CategorySerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all().order_by('-created_at')
    serializer_class = ContractSerializer

# 【新】Category ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    """
    提供合約類型的 CRUD API。
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

@api_view(['GET'])
def contract_analysis_view(request, pk):
    try:
        contract = Contract.objects.get(pk=pk, type='A')
    except Contract.DoesNotExist:
        return Response({'error': 'Type A contract not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    margin_data = contract.calculate_profit_margins()
    if margin_data is None:
        return Response({'error': 'Calculation failed or not applicable.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProfitMarginSerializer(margin_data)
    return Response(serializer.data)
