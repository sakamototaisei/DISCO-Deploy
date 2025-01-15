# function/Child_Disco/generate_background_text.py
from PIL import Image, ImageDraw, ImageFont
import textwrap
from io import BytesIO


def generate_background(texts):
    """
    テキストのリストを受け取り、
    1～2枚目は A の背景画像、3～4枚目は B の背景画像を読み込み、
    文字色は白で描画した画像をリスト（各画像のバイト列）として返す。
    Args:
        texts (list of str): 1P～4P分のテキストが格納されたリスト
        例: [t1, t2, t3, t4]
    Returns:
        list of bytes: テキストを描画した画像のバイト列を4枚分リストで返す
    """
    # --- 背景画像パスを指定 ---
    background_path_A = "disco/images/dance-text.png"  # 1P, 2P 用
    background_path_B = "disco/images/DJ-TEXT.png"  # 3P, 4P 用

    # フォント設定
    font_path = "disco/font_style/hanazomefont/はなぞめフォント.ttf"  # 実際のフォントファイルパスに置き換えてください
    font_size = 43
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        # フォントが見つからない場合、デフォルトフォントを使用
        font = ImageFont.load_default()

    # 画像のサイズ指定
    image_width, image_height = 576, 1024

    # テキストの色を白に変更
    text_color = "white"

    results = []

    # texts は 4 要素を想定
    for i, text in enumerate(texts):
        # 背景画像を選択
        if i < 2:
            # 1番目, 2番目のテキストは A を使用
            bg_img_path = background_path_A
        else:
            # 3番目, 4番目は B を使用
            bg_img_path = background_path_B

        # 背景画像を読み込み＆リサイズ
        try:
            bg_img = Image.open(bg_img_path).convert("RGB")
        except IOError:
            # 背景画像がない場合は白地を生成（保険）
            bg_img = Image.new("RGB", (image_width, image_height), "white")

        bg_img = bg_img.resize((image_width, image_height), Image.LANCZOS)

        draw = ImageDraw.Draw(bg_img)

        # 文章中の「。」「！」の後に改行を入れる
        text = text.replace("。", "。\n").replace("！", "！\n")

        # テキストを改行で分割 → 幅で折り返し
        paragraphs = text.split('\n')
        wrapped_text = []
        for para in paragraphs:
            wrapped_para = textwrap.fill(para, width=12)  # 幅12文字で折り返し
            wrapped_text.append(wrapped_para)
        final_text = "\n".join(wrapped_text)

        # 行ごとに描画する
        lines = final_text.split('\n')
        line_height = font.getsize('A')[1]
        line_spacing = 35  # 行間
        total_text_height = (line_height + line_spacing) * \
            len(lines) - line_spacing

        # 縦方向の開始位置を中央寄せ
        y_start = (image_height - total_text_height) // 2

        # ★ここで微調整したい分だけ下へ移動する
        vertical_offset = 50  # 下へ50px移動（必要に応じて数値を変更）
        y_start += vertical_offset

        x_start = 30  # 左寄せ余白

        y = y_start
        for line in lines:
            draw.text((x_start, y), line, fill=text_color, font=font)
            y += line_height + line_spacing

        # 画像をバイト列に変換
        img_bytes = BytesIO()
        bg_img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        results.append(img_bytes.getvalue())

    return results


# テスト用のコード
def main():
    """
    generate_background 関数にテスト用の texts を渡し、
    生成された画像をファイルに保存して目視確認する。
    """

    # 1P～4P 分のテキスト
    texts = [
        "これは1ページ目の文章です！改行や行間、折り返しの動作を確認します。",
        "2ページ目の文章です。少し長めに記述し、どのように折り返されるかをチェックします。",
        "3ページ目！改行をいくつか入れたりして、表示位置を詳しく検証してみましょう。余白はどうなるでしょうか？",
        "4ページ目のサンプルです！ここで最後に生成された画像を確認して、問題がなければOKです。"
    ]

    # 関数を呼び出して画像バイト列を取得
    results = generate_background(texts)

    # 返ってきたリストは [1P, 2P, 3P, 4P] の4枚分のバイトデータ
    for idx, img_data in enumerate(results, start=1):
        filename = f"test_output_{idx}.png"
        # バイトデータをファイルに書き出し
        with open(filename, "wb") as f:
            f.write(img_data)
        print(f"[INFO] 生成された画像を {filename} として保存しました。")

    print("[INFO] テスト完了。出力された PNG ファイルを開いて内容を確認してください。")


if __name__ == "__main__":
    main()
