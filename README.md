### Photos Upload
Helps uploading all photos from a directory on your system to google photos

## How to run

1. Download `client_secret.json` in the `src` folder.
 - Go to the [Google API Console](https://console.developers.google.com/apis/).
 - From the menu bar, select a project or create a new project.
 - To open the Google API Library, from the Navigation menu, select APIs & Services > Library.
 - Search for "Google Photos Library API". Select the correct result and click Enable.
 - Under Credentials for your project, create OAuth Client ID for **other** and open the newly created credentials link
 - Download JSON as `client_secret.json` in the src folder

```
$ cd src
$ python3 main.py [folder-path]
```

## Features
1. Handles abrupt termination on a sub-directory level. It means that if the program terminates, it restarts uploads from the last directory it was uploading.

## Fututre features
1. Sync from Google photos to make sure that same photos are not uploaded twice
2. Show percentage/progress-bar

## Contributions
Sugesstions and contributions are always welcome. Please open an issue or submit a PR.
