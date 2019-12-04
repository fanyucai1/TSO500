import os
import argparse

def run(TMB,gvcf,outdir,prefix):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    out=outdir+"/"+prefix
    infile=open(TMB,"r")
    outfile=open("%s.vcf"%(out),"w")
    outfile.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
    num,name,dict = 0,[],{}
    for line in infile:
        line = line.strip()
        num += 1
        array = line.split("\t")
        if num == 1:
            for i in range(len(array)):
                name.append(array[i])
        else:
            result = 0
            for i in range(len(name)):
                if name[i] == "CodingVariant" and array[i] == "True":
                    result += 1
                if name[i] == "Nonsynonymous" and array[i] == "True":
                    result += 1
                if name[i] == "GermlineFilterDatabase" and array[i] == "False":
                    result += 1
                if name[i] == "GermlineFilterProxi" and array[i] == "False":
                    result += 1
            if result == 4:
                tmp = array[0] + "\t" + array[1] + "\t" + array[2] + "\t" + array[3]
                dict[tmp] = 1
    infile.close()
    infile = open(gvcf, "r")
    for line in infile:
        line = line.strip()
        if not line.startswith("#"):
            array = line.split("\t")
            tmp = array[0] + "\t" + array[1] + "\t" + array[3] + "\t" + array[4]
            if tmp in dict:
                info = array[-1].split(":")
                outfile.write("%s\t%s\t.\t%s\t%s\t.\t.\tGT=%s;AD=%s;Var=%s\n" % (
                array[0], array[1], array[3], array[4], info[0], info[2], info[4]))
    infile.close()
    outfile.close()

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("-t","--tmb",help="tmb file",required=True)
    parser.add_argument("-g", "--gvcf", help="gvcf file", required=True)
    parser.add_argument("-o", "--outdir", help="output directory", required=True)
    parser.add_argument("-p", "--prefix", help="prefix of output", required=True)
    args = parser.parse_args()
    run(args.tmb,args.gvcf,args.outdir,args.prefix)