from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from .models import MenuItem,midOrder,menuOrder
# Create your views here.
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
import json
import datetime
from django.db import transaction
def get_menu_api(request):
    """API接口：获取菜单数据"""
    menu_items = MenuItem.objects.filter(is_available=True)
    
    menu_data = [
        {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': float(item.price),  # 转换为float以便JSON序列化
            'category': item.category,
            'image': request.build_absolute_uri(item.image.url) if item.image else '',
        }
        for item in menu_items
    ]

    return JsonResponse(menu_data, safe=False)

def show_menu(request,table_number):
    return render(request, 'menu.html',{'table_number':table_number,})

#创建菜单，有则加菜，没有则新建
def create_order(request,table_number):
    
    if request.method == 'POST':
        data = json.loads(request.body)
        dishes = data.get('dishes', [])
        
        #客人结算但是要加菜的情况
        ate_add_orders = menuOrder.objects.filter(status__in=['finshed'],free=False, table_num=table_number).first()
        if ate_add_orders:
            print(ate_add_orders)
            ate_add_orders.status = 'ordered'
            ate_add_orders.save()
            exisiting_orders = ate_add_orders
        else:
            exisiting_orders = menuOrder.objects.filter(status__in=['ordered'], table_num=table_number).first()
        
        if exisiting_orders:
            total_add = 0
            for d in dishes:
                menu_item = MenuItem.objects.get(id=d['id'])
                quantity = d['quantity']
                total_add += menu_item.price * quantity
                midOrder.objects.create(order=exisiting_orders, menu_item=menu_item,quantity=quantity,price=menu_item.price,table_num=table_number)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "kitchen",
                {
                    "type": "send_order_update",
                    "data": {
                        "message": "订单加菜成功",
                    },
                },
            )
            
            return JsonResponse({'message': 'success', 'status':'加菜成功','order_id': exisiting_orders.order_number})
        else:
            menuorder = menuOrder.objects.create(order_number=datetime.datetime.now().strftime('%Y%m%d%H%M%S'),table_num = table_number,free=False)  # 新建订单
            for d in dishes:
                menu_item = MenuItem.objects.get(id=d['id'])
                midOrder.objects.create(order=menuorder, menu_item=menu_item, quantity=d['quantity'],price=menu_item.price,table_num=table_number)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "kitchen",
                {
                    "type": "send_order_update",
                    "data": {
                        "message": "订单创建成功",
                    },
                },
            )
            return JsonResponse({'message': 'success', 'status':'订单新建成功','order_id': menuorder.order_number}) 

def get_order_api(request,table_number):
    orders = menuOrder.objects.prefetch_related('items__menu_item').filter(table_num=table_number,status = 'ordered')
    context = {
        'orders': [
            {
                'id': o.id,
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
                'items': [
                    {'name': i.menu_item.name, 'image': request.build_absolute_uri(i.menu_item.image.url) if i.menu_item.image else '' , 'description': i.menu_item.description ,'quantity': i.quantity, 'price': float(i.menu_item.price),'status':i.status,'midOrderId':str(i.midOrderId)}
                    for i in o.items.all()
                ],
            }
            for o in orders
        ]
    }


    return context

def show_my_order(request,table_number):
    context = get_order_api(request,table_number)
    return render(request, 'my_order.html', {'order_json': json.dumps(context, ensure_ascii=False),'table_number':table_number,})

@login_required(login_url='/login/')
def show_kitchen_history(request):
    return render(request, 'kitchen_history.html')

@login_required(login_url='/login/')
def show_kitchen(request):
    return render(request, 'kitchen.html')

@login_required(login_url='/login/')
def show_orderManage(request):
    return render(request,'orderManage.html')

@login_required(login_url='/login/')
def show_orderMessage(request,table_num):
    return render(request, 'orderMessage.html',{'table_num':table_num})

@login_required(login_url='/login/')
def show_orderManageAdd(request,table_num):
    return render(request,'orderManageAdd.html',{'table_num':table_num})

@login_required(login_url='/login/')
def show_home(request):
    return render(request, 'home.html')

def show_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, '登录成功！')
            return redirect('/home/')  # 登录后跳转主页
        else:
            messages.error(request, '用户名或密码错误！')
            return redirect('/login/')
    return render(request, 'login.html')


def show_logout(request):
    logout(request)
    messages.info(request, '已退出登录')
    return redirect('login')

def get_all_order_api(request):
    orders = menuOrder.objects.prefetch_related('items__menu_item').filter(status = 'ordered').order_by('created_at')
    context = {
        'orders': [
            {
                'id': o.id,
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
                'items': [
                    {'order_id':o.id,'menu_id':i.menu_item.id,'name': i.menu_item.name,  'table_num': o.table_num ,'quantity': i.quantity,'image': request.build_absolute_uri(i.menu_item.image.url) if i.menu_item.image else '' ,'created_at':o.created_at.strftime('%Y-%m-%d %H:%M') ,  'status':i.get_status_display(),'midOrderId':i.midOrderId}
                    for i in o.items.all()
                ],
            }
            for o in orders
        ]
    }
    return JsonResponse(context, safe=False)

