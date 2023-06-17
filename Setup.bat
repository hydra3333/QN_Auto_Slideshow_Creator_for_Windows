@echo on
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

set "vs_CD=%CD%"
if /I NOT "%vs_CD:~-1%" == "\" (set "vs_CD=%vs_CD%\")

set "vs_temp=%vs_CD%temp"
if /I NOT "%vs_temp:~-1%" == "\" (set "vs_temp=%vs_temp%\")

set "vs_path=%vs_CD%Vapoursynth_x64"
if /I NOT "%vs_path:~-1%" == "\" (set "vs_path=%vs_path%\")

REM set "git_path=%vs_CD%PortableGit_x64"
REM if /I NOT "%git_path:~-1%" == "\" (set "git_path=%git_path%\")

REM py_path and vs_path should ALWAYS be the same as should PYTHONPATH
set "py_path=%vs_path%"
set "PYTHONPATH=%py_path%"

set "py_exe=%py_path%python.exe"
set "ffmpeg_exe=%vs_path%ffmpeg.exe"
set "mediainfo_exe=%vs_path%mediainfo.exe"

ECHO DO NOT NOT ever run this as admin %%%% or it will install python stuff into an inaccessible admin user's folder
ECHO DO NOT NOT ever run this as admin %%%% or it will install python stuff into an inaccessible admin user's folder
ECHO DO NOT NOT ever run this as admin %%%% or it will install python stuff into an inaccessible admin user's folder

IF NOT EXIST "%vs_CD%wget.exe" (
	echo Also, Please download wget.exe into this folder "%vs_CD%" first.
	echo Exiting without success.
	pause
	exit
)

CD "%vs_CD%"
if not exist "%vs_temp%" (mkdir "%vs_temp%")
if not exist "%vs_path%" (mkdir "%vs_path%")
REM if not exist "%git_path%" (mkdir "%git_path%")
REM
CD "%vs_CD%"
IF EXIST "%vs_path%7zr.exe" (DEL /F "%vs_path%7zr.exe")
IF EXIST "%%vs_temp%7z2201-extra.7z" (DEL /F "%%vs_temp%7z2201-extra.7z")
IF EXIST "%vs_path%7za.exe" (DEL /F "%vs_path%7za.exe")
echo Fetching 7zip ...
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%7zr.exe" "https://www.7-zip.org/a/7zr.exe"
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%7z2300-extra.7z" "https://www.7-zip.org/a/7z2300-extra.7z"
"%vs_temp%7zr.exe" t "%vs_temp%7z2300-extra.7z" -o"%vs_path%" 7za.exe
"%vs_temp%7zr.exe" x -y -aoa "%vs_temp%7z2300-extra.7z" -o"%vs_path%" 7za.exe
REM
CD "%vs_path%"
IF EXIST "%vs_temp%python.zip" (del /f "%vs_temp%python.zip")
REM https://www.python.org/ftp/python
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%python.zip" "https://www.python.org/ftp/python/3.11.3/python-3.11.3-embed-amd64.zip"
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%python.zip" "https://www.python.org/ftp/python/3.11.2/python-3.11.2-embed-amd64.zip"
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%python.zip" "https://www.python.org/ftp/python/3.10.10/python-3.10.10-embed-amd64.zip"
"%vs_path%7za.exe" t "%vs_temp%python.zip"
"%vs_path%7za.exe" x -y -aoa "%vs_temp%python.zip" -o"%vs_path%" 
REM
CD "%vs_path%"
IF EXIST "%vs_temp%vapoursynth.zip" (del /f "%vs_temp%vapoursynth.zip")
REM https://github.com/vapoursynth/vapoursynth/releases/download/
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%vapoursynth.zip" "https://github.com/vapoursynth/vapoursynth/releases/download/R62/VapourSynth64-Portable-R62.7z"
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%vapoursynth.zip" "https://github.com/vapoursynth/vapoursynth/releases/download/R61/VapourSynth64-Portable-R61.7z"
REM "%vs_path%7za.exe" t "%vs_temp%vapoursynth.zip"
"%vs_path%7za.exe" x -y -aoa "%vs_temp%vapoursynth.zip" -o"%vs_path%" 
REM
CD "%py_path%"
IF EXIST "%py_path%pip.pyz" (del /f "%py_path%pip.pyz")
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%py_path%pip.pyz" "https://bootstrap.pypa.io/pip/pip.pyz"
REM "%py_exe%" pip.pyz --help
REM NOTE: NO QUOTES around %vs_path% or these abort %%%
"%py_exe%" pip.pyz install pip --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install build --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install setuptools --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM for building wheels
"%py_exe%" pip.pyz install wheel --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install twine --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install virtualenv --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM need to uninstall markdown so mkdocs can install an older version .. .for building wheels
REM "%py_exe%" pip.pyz uninstall markdown --yes --break-system-packages
REM "%py_exe%" pip.pyz install mkdocs --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM the reviewer
"%py_exe%" pip.pyz install pip-review --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM install latest certificates for python requests.get
"%py_exe%" pip.pyz --no-cache-dir list > "%vs_path%pip_1.installed.before.txt" 2>&1
"%py_exe%" pip.pyz install certifi --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install cffi --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install numpy --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose

