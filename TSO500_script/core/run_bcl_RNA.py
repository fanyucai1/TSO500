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

def run_docker(analysis,runFolder,SampleSheet,configfile):
     config = Myconf()
     config.read(configfile)
     TSO500=config.get('software','TSO500')
     if not os.path.exists("%s/docker_run.log"%(analysis)):
          subprocess.check_call("rm -rf %s"%(analysis),shell=True)
          cmd="cd %s && %s --resourcesFolder %s/resources --runFolder %s --analysisFolder %s --sampleSheet %s"%(os.path.dirname(TSO500),TSO500,os.path.dirname(TSO500),runFolder,analysis,SampleSheet)
          subprocess.check_call(cmd,shell=True)
          subprocess.check_call("echo done >%s/docker_run.log"%(analysis),shell=True)

def run(indir, project_name, configfile):
  config = Myconf()
  config.read(configfile)
  outdir = indir + "/final_result"
  if not os.path.exists(outdir):
      os.makedirs(outdir)
  for (root, dirs, files) in os.walk(indir):
      for file in files:
          tmp = os.path.join(root, file)
          if tmp.endswith("_CombinedVariantOutput.tsv") or tmp.split("/")[-1] == "MetricsOutput.tsv":
              subprocess.check_call("cp %s -rf %s" % (tmp, outdir), shell=True)
  subprocess.check_call("cd %s && tar -zcvf final_result.tar.gz final_result/" % (indir), shell=True)
  core.copy_file.run(project_name, "%s/final_result.tar.gz" % (indir))

if __name__=="__main__":
    parer=argparse.ArgumentParser()
    parer.add_argument("-a","--analysis",help="analysis directory",required=True)
    parer.add_argument("-c","--config",help="config file",required=True)
    parer.add_argument("-b","--bcl",help="bcl file",required=True)
    parer.add_argument("-s","--samplesheet",help="SampleSheet",required=True)
    parer.add_argument("-p","--project",help="project name",required=True)
    args=parer.parse_args()
    run_docker(args.analysis, args.bcl, args.samplesheet, args.config)
    run(args.analysis, args.project, args.config)