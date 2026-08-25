#!/bin/zsh

set -u

demo_root=${0:A:h}
cd "$demo_root" || exit 1

clear
print "团队 AI 工作台｜隔离测试 DeepSeek Demo"
print ""
print "密钥只保留在本次终端进程内，不会写入仓库或配置文件。"
read -s "DEEPSEEK_API_KEY?请粘贴 DeepSeek API Key（输入隐藏），然后按回车："
print ""

if [[ -z "$DEEPSEEK_API_KEY" ]]; then
  print "未输入 Key，网关未启动。"
  read "reply?按回车关闭窗口。"
  exit 2
fi

export DEEPSEEK_API_KEY
export AI_PROVIDER=deepseek
export DEEPSEEK_MODEL=deepseek-v4-flash
unset HISTFILE
print "正在启动 DeepSeek 网关（确认后仅写入隔离测试副本）……"
print "启动成功后，请打开：http://127.0.0.1:8765/"
print "关闭本窗口即停止网关并清除进程中的 Key。"
print ""

python3 backend/openai_gateway.py --port 8765
status_code=$?
unset DEEPSEEK_API_KEY AI_PROVIDER DEEPSEEK_MODEL

print ""
print "网关已停止（状态码：$status_code）。"
read "reply?按回车关闭窗口。"
