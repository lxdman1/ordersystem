from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('主菜', '主菜'),
        ('汤类', '汤类'),
        ('小吃', '小吃'),
        ('甜点', '甜点'),
        ('饮料', '饮料'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='菜品名称')
    description = models.TextField(verbose_name='描述')
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='价格')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='分类')
    image = models.ImageField(upload_to='images/', verbose_name='图片URL')
    is_available = models.BooleanField(default=True, verbose_name='是否可用')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '菜单项'
        verbose_name_plural = '菜单项'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name
    

class menuOrder(models.Model):
    STATUS_CHOICES = [
        ('ordered', '已下单'),
        ('served', '已上菜'),
        ('finshed','已结算'),
        ('cancelled', '已取消'),
    ]

    order_number = models.CharField(max_length=20, unique=True, verbose_name='订单号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='下单时间')
    table_num = models.IntegerField(verbose_name='桌号')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered', verbose_name='订单状态')
    free = models.BooleanField(default=True, verbose_name='是否空桌')



    def __str__(self):
        return f"订单 {self.order_number} "


class midOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', '已下单'),
        ('cooking', '制作中'),
        ('served', '已上菜'),
        ('cancelled', '已取消'),
        ('finshed', '已完成'),
    ]
    
    order = models.ForeignKey(menuOrder, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    midOrderId = models.UUIDField(default=uuid.uuid4, editable=False)
    table_num = models.IntegerField(verbose_name='桌号')
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=1, verbose_name='折扣')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='单价')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='小计')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')

    def save(self, *args, **kwargs):
        # 自动计算小计
        self.subtotal = self.price * self.quantity * self.discount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity} (订单号: {self.order.order_number})"



