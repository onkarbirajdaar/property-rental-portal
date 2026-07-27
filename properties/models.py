from django.db import models
from django.contrib.auth.models import User

FURNISHED_CHOICES = [
    ("Furnished", "Furnished"),
    ("Semi-Furnished", "Semi-Furnished"),
    ("Unfurnished", "Unfurnished"),
]
PROPERTY_TYPES = [
    ("Apartment", "Apartment"),
    ("House", "House"),
    ("Villa", "Villa"),
    ("Studio", "Studio"),
]

STATUS_CHOICES = [
    ("Available", "Available"),
    ("Rented", "Rented"),
]


class Property(models.Model):
    owner = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="properties",
    null=True,
    blank=True,
)
    # owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    bhk = models.IntegerField()
    furnished = models.CharField(max_length=20, choices=FURNISHED_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Available")
    address = models.TextField()
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    description = models.TextField()
    contact_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to="properties/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Interest(models.Model):
    property = models.ForeignKey(
    Property,
    on_delete=models.CASCADE,
    related_name="interests",
    
)
    tenant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name=  "interests",
        
    )
    message =models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)    

    class Meta: 
            unique_together = ("property", "tenant")

    def __str__(self):
        return f"{self.tenant.username} interested in {self.property.title}"




class Wishlist(models.Model):
    property = models.ForeignKey(
    Property,
    on_delete=models.CASCADE,
    related_name="wishlists",
    
)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name=  "wishlists",
        
    )
    

    created_at = models.DateTimeField(auto_now_add=True)    

    class Meta: 
            unique_together = ("property", "user")

    def __str__(self):
        return f"{self.user.username} wishlisted {self.property.title}"

