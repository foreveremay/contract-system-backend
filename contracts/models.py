from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

class Client(models.Model):
    brand_name = models.CharField(max_length=255, verbose_name='品牌名稱', blank=True, null=True)
    company_name = models.CharField(max_length=255, verbose_name='公司名稱', unique=True)
    tax_id = models.CharField(max_length=20, blank=True, null=True, verbose_name='統一編號')
    phone = models.CharField(max_length=50, blank=True, verbose_name='聯絡電話')
    email = models.EmailField(blank=True, verbose_name='Email')
    def __str__(self):
        return self.company_name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='類型名稱')
    class Meta:
        verbose_name = "合約類型"
        verbose_name_plural = "合約類型"
    def __str__(self):
        return self.name

class Contract(models.Model):
    class ContractType(models.TextChoices):
        A = 'A', _('Type A (主合約)')
        B = 'B', _('Type B (追加合約)')
    class ContractStatus(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', _('進行中')
        OVERDUE = 'OVERDUE', _('逾時')
        CLOSED = 'CLOSED', _('已結案')
        SETTLED = 'SETTLED', _('已結算')

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contracts', verbose_name='客戶')
    parent_contract = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_contracts')
    name = models.CharField(max_length=255, verbose_name='合約名稱')
    contract_number = models.CharField(max_length=100, blank=True, verbose_name='合約編號')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts', verbose_name='合約類型')
    type = models.CharField(max_length=1, choices=ContractType.choices, default=ContractType.A, verbose_name='主/追加')
    status = models.CharField(max_length=20, choices=ContractStatus.choices, default=ContractStatus.IN_PROGRESS, verbose_name='合約狀態')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='合約金額')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_stamped = models.BooleanField(default=False)
    
    bonus_total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bonus_split_a = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bonus_split_b = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def calculate_profit_margins(self):
        if self.type != self.ContractType.A: return None
        costs_a = self.cost_items.aggregate(total=Sum('amount'))['total'] or 0
        b_contracts = self.sub_contracts.filter(type=self.ContractType.B)
        total_b_amount, total_b_costs = 0, 0
        for b in b_contracts:
            total_b_amount += b.amount
            total_b_costs += b.cost_items.aggregate(total=Sum('amount'))['total'] or 0
        profit_b = total_b_amount - total_b_costs
        profit_a = self.amount - costs_a - total_b_amount
        overall_profit = self.amount - costs_a - total_b_costs
        return {'profit_a': profit_a, 'profit_b': profit_b, 'overall_profit': overall_profit}

class CostItem(models.Model):
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE, related_name='cost_items')
    category = models.CharField(max_length=100, blank=True, verbose_name='成本分類')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self):
        return f"{self.description} - ${self.amount}"

class Payment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField(verbose_name='付款日期')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='付款金額')
    method = models.CharField(max_length=50, blank=True, verbose_name='付款方式')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.contract.name} - Payment of ${self.amount}"

class Invoice(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=100, unique=True, verbose_name='發票號碼')
    date = models.DateField(verbose_name='開票日期')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='發票金額')
    is_issued = models.BooleanField(default=True, verbose_name='是否已開立')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.contract.name}"