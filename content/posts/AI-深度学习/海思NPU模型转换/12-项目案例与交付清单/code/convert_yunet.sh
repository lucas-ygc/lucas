#!/usr/bin/env bash
# 在本项目 SVP 转换容器内运行，仅写入指定实验目录。
set -eo pipefail
source /usr/local/Ascend/ascend-toolkit/svp_latest/x86_64-linux/script/setenv.sh
set -u
if [ "$#" -ne 1 ]; then
    echo 'usage: bash convert_yunet.sh /workspace/application/.temp/my-yunet-run' >&2
    exit 2
fi
case_dir="$1"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
test -s "$case_dir/yunet320_input255.onnx"
test -s "$case_dir/calibration.txt"
if [ -e "$case_dir/om" ]; then
    echo 'om directory already exists; use a fresh experiment directory' >&2
    exit 2
fi
mkdir "$case_dir/om"
cp "$script_dir/aipp_yunet.cfg" "$case_dir/om/aipp.cfg"
cp "$0" "$case_dir/om/convert-command.sh"
atc --version > "$case_dir/om/atc-version.txt" 2>&1
atc --model="$case_dir/yunet320_input255.onnx" \
  --framework=5 --soc_version=Hi3516CV610 \
  --input_shape='input:1,3,320,320' --input_type='input:UINT8' \
  --input_format=NCHW --batch_num=1 --online_model_type=0 \
  --insert_op_conf="$case_dir/om/aipp.cfg" \
  --compile_mode=1 --quant_mode=0 --weight_quant_per_channel=1 \
  --image_list="input:$case_dir/calibration.txt" \
  --output="$case_dir/om/yunet320" \
  --output_reorder=0 --output_type=FP32 \
  --save_original_model=true --dump_data=0 --log_level=0 \
  > "$case_dir/om/convert.log" 2>&1
test -s "$case_dir/om/yunet320_original.om"
sha256sum "$case_dir/om/yunet320_original.om" > "$case_dir/om/model.sha256"
