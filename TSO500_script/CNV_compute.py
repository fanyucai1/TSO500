import smtplib
from email.mime.text import MIMEText
from email.header import Header
import sys
import argparse
import os
import re
root_dir="/data/TSO500"
def run(sample_name,purity):
    result=0
    for (root,dirs,files) in os.walk(root_dir):
        for file in files:
            tmp=os.path.join(root,file)
            if sample_name==tmp.split("/")[-1] and tmp.endswith("%s_CopyNumberVariants.vcf"%(sample_name)):
                result=1
                infile=open(tmp,"r")
                outfile=open("%s.final.CNV.tsv","w")
                outfile.write("#Chr\tStart\tend\tRef\tType\tGene\tCopyNumber\n")
                for line in infile:
                    line=line.strip()
                    if not line.startswith("#"):
                        array=line.split("\t")
                        if array[4]=="<DUP>" or array[4]=="<DEL>":
                            p1=re.compile(r'END=(\d+)')
                            p2=re.compile(r'ANT=(\S+)')
                            end=p1.findall(line)[0]
                            gene=p2.findall(line)[0]
                            X=float(purity)
                            Y=float(array[-1])
                            n = ((200 * Y) - 2 * (100 - X)) / X
                            outfile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(array[0],array[1],end,array[3],array[4],gene,n))
    if result==0:
        print("You input sample name erro,please check it")



if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("-s","--sample",help="sample name",required=True)
    parser.add_argument("-p","--purity",help="tumor purity",required=True)
    args=parser.parse_args()
    run(args.sample,args.purity)