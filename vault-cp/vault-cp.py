#!/usr/bin/env python3

import config as cfg
import hvac
from progress.bar import ShadyBar, Bar
from progress.spinner import PixelSpinner, Spinner
import re

global_suffix='%(index)d - %(avg).4f - %(elapsed)ds'

def lreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)

def copy_secrets(client_old, client_new, path, result_list=[], bar=ShadyBar("Copying secrets ")):
    list_secrets_result = client_old.list(path=path)
    for secret in list_secrets_result["data"]["keys"]:
        if secret.endswith("/"):
            copy_secrets(client_old=client_old, client_new=client_new, path=path+secret, result_list=result_list, bar=bar)
        else:
            data = client_old.read(path+secret)["data"]
            client_new.write(lreplace(cfg.old["mount"], cfg.new["mount"], path+secret), **data)
            bar.suffix = global_suffix + ' - ' + path+secret
        bar.next()
    return None

client_old = hvac.Client(url=cfg.old["url"], token=cfg.old["token"])
client_new = hvac.Client(url=cfg.new["url"], token=cfg.new["token"])

bar=ShadyBar("Copying secrets ", max=1)
copy_secrets(client_old=client_old, client_new=client_new, path=cfg.old["mount"], bar=bar)
bar.finish()
