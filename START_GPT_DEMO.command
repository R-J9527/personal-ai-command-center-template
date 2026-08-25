#!/bin/zsh

set -u

demo_root=${0:A:h}
cd "$demo_root" || exit 1

clear
print "团队 AI 工作台｜只读 GPT Demo"
print ""
print "密钥只保留在本次终端进程内，不会写入仓库或配置文件。"
read -s "OPENAI_API_KEY?请粘贴 OpenAI API Key（输入隐藏），然后按回车："
print ""

if [[ -z "$OPENAI_API_KEY" ]]; then
  print "未输入 Key，网关未启动。"
  read "reply?按回车关闭窗口。"
  exit 2
fi

export OPENAI_API_KEY
unset HISTFILE
print "正在启动只读 GPT 网关……"
print "启动成功后，请打开：http://127.0.0.1:8765/"
print "关闭本窗口即停止 GPT 网关并清除进程中的 Key。"
print ""

python3 backend/openai_gateway.py --port 8765
status_code=$?
unset OPENAI_API_KEY

print ""
print "网关已停止（状态码：$status_code）。"
read "reply?按回车关闭窗口。"
