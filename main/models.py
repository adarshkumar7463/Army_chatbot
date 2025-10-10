from django.db import models

class Officer(models.Model):
    army_number = models.CharField(max_length=20, primary_key=True)
    full_name = models.CharField(max_length=100)
    rank = models.CharField(max_length=50)
    position = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    dob = models.DateField()
    enlistment_date = models.DateField()
    phone = models.CharField(max_length=10)
    email = models.EmailField()
    address = models.TextField()
    blood_group = models.CharField(max_length=5)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.rank} {self.full_name} ({self.army_number})"


class Education(models.Model):
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE,to_field='army_number', related_name='educations')
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    year_of_passing = models.IntegerField()
    grade = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.degree} - {self.officer.full_name}"


class Family(models.Model):
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE, to_field='army_number', related_name='family_members')
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    dob = models.DateField()
    occupation = models.CharField(max_length=100)
    contact = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.relation}) - {self.officer.full_name}"


class Award(models.Model):
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE, to_field='army_number', related_name='awards')
    award_name = models.CharField(max_length=100)
    reason = models.TextField()
    date_awarded = models.DateField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.award_name} - {self.officer.full_name}"