# Simple python3 vbf decoder/info displayer

Requires python 3.3+, tested on 3.6.
VBF files are used for updating firmware on volvo/mazda and ford cars.
Ford decoded to include the apperantly broken description as comments so it tries to find that as well. Software is as is (e.g. crappy, bad find command), ymmv.

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
File is a ford ACM file.

```
python3 vbfdecode.py F1BT-14C044-HJ.vbf 
VBF [v2.4]:
Description: Strategy for ACU [Audio Control Unit]
09.5MY Ford C344E L0CPlus
Created on 2016/03/02
Released by [email removed for privacy reasons] 
Comment: c346e_ahu_ngl0cplus_mid_dab_c_prod
                  
Software part: F1BT-14C044-HJ type: EXE
Network: CAN_HS @ 0x727
Frame_format:CAN_STANDARD
Erase frames:
0x00004000
0x000BC000
Data blobs:
0x00004000	649720	 b6d8
0x000B9000	27816	 5d14
```
