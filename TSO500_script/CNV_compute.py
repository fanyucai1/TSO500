
import argparse
import re
import subprocess

def run(cnv_vcf,purity,prefix):
    infile=open(cnv_vcf,"r")
    outfile=open("%s.final.CNV.tsv"%(prefix),"w")
    outfile.write("#Chr\tStart\tend\tRef\tType\tGene\tCopyNumber\n")
    num=0
    for line in infile:
        line=line.strip()
        if not line.startswith("#"):
            array=line.split("\t")
            if array[4]=="<DUP>" or array[4]=="<DEL>":
                num+=1
                p1=re.compile(r'END=(\d+)')
                p2=re.compile(r'ANT=(\S+)')
                end=p1.findall(line)[0]
                gene=p2.findall(line)[0]
                X=float(purity)
                Y=float(array[-1])
                n = ((200 * Y) - 2 * (100 - X)) / X
                outfile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(array[0],array[1],end,array[3],array[4],gene,n))
    outfile.close()
    if num==0:
        subprocess.check_call("rm -rf %s.final.CNV.tsv"%(prefix),shell=True)
        print("sample %s not find DUP and DEL."%(prefix))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("-cv","--cnv_vcf",help="cnv vcf",required=True)
    parser.add_argument("-t","--purity",help="tumor purity",required=True)
    parser.add_argument("-p","--prefix",help="prefix of output",required=True)
    args=parser.parse_args()
    run(args.cnv_vcf,args.purity,args.prefix)