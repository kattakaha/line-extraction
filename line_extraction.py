import cv2
import os
import sys


OUTPUT_DIR_NAME = "output"
# 出力するファイルのフォーマットを指定する定数
OUTPUT_EXTENTION = "png"

# openCV imwriteの仕様により指定できるフォーマットは限定されています
# 詳しくはopenCV imwriteのドキュメントをご確認ください
# URL: https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html#gabbc7ef1aa2edfaa87772f1202d67e0ce


def normalize_path(path):
    """パスを正規化する
    Unix系のOSでは"/"を使うがWindowsでは"\\"を使うため,
    これを"/"に正規化する
    """
    return os.path.normpath(path.replace('/', '\\'))


def is_absolute_path(path):
    """パスが絶対パスか判定"""
    return os.path.isabs(path)


def get_inputfile_abs_path(path):
    """入力ファイルのパスの絶対パスを取得
    Returns (str): 入力ファイルの絶対パスを返す
    """

    # 入力が絶対パスかどうか判定
    if not is_absolute_path(path):
        absolute_path = os.path.abspath(path)
    else:
        absolute_path = path

    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"{absolute_path} が見つかりません")

    return absolute_path


def get_output_dir_path():
    """OUTPUT_DIR_NAMEディレクトリの絶対パス
        Return (str): このスクリプトと同階層にあるOUTPUT_DIR_NAMEディレクトリの絶対パスを返します
    """
    # このスクリプトの実行されている絶対パスのディレクトリのパスを返す
    script_abs_dir_path = os.path.dirname(__file__)
    output_dir_path = os.path.join(script_abs_dir_path, OUTPUT_DIR_NAME)

    # ouputディレクトリが存在しない場合
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
        print(f"{output_dir_path}ディレクトリを作成しました")
        return output_dir_path

    return output_dir_path


def get_file_basename_without_extention(file_path):
    """ファイルのパスから拡張子なしのファイル名を取得
    Args:
        file_path (str): ファイルの絶対パスまたは相対パス
    Returns (str) : ファイルパスから拡張子なしのファイル名を取得します
    """
    basename = os.path.basename(file_path)
    file_name_without_extention = os.path.splitext(basename)[0]
    return file_name_without_extention


def get_output_file_path(input_file_path, lower_limit, upper_limit):
    """出力ファイルのファイルパスを取得
    Args:
        input_file_path (str): 入力するファイルのファイルパス
        lower_limit (int): 閾値の下限を与える
        upper_limit (int): 閾値の上限を与える

    Return (str): 出力先のファイルの絶対パス
    """

    output_dir_path = get_output_dir_path()
    basename = get_file_basename_without_extention(input_file_path)

    # 出力ファイルのファイル名のフォーマット
    # 元のファイル名_閾値下限_閾値上限.出力フォーマットの拡張子
    output_file_name = f"{basename}_{lower_limit}_{upper_limit}.{OUTPUT_EXTENTION}"

    output_file_path = os.path.join(output_dir_path, output_file_name)
    return output_file_path


def decorator_print_arguments_and_result(original_function):
    """引数と結果を描画するデコレータ"""
    def wrapper_function(*args, **kwargs):
        # 引数の表示
        print("=" * 60)
        print(f"引数: {args}, {kwargs}")
        # 関数の実行
        result = original_function(*args, **kwargs)
        # 結果の表示
        print(f"結果: {result}")
        print("=" * 60)

        return result
    return wrapper_function


@decorator_print_arguments_and_result
def get_line_extraction(input_file_path, lower_limit, upper_limit):
    """画像から線画抽出して画像ファイルに出力
    Args:
        注意：
            閾値の下限・上限はある程度実験的に選ぶ必要がある
            一般的には下限を高めに設定して高い閾値は低い閾値の2~3倍にすることが推奨されている
            最適な値は試行錯誤によって見つける必要があります

        lower_limit (int): 閾値の下限を与える
        upper_limit (int): 閾値の上限を与える

    Return (str): 出力先のファイルの絶対パス
    """
    # 画像をグレースケールで読み込む
    image = cv2.imread(input_file_path, 0)

    # エッジを検出
    edges = cv2.Canny(image, lower_limit, upper_limit)

    # 出力ファイル名を取得
    outptu_file_path = get_output_file_path(
        input_file_path, lower_limit, upper_limit)

    cv2.imwrite(outptu_file_path, edges)

    return outptu_file_path


# バリデーション時のエラーを定義
class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def is_integer(value):
    """整数かどうか判定"""
    if isinstance(value, int):
        return True
    else:
        return False


def validation_check(input_file_path, lower_limit, upper_limit):
    """入力時のバリデーションチェック"""

    # 入力引数の絶対パスを取得
    inputfile_abs_path = get_inputfile_abs_path(
        normalize_path(input_file_path))

    # ファイルが存在するか確認
    if not os.path.exists(inputfile_abs_path):
        raise ValidationError(f"{inputfile_abs_path}が見つかりません")

    # 閾値が整数か確認
    if not (is_integer(lower_limit) and is_integer(upper_limit)):
        raise ValidationError("閾値は整数で入力してください")

    # 閾値の範囲が適切か確認
    if not (lower_limit > 0 and upper_limit > 0):
        raise ValidationError("閾値は自然数で入力してください")
    if not (lower_limit <= upper_limit):
        raise ValidationError("閾値は下限，上限の順に入力してください")

    return True


def main():
    args = sys.argv
    if len(args) != 4:
        raise ValidationError("コマンドライン引数が無効です")

    # 引数の受け取り
    input_file_path = args[1]
    lower_limit = int(args[2])
    upper_limit = int(args[3])

    # バリデーションチェック
    if validation_check(input_file_path, lower_limit, upper_limit):
        get_line_extraction(input_file_path, lower_limit, upper_limit)


if __name__ == '__main__':
    main()
