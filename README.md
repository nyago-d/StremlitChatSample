# StremlitChatSample

## 説明

SteremlitとLangChain、LangGraphを利用した簡単なチャットアプリです。

## 準備

#### `.env.example`を参考に`.env`を作成します  
利用するLLMを変更する際には、併せて対応してください。

#### 仮想環境を作ります
```sh
python -m venv venv
```

#### 仮想環境を有効化します  
※Windowsの場合
```sh
.venv\Scripts\activate
```
※Linuxの場合
```sh
source venv/bin/activate
```

#### パッケージをインストールします
```sh
pip install -r requirements.txt
```

#### アプリを起動します
```sh
streamlit run chat1.py
```
