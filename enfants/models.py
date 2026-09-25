from django.db import models


class Groupe(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Enfant(models.Model):
    nom = models.CharField(max_length=100)
    groupe = models.ForeignKey(Groupe, on_delete=models.PROTECT)
    date_naissance = models.DateField()

    def __str__(self):
        return self.nom

class Allergie(models.Model):
    enfant = models.ForeignKey(Enfant, on_delete=models.CASCADE)
    type_allergie = models.CharField(max_length=100)
    reaction = models.TextField()

    def __str__(self):
        return self.type_allergie

class ContactUrgence(models.Model):
    enfant = models.ForeignKey(Enfant, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    

    def __str__(self):
        return self.nom

class PersonneAutorisee(models.Model):
    enfant = models.ForeignKey(Enfant, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    relation = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    

    def __str__(self):
        return self.nom
