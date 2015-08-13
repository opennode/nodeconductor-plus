from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

from nodeconductor.structure import models as structure_models


class SignalsTest(TransactionTestCase):

    def test_first_customer_and_project_creation_on_user_creation(self):
        user = get_user_model().objects.create_user(username='test', password='test', full_name='test_user')

        customer = structure_models.Customer.objects.get(name=user.full_name)
        project = structure_models.Project.objects.get(name='Default', customer__name=user.full_name)
        self.assertTrue(customer.has_user(user, structure_models.CustomerRole.OWNER))
        self.assertTrue(project.has_user(user, structure_models.ProjectRole.ADMINISTRATOR))

    def test_first_customer_name_update_on_user_full_name_update(self):
        user = get_user_model().objects.create_user(username='test', password='test', full_name='test_user')
        self.assertTrue(structure_models.Customer.objects.filter(name=user.full_name).exists())
        user.full_name = 'new_full_name'
        user.save()
        self.assertTrue(structure_models.Customer.objects.filter(name=user.full_name).exists())
