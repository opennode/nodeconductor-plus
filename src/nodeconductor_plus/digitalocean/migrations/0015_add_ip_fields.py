# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def copy_ip_address_to_external_ips(apps, schema_editor):
    Droplet = apps.get_model('digitalocean', 'Droplet')
    for droplet in Droplet.objects.all():
        droplet.external_ips = droplet.ip_address
        droplet.save(update_fields=['external_ips'])


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0014_droplet_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='droplet',
            name='external_ips',
            field=models.GenericIPAddressField(null=True, protocol='IPv4', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='droplet',
            name='internal_ips',
            field=models.GenericIPAddressField(null=True, protocol='IPv4', blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(copy_ip_address_to_external_ips),
    ]
