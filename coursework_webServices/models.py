from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import datetime


class Professor(models.Model):
    name = models.CharField(max_length=30)
    professor_code = models.CharField(unique=True, max_length=3)

    def __str__(self):
        return u'%s %s \n' % (self.name, self.professor_code)


class Module(models.Model):
    semesters = [1, 2]
    module_code = models.CharField(max_length=3, unique=True)
    module_name = models.CharField(max_length=30)

    def __str__(self):
        return u'%s %s\n' % (self.module_code, self.module_name)


class ModuleInstance(models.Model):
    module = models.ForeignKey(to=Module, on_delete=models.CASCADE, default=None)
    module_semester = models.IntegerField(default=1, validators=[MaxValueValidator(2), MinValueValidator(1)])
    professor_names = models.ManyToManyField(Professor)
    academic_year = models.IntegerField(default=datetime.datetime.now().year)

    def __str__(self):
        return u'%s %d %d \n' % (
            self.module, self.module_semester, self.academic_year)


class Rating(models.Model):
    professor_code = models.ForeignKey(to=Professor, on_delete=models.CASCADE, default=None)
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    module = models.ForeignKey(to=ModuleInstance, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return u'%s %s %s \n' % (self.professor_code, self.rating, self.module)
