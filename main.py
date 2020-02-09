from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk
import sensor_setting
import serial
import os
from datetime import datetime
from pytz import timezone
import pymysql.cursors

# MySQL の設定
host="localhost"
user="sensorpi"
password="raspberry"
db="sensor"
charset="utf8mb4"

# センサー情報の DB 登録クラス
class Sensor2DB(ttk.Frame):
    # コンストラクタ
    def __init__(self, master=None, *args, **kwargs):
        # 親クラスのコンストラクタ
        super().__init__(args, **kwargs)

        self.label1=Label(self, text="接続先", bg="white", font=("Sans", 16, "normal"))
        self.label1.grid(row=0, column=0, sticky="news", ipadx=5, ipady=2)

        self.frame2=Frame(self, bg="white")
        self.frame2.grid(row=0, column=1, sticky="news")
        self.frame2.columnconfigure(0, weight=1)
        self.label2=Label(self.frame2, text="", bg="#E4E4FF", font=("Sans", 16, "normal"))
        self.label2.grid(row=0, column=0, sticky="news", padx=5, pady=2)

        self.label3=Label(self, text="通信速度", bg="white", font=("Sans", 16, "normal"))
        self.label3.grid(row=1, column=0, sticky="news", ipadx=5, ipady=2)

        self.frame4=Frame(self, bg="white")
        self.frame4.grid(row=1, column=1, sticky="news")
        self.frame4.columnconfigure(0, weight=1)
        self.label4=Label(self.frame4, text="", bg="#E4E4FF", font=("Sans", 16, "normal"))
        self.label4.grid(row=0, column=0, sticky="news", padx=5, pady=2)

        self.label5=Label(self, text="温度 (D8)", bg="white", font=("Sans", 16, "normal"))
        self.label5.grid(row=2, column=0, sticky="news", ipadx=5, ipady=2)

        self.frame6=Frame(self, bg="white")
        self.frame6.grid(row=2, column=1, sticky="news")
        self.frame6.columnconfigure(0, weight=1)
        self.label6=Label(self.frame6, text="", bg="#E4FFE4", font=("Sans", 16, "normal"))
        self.label6.grid(row=0, column=0, sticky="news", padx=5, pady=2)

        self.label7=Label(self, text="湿度 (D8)", bg="white", font=("Sans", 16, "normal"))
        self.label7.grid(row=3, column=0, sticky="news", ipadx=5, ipady=2)

        self.frame8=Frame(self, bg="white")
        self.frame8.grid(row=3, column=1, sticky="news")
        self.frame8.columnconfigure(0, weight=1)
        self.label8=Label(self.frame8, text="", bg="#E4FFE4", font=("Sans", 16, "normal"))
        self.label8.grid(row=0, column=0, sticky="news", padx=5, pady=2)

        self.label9=Label(self, text="体感 (D8)", bg="white", font=("Sans", 16, "normal"))
        self.label9.grid(row=4, column=0, sticky="news", ipadx=5, ipady=2)

        self.frame10=Frame(self, bg="white")
        self.frame10.grid(row=4, column=1, sticky="news")
        self.frame10.columnconfigure(0, weight=1)
        self.label10=Label(self.frame10, text="", bg="#E4FFE4", font=("Sans", 16, "normal"))
        self.label10.grid(row=0, column=0, sticky="news", padx=5, pady=2)

        self.label11=Label(self, text="気圧 (A2)", bg="white", font=("Sans", 16, "normal"))
        self.label11.grid(row=5, column=0, sticky="news", ipadx=5, ipady=2)

        self.frame12=Frame(self, bg="white")
        self.frame12.grid(row=5, column=1, sticky="news")
        self.frame12.columnconfigure(0, weight=1)
        self.label12=Label(self.frame12, text="", bg="#E4FFE4", font=("Sans", 16, "normal"))
        self.label12.grid(row=0, column=0, sticky="news", padx=5, pady=2)

        self.label13=Label(self, text="照度 (A3)", bg="white", font=("Sans", 16, "normal"))
        self.label13.grid(row=6, column=0, sticky="news", ipadx=5, ipady=2)

        self.frame14=Frame(self, bg="white")
        self.frame14.grid(row=6, column=1, sticky="news")
        self.frame14.columnconfigure(0, weight=1)
        self.label14=Label(self.frame14, text="", bg="#E4FFE4", font=("Sans", 16, "normal"))
        self.label14.grid(row=0, column=0, sticky="news", padx=5, pady=2)

        # 通信準備中
        self.ser_init=False

        # デバイス名
        self.ser_name=""

        # 気温、湿度、体感温度、気圧、照度の最大値[0]・平均値[1]・最小値[2]
        self.temp=[0.0, 0.0, 0.0]
        self.humi=[0.0, 0.0, 0.0]
        self.hidx=[0.0, 0.0, 0.0]
        self.press=[0, 0, 0]
        self.photo=[0, 0, 0]

        # 平均値を求めるためのカウンタ
        self.count=0

        # 終了ボタンを押したとき
        def button_clicked():
            # 通信準備完了かつ、センサーデバイスが OS に認識されている場合
            if self.ser_init and self.ser_name != "":
                # シリアル通信を終了
                self.ser.close()

            # 閉じるボタンイベント
            on_closing()

        self.frame=Frame(self, bg="white")
        self.frame.grid(row=7, column=0, columnspan=2, sticky="news")
        self.frame.columnconfigure(0, weight=1)
        self.button=Button(self.frame, text="アプリケーション終了", command=button_clicked)
        self.button.grid(row=0, column=0, sticky="news", padx=40, pady=15)

        # 各行の列幅を相対的に指定
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        # バックライト状態（0=消灯, 1=点灯）
        self.backlight_state=1

    # 表示を更新
    def update(self):
        # センサーデバイスを探す
        self.ser_name=sensor_setting.dev_search()

        try:
            # 通信準備中かつ、センサーデバイスが OS に認識されている場合
            if not self.ser_init and self.ser_name != "":
                # シリアル通信の初期化
                self.ser=serial.Serial(self.ser_name, sensor_setting.bps, timeout=sensor_setting.timeout)

                # 通信準備完了
                self.ser_init=True

                # 接続先を表示
                self.label2.configure(text=self.ser_name)

                # 接続速度を表示
                self.label4.configure(text="{0}bps".format(sensor_setting.bps))

        # 例外時は何もしない
        except:
            pass

        # 通信準備完了かつ、センサーデバイスが OS に認識されていない場合
        if self.ser_init and self.ser_name == "":
            # シリアル通信を終了
            self.ser.close()

            # 通信準備中
            self.ser_init=False

            # 接続先をクリア
            self.label2.configure(text="")

            # 接続速度をクリア
            self.label4.configure(text="")

        try:
            # シリアル通信を開始
            if self.ser.is_open == False:
                self.ser.open()

            # 1行受信（b'気温,湿度,体感温度,照度¥r¥n' の形式で受信）
            serval=self.ser.readline()

            # 受信バッファをフラッシュする
            self.ser.flushInput()

            if len(serval) >= 0:
                # 改行コードを削除（b'気温,湿度,体感温度,照度'）
                serval=serval.strip()

                # バイナリ形式から文字列に変換（気温,湿度,体感温度,照度）
                serval=serval.decode("utf-8")

                # CSV を分割
                serary=serval.split(",")

                # 分割数が4でない場合は例外
                if len(serary) != 4:
                    raise Exception

                # バックライト点灯中に部屋が暗くなったら
                if int(serary[3]) < 50 and self.backlight_state == 1:
                    # バックライト消灯
                    os.system('sudo sh -c "echo 0 > /sys/class/backlight/soc\:backlight/brightness"')
                    self.backlight_state=0

                # バックライト消灯中に部屋が明るくなったら
                elif int(serary[3]) >= 50 and self.backlight_state == 0:
                    # バックライト点灯
                    os.system('sudo sh -c "echo 1 > /sys/class/backlight/soc\:backlight/brightness"')
                    self.backlight_state=1

                # 気温を更新
                self.label6.configure(text="{0}°c".format(float(serary[0])))

                # 気温の最大値[0]・平均値[1]・最小値[2]
                if self.temp[0] == 0.0 or self.temp[0] < float(serary[0]) and float(serary[0]) < 60:
                    self.temp[0]=float(serary[0])
                self.temp[1]+=float(serary[0])
                if self.temp[2] == 0.0 or self.temp[2] > float(serary[0]) and float(serary[0]) < 60:
                    self.temp[2]=float(serary[0])

                # 湿度を更新
                self.label8.configure(text="{0}%".format(float(serary[1])))

                # 湿度の最大値[0]・平均値[1]・最小値[2]
                if self.humi[0] == 0.0 or self.humi[0] < float(serary[1]) and float(serary[1]) <= 100:
                    self.humi[0]=float(serary[1])
                self.humi[1]+=float(serary[1])
                if self.humi[2] == 0.0 or self.humi[2] > float(serary[1]) and float(serary[1]) <= 100:
                    self.humi[2]=float(serary[1])

                # 体感温度を更新
                self.label10.configure(text="{0}°c".format(float(serary[2])))

                # 体感温度の最大値[0]・平均値[1]・最小値[2]
                if self.hidx[0] == 0.0 or self.hidx[0] < float(serary[2]) and float(serary[2]) < 60:
                    self.hidx[0]=float(serary[2])
                self.hidx[1]+=float(serary[2])
                if self.hidx[2] == 0.0 or self.hidx[2] > float(serary[2]) and float(serary[2]) < 60:
                    self.hidx[2]=float(serary[2])

                # 照度を更新
                self.label14.configure(text=serary[3])

                # 照度の最大値[0]・平均値[1]・最小値[2]
                if self.photo[0] == 0.0 or self.photo[0] < int(serary[3]):
                    self.photo[0]=int(serary[3])
                self.photo[1]+=int(serary[3])
                if self.photo[2] == 0.0 or self.photo[2] > int(serary[3]):
                    self.photo[2]=int(serary[3])

                # 平均値カウントアップ
                self.count+=1

                # 現在の時間が00-01秒のとき
                now=datetime.now(timezone("UTC"))
                if now.second == 0 or now.second == 1:
                    # データベースに接続
                    conn=pymysql.connect(
                        host=host,
                        user=user,
                        password=password,
                        db=db,
                        charset=charset,
                        cursorclass=pymysql.cursors.DictCursor
                    )

                    try:
                        # データベースにセンサーの値を挿入
                        with conn.cursor() as cursor:
                            sql  = "INSERT INTO tbl_serval (time, "
                            sql += "max_temperature, avg_temperature, min_temperature, "
                            sql += "max_humidity, avg_humidity, min_humidity, "
                            sql += "max_heatindex, avg_heatindex, min_heatindex, "
                            sql += "max_photocell, avg_photocell, min_photocell)"
                            sql += "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                            cursor.execute(sql, (
                                "{0:%Y-%m-%d %H:%M:00}".format(now),
                                self.temp[0],
                                round(float(self.temp[1])/self.count, 1),
                                self.temp[2],
                                self.humi[0],
                                round(float(self.humi[1])/self.count, 1),
                                self.humi[2],
                                self.hidx[0],
                                round(float(self.hidx[1])/self.count, 1),
                                self.hidx[2],
                                self.photo[0],
                                round(float(self.photo[1])/self.count, 1),
                                self.photo[2]
                            ))
                        conn.commit()
                    finally:
                        # データベースから切断
                        conn.close()

                    # センサーの値をクリア
                    self.temp=[0.0, 0.0, 0.0]
                    self.humi=[0.0, 0.0, 0.0]
                    self.hidx=[0.0, 0.0, 0.0]
                    self.press=[0, 0, 0]
                    self.photo=[0, 0, 0]

                    # 平均値カウントクリア
                    self.count=0

        # 例外時
        except:
            # センサー表示をクリア
            self.label6.configure(text="")
            self.label8.configure(text="")
            self.label10.configure(text="")
            self.label12.configure(text="")
            self.label14.configure(text="")

        # 2秒後に再表示
        self.master.after(2000, self.update)


# メインウィンドウ作成
root=Tk()

# メインウィンドウタイトル
root.title("Sensor2DB")

# メインウィンドウサイズ
root.geometry("280x320")

# メインウィンドウの背景色
root.configure(bg="white")

# メインウィンドウをリサイズしない
root.resizable(0, 0)

# Sensor2DB クラスのインスタンスを生成
app=Sensor2DB(root)

# 画面に配置
app.pack(expand=1, fill="x")

# センサー表示の更新を開始（update メソッド呼び出し）
app.update()

# 閉じるボタンイベント
def on_closing():
    if messagebox.askyesno("Quit", "終了しますか？"):
        # バックライト点灯
        os.system('sudo sh -c "echo 1 > /sys/class/backlight/soc\:backlight/brightness"')

        # アプリケーション終了
        root.destroy()

# 閉じるボタンイベントを登録
root.protocol("WM_DELETE_WINDOW", on_closing)

# メインループ
root.mainloop()
