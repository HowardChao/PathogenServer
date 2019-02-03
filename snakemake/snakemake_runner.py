import subprocess
import os
import tempfile
import shutil
import pytest

def run(wrapper, cmd, check_log=None):
    origdir = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        dst = os.path.join(d, "master", wrapper)
        print("Destination", dst)
        os.makedirs(dst, exist_ok=True)
        copy = lambda src: shutil.copy(os.path.join(wrapper, src), dst)
        success = False
        for ext in ("py", "R", "Rmd"):
            script = "wrapper." + ext
            if os.path.exists(os.path.join(wrapper, script)):
                copy(script)
                success = True
                break
        assert success, "No wrapper.{py,R,Rmd} found"
        copy("environment.yaml")
        testdir = os.path.join(wrapper, "test")
        # switch to test directory
        os.chdir(testdir)
        if os.path.exists(".snakemake"):
            shutil.rmtree(".snakemake")
        cmd = cmd + ["--wrapper-prefix", "file://{}/".format(d)]
        print("cmd: ", cmd)
        subprocess.check_call(["snakemake", "--version"])

        try:
            subprocess.check_call(cmd)
        except Exception as e:
            # go back to original directory
            os.chdir(origdir)
            logfiles = [os.path.join(d, f)
                for d, _, files in os.walk(os.path.join(testdir, "logs"))
                for f in files]
            for path in logfiles:
                with open(path) as f:
                    msg = "###### Logfile: " + path + " ######"
                    print(msg, "\n")
                    print(f.read())
                    print("#" * len(msg))
            if check_log is not None:
                for f in logfiles:
                    check_log(open(f).read())
            else:
                raise e
        finally:
            # go back to original directory
            os.chdir(origdir)

def test_trimmomatic_pe():
    """Four tests, one per fq-gz combination"""
    #run("bio/trimmomatic/pe",
    #    ["snakemake", "/home/kuan-hao/Documents/bioinformatics/Virus/analysis_results/tmp_project/Projecta4dd8ad0276011e99ddf60f81dacbf14/trimmed/ip96_S13.1.fastq", "--use-conda", "-F",
    #    "-s", "Snakefile_fq_fq", "-r", "-p"])
    run("bio/trimmomatic/pe",
        ["snakemake", "-s", "Snakefile_fq_fq", "-r", "-p", "--use-conda", "-F", "trimmomatic_pe"])
    # run("bio/trimmomatic/pe",
    #     ["snakemake", "trimmed/a.1.fastq.gz", "--use-conda", "-F",
    #     "-s", "Snakefile_fq_gz"])
    # run("bio/trimmomatic/pe",
    #     ["snakemake", "trimmed/a.1.fastq", "--use-conda", "-F",
    #     "-s", "Snakefile_gz_fq"])
    # run("bio/trimmomatic/pe",
    #     ["snakemake", "trimmed/a.1.fastq.gz", "--use-conda", "-F",
    #     "-s", "Snakefile_gz_gz"])

test_trimmomatic_pe()
