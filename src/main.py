import uploads
import auth
import os

from sys import argv

BIN = os.path.join(os.getcwd(), 'bin')

if __name__ == '__main__':
    _, path = argv

    print("Authenticating...")
    SCOPES = ['https://www.googleapis.com/auth/photoslibrary.appendonly']
    service, creds = auth.getService(SCOPES)
    print("Authenticated. Checking for cache[success.json]...")

    if not os.path.isdir(BIN):
        os.makedirs(BIN)

    cache = uploads.getCache(BIN)

    success = uploads.upload(path, creds, service, ignore=cache, bindir=BIN)

    print('SUCCESS' if success==True else 'Unable to upload some files. Please retry')
