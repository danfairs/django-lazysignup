# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.utils.timezone
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        serialize=False,
                        verbose_name="ID",
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("password", models.CharField(verbose_name="password", max_length=128)),
                (
                    "last_login",
                    models.DateTimeField(
                        verbose_name="last login", null=True, blank=True
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        verbose_name="superuser status",
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                    ),
                ),
                (
                    "my_custom_field",
                    models.CharField(null=True, max_length=50, blank=True),
                ),
                (
                    "username",
                    models.CharField(
                        unique=True,
                        verbose_name="username",
                        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[\\w.@+-]+$", "Enter a valid username.", "invalid"
                            )
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        verbose_name="first name", max_length=30, blank=True
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        verbose_name="last name", max_length=30, blank=True
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        verbose_name="email address", max_length=254, blank=True
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        verbose_name="staff status",
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        verbose_name="active",
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        verbose_name="date joined", default=django.utils.timezone.now
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        to="auth.Group",
                        verbose_name="groups",
                        blank=True,
                        related_query_name="user",
                        related_name="user_set",
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        to="auth.Permission",
                        verbose_name="user permissions",
                        blank=True,
                        related_query_name="user",
                        related_name="user_set",
                        help_text="Specific permissions for this user.",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            # managers=[
            #     ('objects', django.contrib.auth.models.UserManager()),
            # ],
        ),
    ]
