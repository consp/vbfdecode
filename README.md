# Simple python3 vbf decoder/info displayer

Requires python 3.3+, tested on 3.6.
VBF files are used for updating firmware on volvo/mazda and ford cars.
Ford decided to include the apperantly broken description as comments so it tries to find that as well. Software is as is (e.g. crappy, quick and dirty, bad find command), ymmv.

## Usage
```
python3 vbfdecode.py --help
usage: Try me with a filename.vbf

positional arguments:
  file          VBF file to show data about

optional arguments:
  -h, --help    show this help message and exit
  -b, --binary  Write binary blobs in vbf to [address].bin
```

## Result
Example file is a ford ACM (radio) vbf file:

```
python3 vbfdecode.py F1BT-14C044-HJ.vbf 
VBF [v2.4]:
Description: Strategy for ACU [Audio Control Unit]
09.5MY Ford C344E L0CPlus
Created on 2018/05/08
Released by VTAMILSE@visteon.com
Comment: c346e_ahu_ngl0cplus_mid_dab_c_prod
                  
Software part: F1BT-14C044-HN type: EXE
Network: CAN_HS @ 0x727
Frame_format:CAN_STANDARD
Erase frames:
0x000BC000 (0x00004000)
Data blobs:
0x00004000	655800	 dd6a
0x000B8000	27976	 38ae
```
