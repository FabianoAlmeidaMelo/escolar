# coding: utf-8

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
)

SEXO = (
    (1, "M"),
    (2, "F"),
    )

# 
