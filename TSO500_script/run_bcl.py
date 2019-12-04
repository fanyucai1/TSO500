
import os
import sys
sub=os.path.abspath(__file__)
dir_name=os.path.dirname(sub)
sys.path.append(dir_name)
import core
import argparse
import configparser
import subprocess

class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)
    def optionxform(self, optionstr):
        return optionstr

def run(analysis,runFolder,SampleSheet,configfile,project_name):
     config = Myconf()
     config.read(configfile)
     TSO500=config.read('software','TSO500')
     if not os.path.exists("%s/docker_run.log"%(analysis)):
          subprocess.check_call("rm -rf %s"%(analysis),shell=True)
          cmd="cd %s && %s --resourcesFolder %s/resources --runFolder %s --analysisFolder %s --sampleSheet %s"%(os.path.dirname(TSO500),TSO500,os.path.dirname(TSO500),runFolder,analysis,SampleSheet)
          subprocess.check_call(cmd,shell=True)
          subprocess.check_call("echo done >%s/docker_run.log"%(analysis),shell=True)
          outdir = analysis + "/final_result"
          ID = []
          if not os.path.exists(outdir):
               os.makedirs(outdir)
               os.makedirs("%s/CNV" % (outdir))
               os.makedirs("%s/SNV_indel" % (outdir))
               os.makedirs("%s/TMB_MSI" % (outdir))
          for (root, dirs, files) in os.walk(analysis):
               for file in files:
                    tmp = os.path.join(root, file)
                    sample = tmp.split("/")[-2]
                    if tmp.endswith("CopyNumberVariants.vcf"):
                         ID.append(sample)
                         print(tmp)
                         core.format_CNV.run(tmp, "%s/CNV" % (outdir), sample)
                    elif tmp.endswith("TMB_Trace.tsv"):
                         print(tmp)
                         gvcf = tmp.replace("TMB_Trace.tsv", "MergedSmallVariants.genome.vcf")
                         core.format_SNV_indel.run(tmp, gvcf, "%s/SNV_indel" % (outdir), sample)
                         core.anno_vcf.run("%s/SNV_indel/%s.vcf" % (outdir, sample), "%s/SNV_indel" % (outdir), sample,
                                           configfile)
                         subprocess.check_call("rm -rf %s/SNV_indel/%s.vcf" % (outdir, sample), shell=True)
                    elif tmp.split("/")[-3] == "StitchedRealigned" and tmp.endswith("bam"):
                         print(tmp)
                         core.copy_file.run(project_name, tmp)
                         core.copy_file.run(project_name, "%s.bai" % (tmp))
                    elif tmp.split("/")[-1] == "MetricsOutput.tsv":
                         print(tmp)
                         subprocess.check_call("cp %s -rf %s" % (tmp, outdir), shell=True)
                    elif tmp.endswith("CombinedVariantOutput.tsv"):
                         print(tmp)
                         subprocess.check_call("cp %s -rf %s/TMB_MSI" % (tmp, outdir), shell=True)
                    else:
                         pass
          subprocess.check_call("cd %s && tar -zcvf final_result.tar.gz final_result/" % (analysis), shell=True)
          core.copy_file.run(project_name, "%s/final_result.tar.gz" % (analysis))

if __name__=="__main__":
    parer=argparse.ArgumentParser()
    parer.add_argument("-a","--analysis",help="analysis directory",required=True)
    parer.add_argument("-c","--config",help="config file",required=True)
    parer.add_argument("-b","--bcl",help="bcl file",required=True)
    parer.add_argument("-s","--samplesheet",help="SampleSheet",required=True)
    parer.add_argument("-p","--project",help="project name",required=True)
    parer.add_argument("-t","--type",help="fastq or bcl",required=True,choices=["bcl","fastq"])
    args=parer.parse_args()
    if args.type=="bcl":
         run(args.analysis, args.bcl, args.samplesheet, args.configfile, args.project)