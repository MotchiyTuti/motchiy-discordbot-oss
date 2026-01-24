# マインクラフトサーバボット
このプロジェクトは、Minecraftサーバーの開始と停止操作を簡単にするための管理ツールです。  
著者が個人的に便利だと感じる機能を含んでいます。  
Ubuntu LTS上のPython 3で構築されており、軽量で実用的な運用に最適化されています。

## 主な機能
- コマンドでMinecraftサーバーの開始・停止が可能
- Discordボット連携を前提に設計（拡張が容易）
- ローカル環境および手動サーバー運用に最適化

## セットアップ
まず、Python3とtmuxをインストールしてください（Ubuntuの場合）:

```bash
sudo apt update -y
sudo apt upgrade -y
sudo apt install python3 python3-venv tmux
```

その後、`.venv/` 仮想環境はすでに作成されており、必要なパッケージもインストール済みです。  
環境を有効化し、プログラムを実行するには以下のコマンドを使用してください:

### token.txtの作成
Discordボットのトークンを生成し、token.txtというファイル名でプレーンテキストとして保存してください。

```bash
source .venv/bin/activate
python3 main.py
```

## 使い方
コマンドの先頭には `!` を付けてください。  
利用可能なコマンド一覧は `!help` で確認できます。