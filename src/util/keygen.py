from optparse import OptionParser

from paramiko import DSSKey
from paramiko import RSAKey
from paramiko.ssh_exception import SSHException
from paramiko.py3compat import u


default_values = {
    "ktype": "dsa",
    "bits": 1024,
    "filename": "rsakey",
    "comment": ""
}

# generating private key
prv = RSAKey.generate(bits=default_values['bits'])
prv.write_private_key_file(default_values['filename'], password='helloworld')

# generating public key
pub = RSAKey(filename=default_values['filename'], password='helloworld')
with open("%s.pub" % default_values['filename'], 'w') as f:
    f.write("%s %s" % (pub.get_name(), pub.get_base64()))