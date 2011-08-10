
from django.conf import settings
from django.conf.urls.defaults import patterns, include, handler404, handler500
from django.contrib import databrowse
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail

from django.contrib import admin #@Reimport
admin.autodiscover()

from ets.models import LtiOriginal, Waybill, EpicStock
import ets.models

COMPAS_STATION = getattr(settings, "COMPAS_STATION", '')

#databrowse.site.register( Waybill )
#databrowse.site.register( EpicStock )
#databrowse.site.register( LtiOriginal )

info_dict_lti = {
    'queryset': LtiOriginal.objects.all()
}
info_dict_waybill = {
    'queryset': Waybill.objects.all()
}

info_dict_waybill_reception = {
    'queryset': Waybill.objects.all(),
    'template_name': 'waybill/reception_list.html'
}


urlpatterns = patterns("ets.views",
                        
    ( r'^$', login_required(direct_to_template), {
        'template': 'index.html',
    }, "index" ),
    
    #Order list
    ( r'^orders/(?P<warehouse_pk>[-\w]+)/$', "order_list", {}, "orders" ),
    ( r'^orders/$', "order_list", {}, "orders"),
    
    #Order detail
    ( r'^order/(?P<object_id>[-\w]+)/$', login_required(object_detail), {
        'queryset': ets.models.Order.objects.all(),
        'template_name': 'order/detail.html',
    }, "order_detail" ),
    
    #Waybill view                   
    ( r'^waybill/(?P<waybill_pk>[-\w]+)/$', 'waybill_view', {
        'queryset': ets.models.Waybill.objects.all(),
        "template_name": 'waybill/detail.html',
    }, "waybill_view" ),
    
    ( r'^waybill/viewlog/', "viewLogView", {}, "viewLogView" ),
    ( r'^waybill/create/(.*)/$', "waybillCreate", {}, "waybillCreate" ),
    ( r'^waybill/dispatch/$', "dispatch", {}, "dispatch" ),
    ( r'^waybill/edit/(?P<waybill_pk>[-\w]+)/$', "waybill_edit", {}, "waybill_edit" ),
    ( r'^waybill/findwb/$', "waybill_search", {}, "waybill_search" ),
    #===================================================================================================================
    # ( r'^waybill/import/$', "import_ltis", {}, "import_ltis" ),
    #===================================================================================================================
    
    ( r'^waybill/print_original_receipt/(?P<waybill_pk>[-\w]+)/$', "waybill_finalize_receipt", {
        'queryset': Waybill.objects.filter(status=Waybill.INFORMED)#destinationWarehouse__pk=COMPAS_STATION),
    }, "waybill_finalize_receipt" ),
    ( r'^waybill/print_original/(?P<waybill_pk>[-\w]+)/$', "waybill_finalize_dispatch", {
        'queryset': Waybill.objects.filter(status=Waybill.NEW, warehouse__pk=COMPAS_STATION),
    }, "waybill_finalize_dispatch" ),
    ( r'^waybill/receive/(?P<waybill_pk>[-\w]+)/$', "waybill_reception", {}, "waybill_reception" ),
    ( r'^waybill/receive/$', "object_list", {
        "template_name": 'waybill/reception_list.html',
        "queryset": Waybill.objects.filter(invalidated=False, recipient_signed_date__isnull=True),
    }, "waybill_reception_list" ),
    ( r'^waybill/test/$', 'object_list', info_dict_lti ),
    ( r'^waybill/validate/$', "direct_to_template", {'template': 'selectValidateAction.html'}, "waybill_validate_action" ),
    ( r'^waybill/validate_dispatch/$', "waybill_validate_dispatch_form", {}, "waybill_validate_dispatch_form" ),
    ( r'^waybill/validate_receipt_form/$', "waybill_validate_receipt_form", {}, "waybill_validate_receipt_form" ),
    ( r'^waybill/validate/(?P<waybill_pk>[-\w]+)/$', "waybill_validate_form_update", {
        'queryset': Waybill.objects.all(),
    }, "waybill_validate_form_update" ),
    ( r'^waybill/viewwb_reception/(?P<waybill_pk>[-\w]+)/$', "waybill_view_reception", {}, "waybill_view_reception" ),
    ( r'^waybill/commit_to_compas_receipt/$', "receiptToCompas", {}, "receiptToCompas" ),
    ( r'^waybill/commit_to_compas_dispatch_one/(?P<waybill_pk>[-\w]+)/$', "singleWBDispatchToCompas", 
      {}, "singleWBDispatchToCompas" ),
    ( r'^waybill/commit_to_compas_receipt_one/(?P<waybill_pk>[-\w]+)/$', "singleWBReceiptToCompas", 
      {}, "singleWBReceiptToCompas" ),
    ( r'^waybill/compass_waybill/$', "direct_to_template", {
        "template": 'compas/list_waybills_compas_all.html',
        "extra_context": {
            'waybill_list': Waybill.objects.filter(invalidated=False, sent_compas=True).all, 
            'waybill_list_rec': Waybill.objects.filter(invalidated=False, rec_sent_compas=True).all,
    }}, "compass_waybill" ),
    ( r'^waybill/invalidate_waybill/(?P<waybill_pk>[-\w]+)/$', "invalidate_waybill",{
        'queryset': Waybill.objects.all(),
    },"invalidate_waybill" ),
    ( r'^waybill/view_stock/$', "direct_to_template", {
        "template": 'stock/stocklist.html',
        "extra_context": {
            'stocklist': EpicStock.objects.all,
    }}, "view_stock" ),
    ( r'^waybill/report/ltis/$', "ltis_report", {}, "ltis_report" ),
    ( r'^waybill/report/select/$', "direct_to_template", {
        "template": 'reporting/select_report.html',
    }, "select_report" ),
    ( r'^waybill/report/dispatch/(.*)/$', "dispatch_report_wh",{},"dispatch_report_wh" ),
    ( r'^waybill/report/receipt/(.*)/(.*)/$', "receipt_report_wh", {}, "receipt_report_wh" ),
    ( r'^waybill/report/receipt/(.*)/$', "receipt_report_cons", {}, "receipt_report_cons" ),
    #===================================================================================================================
    # ( r'^waybill/images/qrcode/(.*)/$', "barcode_qr", {}, "barcode_qr" ),
    #===================================================================================================================
    ( r'^waybill/synchro/upload/', "post_synchronize_waybill", {}, "post_synchronize_waybill" ),
    
    #===================================================================================================================
    # ( r'^waybill/serialize/(?P<waybill_pk>[-\w]+)/$', "serialize" ),
    #===================================================================================================================
    ( r'^waybill/deserialize/$', "deserialize", {}, "deserialize" ),
    
    # download services
    ( r'^waybill/data/select/$', "select_data", {}, "select_data" ),
#=======================================================================================================================
#    ( r'^waybill/synchro/download/([-\w]+)/', "get_synchronize_waybill", {}, "get_synchronize_waybill" ),
#    ( r'^waybill/synchro/download2/', "get_synchronize_waybill2", {}, "get_synchronize_waybill2" ),
# 
#    ( r'^stock/synchro/download/([-\w]+)/', "get_synchronize_stock", {}, "get_synchronize_stock" ),
#    ( r'^lti/synchro/download/([-\w]+)/', "get_synchronize_lti", {}, "get_synchronize_lti" ),
#=======================================================================================================================
    # Additional data
    ( r'^all/synchro/download/file/', "get_all_data_download", {}, "get_all_data_download" ),
    ( r'^all/synchro/download/', "get_all_data", {}, "get_all_data" ),
    ( r'^all/download/stock_ets/', "get_wb_stock", {}, "get_wb_stock" ),
    
    ( r'^accounts/profile', "profile", {}, "profile" ),
    
)

urlpatterns += patterns('',
    ( r'^accounts/', include('django.contrib.auth.urls') ),
    ( r'^databrowse/(.*)', login_required(databrowse.site.root) ),
    ( r'^rosetta/', include('rosetta.urls') ),
    ( r'^admin/', include( admin.site.urls ) ),
    (r'^api/', include('ets.api.urls')),                    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )

    #===================================================================================================================
    # from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # urlpatterns += staticfiles_urlpatterns()
    #===================================================================================================================
