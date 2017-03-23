# Static analyzer for Android


Requires Metrix++ at location: metrixplusplus-1.3.168/metrix++.py
[Metrix++](http://metrixplusplus.sourceforge.net/home.html) which should be placed in the same directory as this git repo. 
The git project you want to look at should also be placed in the same directory.

The following commands should be ran from the directory of the project you want to check. 

Run with:
```bash
../android-static-analyzer/get_data.py CODE-PATH PATH-TO-FILE FILE
../android-static-analyzer/get_full_history_data.sh CODE-PATH PATH-TO-FILE FILE
```
Example:
```bash
../android-static-analyzer/get_data.py ./project_name src/test file_name
../android-static-analyzer/get_full_history_data.sh ./project_name src/test file_name
```
