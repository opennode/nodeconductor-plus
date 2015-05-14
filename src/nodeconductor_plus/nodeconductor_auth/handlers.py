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
    if created:
        return

    if instance.full_name != instance._old_values['full_name']:
        for customer in structure_models.Customer.objects.filter(name=instance._old_values['full_name']):
            if customer.has_user(instance, structure_models.CustomerRole.OWNER):
                customer.name = instance.full_name
                customer.save()
