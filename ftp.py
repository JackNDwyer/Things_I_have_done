import os
import pysftp
from ftplib import FTP
import pdb
import logging
logging.basicConfig(level=logging.DEBUG)

# get file from FTP server
def get_ftp_file(remote_file, local_file_path, host, username, password, directory):
   try:
       with pysftp.Connection(host=host, username=username, password=password) as sftp:
           with sftp.cd(directory):
               sftp.get(remote_file, local_file_path)
   except Exception as ex:
       print(ex)

   sftp.close()

def get_sentient_ftp_file(local_file_path, directory):
   """ get file from Sentient FTP server """
   try:
       ftp = FTP("52.14.25.16", timeout=9999999)
       ftp.set_debuglevel(2)
       ftp.sendcmd('USER blast')
       ftp.sendcmd('PASS bL@$T_AM')
       ftp.getwelcome()

       # ftp passive needs to be set to "passive" or EC2 will thrown a 500 error
       ftp.set_pasv(True)  # passive
       ftp.cwd(directory)

       # get list of files
       files = ftp.nlst()
       for infile in files:
           if infile == "archive":
               continue

           with open(local_file_path, "wb+") as f:
               ftp.retrbinary("RETR " + infile, f.write, 2048)

           # move file to archive
           ftp.sendcmd("RNFR " + infile)
           ftp.sendcmd("RNTO " + directory + "/archive/" + infile)

       ftp.quit()
   except Exception as ex:
       print(ex)
