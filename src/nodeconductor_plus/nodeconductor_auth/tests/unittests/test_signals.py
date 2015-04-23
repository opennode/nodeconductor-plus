from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

from nodeconductor.structure import models as structure_models


class SignalsTest(TransactionTestCase):

    def test_first_customer_and_project_creation_on_user_creation(self):
        user = get_user_model().objects.create_user(username='test', password='test')

        customer = structure_models.Customer.objects.get(name=user.username)
        project = structure_models.Project.objects.get(name='My First Project', customer__name=user.username)
        self.assertTrue(customer.has_user(user, structure_models.CustomerRole.OWNER))
        self.assertTrue(project.has_user(user, structure_models.ProjectRole.ADMINISTRATOR))
