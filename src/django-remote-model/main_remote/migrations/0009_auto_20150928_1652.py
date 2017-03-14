# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0008_auto_20150917_1545'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='businessprocessparam',
            options={'managed': False, 'verbose_name_plural': 'значения шаблонов бизнес-процессов', 'verbose_name': 'значение шаблона бизнес-процесса'},
        ),
    ]
