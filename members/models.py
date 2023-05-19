from django.db import models
import random


"""
Classe porteFeuille possède une dictionnaire actions et un montant qui est de 10 000 $ lors de l'intialisation
"""
class PorteFeuille(models.Model):
    #member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    actions = models.JSONField(default=dict, null= True)
    montant = models.IntegerField(null=True, default=10000)



"""
Classe Member possède un nom, un id, un username et une porte feuille
"""
class Member(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phone = models.IntegerField(null=True)
    joined_date = models.DateField(auto_now_add=True, null=True)
    id = models.CharField(max_length=6, unique=True, primary_key=True)
    username = models.CharField(max_length=255, unique=True, null=True)
    portefeuille = models.ForeignKey(PorteFeuille, on_delete=models.CASCADE, null=True, blank=True)


    """
    Methode save aide a generer un id aléatoire pour chaque nouveau utilisateur
    """
    def save(self, *args, **kwargs):
        if not self.id:
            random_number = random.randint(100000, 999999)
            while Member.objects.filter(id=random_number).exists():
                random_number = random.randint(100000, 999999)
            self.id = str(random_number)
        super(Member, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


"""
Classe Action n'est pas utilise dans la version actuel de l'application
"""
class Action(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField(null=True)


''''
Apple Inc. (AAPL)
Microsoft Corporation (MSFT)
Alphabet Inc. (GOOGL)
Amazon.com, Inc. (AMZN)
Meta (Meta)
Tesla, Inc. (TSLA)
Visa Inc. (V)
Walt Disney Co. (DIS)
Coca-Cola Co. (KO)
Walmart Inc. (WMT)
McDonald's Corp. (MCD)
The Boeing Co. (BA)
IBM Corporation (IBM)

'''
