# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab', '0010_make_group_required_for_project'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='gitlabserviceprojectlink',
            unique_together=set([('service', 'project')]),
        ),
    ]
