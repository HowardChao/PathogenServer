import os
from django_q.tasks import async_task, result, fetch
from . import utils_func

def django_q_check(project_name, email, analysis_code):
    new_task_name = project_name + email + analysis_code
    fetch_job = fetch(project_name + email + analysis_code)
    if fetch_job is None:
        print("@@@@@@@@@@@@ The job is not started yet!! ")
        # Task is failed
        # Return to fail page!!
        return False
    else:
        fetch_job_success = fetch_job.success
        if fetch_job.success:
            print("@@@@@@@@@@@@ The job is started and finished successfully: ")
            print("fetch_job: ", fetch_job)
            print("fetch_job.id: ", fetch_job.id)
            print("fetch_job.name: ", fetch_job.name)
            print("fetch_job.func: ", fetch_job.func)
            print("fetch_job.hook: ", fetch_job.hook)
            print("fetch_job.kwargs: ", fetch_job.kwargs)
            print("fetch_job.result: ", fetch_job.result)
            print("fetch_job.started: ", fetch_job.started)
            print("fetch_job.stopped: ", fetch_job.stopped)
            print("fetch_job.success: ", fetch_job.success)
            return fetch_job_success
        else:
            print("@@@@@@@@@@@@ The job is started but not finish yet: ")
            return fetch_job_success

def Whole_check_reference_based_results(url_base_dir, base_dir, sample_list):
    samples_all_info = {}
    for sample_name in sample_list:
        url_sample_base_dir = os.path.join(url_base_dir, sample_name)
        samples_all_info[sample_name] = {}
        one_sample_all_info = {}
        sample_datadir = os.path.join(base_dir, sample_name)
        ## Checking files
        ## Reference-based file checking!!
        Step_1_check_first_qc = utils_func.Step_1_check_first_qc(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_1_check_first_qc"] = Step_1_check_first_qc[0]
        Step_1_check_trimming_qc = utils_func.Step_1_check_trimming_qc(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_1_check_trimming_qc"] = Step_1_check_trimming_qc[0]
        Step_1_check_second_qc = utils_func.Step_1_check_second_qc(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_1_check_second_qc"] = Step_1_check_second_qc[0]
        Step_2_check_reference_based_bwa_sam = utils_func.Step_2_check_reference_based_bwa_sam(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_2_check_reference_based_bwa_sam"] = Step_2_check_reference_based_bwa_sam[0]
        Step_2_check_reference_based_bwa_report_txt = utils_func.Step_2_check_reference_based_bwa_report_txt(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_2_check_reference_based_bwa_report_txt"] = Step_2_check_reference_based_bwa_report_txt[0]
        Step_3_check_reference_based_samtools_fixmate_bam = utils_func.Step_3_check_reference_based_samtools_fixmate_bam(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_3_check_reference_based_samtools_fixmate_bam"] = Step_3_check_reference_based_samtools_fixmate_bam[0]
        Step_3_check_reference_based_samtools_sorted_bam = utils_func.Step_3_check_reference_based_samtools_sorted_bam(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_3_check_reference_based_samtools_sorted_bam"] = Step_3_check_reference_based_samtools_sorted_bam[0]
        Step_4_check_reference_based_bcftools_vcf = utils_func.Step_4_check_reference_based_bcftools_vcf(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_4_check_reference_based_bcftools_vcf"] = Step_4_check_reference_based_bcftools_vcf[0]
        Step_4_check_reference_based_bcftools_vcf_revise = utils_func.Step_4_check_reference_based_bcftools_vcf_revise(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_4_check_reference_based_bcftools_vcf_revise"] = Step_4_check_reference_based_bcftools_vcf_revise[0]
        Step_5_check_reference_based_snpeff_vcf_annotation = utils_func.Step_5_check_reference_based_snpeff_vcf_annotation(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_5_check_reference_based_snpeff_vcf_annotation"] = Step_5_check_reference_based_snpeff_vcf_annotation[0]
        samples_all_info[sample_name] = one_sample_all_info
    sample_checker_list = []
    for sample_key, sample_check_info in samples_all_info.items():
        ans = all(value == True for value in sample_check_info.values())
        sample_checker_list.append(ans)
    #This is for checking everything is fine~~~
    # sample_checker_list.append(False)
    overall_sample_result_checker = all(item == True for item in sample_checker_list)
    return (overall_sample_result_checker, samples_all_info)
