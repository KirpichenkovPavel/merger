# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('polyauth_remote', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LdapProxyPermissionInst',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('user', models.CharField(max_length=5, verbose_name='ID сотрудника')),
                ('type', models.CharField(max_length=32, choices=[('LOGIN', 'вход'), ('NOT_LOGIN', 'запрет входа'), ('LOGIN_AS', 'вход под чужим именем'), ('ADMIN', 'администрирование')], verbose_name='право')),
            ],
            options={
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
