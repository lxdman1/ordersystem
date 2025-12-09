from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_home, name='home'),
    path('home/', views.show_home, name='home'),
    path('menu/<int:table_number>/', views.show_menu, name='show_menu'),
    path('api/menu/', views.get_menu_api, name='get_menu_api'),
    path('create_order/<int:table_number>/', views.create_order, name='create_order'),
    path('my_order/<int:table_number>/', views.show_my_order, name='show_my_order'),
    path('kitchen/',views.show_kitchen, name='show_kitchen'),
    path('kitchen_history/',views.show_kitchen_history, name='show_kitchen_history'),
    path('api/get_all_order_api/', views.get_all_order_api, name='get_all_order_api'),
    path('api/get_desks_api/<int:table_num>/',views.get_desks_api, name='get_desks_api'),
    path('api/get_kitchen_history_api/', views.get_kitchen_history_api, name='get_kitchen_history_api'),
    path('kitchen/api/serve/<str:midOrderId>/', views.server_the_dish_api, name='server_the_dish_api'),
    path('orderManage/', views.show_orderManage, name='show_orderManage'),
    path('orderMessage/<int:table_num>/',views.show_orderMessage,name='show_orderMessage'),
    path('api/get_desk_message_api/<int:table_num>/',views.get_desk_message_api,name='get_desk_message_api'),
    path('orderManageAdd/<int:table_num>/',views.show_orderManageAdd,name='show_orderManageAdd'),
    path('api/set_midOrder_api/<str:midOrderId>/',views.set_midOrder_api,name='set_midOrder_api'),
    path('api/free_table_api/<int:table_num>/',views.free_table_api,name='free_table_api'),
    path('api/settlement_api/<int:table_num>/',views.settlement_api,name='settlement_api'),
    path('login/',views.show_login,name='show_login'),
]




