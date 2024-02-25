from django.urls import path

from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/units/search/', search_unit),  # GET
    path('api/units/<int:unit_id>/', get_unit_by_id),  # GET
    path('api/units/<int:unit_id>/update/', update_unit),  # PUT
    path('api/units/<int:unit_id>/delete/', delete_unit),  # DELETE
    path('api/units/create/', create_unit),  # POST
    path('api/units/<int:unit_id>/add_to_calculation/', add_unit_to_calculation),  # POST
    path('api/units/<int:unit_id>/image/', get_unit_image),  # GET
    path('api/units/<int:unit_id>/update_image/', update_unit_image),  # PUT

    # Набор методов для заявок
    path('api/calculations/search/', get_calculations),  # GET
    path('api/calculations/<int:calculation_id>/', get_calculation_by_id),  # GET
    path('api/calculations/<int:calculation_id>/update/', update_calculation),  # PUT
    path('api/calculations/<int:calculation_id>/update_status_user/', update_status_user),  # PUT
    path('api/calculations/<int:calculation_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/calculations/<int:calculation_id>/delete/', delete_calculation),  # DELETE
    path('api/calculations/<int:calculation_id>/delete_unit/<int:unit_id>/', delete_unit_from_calculation),  # DELETE
]