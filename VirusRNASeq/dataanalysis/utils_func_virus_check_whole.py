import os
from . import utils_func

def Whole_check_denovo_based_results(url_base_dir, base_dir, sample_list):
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


        Step_2_check_bwa_subtraction_bwa_mem = utils_func.check_bwa_subtraction_bwa_mem(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_2_check_bwa_subtraction_bwa_mem"] = Step_2_check_bwa_subtraction_bwa_mem[0]
        # check_bwa_subtraction_samtools_sam2bam
        Step_2_check_bwa_subtraction_samtools_sam2bam = utils_func.check_bwa_subtraction_samtools_sam2bam(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_2_check_bwa_subtraction_samtools_sam2bam"] = Step_2_check_bwa_subtraction_samtools_sam2bam[0]
        # check_bwa_subtraction_samtools_flagstat
        Step_2_check_bwa_subtraction_samtools_flagstat = utils_func.check_bwa_subtraction_samtools_flagstat(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_2_check_bwa_subtraction_samtools_flagstat"] = Step_2_check_bwa_subtraction_samtools_flagstat[0]
        # check_bwa_subtraction_samtools_view_unmapped_bam
        Step_2_check_bwa_subtraction_samtools_view_unmapped_bam = utils_func.check_bwa_subtraction_samtools_view_unmapped_bam(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_2_check_bwa_subtraction_samtools_view_unmapped_bam"] = Step_2_check_bwa_subtraction_samtools_view_unmapped_bam[0]
        # check_bwa_subtraction_samtools_view_unmapped_sorted_bam
        Step_2_check_bwa_subtraction_samtools_view_unmapped_sorted_bam = utils_func.check_bwa_subtraction_samtools_view_unmapped_sorted_bam(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_2_check_bwa_subtraction_samtools_view_unmapped_sorted_bam"] = Step_2_check_bwa_subtraction_samtools_view_unmapped_sorted_bam[0]
        # check_bwa_subtraction_bedtools_bam2fastq
        Step_2_check_bwa_subtraction_bedtools_bam2fastq = utils_func.check_bwa_subtraction_bedtools_bam2fastq(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_2_check_bwa_subtraction_bedtools_bam2fastq"] = Step_2_check_bwa_subtraction_bedtools_bam2fastq[0]



        Step_3_check_denovo_a5_miseq = utils_func.Step_2_check_denovo_a5_miseq(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_3_check_denovo_a5_miseq"] = Step_3_check_denovo_a5_miseq[0]

        Step_4_check_quast_assessment = utils_func.Step_3_check_quast_assessment(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_4_check_quast_assessment"] = Step_4_check_quast_assessment[0]

        Step_4_check_bowtie2_assessment = utils_func.Step_3_check_bowtie2_assessment(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_info["Step_4_check_bowtie2_assessment"] = Step_4_check_bowtie2_assessment[0]

        samples_all_info[sample_name] = one_sample_all_info
    sample_checker_list = []
    for sample_key, sample_check_info in samples_all_info.items():
        ans = all(value == True for value in sample_check_info.values())
        sample_checker_list.append(ans)
    #This is for checking everything is fine~~~
    # sample_checker_list.append(False)
    overall_sample_result_checker = all(item == True for item in sample_checker_list)
    overall_sample_result_checker = True
    return (overall_sample_result_checker, samples_all_info)
