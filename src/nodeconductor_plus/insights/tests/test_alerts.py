from django.contrib.contenttypes.models import ContentType
import factory
from rest_framework import test

from nodeconductor.logging.models import Alert
from nodeconductor.structure import SupportedServices
from nodeconductor.structure.models import ServiceSettings, CustomerRole
from nodeconductor.structure.tests import factories


class CustomerAlertsTest(test.APITransactionTestCase):

    def test_when_customer_is_created_alerts_are_created(self):
        customer = factories.CustomerFactory()
        alert_types = (
            'customer_has_zero_services',
            'customer_has_zero_resources',
            'customer_has_zero_projects'
        )
        for alert_type in alert_types:
            self.assertTrue(self.has_alert(customer, alert_type))

    def test_when_service_created_alert_closed_when_service_deleted_alert_reopened(self):
        customer = factories.CustomerFactory()

        service = self.create_service(customer)
        self.assertFalse(self.has_alert(customer, 'customer_has_zero_services'))

        service.delete()
        self.assertTrue(self.has_alert(customer, 'customer_has_zero_services'))

    def test_when_project_created_alert_closed_when_project_deleted_alert_reopened(self):
        customer = factories.CustomerFactory()

        project = factories.ProjectFactory(customer=customer)
        self.assertFalse(self.has_alert(customer, 'customer_has_zero_projects'))

        project.delete()
        self.assertTrue(self.has_alert(customer, 'customer_has_zero_projects'))

    def create_service(self, customer):
        service_type, models = SupportedServices.get_service_models().items()[0]

        class ServiceFactory(factory.DjangoModelFactory):
            class Meta(object):
                model = models['service']

        settings = factories.ServiceSettingsFactory(customer=customer, type=service_type)
        service = ServiceFactory(customer=customer, settings=settings)
        return service

    def has_alert(self, customer, alert_type):
        try:
            content_type = ContentType.objects.get_for_model(customer)
            alert = Alert.objects.get(object_id=customer.id,
                                      content_type=content_type,
                                      alert_type=alert_type,
                                      closed__isnull=True)
            return True
        except Alert.DoesNotExist:
            return False
