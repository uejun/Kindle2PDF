# Kindle2PDF for macOS

MacのKindleアプリで表示している書籍をPDF化するPythonアプリケーション.  
本アプリケーションは, Kindleのキャプチャ画像をPDFにする方式をとっている. 

これにより，既存のソフトウェアに存在する以下の課題を解決している.  

- 画像ベースのKindle書籍はPDF化できない
- 日本語の文字化けが生じる


## 使い方

必要条件: Python3.6+

### ①プロジェクトのダウンロード  
```
git clone https://github.com/uejun/Kindle2PDF
```

### ②依存ライブラリをインストール
```
!pip install -r requirements.txt
```

### ③実行コマンド

```
!python make_pdf.py 
```

#### ページめくりの方向オプション
デフォルトでは，Kindleの次ページが右方向であると想定している.  
もし左方向(左矢印キー)で次ページに進む形式の書籍の場合はdirectionオプションを指定する.  

```
!python make_pdf.py --direction left

```

### ④キャプチャするエリアをドラッグで指定する.  

Kindleのスクリーンキャプチャ画面が表示されるので，
ドラッグにより領域を指定する.  

 Enterキー押下で, KindleのPDF取込がスタートする

### ⑤ 取込終了後，distフォルダ（プロジェクト内）にPDFが出力される. 
