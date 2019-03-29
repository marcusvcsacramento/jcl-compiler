import ftplib
import re
import datetime
import configparser
import sys
import io


ftp = ftplib.FTP()
ftp.connect('zosdev', 21)
ftp.set_debuglevel(1)
ftp.login('TE89323', '1983cs')
ftp.cwd('..')
## SHRDES.GE.A
ftp.cwd('SHRDES.GE.A.NEWSEG.PGMLIB.COB2.SMART')
ftp.retrlines('LIST SZ*')
ftp.retrlines('LIST SPB*')
ftp.quit()