"%py_exe%" pip.pyz install decorator==4.4.2 --target=%vs_path% --no-cache-dir --check-build-dependencies --force-reinstall --upgrade --verbose

"%py_exe%" pip.pyz install piexif --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install exifread --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install pillow --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install pymediainfo --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install pydub --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install pymediainfo --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install pathlib --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install sockets --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install requests --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install datetime --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install packaging --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install python-utils --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install python-dotenv --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install progressbar2 --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install pyyaml --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install html5lib --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install configparser --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz install opencv-python-headless --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM "%py_exe%" pip.pyz install rich --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM "%py_exe%" pip.pyz install vstools --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM "%py_exe%" pip.pyz install vsexprtools --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM "%py_exe%" pip.pyz install vstransitions --target=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
"%py_exe%" pip.pyz cache purge
"%py_exe%" pip.pyz --no-cache-dir list > "%vs_path%pip_2.installed.after.txt" 2>&1
"%py_exe%" pip.pyz --no-cache-dir list
"%py_exe%" pip.pyz --no-cache-dir list --outdated
"%py_exe%" pip.pyz --no-cache-dir check
REM note the underscores next
"%py_exe%" -m pip_review --verbose
REM Unfortuinately cannot do this to auto-upgrade: 
"%py_exe%" -m pip_review --verbose --auto --continue-on-fail 

REM "%py_exe%" pip.pyz install decorator==4.4.2 --target=%vs_path% --no-cache-dir --check-build-dependencies --force-reinstall --upgrade --verbose
REM "D:\ssTEST\Vapoursynth_x64\python.exe" pip.pyz --no-cache-dir list



