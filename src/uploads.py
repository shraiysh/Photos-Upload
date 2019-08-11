import os, json, imghdr
import sys, requests

def getCache(BIN):
    uploaded = []
    cachefile = os.path.join(BIN, 'cache.json')
    if os.path.isfile(cachefile):
        with open(cachefile, 'r') as f:
            try:
                uploaded = json.load(f)
            except:
                print("Invalid file:", cachefile, "Starting new upload...")
    else:
        print("No cache found.")
    return uploaded

def upload(path, creds, service, ignore=[], bindir=os.path.join(os.getcwd(), 'bin')):
    BIN=bindir
    allFiles = []
    
    if(not os.path.isabs(path)):
        scriptDir = os.path.dirname(__file__)
        path = os.path.join(script_dir, path)

    for root, dirs, files in os.walk(path):
        for ifile in files:
            fullName = os.path.join(root, ifile)
            if imghdr.what(fullName) and not fullName in ignore:
                allFiles.append(fullName)
    return uploadFiles(allFiles, creds, service, BIN)

def updateCache(doneUploads, BIN):
    data = []
    if(os.path.isfile(os.path.join(BIN, 'cache.json'))):
        with open(os.path.join(BIN, 'cache.json'), 'r') as f:
            data = json.load(f)
    data += doneUploads
    with open(os.path.join(BIN, 'cache.json'), 'w') as f:
        json.dump(data, f)

def updateProgress(fraction, filename):
    sys.stdout.write('\033[K')
    print('['+'-'*int(fraction*10)+' '*int((1-fraction)*10)+']', int(fraction*100), '% ', end="")
    print(filename, end='\r')


def uploadFiles(files, creds, service, BIN):
    fraction = 0
    doneUploads = []
    newMediaItems = []
    headers = {
        'Content-Type': "application/octet-stream",
        'X-Goog-Upload-Protocol': "raw",
        'Authorization': "Bearer " + creds.token,
    }

    # Run service after every loop files
    loop = 2
    for idx, ifile in enumerate(files):
        
        if (idx+1)%loop == 0:
            uploadStatus = service.mediaItems().batchCreate(
                    body={'newMediaItems': newMediaItems}).execute()
            fraction += loop/len(files)
            updateCache(doneUploads, BIN)
            doneUploads = []

        updateProgress(fraction, ifile)

        headers['X-Goog-Upload-File-Name']=str(ifile)
        data = open(ifile, 'rb').read()
        response = requests.post('https://photoslibrary.googleapis.com/v1/uploads', headers=headers, data=data)
        assert response.status_code == 200
        doneUploads.append(ifile)
        image_token = response.text
        newMediaItems.append({
            'simpleMediaItem': {'uploadToken': image_token}
        })
    
    if len(newMediaItems) > 0:
        uploadStatus = service.mediaItems().batchCreate(
                body={'newMediaItems': newMediaItems}).execute()
        updateCache(doneUploads, BIN)
        doneUploads = []

    with open(os.path.join(BIN, 'cache.json'), 'r') as f:
        data = json.load(f)
        uploadedAll = True
        for i in files:
            uploadedAll = uploadedAll and (i in data)
        if uploadedAll == True:
            return True
        else: return False

