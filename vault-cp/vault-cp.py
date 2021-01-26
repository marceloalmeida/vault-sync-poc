#!/usr/bin/env python3

from argparse import ArgumentParser
import hvac
from progress.bar import ShadyBar, Bar
from progress.spinner import PixelSpinner, Spinner
import re
from urllib3 import disable_warnings

global_suffix='%(index)d/%(max)d - %(percent).1f%% - %(avg).4f - %(elapsed)ds - %(eta)ds'

def parse_args():
    '''Initialization of global variables'''
    parser = ArgumentParser(description="Vault to Vault Sync")
    parser.add_argument('--source-vault-url', metavar='URL', type=str, required=True,
                        help='Vault URL to copy secrets from')
    parser.add_argument('--source-vault-token', metavar='Token', type=str, required=True,
                        help='Vault token to copy secrets from')
    parser.add_argument('--source-vault-mount', metavar='Mount', type=str, default='secret/',
                        help='Vault mount to copy secrets from')
    parser.add_argument('--target-vault-url', metavar='URL', type=str, required=True,
                        help='Vault URL to copy secrets from')
    parser.add_argument('--target-vault-token', metavar='Token', type=str, required=True,
                        help='Vault token to copy secrets from')
    parser.add_argument('--target-vault-mount', metavar='Mount', type=str, default='secret/',
                        help='Vault mount to copy secrets from')
    args = parser.parse_args()

    return args

def lreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)

def copy_secrets(client_old, client_new, source_mount, target_mount, path, result_list=[], bar=ShadyBar("Copying secrets ")):
    list_secrets_result = client_old.list(path=path)
    for secret in list_secrets_result["data"]["keys"]:
        if secret.endswith("/"):
            copy_secrets(client_old=client_old, client_new=client_new, source_mount=source_mount, target_mount=target_mount, path=path+secret, result_list=result_list, bar=bar)
        else:
            data = client_old.read(path+secret)["data"]
            client_new.write(lreplace(source_mount, target_mount, path+secret), **data)
            bar.suffix = global_suffix + ' - ' + path+secret
        bar.next()
    return None

if __name__ == '__main__':
    disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    cfg = parse_args()

    client_old = hvac.Client(url=cfg.source_vault_url, token=cfg.source_vault_token, verify=False)
    client_new = hvac.Client(url=cfg.target_vault_url, token=cfg.target_vault_token, verify=False)

    bar=ShadyBar("Copying secrets ", max=1)
    copy_secrets(client_old=client_old, client_new=client_new, source_mount=cfg.source_vault_mount, target_mount=cfg.target_vault_mount, path=cfg.source_vault_mount, bar=bar)
    bar.finish()