def get_kitchen_history_api(request):
    orders = menuOrder.objects.prefetch_related('items__menu_item').order_by('-created_at')
    context = {
        'orders': [
            {
                'id': o.id,
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
                'items': [
                    {'order_id':o.id,'menu_id':i.menu_item.id,'name': i.menu_item.name,  'table_num': o.table_num ,'quantity': i.quantity,'image': request.build_absolute_uri(i.menu_item.image.url) if i.menu_item.image else '' ,'created_at':o.created_at.strftime('%Y-%m-%d %H:%M') ,  'status':i.get_status_display(),'midOrderId':i.midOrderId}
                    for i in o.items.all()
                ],
            }
            for o in orders
        ]
    }
    return JsonResponse(context, safe=False)

def server_the_dish_api(request,midOrderId):
    midorder = get_object_or_404(midOrder, midOrderId=midOrderId)
    midorder.status = 'served'
    midorder.save()
    orders = menuOrder.objects.prefetch_related('items__menu_item').filter(status = 'ordered')
    for o in orders:
        if all((item.status == 'served' or item.status == 'finshed') for item in o.items.all()):
            o.status = 'served'
            o.save()
        
    return JsonResponse({'message': 'success'})




def get_desks_api(request,table_num):
    order = menuOrder.objects.filter(table_num=table_num,free=False).first()
    if order:
        return JsonResponse({'message': 'success', 'status':order.get_status_display(),'free':order.free})
    else:
        return JsonResponse({'message': 'success', 'status':'','free':True})
    
def get_desk_message_api(request,table_num):
    order = menuOrder.objects.prefetch_related('items__menu_item').filter(table_num=table_num,free=False).order_by('created_at').first()
    if order:
        context = {
        'orders': [
            {
                'id': order.id,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                'items': [
                    {'order_id':order.id,'menu_id':i.menu_item.id,'name': i.menu_item.name,  'table_num': order.table_num ,'quantity': float(i.quantity),'image': request.build_absolute_uri(i.menu_item.image.url) if i.menu_item.image else '' ,'created_at':order.created_at.strftime('%Y-%m-%d %H:%M') , 'price': float(i.menu_item.price),'discount':float(i.discount), 'status':i.get_status_display(),'midOrderId':i.midOrderId}
                    for i in order.items.all()
                ],
            }
            
        ]
    }
        return JsonResponse(context, safe=False)
    else:
        return JsonResponse({'free':True})
    
def set_midOrder_api(request,midOrderId):
    if request.method == 'POST':
        data = json.loads(request.body)
        set_dict = data.get('data')
        #'item_id': menuId, 'quantity': qty, 'discount': discount, 'status': status
        #order_id = set_dict.get('order_id')
        menu_item_id = set_dict.get('item_id')
        discount = set_dict.get('discount')
        status = set_dict.get('status')
        qty = set_dict.get('quantity')
        midorder = midOrder.objects.filter(midOrderId=midOrderId)
        if midorder:
            if qty == 0:
                midorder.delete()
            else:
                midorder.update(quantity=qty,discount=discount,status=status)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "kitchen",
                {
                    "type": "send_order_update",
                    "data": {
                        "message": "订单加菜成功",
                    },
                },
            )
            return JsonResponse({'message':'success'})   
        else:
            return JsonResponse({'message':'failed'})

def free_table_api(request,table_num):
    if request.method == 'POST':
        print('free_table_api')
        order = menuOrder.objects.prefetch_related('items__menu_item').filter(table_num=table_num).last()
        for i in order.items.all():
            if i.status != 'finshed' :
                return JsonResponse({'message':'failed'})

        order.free = True
        order.save()
        return JsonResponse({'message':'success'})

    return JsonResponse({'message': 'invalid_request'}, status=400)

def settlement_api(request,table_num):
    if request.method == 'POST':
        order = menuOrder.objects.prefetch_related('items__menu_item').filter(table_num=table_num,status__in=['served','ordered']).first()
        print(order)
        if order:
            sum = 0
            for i in order.items.all():
                if i.status == 'served':
                    sum += i.subtotal
                    i.status = 'finshed'
                    i.save()
            order.status = 'finshed'
            order.save()  
            return JsonResponse({'message':'结算成功','sum':sum})    
        else:
            order = menuOrder.objects.prefetch_related('items__menu_item').filter(table_num=table_num,status='finshed',free=False).first()
            if order:
                return JsonResponse({'message':'已结算，顾客未离开'})
            
            return JsonResponse({'message':'有菜品未完成'})
            
                    

           
            
            
            
       


