LOGO = r"""


                               $$$$$$\  $$\            $$\                         $$\ 
                              $$  __$$\ \__|           $$ |                        $$ |
 $$$$$$$\  $$$$$$\  $$$$$$$\  $$ /  \__|$$\  $$$$$$\ $$$$$$\    $$$$$$\   $$$$$$\  $$ |
$$  _____|$$  __$$\ $$  __$$\ $$$$\     $$ |$$  __$$\\_$$  _|  $$  __$$\ $$  __$$\ $$ |
$$ /      $$ /  $$ |$$ |  $$ |$$  _|    $$ |$$ /  $$ | $$ |    $$ /  $$ |$$ /  $$ |$$ |
$$ |      $$ |  $$ |$$ |  $$ |$$ |      $$ |$$ |  $$ | $$ |$$\ $$ |  $$ |$$ |  $$ |$$ |
\$$$$$$$\ \$$$$$$  |$$ |  $$ |$$ |      $$ |\$$$$$$$ | \$$$$  |\$$$$$$  |\$$$$$$  |$$ |
 \_______| \______/ \__|  \__|\__|      \__| \____$$ |  \____/  \______/  \______/ \__|
                                            $$\   $$ |                                 
                                            \$$$$$$  |                                 
                                             \______/                                  

"""

ENC_PRESETS = """
[MACROS]
4K: -vf scale=3840:-2:flags=neighbor
COPY: -c:a copy
OPUS: -c:a libopus -b:a 128k
YUV444: -pix_fmt yuv444p

[H264/AVC]
NVENC:     -c:v h264_nvenc -preset p7 -rc vbr -b:v 250M -cq 14
AMF:       -c:v h264_amf -quality quality -qp_i 16 -qp_p 18 -qp_b 22
QUICKSYNC: -c:v h264_qsv -preset veryslow -global_quality:v 15
CPU:       -c:v libx264 -preset slow -aq-mode 3 -crf 16

[H265/HEVC]
NVENC:      -c:v hevc_nvenc -preset p7 -rc vbr -b:v 250M -cq 20
AMF:        -c:v hevc_amf -quality quality -qp_i 18 -qp_p 20 -qp_b 24
QuickSync:  -c:v hevc_qsv -preset veryslow -global_quality:v 18
CPU:        -c:v libx265 -preset medium -x265-params aq-mode=3:no-sao=1 -crf 20

[MISC/OTHER]
SVTAV1: -c:v libsvtav1 -crf 20 -preset 4 -g 480
UTVIDEO: -c:v utvideo
"""

YES = ["on", "True", "true", "yes", "y", "1", "yeah", "yea", "yep", "sure", "positive"]
