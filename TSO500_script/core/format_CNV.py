import os
import re
import subprocess
import argparse

def run(vcf,outdir,prefix):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    out=outdir+"/"+prefix
    infile = open(vcf, "r")
    outfile = open("%s.cnv.tsv" % (out), "w")
    outfile.write("#Chr\tStart\tend\tRef\tType\tGene\n")
    i = 0
    for line in infile:
        if not line.startswith("#"):
            line = line.strip()
            array = line.split()
            if array[4] == "<DUP>" or array[4] == "<DEL>":
                i += 1
                p1 = re.compile(r'END=(\d+)')
                p2 = re.compile(r'ANT=(\S+)')
                a = p1.findall(line)
                b = p2.findall(line)
                tmp = array[0] + "\t" + array[1] + "\t" + a[0] + "\t" + array[3] + "\t" + array[4] + "\t" + b[0]
                outfile.write("%s\n" % (tmp))
    outfile.close()
    if i == 0:
        subprocess.check_call("rm -rf %s.cnv.tsv" % (out), shell=True)
        print("sample %s not find CNV" % (id))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("-v","--vcf",help="vcf file from CNV",required=True)
    parser.add_argument("-o","--outdir",help="output directory",required=True)
    parser.add_argument("-p","--prefix",help="prefix of output",required=True)
    args=parser.parse_args()
    CNV(args.vcf,args.outdir,args.prefix)