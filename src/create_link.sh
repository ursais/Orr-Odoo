#! /bin/sh
cd link-addons

rm stock_analytic
ln -s ../account-analytic/stock_analytic stock_analytic

rm partner_aging
ln -s ../account-payment/partner_aging partner_aging

rm fieldservice
rm fieldservice_account
rm fieldservice_purchase
rm fieldservice_recurring
rm fieldservice_sale
rm fieldservice_skill
rm fieldservice_stock
rm fieldservice_isp_account
rm fieldservice_project
rm fieldservice_account_analytic
rm fieldservice_crm
rm fieldservice_vehicle
rm fieldservice_vehicle_stock
rm fieldservice_delivery
rm fieldservice_activity
rm fieldservice_location_builder
ln -s ../field-service/fieldservice fieldservice
ln -s ../field-service/fieldservice_account fieldservice_account
ln -s ../field-service/fieldservice_purchase fieldservice_purchase
ln -s ../field-service/fieldservice_recurring fieldservice_recurring
ln -s ../field-service/fieldservice_sale fieldservice_sale
ln -s ../field-service/fieldservice_skill fieldservice_skill
ln -s ../field-service/fieldservice_stock fieldservice_stock
ln -s ../field-service/fieldservice_isp_account fieldservice_isp_account
ln -s ../field-service/fieldservice_project fieldservice_project
ln -s ../field-service/fieldservice_account_analytic fieldservice_account_analytic
ln -s ../field-service/fieldservice_crm fieldservice_crm
ln -s ../field-service/fieldservice_vehicle fieldservice_vehicle
ln -s ../field-service/fieldservice_vehicle_stock fieldservice_vehicle_stock
ln -s ../field-service/fieldservice_delivery fieldservice_delivery
ln -s ../field-service/fieldservice_activity fieldservice_activity
ln -s ../field-service/fieldservice_location_builder fieldservice_location_builder

rm base_geoengine
rm base_google_map
rm geoengine_swisstopo
rm web_widget_google_marker_icon_picker
rm geoengine_bing
rm web_view_google_map
rm test_base_geoengine
rm base_geoengine_demo
ln -s ../geospatial/base_geoengine base_geoengine
ln -s ../geospatial/base_google_map base_google_map
ln -s ../geospatial/geoengine_swisstopo geoengine_swisstopo
ln -s ../geospatial/web_widget_google_marker_icon_picker web_widget_google_marker_icon_picker
ln -s ../geospatial/geoengine_bing geoengine_bing
ln -s ../geospatial/web_view_google_map web_view_google_map
ln -s ../geospatial/test_base_geoengine test_base_geoengine
ln -s ../geospatial/base_geoengine_demo base_geoengine_demo

rm hr_skill
ln -s ../hr/hr_skill hr_skill

rm osi_account_bank_statement
rm osi_analytic_segments
rm osi_analytic_segments_defaults
rm osi_analytic_segments_expenses
rm osi_analytic_segments_purchase
rm osi_analytic_segments_sales
rm osi_payment_method
rm osi_vendor_reference
rm expense_extended
ln -s ../osi-addons/expense_extended expense_extended
ln -s ../osi-addons/osi_account_bank_statement osi_account_bank_statement
ln -s ../osi-addons/osi_analytic_segments osi_analytic_segments
ln -s ../osi-addons/osi_analytic_segments_defaults osi_analytic_segments_defaults
ln -s ../osi-addons/osi_analytic_segments_expenses osi_analytic_segments_expenses
ln -s ../osi-addons/osi_analytic_segments_purchase osi_analytic_segments_purchase
ln -s ../osi-addons/osi_analytic_segments_sales osi_analytic_segments_sales
ln -s ../osi-addons/osi_payment_method osi_payment_method
ln -s ../osi-addons/osi_vendor_reference osi_vendor_reference

rm l10n_us_account_profile
rm l10n_us_form_1099
ln -s ../l10n-usa/l10n_us_account_profile l10n_us_account_profile
ln -s ../l10n-usa/l10n_us_form_1099 l10n_us_form_1099

rm stock_request_analytic
rm stock_request
rm stock_request_purchase
rm stock_request_direction
rm stock_request_submit
rm stock_request_picking_type
rm stock_putaway_method
ln -s ../stock-logistics-warehouse/stock_request_analytic stock_request_analytic
ln -s ../stock-logistics-warehouse/stock_request stock_request
ln -s ../stock-logistics-warehouse/stock_request_purchase stock_request_purchase
ln -s ../stock-logistics-warehouse/stock_request_direction stock_request_direction
ln -s ../stock-logistics-warehouse/stock_request_submit stock_request_submit
ln -s ../stock-logistics-warehouse/stock_request_picking_type stock_request_picking_type
ln -s ../stock-logistics-warehouse/stock_putaway_method stock_putaway_method

rm partner_fax
ln -s ../partner-contact/partner_fax partner_fax

rm web_timeline
rm web_environment_ribbon
ln -s ../web/web_timeline web_timeline
ln -s ../web/web_environment_ribbon web_environment_ribbon
