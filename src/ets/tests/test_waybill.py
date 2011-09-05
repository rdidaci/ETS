### -*- coding: utf-8 -*- ####################################################

import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpResponseNotAllowed
from django.utils.datastructures import MultiValueDictKeyError 
from django.contrib.auth.forms import AuthenticationForm

import ets.models
from .utils import TestCaseMixin


class WaybillTestCase(TestCaseMixin, TestCase):
    
    def setUp(self):
        "Hook method for setting up the test fixture before exercising it."
        
        super(WaybillTestCase, self).setUp()
        
        self.client.login(username='admin', password='admin')
        self.user = User.objects.get(username="admin")
        self.dispatcher = User.objects.get(username="dispatcher")
        self.receipient = User.objects.get(username="recepient")
        self.waybill = ets.models.Waybill.objects.get(pk="ISBX00211A")
        self.reception_waybill = ets.models.Waybill.objects.get(pk="ISBX00311A")
        self.delivered_waybill = ets.models.Waybill.objects.get(pk="ISBX00312A")
        self.order = ets.models.Order.objects.get(pk='OURLITORDER')
        self.warehouse = ets.models.Warehouse.objects.get(pk="ISBX002")
        #self.lti = LtiOriginal.objects.get(pk="QANX001000000000000005217HQX0001000000000000984141")
        #self.stock = EpicStock.objects.get(pk="KARX025KARX0010000944801MIXMIXHEBCG15586")
     
    #===================================================================================================================
    # def tearDown(self):
    #    "Hook method for deconstructing the test fixture after testing it."
    #===================================================================================================================
    
    def test_serialize(self):
        """Checks methods serialize of waybill instance"""
        data = self.waybill.serialize()
        self.assertTrue(data.startswith('[{"pk": "ISBX00211A", "model": "ets.waybill", "fields": {"dispatcher_person": "ISBX0020000586"'))
    
    def test_compress(self):
        """Checks methods compress of waybill instance"""
        data = self.waybill.compress()
        self.assertTrue(isinstance(data, str))
    
    def test_login_form(self):
        self.client.logout()
        #Check login
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], AuthenticationForm))
    
    def test_index(self):
        """ tests index direct_to_template page """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
    
    def test_order_list(self):
        """ets.views.order_list"""
        self.client.login(username='dispatcher', password='dispatcher')
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)

    def test_order_detail(self):
        """Order's detail page"""
        response = self.client.get(reverse('order_detail', kwargs={'object_id': self.order.pk,}))
        self.assertEqual(response.status_code, 200)
    
    def test_waybill_view(self):
        """ets.views.waybill_view test"""
        response = self.client.get(reverse('waybill_view', kwargs={'waybill_pk': self.waybill.pk,}))
        self.assertEqual(response.status_code, 200)
    
    def test_waybill_search(self):
        """ets.views.waybill_search test"""
        #from ..forms import WaybillSearchForm
        # Empty search query
        self.client.login(username='dispatcher', password='dispatcher')
        response = self.client.post(reverse('waybill_search'))
        self.assertEqual(response.status_code, 200)
        self.assertTupleEqual(tuple(response.context['object_list']), 
                              (self.waybill, self.reception_waybill, self.delivered_waybill))
        #=======================================================================
        # form = WaybillSearchForm({ 'q' : 'ISBX00211A'})
        # response = self.client.post(reverse('waybill_search'), data={'form': form, 'q': 'ISBX00211A'})
        #=======================================================================
        # Search query with existing waybill code  
        response = self.client.get(reverse('waybill_search'), data={'q': 'ISBX00211A'})
        self.assertEqual(response.status_code, 200)
        self.assertTupleEqual(tuple(response.context['object_list']), (self.waybill,))
        # Search query with not existing waybill code 
        response = self.client.get(reverse('waybill_search'), data={'q': 'ISBX00211A1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)
        
         
    def test_create_waybill(self):
        """ets.views.waybill_create test"""
        from ..forms import DispatchWaybillForm
        
        self.client.login(username='dispatcher', password='dispatcher')        
        response = self.client.get(reverse('waybill_create', kwargs={'order_pk': self.order.pk,}))
        self.assertEqual(response.status_code, 200)
        
        #Check form
        form = response.context['form']
        self.assertTrue(isinstance(form, DispatchWaybillForm))
        #Check that destination has only one possible choice
        self.assertEqual(tuple(form.fields['destination'].queryset.all()), 
                         (ets.models.Warehouse.objects.get(pk="ISBX003"),))
        
        response = self.client.post(reverse('waybill_create', kwargs={'order_pk': self.order.pk,}), data={
            'loading_date': self.order.dispatch_date,
            'dispatch_date': self.order.dispatch_date,
            'destination': 'ISBX003',
            'transaction_type': u'WIT',
            'transport_type': u'02',
            'dispatch_remarks': 'You are funny guys!',
            'transport_sub_contractor': 'Arpaso',
            'transport_driver_name': 'Ahmed',
            'transport_driver_licence': 'KE23455',
            'transport_vehicle_registration': 'BG2345',
            
            'item-0-stock_item': 'testme0123',
            'item-0-number_of_units': '12',
            
            'item-TOTAL_FORMS': 5,
            'item-INITIAL_FORMS': 0,
            'item-MAX_NUM_FORMS': 5,
        })
        self.assertEqual(response.status_code, 302)
        
        #check created waybill and loading details
        waybill = ets.models.Waybill.objects.all()[1]
        self.assertEqual(waybill.loading_details.count(), 1)
    
    def test_waybill_edit(self):
        """ets.views.waybill_edit"""
        self.client.login(username='dispatcher', password='dispatcher')
        
        edit_url = reverse('waybill_edit', kwargs={
            'order_pk': self.order.pk, 
            'waybill_pk': self.waybill.pk,
        })
        response = self.client.get(edit_url)
        self.assertContains(response, "Edit waybill: ISBX00211A", status_code=200)
        
        today = datetime.date.today()
        
        data={
            'loading_date': today,
            'dispatch_date': today,
            'destination': 'ISBX0034',
            'transaction_type': u'WIT',
            'transport_type': u'02',
            'dispatch_remarks': 'You are funny guys!',
            'transport_sub_contractor': 'Arpaso',
            'transport_driver_name': 'Ahmed',
            'transport_driver_licence': 'KE23455',
            'transport_vehicle_registration': 'BG2345',
            
            'item-0-slug': 'ISBX00211A1',
            'item-0-waybill': 'ISBX00211A',
            'item-0-stock_item': 'testme0123',
            'item-0-number_of_units': '12',
            
            'item-TOTAL_FORMS': 5,
            'item-INITIAL_FORMS': 1,
            'item-MAX_NUM_FORMS': 5,
        }
        
        #let's check validation. Provide wrong destination warehouse
        response = self.client.post(edit_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['destination'].errors.as_text(), '* Select a valid choice. That choice is not one of the available choices.')
        
        data['destination'] = 'ISBX003'
        data['item-0-number_of_units'] = '10'    
        #Valid data
        response = self.client.post(edit_url, data=data)
        self.assertEqual(response.status_code, 302)
        
        #check updated waybill and loading details
        waybill = ets.models.Waybill.objects.get(pk=self.waybill.pk)
        self.assertEqual(waybill.loading_date, today)
        self.assertEqual(waybill.loading_details.get().number_of_units, 10)
        
        
    def test_waybill_finalize_dispatch(self):
        """ets.views.waybill_finalize_dispatch"""
        self.client.login(username='dispatcher', password='dispatcher')
        response = self.client.get(reverse('waybill_finalize_dispatch', kwargs={"waybill_pk": self.waybill.pk,}))
        self.assertEqual(response.status_code, 302)
        
        waybill = ets.models.Waybill.objects.get(pk="ISBX00211A")
        self.assertEqual(waybill.status, waybill.SIGNED)
    
    def test_waybill_reception(self):
        """ets.views.waybill_reception test"""
        from ..forms import WaybillRecieptForm
        
        self.client.login(username='dispatcher', password='dispatcher')
        
        path = reverse('waybill_reception', kwargs={'waybill_pk': self.reception_waybill.pk,})
        #check it with dispatching waybill. It must fail
        response = self.client.get(reverse('waybill_reception', kwargs={'waybill_pk': self.waybill.pk,}))
        self.assertEqual(response.status_code, 404)
        
        #Check proper waybill
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], WaybillRecieptForm))
        
        #Let's receive some invalid data (not enough items)
        data = {
            'item-TOTAL_FORMS': 1,
            'item-INITIAL_FORMS': 1,
            'item-MAX_NUM_FORMS': 5,
            
            'item-0-stock_item': 'anotherstock1234',
            'item-0-number_units_good': 25,
            'item-0-number_units_lost': 0,
            'item-0-units_lost_reason': '',
            'item-0-number_units_damaged': 0,
            'item-0-units_damaged_reason': '',
            
            'item-0-slug': 'ISBX00311A1',
            'item-0-waybill': 'ISBX00311A',
            
            'arrival_date': '2011-08-24',
            'start_discharge_date': '2011-08-24',
            'end_discharge_date': '2011-08-24',
            'container_one_remarks_reciept': '',
            'container_two_remarks_reciept': '',
            'distance': 5,
            'remarks': 'test remarks',
        }
        response = self.client.post(path, data=data)
        self.assertContains(response, "35.000 Units loaded but 25.000 units accounted for")
        
        #Let's say we lost 5 units without a reason
        data.update({
            'item-0-number_units_lost': 5,
        })
        
        response = self.client.post(path, data=data)
        self.assertContains(response, "You must provide a loss reason")
        
        # Let's provide a reason and damaged units
        data.update({
            'item-0-units_lost_reason': 'lsed',
            'item-0-number_units_damaged': 5,
        })
        
        response = self.client.post(path, data=data)
        self.assertContains(response, "You must provide a damaged reason")
        
        #Provide a reason of damage
        data.update({
            'item-0-units_damaged_reason': 'dsed',
        })
        
        response = self.client.post(path, data=data)
        # Now everything should be all right
        self.assertRedirects(response, self.reception_waybill.get_absolute_url())
        self.assertEqual(self.reception_waybill.get_receipt().remarks, 'test remarks')
    
    def test_waybill_delete(self):
        """ets.views.waybill_delete"""  
        self.client.login(username='dispatcher', password='dispatcher')
        col = ets.models.Waybill.objects.all().count()     
        response = self.client.get(reverse('waybill_delete', kwargs={'waybill_pk': self.waybill.pk,}))
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(ets.models.Waybill.objects.all().count(), col-1)
    
    def waybill_validate(self):
        """ets.views.waybill_validate"""
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse("waybill_validate_dispatch_form"))
        self.assertEqual(response.status_code, 200)
        
        
        response = self.client.get(reverse('waybill_validate_receipt_form'))
        self.assertEqual(response.status_code, 200)
        #Check there is no validated waybill
        self.assertEqual(response.context['validated_waybills'].count(), 0)
        
        #Validate some
        response = self.client.post(reverse('waybill_validate_receipt_form'), data={
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 1,
            'form-MAX_NUM_FORMS': '',
            'form-0-slug': 'isbx00311a',
            'form-0-validated': True,
        }, follow=True)
        self.assertRedirects(response, reverse('waybill_validate_receipt_form'))
        self.assertEqual(response.context['validated_waybills'].count(), 1)
        
    def test_viewLogView(self):
        """ets.views.viewLogView"""
        response = self.client.get(reverse('viewLogView'))
        self.assertEqual(response.status_code, 200)  
        
    #===================================================================================================================
    # def test_barcode_qr(self):
    #    """ets.views.barcode_qr"""
    #    response = self.client.get(reverse('barcode_qr', args=(self.waybill.pk,) ))
    #    self.assertEqual(response.status_code, 200) 
    #===================================================================================================================
               
    def test_waybill_finalize_receipt(self):
        """ets.views.waybill_finalize_receipt"""
        
        self.client.login(username='dispatcher', password='dispatcher')
        
        response = self.client.get(reverse('waybill_finalize_receipt', kwargs={'waybill_pk': 'ISBX00312A',}))
        self.assertRedirects(response, reverse("waybill_reception_list"))
            