import os
from . import utils_func





    # # List of django_q models
    # task_list = django_q.models.Task.objects
    # success_list = django_q.models.Success.objects
    # failure_list = django_q.models.Failure.objects
    # ormqs_list = django_q.models.OrmQ.objects
    # # All objects in each django_q models
    # tasks_all = task_list.all()
    # success_all = success_list.all()
    # failure_all = failure_list.all()
    # ormq_all = ormqs_list.all()
    # print("!!!!!!!!!tasks_all: ", tasks_all)
    # print(len(tasks_all))
    # print("!!!!!!!!!success_all: ", success_all)
    # print(len(success_all))
    # print("!!!!!!!!!failure_all: ", failure_all)
    # print(len(failure_all))
    # print("!!!!!!!!!ormq_all: ", ormq_all)
    # print(len(ormq_all))
    #
    #
    # # Check whether in success_list (task is established and succeed)
    # success_select = success_list.filter(name = new_task_name)
    # print("success_select: ", success_select)
    # # Check whether in failer_list (task is established and failed)
    # failure_select = failure_list.filter(name = new_task_name)
    # print("failure_select: ", failure_select)
    #
    # # Check whether in queue list (task is not created)
    # queue_select = [o for o in ormq_all if o.name() == new_task_name]
    # print("queue_select: ", queue_select)
    #
    # print("!!!!!!!!!success_select: ", success_select)
    # print("!!!!!!!!!failure_select: ", failure_select)
    # print("!!!!!!!!!queue_select: ", queue_select)
    #
    # # Target : check whether the running jobs is in which status
    # # 1. Still in Queue
    # # 2. Running
    # # 3. Success
    # # 4. Failed
    # # ** It will not be in the Schedule list ~
    # if len(success_select) == 1:
    #     return "Success"
    # if len(success_select) == 0:
    #     print("length failure_select is zero!!")
    #
    # if len(failure_select) == 1:
    #     return "Failure"
    # if len(failure_select) == 0:
    #     print("length failure_select is zero!!")
    #
    # if len(queue_select) == 1:
    #     return "Queue"
    # if len(queue_select) == 0:
    #     print("length queue_select is zero!!")
    #
    # if len(success_select) == 0 and len(failure_select) == 0 and len(queue_select) == 0 :
    #     return "None"



    # print("ormq_select: ", ormq_select)

    # args, func, group, hook, id, kwargs, name, result, started, stopped, success
    # print("@@@ tasks_all args: ", tasks_all[0].args)
    # print("@@@ tasks_all func: ", tasks_all[0].func)
    # print("@@@ tasks_all group: ", tasks_all[0].group)
    # print("@@@ tasks_all hook: ", tasks_all[0].hook)
    # print("@@@ tasks_all id: ", tasks_all[0].id)
    # print("@@@ tasks_all kwargs: ", tasks_all[0].kwargs)
    # print("@@@ tasks_all name: ", tasks_all[0].name)
    # print("@@@ tasks_all result: ", tasks_all[0].result)
    # print("@@@ tasks_all started: ", tasks_all[0].started)
    # print("@@@ tasks_all stopped: ", tasks_all[0].stopped)
    # print("@@@ tasks_all success: ", tasks_all[0].success)
    #
    # print("@@@ success_all", success_all)
    # print("@@@ failure_all", failure_all)
    # print("@@@ ormq_all", ormq_all)
    # print("@@@ ormq_all", ormq_all[0].id)
    # print("@@@ ormq_all", ormq_all[0].name())
    # print("@@@ ormq_all", ormq_all[0].task_id())
    #
    # print("@@@ ormq_all", ormq_all[0].key)
    # print("@@@ ormq_all", ormq_all[0].lock)
    # print("@@@ ormq_all", ormq_all[0].payload)

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
