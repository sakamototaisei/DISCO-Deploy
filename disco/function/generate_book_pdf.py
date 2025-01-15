from PIL import Image, ImageDraw
import random
from fpdf import FPDF
import tempfile
from PIL import Image
from io import BytesIO
from typing import List


def generate_pdf(illustration_data_list: List[bytes], background_data_list: List[bytes]) -> bytes:
    """
    イラスト画像と背景画像を1ページ内で左右に並べて合成し、
    各ペアを1ページとしてPDFファイルを生成。

    - 各画像は正方形のアスペクト比を想定し、左右に並べて横幅を2倍にして合成し、
      最終的に正方形 × 2(横に連結)のサイズとなる大きな画像を1ページに配置します。
    - 出力PDFはページサイズを (2048pt × 2048pt) の正方形に設定し、
      左半分(幅1024px)にイラスト、右半分(幅1024px)にテキスト背景をそれぞれリサイズ配置します。

    Args:
        illustration_data_list (list): イラスト画像のバイトデータのリスト（要素数 n）
        background_data_list (list): 背景画像のバイトデータのリスト（要素数 n）

    Returns:
        bytes: PDFデータをバイト列として返します
    """
    if len(illustration_data_list) != len(background_data_list):
        raise ValueError("イラスト画像と背景画像のリストは同じ数である必要があります。")

    # FPDF でページサイズを 2048×2048 pt の正方形に設定
    pdf_width = 2250  # 2048 + 12pt の余白
    pdf_height = 2048
    pdf = FPDF(unit="pt", format=[pdf_width, pdf_height])
    pdf.set_auto_page_break(auto=False)

    # 左右に分割して貼り付ける幅・高さ
    left_img_width = pdf_width // 2   # 1024
    left_img_height = pdf_height      # 2048
    right_img_width = pdf_width // 2  # 1024
    right_img_height = pdf_height     # 2048

    # 各イラスト＆背景画像のペアごとにページを追加
    for i, (illus_data, back_data) in enumerate(zip(illustration_data_list, background_data_list)):
        # 1. 左のイラスト画像を開いてリサイズ
        try:
            illus_img = Image.open(BytesIO(illus_data)).convert('RGB')
        except Exception as e:
            raise ValueError(f"{i+1}番目のイラスト画像を開けませんでした: {e}")

        illus_img = illus_img.resize(
            (left_img_width, left_img_height), Image.LANCZOS)

        # 2. 右の背景画像を開いてリサイズ
        try:
            back_img = Image.open(BytesIO(back_data)).convert('RGB')
        except Exception as e:
            raise ValueError(f"{i+1}番目の背景画像を開けませんでした: {e}")

        back_img = back_img.resize(
            (right_img_width, right_img_height), Image.LANCZOS)

        # 3. 新たな空イメージ(2048×2048)を作成し、左にイラスト・右に背景を貼り付け
        combined_img = Image.new(
            "RGB", (pdf_width, pdf_height), (255, 255, 255))
        combined_img.paste(illus_img, (0, 0))
        combined_img.paste(back_img, (left_img_width, 0))

        # 4. ページを追加し、合成画像を一時ファイルに保存→PDFに貼り付け
        pdf.add_page()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
            combined_img.save(tmpfile, format='JPEG')
            tmpfile.seek(0)
            # PDF上で (0, 0) に 2048×2048 pt で配置
            pdf.image(tmpfile.name, x=0, y=0, w=pdf_width, h=pdf_height)

    # PDFデータをバイト列として取得
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes


# テスト用コード
def main():
    # ダミーのイラスト画像4枚 + 背景画像4枚を用意する
    illustration_data_list = []
    background_data_list = []

    # ここではダミーとして 900×1600 の画像を作成
    # （実際には正方形前提でもテストしやすいよう任意サイズの画像を使う）
    base_w, base_h = 900, 1600

    for i in range(4):
        # イラスト用ダミー画像
        illus_img = Image.new("RGB", (base_w, base_h), color=_random_color())
        draw_illus = ImageDraw.Draw(illus_img)
        draw_illus.text((50, 50), f"Illustration {i+1}", fill=(255, 255, 255))

        illus_bytes = BytesIO()
        illus_img.save(illus_bytes, format="PNG")
        illus_bytes.seek(0)
        illustration_data_list.append(illus_bytes.getvalue())

        # 背景用ダミー画像
        back_img = Image.new("RGB", (base_w, base_h), color=_random_color())
        draw_back = ImageDraw.Draw(back_img)
        draw_back.text((50, 50), f"Background {i+1}", fill=(255, 255, 255))

        back_bytes = BytesIO()
        back_img.save(back_bytes, format="PNG")
        back_bytes.seek(0)
        background_data_list.append(back_bytes.getvalue())

    # PDF生成
    pdf_data = generate_pdf(illustration_data_list, background_data_list)

    # ファイルに書き出して確認
    output_filename = "sample_output.pdf"
    with open(output_filename, "wb") as f:
        f.write(pdf_data)

    print(f"[INFO] PDFを '{output_filename}' に出力しました。")


def _random_color():
    """背景色として適当なRGB値のタプルを返すヘルパー関数"""
    return tuple(random.randint(0, 255) for _ in range(3))


if __name__ == "__main__":
    main()
