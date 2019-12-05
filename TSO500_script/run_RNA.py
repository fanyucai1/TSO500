import os
import sys
sub=os.path.abspath(__file__)
dir_name=os.path.dirname(sub)
sys.path.append(dir_name)
import core
import argparse
import configparser
import subprocess
from multiprocessing import Process
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)
    def optionxform(self, optionstr):
        return optionstr

def run(pe1,pe2,outdir,prefix,indexID,configfile):
###########################################
    config = Myconf()
    config.read(configfile)
    TSO500 = config.get('software', 'TSO500')
    infile=open("%s/resources/sampleSheet/TSO500_NovaSeq_Sample_Sheet_Template.csv"%(os.path.dirname(TSO500)),"r")
    index, index2="",""
    for line in infile:
        line=line.strip()
        array=line.split(",")
        if array[4]==indexID:
            index=array[5]
            index2=array[6]
    infile.close()
##########step1:print samplesheet############
    outfile=open("%s/SampleSheet.csv"%(outdir),"w")
    outfile.write("""
[Header],,,,,,,
IEMFileVersion,4,,,,,,
Investigator Name,User Name,,,,,,
Experiment Name,Experiment,,,,,,
Date,2019/12/1,,,,,,
Workflow,From GenerateFASTQ,,,,,,
Application,NovaSeq,,,,,,
Assay,,,,,,,
Description,,,,,,,
Chemistry,Default,,,,,,
,,,,,,,
[Reads],,,,,,,
151,,,,,,,
151,,,,,,,
,,,,,,,
[Settings],,,,,,,
OverrideCycles,Y101;I8;I8;Y101,,,,,,
,,,,,,,
[Data],,,,,,,,
Sample_ID,Sample_Name,Sample_Plate,Sample_Well,Index_ID,index,index2,Sample_Type,Pair_ID
%s,,,,%s,%s,%s,RNA,%s"""%(prefix,indexID,index,index2,prefix))
    outfile.close()
    if not os.path.exists("%s/fastq/%s" % (outdir, prefix)):
        os.makedirs("%s/fastq/%s" % (outdir, prefix))
    if not os.path.exists("%s/fastq/%s/%s_S1_R1_001.fastq.gz"%(outdir,prefix,prefix)):
        subprocess.check_call("cp %s %s/fastq/%s/%s_S1_R1_001.fastq.gz"%(pe1,outdir,prefix,prefix),shell=True)
        subprocess.check_call("cp %s %s/fastq/%s/%s_S1_R2_001.fastq.gz" % (pe2, outdir, prefix,prefix), shell=True)
    if not os.path.exists("%s/analysis_RNA/docker_run.log" % (outdir)):
        cmd = "cd %s && %s --resourcesFolder %s/resources --fastqFolder %s/fastq/ --analysisFolder %s/analysis_RNA/ --sampleSheet %s/SampleSheet.csv" % (
        os.path.dirname(TSO500), TSO500, os.path.dirname(TSO500), outdir,outdir, outdir)
        subprocess.check_call(cmd, shell=True)
        subprocess.check_call("echo done >%s/analysis/docker_run.log" % (outdir), shell=True)
