import os
import sys
sub=os.path.abspath(__file__)
dir_name=os.path.dirname(sub)
sys.path.append(dir_name)
import core
import configparser
import subprocess
import argparse
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)
    def optionxform(self, optionstr):
        return optionstr

def run(indir,project_name,configfile):
    config = Myconf()
    config.read(configfile)
    outdir=indir+"/final_result"
    ID=[]
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        os.makedirs("%s/CNV"%(outdir))
        os.makedirs("%s/SNV_indel" % (outdir))
        os.makedirs("%s/TMB_MSI" % (outdir))
    for(root,dirs,files) in os.walk(indir):
        for file in files:
            tmp=os.path.join(root,file)
            sample = tmp.split("/")[-2]
            if tmp.endswith("CopyNumberVariants.vcf"):
                ID.append(sample)
                print(tmp)
                core.format_CNV.run(tmp,"%s/CNV"%(outdir),sample)
            elif tmp.endswith("TMB_Trace.tsv"):
                print(tmp)
                gvcf=tmp.replace("TMB_Trace.tsv","MergedSmallVariants.genome.vcf")
                core.format_SNV_indel.run(tmp,gvcf,"%s/SNV_indel"%(outdir),sample)
                core.anno_vcf.run("%s/SNV_indel/%s.vcf"%(outdir,sample),"%s/SNV_indel"%(outdir),sample,configfile)
                subprocess.check_call("rm -rf %s/SNV_indel/%s.vcf"%(outdir,sample),shell=True)
            elif tmp.split("/")[-3]=="StitchedRealigned" and tmp.endswith("bam"):
                print(tmp)
                core.copy_file.run(project_name,tmp)
                core.copy_file.run(project_name,"%s.bai"%(tmp))
            elif tmp.split("/")[-1]=="MetricsOutput.tsv":
                print(tmp)
                subprocess.check_call("cp %s -rf %s"%(tmp,outdir),shell=True)
            elif tmp.endswith("CombinedVariantOutput.tsv"):
                print(tmp)
                subprocess.check_call("cp %s -rf %s/TMB_MSI"%(tmp,outdir),shell=True)
            else:
                pass
    subprocess.check_call("cd %s && tar -zcvf final_result.tar.gz final_result/"%(indir),shell=True)
    core.copy_file.run(project_name,"%s/final_result.tar.gz"%(indir))

if __name__=="__main__":
    parer=argparse.ArgumentParser()
    parer.add_argument("-i","--indir",help="analysis directory",required=True)
    parer.add_argument("-c","--config",help="config file",required=True)
    parer.add_argument("-p","--project",help="project name",required=True)
    args=parer.parse_args()
    run(args.indir,args.project,args.config)