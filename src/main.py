from __future__ import print_function
from sys import argv
import imghdr
import os
import json
import sys

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import requests

def getAuthCreds(SCOPES):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def uploadDir(path, creds, service):
    doneUploads = resumeUpload([], path, creds, service)
    return doneUploads

def resumeUpload(done, path, creds, service):

    if(not os.path.isabs(path)):
        # Get absolute path from the relative path mentioned
        script_dir = os.path.dirname(__file__)
        path = os.path.join(script_dir, path)

    doneUploads = done.copy()

    for root, dirs, files in os.walk(path):
        # newMediaItems = []
        file_list = []
        for ifile in files:
            fullname = os.path.join(root, ifile)
            if imghdr.what(fullname) and not fullname in done:
                file_list.append(os.path.join(root, ifile))
        doneUploads += upload(file_list, creds, service)

    return doneUploads


def upload(files, creds, service):
    
    headers = {
        'Content-Type': "application/octet-stream",
        'X-Goog-Upload-Protocol': "raw",
        'Authorization': "Bearer " + creds.token,
    }

    doneUploads = []
    newMediaItems = []

    for ifile in files:
        if(imghdr.what(os.path.join(ifile))):
            sys.stdout.write("\033[K")
            print("Uploading:", ifile, end="\r")
            headers['X-Goog-Upload-File-Name']=str(ifile)
            data = open(ifile, 'rb').read()
            response = requests.post('https://photoslibrary.googleapis.com/v1/uploads', headers=headers, data=data)
            assert response.status_code == 200
            doneUploads.append(ifile)
            image_token = response.text
            newMediaItems.append({
                'simpleMediaItem': {'uploadToken': image_token}
            })        
        
    if len(newMediaItems):
        uploadStatus = service.mediaItems().batchCreate(
                body={'newMediaItems': newMediaItems}).execute()

    return doneUploads


if __name__ == '__main__':
    _, path = argv

    print("Authenticating...")
    SCOPES = ['https://www.googleapis.com/auth/photoslibrary.appendonly']
    creds = getAuthCreds(SCOPES)
    service = build('photoslibrary', 'v1', credentials=creds)
    print("Authenticated. Checking for cache[success.json]...")
    success = {}
    if os.path.isfile('success.json'):
        with open('success.json', 'r') as f:
            try:
                success = json.load(f)
            except:
                print("Invalid file: 'success.json'. Starting Upload...")
                os.remove('success.json')
    else:
        print("No cache")

    successfulUploads = None
    
    if(path in success):
        print("Cache found. Retrying failed uploads...")
        successfulUploads = resumeUpload(success[path], path, creds, service)
    else:
        print("Uploading...")
        successfulUploads = resumeUpload([], path, creds, service)
    
    success[path] = successfulUploads
    with open('success.json', 'w', encoding='utf-8') as f:
         json.dump(success, f, ensure_ascii=False, indent=4)
    print("\nUpload successful")