REM sice mardown version <4 is required by mkdocs :(
REM
REM --------------------------------------------------------------------------------------------------------------------------------------------------------
REM vs-tools ...
REM for older release of vs-tools:     "%py_exe%" pip.pyz install vstools --prefix=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM for current git head of vs-tools: "%py_exe%" pip.pyz install git+https://github.com/Irrational-Encoding-Wizardry/vs-tools.git  --prefix=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM set "reinstall_vs_tools=%vs_CD%reinstall_vs_tools.bat"
REM del /f "%reinstall_vs_tools%" >NUL 2>&1
REM echo ^@echo on >>"%reinstall_vs_tools%" 2>&1
REM echo ^@setlocal ENABLEDELAYEDEXPANSION >>"%reinstall_vs_tools%" 2>&1
REM echo ^@setlocal enableextensions >>"%reinstall_vs_tools%" 2>&1
REM echo CD "%vs_CD%" >>"%reinstall_vs_tools%" 2>&1
REM CD "%vs_CD%"
REM echo "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%vs-tools.git.zip" "https://github.com/Irrational-Encoding-Wizardry/vs-tools/archive/refs/heads/master.zip" >>"%reinstall_vs_tools%" 2>&1
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%vs-tools.git.zip" "https://github.com/Irrational-Encoding-Wizardry/vs-tools/archive/refs/heads/master.zip"
REM echo if exist "%vs_temp%vs-tools.git" ^(rmdir "%vs_temp%\vs-tools-master" /s /q ^>NUL 2^>^&1^) >>"%reinstall_vs_tools%" 2>&1
REM if exist "%vs_temp%vs-tools.git" (rmdir "%vs_temp%\vs-tools-master" /s /q >NUL 2>&1)
REM echo "%vs_path%7za.exe" x -y -aoa "%vs_temp%vs-tools.git.zip" -o"%vs_temp%" >>"%reinstall_vs_tools%" 2>&1
REM "%vs_path%7za.exe" x -y -aoa "%vs_temp%vs-tools.git.zip" -o"%vs_temp%"
REM rem echo cd "%vs_temp%\vs-tools-master" >>"%reinstall_vs_tools%" 2>&1
REM rem cd "%vs_temp%\vs-tools-master"
REM rem echo "%py_exe%" -m build --wheel --outdir dist/ >>"%reinstall_vs_tools%" 2>&1
REM rem "%py_exe%" -m build --wheel --outdir dist/
REM echo CD "%py_path%" >>"%reinstall_vs_tools%" 2>&1
REM CD "%py_path%"
REM echo set "PYTHONPATH=%py_path%" >>"%reinstall_vs_tools%" 2>&1
REM set "PYTHONPATH=%py_path%"
REM echo dir %PYTHONPATH% >>"%reinstall_vs_tools%" 2>&1
REM dir %PYTHONPATH%
REM echo "%py_exe%" pip.pyz install --editable "%vs_temp%\vs-tools-master" --prefix=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose >>"%reinstall_vs_tools%" 2>&1
REM "%py_exe%" pip.pyz install --editable "%vs_temp%\vs-tools-master" --prefix=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM
REM ================
REM
REM vs-kernels ...
REM documentation says the following libraries are required: descale fmtconv vstools
REM for older release of vs-kernels (depends on vstools): "%py_exe%" pip.pyz install vskernels --prefix=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM for current git head of vs-kernels (depends on vstools): "%py_exe%" pip.pyz install  git+https://github.com/Irrational-Encoding-Wizardry/vs-kernels.git --prefix=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM set "reinstall_vs_kernels=%vs_CD%reinstall_vs_kernels.bat"
REM del /f "%reinstall_vs_kernels%" >NUL 2>&1
REM echo ^@echo on >>"%reinstall_vs_kernels%" 2>&1
REM echo ^@setlocal ENABLEDELAYEDEXPANSION >>"%reinstall_vs_kernels%" 2>&1
REM echo ^@setlocal enableextensions >>"%reinstall_vs_kernels%" 2>&1
REM echo CD "%vs_CD%" >>"%reinstall_vs_kernels%" 2>&1
REM CD "%vs_CD%"
REM echo "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%vs-kernels.git.zip" "https://github.com/Irrational-Encoding-Wizardry/vs-kernels/archive/refs/heads/master.zip" >>"%reinstall_vs_kernels%" 2>&1
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%vs-kernels.git.zip" "https://github.com/Irrational-Encoding-Wizardry/vs-kernels/archive/refs/heads/master.zip"
REM echo if exist "%vs_temp%vs-kernels.git" ^(rmdir "%vs_temp%\vs-kernels-master" /s /q ^>NUL 2^>^&1^) >>"%reinstall_vs_kernels%" 2>&1
REM if exist "%vs_temp%vs-kernels.git" (rmdir "%vs_temp%\vs-kernels-master" /s /q >NUL 2>&1)
REM echo "%vs_path%7za.exe" x -y -aoa "%vs_temp%vs-kernels.git.zip" -o"%vs_temp%" >>"%reinstall_vs_kernels%" 2>&1
REM "%vs_path%7za.exe" x -y -aoa "%vs_temp%vs-kernels.git.zip" -o"%vs_temp%"
REM echo CD "%py_path%" >>"%reinstall_vs_kernels%" 2>&1
REM CD "%py_path%"
REM echo set "PYTHONPATH=%py_path%" >>"%reinstall_vs_kernels%" 2>&1
REM set "PYTHONPATH=%py_path%"
REM echo dir %PYTHONPATH% >>"%reinstall_vs_kernels%" 2>&1
REM dir %PYTHONPATH%
REM echo "%py_exe%" pip.pyz install --editable "%vs_temp%\vs-kernels-master" --prefix=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose >>"%reinstall_vs_kernels%" 2>&1
REM "%py_exe%" pip.pyz install --editable "%vs_temp%\vs-kernels-master" --prefix=%vs_path% --prefix=%vs_path% --no-cache-dir --upgrade --check-build-dependencies --force-reinstall --upgrade-strategy eager --verbose
REM echo pause >>"%reinstall_vs_kernels%" 2>&1
REM
REM --------------------------------------------------------------------------------------------------------------------------------------------------------
REM
CD "%vs_path%"
set "vs_path_drive=%vs_path:~,2%"
REM set the path otherwise vsrepo.py aborts because it cannot do import vapoursynth
PATH
PATH=%vs_path%;%PATH%
PATH
REM IF EXIST "%py_path%vsrepo.py" (del /f "%py_path%vsrepo.py")
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_path%vsrepo.py" "https://raw.githubusercontent.com/vapoursynth/vsrepo/master/vsrepo.py"
REM IF EXIST "%py_path%vsrupdate.py" (del /f "%py_path%vsrupdate.py")
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_path%vsrupdate.py" "https://raw.githubusercontent.com/vapoursynth/vsrepo/master/vsrupdate.py"
IF EXIST "%vs_temp%vsrepo.zip" (del /f "%vs_temp%vsrepo.zip")
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%vsrepo.zip" "https://github.com/vapoursynth/vsrepo/archive/refs/heads/master.zip"
"%vs_path%7za.exe" t "%vs_temp%vsrepo.zip"
"%vs_path%7za.exe" e -y -aoa "%vs_temp%vsrepo.zip" -o"%vs_path%" vsrepo-master\vsrepo.py vsrepo-master\vsrupdate.py vsrepo-master\vsgenstubs.py
"%vs_path%7za.exe" e -y -aoa "%vs_temp%vsrepo.zip" -o"%vs_path%vsgenstubs4" vsrepo-master\vsgenstubs4
REM
REM
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" update
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" paths
REM "%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" installed | SORT
REM "%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" available | SORT
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" installed | SORT > "%vs_path%run_vsrepo_1.installed.before.txt" 2>&1
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" available | SORT > "%vs_path%run_vsrepo_2.available.before.txt" 2>&1
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install fftw3_library
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install Subtext
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install AssRender
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install MVTools
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install Cnr2
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install TCanny
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install DCTFilter
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install Deblock
REM "%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install FineSharp
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install DFTTest
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install LimitedSharpen2 
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install Deblockpp7
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install AWarpSharp
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install AWarpSharp2
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install LGhost
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install Histogram
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install LSMASHSource
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install FFmpegSource2
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install imwri
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install adjust
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install mvmulti
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install muvsfunc
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install mvsfunc
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install havsfunc
REM hnwvsfunc replaced by G41Fun
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install hqdn3d
REM "%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install G41Fun  # no not this
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install yadifmod
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install BWDIF
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install ZNEDI3
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install degrainmedian 
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install MCDenoise
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install dfttest 
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install fft3dfilter
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install eedi2
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install nnedi3
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install nnedi3_resample
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install nnedi3_rpow2
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install nnedi3_weights
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install sangnom
REM REM for vstools, vskernel, vs_transitions :-
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install descale 
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" install fmtconv
REM
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" upgrade-all
REM
REM Some apparently import others :( ... Portable vapoursynth stuff only works if the .py are at the root level, so copy them over.
echo COPY /Y /V "%vs_path%vapoursynth64\plugins\libfftw3*.dll" "%vs_path%"
COPY /Y /V "%vs_path%vapoursynth64\plugins\libfftw3*.dll" "%vs_path%"
echo copy /Y /V "%vs_path%vapoursynth64\scripts"\*.py "%vs_path%"
copy /Y /V "%vs_path%vapoursynth64\scripts"\*.py "%vs_path%"
REM
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" installed | SORT > "%vs_path%run_vsrepo_3.installed.after.txt" 2>&1
"%py_exe%" "%vs_path%vsrepo.py" -p -t win64 -f -b "%vs_path%vapoursynth64\plugins" -s "%vs_path%vapoursynth64\scripts" available | SORT > "%vs_path%run_vsrepo_4.available.after.txt" 2>&1
REM
CD "%vs_path%"
IF EXIST "%vs_temp%MediaInfo*.zip" (del /f "%vs_temp%MediaInfo*.zip")
IF EXIST "%vs_temp%MediaInfo*.dll" (del /f "%vs_temp%MediaInfo*.dll")
IF EXIST "%vs_temp%MediaInfo*.py" (del /f "%vs_temp%MediaInfo*.py")
IF EXIST "%vs_path%MediaInfo*.zip" (del /f "%vs_path%MediaInfo*.zip")
IF EXIST "%vs_path%MediaInfo*.dll" (del /f "%vs_path%MediaInfo*.dll")
IF EXIST "%vs_path%MediaInfo*.py" (del /f "%vs_path%MediaInfo*.py")
set "f=MediaInfo_DLL_23.04_Windows_x64_WithoutInstaller"
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%MediaInfo.zip" "https://mediaarea.net/download/binary/libmediainfo0/23.04/MediaInfo_DLL_23.04_Windows_x64_WithoutInstaller.zip"
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%MediaInfo.zip" "https://mediaarea.net/download/binary/libmediainfo0/23.03/MediaInfo_DLL_23.03_Windows_x64_WithoutInstaller.zip"
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%MediaInfo.zip" "https://mediaarea.net/download/binary/libmediainfo0/22.12/MediaInfo_DLL_23.03_Windows_x64_WithoutInstaller.zip"
"%vs_path%7za.exe" t "%vs_temp%MediaInfo.zip"
"%vs_path%7za.exe" e -y -aoa "%vs_temp%MediaInfo.zip" -o"%vs_path%" MediaInfo.dll Developers\Source\MediaInfoDLL\MediaInfoDLL.py Developers\Source\MediaInfoDLL\MediaInfoDLL3.py
copy /b /y /z "%vs_path%MediaInfo*.py" "%vs_path%vapoursynth64\scripts\"
REM
IF EXIST "%vs_temp%MediaInfoCLI*.zip" (del /f "%vs_temp%MediaInfoCLI*.zip")
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%MediaInfoCLI.zip" https://mediaarea.net/download/binary/mediainfo/23.04/MediaInfo_CLI_23.04_Windows_x64.zip
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%MediaInfoCLI.zip" https://mediaarea.net/download/binary/mediainfo/23.03/MediaInfo_CLI_23.03_Windows_x64.zip
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%MediaInfoCLI.zip" https://mediaarea.net/download/binary/mediainfo/22.12/MediaInfo_CLI_22.12_Windows_x64.zip
"%vs_path%7za.exe" t "%vs_temp%MediaInfoCLI.zip"
"%vs_path%7za.exe" e -y -aoa "%vs_temp%MediaInfoCLI.zip" -o"%vs_path%" MediaInfo.exe
REM
IF EXIST "%vs_temp%ffmpeg.zip" (del /f "%vs_temp%ffmpeg.zip")
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%ffmpeg.zip" https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
"%vs_path%7za.exe" e -y -aoa "%vs_temp%ffmpeg.zip" -o"%vs_path%" ffmpeg-master-latest-win64-gpl\bin
copy /Y /V "%vs_path%ffmpeg.exe" "%vs_CD%"
copy /Y /V "%vs_path%ffmpeg.exe" "%vs_path%"
copy /Y /V "%vs_path%ffprobe.exe" "%vs_CD%"
copy /Y /V "%vs_path%ffprobe.exe" "%vs_path%"

REM THIS WORKS TO RETRIEVE THE LATEST RELEASE FROM GITHUB
CD "%py_path%"
"%py_exe%" pip.pyz uninstall pydub --verbose
CD "%vs_path%"
del /f "%vs_temp%pydub.zip"
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%pydub.zip" https://github.com/jiaaro/pydub/archive/refs/heads/master.zip
rmdir /s /q "%vs_path%pydub"
"%vs_path%7za.exe" e -y -aoa "%vs_temp%pydub.zip" -o"%vs_path%pydub" "pydub-master\pydub\*"

REM THIS WORKS TO RETRIEVE THE LATEST RELEASE FROM GITHUB
REM THE FILENAME IS LIKE hydra3333-vpy_slideshow-v00.01-1-ge6afec1.zip
REM https://github.com/hydra3333/vpy_slideshow/zipball/main
IF EXIST "%vs_temp%vpy_slideshow.zip" (del /f "%vs_temp%vpy_slideshow.zip")
REM get the latests release ...
REM "%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%vpy_slideshow.zip" https://github.com/hydra3333/vpy_slideshow/zipball/main
REM get the latest git head ...
"%vs_CD%wget.exe" -v -t 1 --server-response --no-check-certificate --timeout=360 -nd -np -nH --no-cookies --output-document="%vs_temp%vpy_slideshow.zip" https://github.com/hydra3333/vpy_slideshow/archive/refs/heads/main.zip
"%vs_path%7za.exe" t "%vs_temp%vpy_slideshow.zip"
"%vs_path%7za.exe" e -y -aoa "%vs_temp%vpy_slideshow.zip" -o"%vs_CD%"   *\vpy_slideshow.vpy *\vpy_slideshow.bat *\SLIDESHOW_PARAMETERS.ini *\show_unique_properties.bat *\show_unique_properties.vpy
"%vs_path%7za.exe" e -y -aoa "%vs_temp%vpy_slideshow.zip" -o"%vs_path%" *\vs_transitions.py

CD "%vs_CD%"
pause
exit
