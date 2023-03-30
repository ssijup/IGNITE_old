from django.db import models




STATUS_CHOICES = (
    ('Pending' , 'Pending'),
    ('Order Cancelled', 'Order Cancelled'),
    ('Return', 'Return'),
    ('Packed', 'Packed'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    )       


STATE_CHOICES = (
    ('KERALA' , 'KERALA'),
    ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('BR', 'Bihar'),
    ('Chandigarh', 'Chandigarh'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('Delhi', 'Delhi'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Ladakh', 'Ladakh'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Puducherry', 'Puducherry'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('TNTamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
)

PAYMENT_METHOD_CHOICES = (
        ('Razor Pay', 'Razor Pay'),
        ('PayPal', 'PayPal'),
        ('Cash on Delivery', 'Cash on Delivery'),
    )

GENDER_CHOICE=(
        ('Male','Male'),
        ('Female','Female'),
        ('Other','Other')
    )

# Create your models here.


class Userdetails(models.Model):
    user_name = models.CharField(max_length=50)
    user_email = models.CharField(max_length=100)
    user_password = models.CharField(max_length=50)
    phone_number=models.PositiveBigIntegerField(null=False, blank=False, default=1)
    gender=models.CharField(max_length=25,choices=GENDER_CHOICE,null=True,blank=True)
    u_active = models.BooleanField(default=True)
    def __str__(self): 
        return self.user_name 



class Category(models.Model):
    cate_name = models.CharField(max_length=100)
    catewise_dicount_price=models.PositiveIntegerField(blank=True,null=True)
    
    def __str__(self): 
        return self.cate_name 
    
    

class Subcategory(models.Model):
    subcategory_name=models.CharField(max_length=150)
    sub_catefor=models.ForeignKey(Category,on_delete=models.CASCADE)

    def __str__(self):
        return self.subcategory_name
    

class Variants(models.Model):
    varient_name=models.CharField(max_length=150)

    def __str__(self):
        return self.varient_name


# class Variantoptions(models.Model):
#     voption_key=models.ForeignKey(Products,on_delete=)
#     variantoption_name=models.CharField(max_length=150)
#     #variantoption_for=models.ForeignKey(Variants,on_delete=models.CASCADE)
#     price=models.PositiveIntegerField()
#     product_stock=models.PositiveIntegerField(blank=True,null=True)

#     def __str__(self):
#         return self.variantoption_name 

class Products(models.Model):
    book_title = models.CharField(max_length=100)
    #author = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    #product_stock=models.PositiveIntegerField(blank=True,null=True)
    #price = models.IntegerField()
    image = models.ImageField(upload_to='prod_images',blank=True,null=True)
    p_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    p_subcategory_for=models.ForeignKey(Subcategory,on_delete=models.CASCADE,blank=True,null=True)
    p_variant_for=models.ForeignKey(Variants,on_delete=models.CASCADE,blank=True,null=True)
    #p_variantoption_for=models.ManyToManyField(Variantoptions)
    #p_variantoption_for=models.ForeignKey(Variantoptions,on_delete=models.CASCADE,blank=True,null=True)

    # def get_variant_options(self):
    #     return ", ".join([str(vo.variantoption_name) for vo in self.variant_options.all()])
    def get_variant_options(self):
        return self.variant_options.all()
    
    def get_variant_options_price(self):
        return ", ".join([str(vo.price) for vo in self.variant_options.all()])
    
    def get_default_price(self):
        variant_option = self.variant_options.all()
        if variant_option:
            return variant_option[0] 
        else:
            return None

    # def cate_dicount(self):

        

        
    def get_variantoption_price(self):
        variant_option = self.variant_options.first()
        if variant_option:
            return variant_option.price
        else:
            return None
        
    def get_variantoption_discount_by_cateprice(self):
        variant_option = self.variant_options.first()
        if variant_option:
            return variant_option.discount_price
        else:
            return None
        
    def get_variantoption_id(self):
        variant_option = self.variant_options.first()
        if variant_option:
            return variant_option.id
        else:
            return None
    
    def get_multipleimages(self):
        multi_imge=self.multiple_images.all()
        return multi_imge


# from rest_framework import serializers


# class ProductsSerializer(serializers.Serializer):
#     book_title = serializers.CharField(max_length=100)
#     description = serializers.CharField(max_length=1000)
#     image = serializers.ImageField()
#     p_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
#     p_subcategory_for = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all(), allow_null=True, required=False)
#     p_variant_for = serializers.PrimaryKeyRelatedField(queryset=Variants.objects.all(), allow_null=True, required=False)


# class ProductsSerializer(serializers.Serializer):
#     book_title = serializers.CharField(max_length=100)
#     description = serializers.CharField(max_length=1000)
#     image = serializers.ImageField()
#     p_category = serializers.ForeignKey(Category, on_delete=models.CASCADE)
#     p_subcategory_for=serializers.ForeignKey(Subcategory,on_delete=models.CASCADE,blank=True,null=True)
#     p_variant_for=serializers.ForeignKey(Variants,on_delete=models.CASCADE,blank=True,null=True)




class Variantoptions(models.Model):
    voption_vartaint_key=models.ForeignKey(Variants,on_delete=models.CASCADE)
    voption_prod_key=models.ForeignKey(Products,on_delete=models.CASCADE,blank=True,null=True, related_name='variant_options')
    variantoption_name=models.CharField(max_length=150)
    #variantoption_for=models.ForeignKey(Variants,on_delete=models.CASCADE)
    price=models.PositiveIntegerField()
    product_stock=models.PositiveIntegerField(blank=True,null=True)
    unit=models.CharField(max_length=5,blank=True,null=True)
    discount_price=models.PositiveIntegerField(blank=True,null=True)

    def __str__(self):
        return self.variantoption_name 


    def default_variantprice(self):
        return self.price

    # def __str__(self):
    #     return self.book_title 
    


class Productimages(models.Model):
    prod_img_key=models.ForeignKey(Products,on_delete=models.CASCADE,blank=True,null=True,related_name='multiple_images')
    multiple_image=models.ImageField(upload_to='prod_images')



class Cart(models.Model):
    user = models.ForeignKey(Userdetails, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    c_product_vatiantoption_key=models.ForeignKey(Variantoptions,on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.PositiveIntegerField()

    # def total_price(self):
    #     value=0
    #     shipping_price=40
    #     for i in self:
    #         total=i.quantity*i.c_product_vatiantoption_key.price
    #         value=total+value
    #     total_amount=shipping_price+value
    #     return total_amount
    @property
    def subtotal(self):
        if self.c_product_vatiantoption_key.voption_prod_key.p_category.catewise_dicount_price:
            return  int(self.c_product_vatiantoption_key.discount_price)*int(self.quantity)
        
        return int(self.c_product_vatiantoption_key.price)*int(self.quantity)


class Useraddress(models.Model):
    mainuser = models.ForeignKey(Userdetails,on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    mobnumber = models.BigIntegerField(default=0)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(choices=STATE_CHOICES,max_length=150)
    landmark = models.CharField(max_length=300)
    pincode = models.IntegerField()



class Payment(models.Model):
    payment_user=models.ForeignKey(Userdetails,on_delete=models.CASCADE)
    payment_amount=models.FloatField(blank=True,null=True)
    payment_status=models.BooleanField(default=False)
    payment_method =models.CharField(max_length=200, choices=PAYMENT_METHOD_CHOICES,default='default_payment_method')
    
    def __str__(self):
        return self.payment_method
       

    
class Order(models.Model):
    name=models.ForeignKey(Userdetails,on_delete=models.CASCADE)
    product=models.ForeignKey(Products,on_delete=models.CASCADE)
    address=models.ForeignKey(Useraddress,on_delete=models.CASCADE)
    order_date=models.DateTimeField(auto_now_add=True)
    payment_type=models.CharField(max_length=150,default='Cash on delivery')
    order_status=models.CharField(max_length=150,choices=STATUS_CHOICES,default='Pending')
    order_payment_key=models.ForeignKey(Payment,on_delete=models.CASCADE,blank=True,null=True)
    ordered_product_quantity=models.PositiveIntegerField(null=True,blank=True)
    ordered_product_price=models.PositiveIntegerField(null=True,blank=True)
    

    def __str__(self): 
        return self.order_status 

class Coupon(models.Model):
    coupon_name=models.CharField(max_length=200)
    expiry_at=models.BooleanField(default=True)
    coupon_dis_amount=models.PositiveIntegerField(default=100)
    coupon_minmun_amount=models.PositiveIntegerField(default=1000)


class BannerVedio(models.Model):
    banVedio=models.ImageField(upload_to='banVedio',default='I')
    description=models.CharField(max_length=250,blank=True,null=True,default='No descrition added]')







    


