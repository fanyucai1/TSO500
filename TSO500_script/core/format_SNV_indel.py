import os
import argparse,configparser
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)
    def optionxform(self, optionstr):
        return optionstr

def run(TMB,gvcf,outdir,prefix,configfile):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    out=outdir+"/"+prefix
    config = Myconf()
    config.read(configfile)
    hotspot=open(config.get('database','hotspot'),"r")
    backlist={}
    for line in hotspot:
        line=line.strip()
        array=line.split("\t")
        backlist[array[0]+"\t"+array[1]+"\t"+array[2]+"\t"+array[3]]=1
    hotspot.close()
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
            tmp = array[0] + "\t" + array[1] + "\t" + array[2] + "\t" + array[3]
            if result == 4 or tmp in backlist:
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
    parser.add_argument("-c","--config",help="config file",default="/home/fanyucai/config/config.ini")
    args = parser.parse_args()
    run(args.tmb,args.gvcf,args.outdir,args.prefix,args.config)