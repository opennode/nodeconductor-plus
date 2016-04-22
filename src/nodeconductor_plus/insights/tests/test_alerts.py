import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
import factory
import mock
from rest_framework import test

from nodeconductor.cost_tracking.models import PriceEstimate
from nodeconductor.logging.models import Alert
from nodeconductor.structure import SupportedServices
from nodeconductor.structure.models import ServiceSettings
from nodeconductor.structure.tests import factories

from nodeconductor_plus.insights import tasks
from nodeconductor_plus.insights.tasks import check_customer_costs


class BaseAlertTest(object):
    def create_service(self, customer=None):
        if not customer:
            customer = factories.CustomerFactory()

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


class CustomerAlertsTest(BaseAlertTest, test.APITransactionTestCase):

    def test_initial_alerts(self):
        """
        When customer is created alerts are created.
        """
        customer = factories.CustomerFactory()
        alert_types = (
            'customer_has_zero_services',
            'customer_has_zero_resources',
            'customer_has_zero_projects'
        )
        for alert_type in alert_types:
            self.assertTrue(self.has_alert(customer, alert_type))

    def test_services_alert(self):
        """
        When service is created, alert is closed.
        When service is deleted, alert is reopened.
        """
        customer = factories.CustomerFactory()

        service = self.create_service(customer)
        self.assertFalse(self.has_alert(customer, 'customer_has_zero_services'))

        service.delete()
        self.assertTrue(self.has_alert(customer, 'customer_has_zero_services'))

    def test_projects_alert(self):
        """
        When project is created, alert is closed.
        When project is deleted, alert is reopened.
        """
        customer = factories.CustomerFactory()

        project = factories.ProjectFactory(customer=customer)
        self.assertFalse(self.has_alert(customer, 'customer_has_zero_projects'))

        project.delete()
        self.assertTrue(self.has_alert(customer, 'customer_has_zero_projects'))


@mock.patch('nodeconductor.structure.models.Service.get_backend')
class ServiceAlertTest(BaseAlertTest, test.APITransactionTestCase):

    def test_when_service_is_gone_task_is_skipped(self, mock_backend):
        service = self.create_service()
        service_str = service.to_string()
        service.delete()

        tasks.check_service_availability(service_str)
        self.assertFalse(mock_backend.called)

        tasks.check_service_availability(service_str)
        self.assertFalse(mock_backend.called)

        tasks.check_service_resources_availability(service_str)
        self.assertFalse(mock_backend.called)

    def test_when_service_is_unavailable_alert_is_created(self, mock_backend):
        service = self.create_service()

        mock_backend().ping.return_value = False
        tasks.check_service_availability(service.to_string())
        self.assertTrue(mock_backend.called)
        self.assertTrue(self.has_alert(service, 'service_unavailable'))

    def test_when_erred_service_responds_to_ping_it_is_recovered(self, mock_backend):
        service = self.create_service()
        service.settings.set_erred()
        service.settings.save()

        mock_backend().ping.return_value = True
        tasks.check_service_availability(service.to_string())
        self.assertFalse(self.has_alert(service, 'service_unavailable'))

        service.refresh_from_db()
        self.assertTrue(ServiceSettings.States.OK, service.settings.state)


@mock.patch('nodeconductor_plus.insights.tasks.alert_logger')
class CustomerCostsTest(BaseAlertTest, test.APITransactionTestCase):
    def test_when_cost_exceeded_alert_created(self, mocked_event_logger):
        customer = factories.CustomerFactory()
        self.create_price_estimates(customer, 10, 100)

        check_customer_costs(customer.uuid.hex)

        mocked_event_logger.customer_state.warning.assert_called_once_with(
            'This month estimated costs for customer {customer_name} exceeded',
            scope=customer,
            alert_type='customer_projected_costs_exceeded',
            alert_context={'customer': customer}
        )

    def test_when_cost_is_not_exceeded_alert_is_not_created(self, mocked_event_logger):
        customer = factories.CustomerFactory()
        self.create_price_estimates(customer, 10, 11)

        check_customer_costs(customer.uuid.hex)

        self.assertFalse(mocked_event_logger.customer_state.warning.called)

    def create_price_estimates(self, customer, prev, current):
        dt_now = datetime.datetime.now()
        dt_prev = dt_now - relativedelta(months=1)

        PriceEstimate.objects.create(scope=customer, month=dt_now.month, year=dt_now.year, total=current)
        PriceEstimate.objects.create(scope=customer, month=dt_prev.month, year=dt_prev.year, total=prev)
