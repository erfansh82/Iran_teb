from unittest import result
from py_code_meli import is_valid
from django.core.exceptions import ValidationError
from patients import models


# function for validations of Iranian national code
def national_code_validator(value):
    print(value)
    if  not is_valid(value):
        raise ValidationError(f'{str(value)}+ is not valid')


