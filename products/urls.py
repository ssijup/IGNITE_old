from django.urls import path,include
from .import views

urlpatterns =[
    path("",views.index_3_home,name = "index_3_home"),
    path('user_login',views.user_login, name = 'user_login'),
    path('user_signup/',views.user_signup,name = "user_signup"),
    path('user_login',views.user_login, name = 'user_login'),
    path('user_logout/',views.user_logout,name="user_logout"),

    path('admin_login/',views.admin_login,name = 'admin_login'),
    path('admin_userlist/',views.admin_userlist,name = 'admin_userlist'),

    path('admin_addproducts/',views.admin_addproducts,name = 'admin_addproducts'),
    path('admin_productslist/',views.admin_productslist,name = 'admin_productslist'),
    path('shop_list_left_books/',views.shop_list_left_books,name = 'shop_list_left_books'),
    path('product_details',views.product_details,name = 'product_details'),
    
    path('admin_logout/',views.admin_logout,name = 'admin_logout'),
    path('admin_addcategory/',views.admin_addcategory,name = 'admin_addcategory'),
    path('admin_categorylist/',views.admin_categorylist,name = 'admin_categorylist'),
    path('userblock/',views.userblock,name = 'userblock'),
    path('admin_updateuser/',views.admin_updateuser,name = 'admin_updateuser'),
    path('admin_editproducts/',views.admin_editproducts,name = 'admin_editproducts'),
    path('admin_editcategory/',views.admin_editcategory,name = 'admin_editcategory'),
    path('admin_deletecategory/',views.admin_deletecategory,name = 'admin_deletecategory'),
    path('admin_deleteproduct/',views.admin_deleteproduct,name = 'admin_deleteproduct'),
    path('admin_addmultiple_image/',views.admin_addmultiple_image,name = 'admin_addmultiple_image'),

   

    path('admin_dashboard/',views.admin_dashboard, name = 'admin_dashboard'),

    #cart
    path('create_cart/',views.create_cart, name = 'create_cart'),
    path('cart_table/',views.cart_table, name = 'cart_table'),
    path('cart_deleteproduct/',views.cart_deleteproduct, name= 'cart_deleteproduct'),

    path('pluscart/',views.pluscart),
    path('minuscart/',views.minuscart),


    #user address
    path('add_address',views.add_address, name = 'add_address'),
    path('address_checkout',views.address_checkout, name = 'address_checkout'),

    #checkout
    path('checkout_summary/',views.checkout_summary, name = 'checkout_summary'),
    path('otp_login/',views.otp_login, name = 'otp_login'),
    path('otp_login_inor',views.otp_login_inor, name = 'otp_login_inor'),
    path('user_otp_check',views.user_otp_check, name = 'user_otp_check'),



    #p oder
    path('place_order/',views.place_order, name = 'place_order'),
    path('user_order/',views.user_order, name = 'user_order'),
    path('order_thanku',views.order_thanku, name = 'order_thanku'),
    path('admin_orderlist',views.admin_orderlist, name = 'admin_orderlist'),
    path('user_cancellation',views.user_cancellation, name = 'user_cancellation'),
    path('user_returnproduct',views.user_returnproduct, name = 'user_returnproduct'),
    path('user_manageaccount',views.user_manageaccount, name = 'user_manageaccount'),
    path('user_editprofile',views.user_editprofile, name = 'user_editprofile'),
    path('user_profile',views.user_profile, name = 'user_profile'),
    path('user_aboutus',views.user_aboutus, name = 'user_aboutus'),
    path('user_contact',views.user_contact, name = 'user_contact'),





    #FILTER BY PRICE     
    path('filter_byprice/',views.filter_byprice, name = 'filter_byprice '),

    #admin chart and graph
    path('admin_chart/',views.admin_chart, name = 'admin_chart '),


    #admin category
    path('admin_updateorderstatus',views.admin_updateorderstatus, name = 'admin_updateorderstatus'),
    path('admin_subcategorylist/',views.admin_subcategorylist, name = 'admin_subcategorylist'),
    path('admin_addsubcategory/',views.admin_addsubcategory, name = 'admin_addsubcategory'),
    path('admin_variantlist/',views.admin_variantlist, name = 'admin_variantlist'),
    path('admin_addvarient/',views.admin_addvarient, name = 'admin_addvarient'),
    path('admin_addvariantoptions/',views.admin_addvariantoptions, name = 'admin_addvariantoptions'),
    path('admin_variantoptionlist/',views.admin_variantoptionlist, name = 'admin_variantoptionlist'),
    path('admin_delete_variantoption/',views.admin_delete_variantoption, name = 'admin_delete_variantoption'),
    path('admin_addvariantoptions/',views.admin_addvariantoptions, name = 'admin_addvariantoptions'),
    path('admin_editproduct_variantoptions/',views.admin_editproduct_variantoptions, name = 'admin_editproduct_variantoptions'),
    path('admin_deleteproduct_variantoptions/',views.admin_deleteproduct_variantoptions, name = 'admin_deleteproduct_variantoptions'),
    path('admin_editvariant/',views.admin_editvariant, name = 'admin_editvariant'),
    path('admin_deletevariant/',views.admin_deletevariant, name = 'admin_deletevariant'),
    path('admin_editmultiple_image/',views.admin_editmultiple_image, name = 'admin_editmultiple_image'),
    path('admin_delete_multipleimage/',views.admin_delete_multipleimage, name = 'admin_delete_multipleimage'),
    path('admin_addVedioBanner/',views.admin_addVedioBanner, name = 'admin_addVedioBanner'),
    path('adnin_VedioBannerList/',views.adnin_VedioBannerList, name = 'adnin_VedioBannerList'),
    path('admin_addcategory_discount/',views.admin_addcategory_discount, name = 'admin_addcategory_discount'),


   
   # coupon and sales report
    path('admin_addcoupon/',views.admin_addcoupon, name = 'admin_addcoupon'),
    path('admin_salesreport/',views.admin_salesreport, name = 'admin_salesreport'),
    path('admin_couponlist/',views.admin_couponlist, name = 'admin_couponlist'),
    path('delete_coupon/',views.delete_coupon, name = 'delete_coupon'),


    # path('coupon_dis_totalamount/',views.coupon_dis_totalamount, name = 'coupon_dis_totalamount'),




    #variant option ajax
    path('product_variantoption_selecting/',views.product_variantoption_selecting, name = 'product_variantoption_selecting'),
    path('filter_products_byprice/',views.filter_products_byprice, name = 'filter_products_byprice'),
    path('search_products/',views.search_products, name = 'search_products'),
    path('filter_bycategory/',views.filter_bycategory, name = 'filter_bycategory'),



#payment - razorpay
    path('razorpay_payment/',views.razorpay_payment, name = 'razorpay_payment'),

    path('venue_pdf/',views.venue_pdf, name = 'venue_pdf'),
    path('venue_csv/',views.venue_csv, name = 'venue_csv'),





]