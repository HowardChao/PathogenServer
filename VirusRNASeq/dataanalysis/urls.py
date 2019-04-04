from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from dataanalysis import views

urlpatterns = [
    path('<slug:slug_project>/reference-mapping/settings', views.reference_mapping_whole_dataanalysis, name='reference_mapping_dataanalysis_home'),
    # path('<slug:slug_project>/de-novo-assembly/settings', views.whole_dataanalysis, name='de_novo_assembly_dataanalysis_home'),
    path('<slug:slug_project>/reference-mapping/data-upload', views.BasicUploadView.as_view(), name='reference_mapping_dataanalysis_data_upload'),
    path('<slug:slug_project>/de-novo-assembly/data-upload', views.BasicUploadView.as_view(), name='de_novo_assembly_dataanalysis_data_upload'),
    path('result/<slug:slug_project>/', views.show_result, name="dataanalysis_result"),
    path('result/<slug:slug_project>/reference-mapping/overview/',
         views.reference_mapping_show_result_overview, name="reference_mapping_dataanalysis_result_overview"),
    # path('result/<slug:slug_project>/de-novo-assembly/overview/',
    #      views.show_result_overview, name="de_novo_assembly_dataanalysis_result_overview"),
    path('result/<slug:slug_project>/reference-mapping/current-status/',
         views.reference_mapping_current_status, name="reference_mapping_dataanalysis_result_current_status"),
    # path('result/<slug:slug_project>/de-novo-assembly/current-status/',
    #      views.current_status, name="de_novo_assembly_dataanalysis_result_current_status"),
    path('result/<slug:slug_project>/<slug:slug_sample>/reference-mapping/current-status/QC/pre/multiqc_before_report', views.pre_qc_html_view_multiqc, name="reference_mapping_dataanalysis_result_current_status_pre_multiqc_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/reference-mapping/current-status/QC/pre/fastqc_r1_before_report', views.pre_qc_html_view_r1, name="reference_mapping_dataanalysis_result_current_status_pre_fastqc_r1_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/reference-mapping/current-status/QC/pre/fastqc_r2_before_report', views.pre_qc_html_view_r2, name="reference_mapping_dataanalysis_result_current_status_pre_fastqc_r2_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/reference-mapping/current-status/QC/post/multiqc_after_report', views.post_qc_html_view_multiqc, name="reference_mapping_dataanalysis_result_current_status_post_multiqc_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/reference-mapping/current-status/QC/post/fastqc_r1_after_report', views.post_qc_html_view_r1, name="reference_mapping_dataanalysis_result_current_status_post_fastqc_r1_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/reference-mapping/current-status/QC/post/fastqc_r2_after_report', views.post_qc_html_view_r2, name="reference_mapping_dataanalysis_result_current_status_post_fastqc_r2_html"),


    path('result/<slug:slug_project>/<slug:slug_sample>/de-novo-assembly/current-status/QC/pre/multiqc_before_report', views.pre_qc_html_view_multiqc, name="de_novo_assembly_dataanalysis_result_current_status_pre_multiqc_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/de-novo-assembly/current-status/QC/pre/fastqc_r1_before_report', views.pre_qc_html_view_r1, name="de_novo_assembly_dataanalysis_result_current_status_pre_fastqc_r1_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/de-novo-assembly/current-status/QC/pre/fastqc_r2_before_report', views.pre_qc_html_view_r2, name="de_novo_assembly_dataanalysis_result_current_status_pre_fastqc_r2_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/de-novo-assembly/current-status/QC/post/multiqc_after_report', views.post_qc_html_view_multiqc, name="de_novo_assembly_dataanalysis_result_current_status_post_multiqc_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/de-novo-assembly/current-status/QC/post/fastqc_r1_after_report', views.post_qc_html_view_r1, name="de_novo_assembly_dataanalysis_result_current_status_post_fastqc_r1_html"),
    path('result/<slug:slug_project>/<slug:slug_sample>/de-novo-assembly/current-status/QC/post/fastqc_r2_after_report', views.post_qc_html_view_r2, name="de_novo_assembly_dataanalysis_result_current_status_post_fastqc_r2_html"),

    # path('result/<slug:slug_project>/current-status/QC/post/<slug:slug_filename>', views.post_qc_html_view, name="dataanalysis_result_current_status_post_qc_html"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
