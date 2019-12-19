import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import argparse
import os
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
    ##################################################
    mail_host = "smtp.exmail.qq.com"
    sender = "yucaifan@chosenmedtech.com"
    password = "Fyc240290"
    receivers = ["ycz@chosenmedtech.com","bmc@chosenmedtech.com"]
    ####################################################
    if num==0:
        subprocess.check_call("rm -rf %s.final.CNV.tsv"%(prefix),shell=True)
        info="sample %s not find DUP and DEL."%(prefix)
        message = MIMEText(info, 'plain', 'utf-8')
        message['From'] = formataddr(["From BMC", sender])  # 发送者
        message['To'] = formataddr(['To Genetic Counseling', ",".join(receivers)])  # 接受者
        message['Subject'] = Header('TSO500样本%s的CNV分析结果' % (prefix), 'utf-8')
        ########################################################
        try:
            smtpObj = smtplib.SMTP(mail_host, 25)
            smtpObj.login(sender, password)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")
    if os.path.exists("%s.final.CNV.tsv"%(prefix)):
        message = MIMEMultipart()
        message.attach(MIMEText('sample %s find DUP and DEL.'%(prefix), 'plain', 'utf-8'))
        message['From'] = formataddr(["From BMC", sender])  # 发送者
        message['To'] = formataddr(['To Genetic Counseling', ",".join(receivers)])  # 接受者
        message['Subject'] = Header('TSO500样本%s的CNV分析结果' % (prefix), 'utf-8')
        att1 = MIMEText(open('%s.final.CNV.tsv'%(prefix), 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = 'attachment; filename='+"%s.final.CNV.tsv"%(prefix)
        message.attach(att1)
        ########################################################
        try:
            smtpObj = smtplib.SMTP(mail_host, 25)
            smtpObj.login(sender, password)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")
        subprocess.check_call("rm -rf %s.final.CNV.tsv"%(prefix),shell=True)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("-cv","--cnv_vcf",help="cnv vcf",required=True)
    parser.add_argument("-t","--purity",help="tumor purity",required=True)
    parser.add_argument("-p","--prefix",help="prefix of output",required=True)
    args=parser.parse_args()
    run(args.cnv_vcf,args.purity,args.prefix)