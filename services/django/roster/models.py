from django.db import models


class Person(models.Model):
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"
    MASTERS = "masters"
    DOCTORAL = "doctoral"
    NOT_STUDENT = "not_student"

    CLASS_CHOICES = (
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
        (MASTERS, 'Masters'),
        (DOCTORAL, 'Doctoral'),
        (NOT_STUDENT, 'Not a Student'),
    )

    first = models.CharField(blank=True, max_length=100)
    last = models.CharField(blank=True, max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15)
    classification = models.CharField(blank=True, max_length=15,
                                      choices=CLASS_CHOICES)

    class Meta:
        verbose_name_plural = 'people'

    def __str__(self):
        if self.first and self.last:
            return self.first + " " + self.last
        else:
            return self.phone