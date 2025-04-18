from django.db import models
from django.contrib.auth.models import User


class Person(models.Model): 
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  phone = models.CharField(max_length=20)
  location = models.CharField(max_length=200)
  image = models.ImageField(upload_to="uploads/person/", blank=True, null=True)

  def __str__(self):
    return self.user.email
  
class Merchant(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE) 
  store_name = models.CharField(max_length=100)
  store_link = models.CharField(max_length=300)
  category = models.CharField(max_length=100)

  def __str__(self):
    return self.store_name

class History(models.Model):
  file_name = models.CharField(max_length=255)
  uploaded = models.DateField(auto_now_add=True)
  type = models.CharField(max_length=50)
  size = models.CharField(max_length=50)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  event = models.BooleanField(default=False)

  def __str__(self):
    return self.id 
  
class Analysis(models.Model):
  customer_review = models.ImageField(upload_to="uploads/analysis/")
  # Fig
  overall_sentiment = models.ImageField(upload_to="uploads/analysis/")
  # Fig 2
  product_sentiment = models.ImageField(upload_to="uploads/analysis/")
  word_cloud = models.ImageField(upload_to="uploads/analysis/")
  # Fig 3
  positive_sentiment = models.ImageField(upload_to="uploads/analysis/")
  history = models.ForeignKey(History, on_delete=models.CASCADE)

  def __str__(self):
    return f"{self.customer_review}"