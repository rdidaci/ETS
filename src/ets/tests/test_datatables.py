import datetime

from django.utils import simplejson as json
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User

import ets.models
from ets.tests.utils import TestCaseMixin


class DatatablesTestCase(TestCaseMixin, TestCase):
    
    def setUp(self):
        "Hook method for setting up the test fixture before exercising it."        
        super(DatatablesTestCase, self).setUp()
        user_name = "dispatcher"
        self.client.login(username=user_name, password=user_name)
        self.user = User.objects.get(username=user_name)
    
    def test_table_stock_items(self):
        # All stock items
        warehouse = ets.models.Warehouse.objects.get(pk="ISBX003")
        response = self.client.get(reverse("table_stock_items", kwargs={"param_name": "wh_id"} ), data={'wh_id': warehouse.pk,})
        result = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        self.assertEqual(result["iTotalRecords"], warehouse.stock_items.count())

    def test_table_orders(self):
        # Orders related to user
        response = self.client.get(reverse("table_orders"))
        self.assertContains(response, 'OURLITORDER', status_code=200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        result = json.loads(response.content)
        self.assertEqual(result["iTotalRecords"], 1)

    def test_table_waybills(self):
        # All waybills
        response = self.client.get(reverse("table_waybills", kwargs={ 'filtering': 'user_related'}))
        result = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        self.assertEqual(result["iTotalRecords"], ets.models.Waybill.objects.count())

    def test_table_dispatch_waybills(self):
        # All dispatch waybills
        response = self.client.get(reverse("table_waybills", kwargs={ 'filtering': 'dispatches'}))
        result = json.loads(response.content)
        self.assertContains(response, 'ISBX00211A', status_code=200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        self.assertEqual(result["iTotalRecords"], ets.models.Waybill.dispatches(self.user).count())

    def test_table_reception_waybills(self):
        # All reception waybills
        person = ets.models.Person.objects.get(username=self.user.username)
        person.receive = True
        person.save()
        response = self.client.get(reverse("table_waybills", kwargs={ 'filtering': 'receptions'}))
        result = json.loads(response.content)
        self.assertContains(response, 'ISBX00311A', status_code=200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        self.assertEqual(result["iTotalRecords"], ets.models.Waybill.receptions(self.user).count())

    def test_table_validate_dispatch_waybills(self):
        # All waybills
        waybill_pk = 'ISBX00311A'
        waybill = ets.models.Waybill.objects.get(pk=waybill_pk)
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse("table_validate_waybill", kwargs={ 'filtering': 'validate_dispatch'}))
        result = json.loads(response.content)
        self.assertContains(response, waybill_pk, status_code=200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        self.assertEqual(result["iTotalRecords"], 2)
        waybill.validated=True
        waybill.save()
        response = self.client.get(reverse("table_validate_waybill", kwargs={ 'filtering': 'dispatch_validated'}))
        result = json.loads(response.content)
        self.assertContains(response, waybill_pk, status_code=200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        self.assertEqual(result["iTotalRecords"], 1)
        
    def test_table_validate_receipt_waybills(self):
        waybill_pk = 'ISBX00211A'
        waybill = ets.models.Waybill.objects.get(pk=waybill_pk)
        self.client.login(username='admin', password='admin')
        waybill.transport_dispach_signed_date = datetime.date.today()
        waybill.receipt_signed_date = datetime.date.today()
        waybill.save()
        response = self.client.get(reverse("table_validate_waybill", kwargs={ 'filtering': 'validate_receipt'}))
        result = json.loads(response.content)
        self.assertContains(response, waybill_pk, status_code=200)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        self.assertEqual(result["iTotalRecords"], 1)
        waybill.receipt_validated=True
        waybill.save()
        response = self.client.get(reverse("table_validate_waybill", kwargs={ 'filtering': 'receipt_validated'}))
        result = json.loads(response.content)
        self.assertContains(response, waybill_pk, status_code=200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        self.assertEqual(result["iTotalRecords"], 1)
