from django.db import models

class Package(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    treePerPackage = models.IntegerField()

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.id
    

class CartQuantity(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    
class Address(models.Model):
    street1 = models.CharField(max_length=100)
    street2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.street1
    
class Bill(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    companyName = models.CharField(max_length=100, blank=True, null=True)
    phoneNumber = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)

    def __str__(self):
        return self.firstName
    
class Order(models.Model):
    bill = models.OneToOneField(Bill, on_delete=models.CASCADE)
    note = models.CharField(max_length=100, blank=True, null=True)
    approval = models.BooleanField(default=True)
    orderDate = models.DateTimeField(auto_now_add=True)
    
    
class OrderQuantity(models.Model):
    quantity = models.IntegerField()
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    
class Tracking(models.Model):
    status = models.CharField(max_length=100)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    approval = models.BooleanField(default=False)

class Certificate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    receiverName = models.CharField(max_length=100, blank=True, null=True)
    receiverEmail = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    orderQuantity = models.OneToOneField(OrderQuantity, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='media', blank=True, null=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    def __str__(self):
        if self.receiverName is None:
            return self.order.bill.firstName
        return self.receiverName
    
    def getTotalTrees(self):
        return self.orderQuantity.quantity * self.orderQuantity.package.treePerPackage