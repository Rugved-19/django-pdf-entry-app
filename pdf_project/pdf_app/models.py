from django.db import models
class User(models.Model):  # <-- This should match
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_input = models.TextField()
    amount = models.IntegerField()
    total = models.IntegerField(default=0)  # ✅ Added default


    def __str__(self):
        return f"{self.raw_input} - {self.amount} - {self.total}"
