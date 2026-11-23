# QQ 合并转发的发送者

WT 把多页图鉴等内容作为 GsCore 合并消息发送。节点的 QQ 号和昵称由 AstrBot 发信端填写。此补丁适配 xixi 使用的 `astrbot_plugin_gscore_adapter` 0.5.7，在普通群聊和私聊的合并转发中使用当前 OneBot 连接的登录账号及昵称。QQ 客户端根据节点 QQ 号显示头像。群临时私聊继续沿用适配器的逐条发送方式。

更新发信端时，在适配器目录执行以下命令，将路径替换为补丁的实际位置。第一条检查版本是否兼容，成功后再应用并重载该适配器。

```sh
git apply --check /path/to/onebot-forward-sender.patch
git apply /path/to/onebot-forward-sender.patch
```

每次合并发送最多查询一次机器人身份。身份接口暂时不可用时沿用原节点信息，消息仍可发送。修改对经该适配器发出的匿名合并节点生效。
