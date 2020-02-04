from tkinter import Tk, messagebox
import serial.tools.list_ports
import sys

bps="9600"    # 通信速度は固定
timeout=None  # タイムアウトなし

# センサーデバイスを検索
def dev_search():
    dev=""

    # デバイスリストを取得
    devices=serial.tools.list_ports.comports()
    for device in devices:
        # センサーデバイス名を取得
        if device.usb_description()=="Arduino Micro":
            dev=device[0]

    # センサーデバイス名を返却
    return dev

# import sensor_setting による呼び出しでなければ単独処理を実行
if __name__ == "__main__":
    # デバイスを検索
    dev=dev_search()

    # メッセージボックスだけ表示する
    root=Tk()
    root.withdraw()

    # 検索結果を表示
    if dev!="":
        messagebox.showinfo("結果", "センサーデバイス名：\n" + dev)
    else:
        messagebox.showerror("結果", "センサーデバイスが見つかりませんでした")

    # 終了
    sys.exit()
