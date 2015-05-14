from django.contrib.auth import get_user_model

from nodeconductor.structure import models as structure_models
from .models import AuthProfile


def create_auth_profile(sender, instance=None, created=False, **kwargs):
    if created:
        AuthProfile.objects.create(user=instance)


def create_user_first_customer_and_project(sender, instance=None, created=False, **kwargs):
    if not created:
        return

    user = instance
    customer = structure_models.Customer.objects.create(name=user.full_name, native_name=user.full_name)
    customer.add_user(user, structure_models.CustomerRole.OWNER)
    project = structure_models.Project.objects.create(customer=customer, name='My First Project')
    project.add_user(user, structure_models.ProjectRole.ADMINISTRATOR)


def update_user_first_customer_name_on_user_name_change(sender, instance=None, created=False, **kwargs):
    if instance.id is None:
        return

    new_user = instance
    old_user = get_user_model().objects.get(id=instance.id)
    if new_user.full_name != old_user.full_name:
        structure_models.Customer.objects.filter(name=old_user.full_name).update(name=new_user.full_name)
