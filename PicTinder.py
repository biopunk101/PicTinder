import os
import sys
import json

__version__ = "1.1.0"

print("啟動中：正在檢查/載入必備模組...")
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog
except ImportError:
    print("❌ 錯誤: 找不到 tkinter 模組 (請確認安裝 Python 時有勾選 tcl/tk，或在 Mac 執行 brew install python-tk)")
    sys.exit(1)

try:
    from PIL import Image, ImageTk, ImageOps
except ImportError:
    print("❌ 錯誤: 找不到 Pillow 套件。請執行指令：pip install Pillow")
    sys.exit(1)

try:
    from send2trash import send2trash  # 安全刪除：將檔案移至資源回收桶
except ImportError:
    print("❌ 錯誤: 找不到 send2trash 套件。請執行指令：pip install send2trash")
    sys.exit(1)


class PicTinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"🔥 PicTinder v{__version__}")
        self.root.geometry("900x700")

        self.image_list = []
        self.current_index = 0
        self.history = []
        self.trash_queue = []
        self.is_processing = False
        self.last_rename_name = ""

        self.config_file = os.path.expanduser("~/.pictinder_config.json")
        self.progress = {}
        self.load_config()

        # --- UI 佈局 ---
        # 頂部控制區
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=10, padx=20)

        self.btn_select = tk.Button(
            self.top_frame, text="選擇資料夾 (Step 0)", command=self.select_folder, font=("Arial", 12))
        self.btn_select.pack(side=tk.LEFT)

        self.btn_reset = tk.Button(
            self.top_frame, text="🔄 重置進度", command=self.reset_progress, font=("Arial", 12))
        self.btn_reset.pack(side=tk.LEFT, padx=10)

        self.btn_exit = tk.Button(
            self.top_frame, text="🚪 完成並離開", command=self.on_closing, font=("Arial", 12))
        self.btn_exit.pack(side=tk.RIGHT)

        self.lbl_status = tk.Label(
            self.top_frame, text="請選擇包含圖片的資料夾", font=("Arial", 12))
        self.lbl_status.pack(expand=True, pady=5)

        # 中間主顯示區 (包含左右常駐提示與圖片)
        self.center_frame = tk.Frame(root)
        self.center_frame.pack(expand=True, fill=tk.BOTH)

        # 固定在左側的刪除提示
        self.lbl_left_hint = tk.Label(
            self.center_frame, text="❌\n(左滑)", font=("Arial", 40, "bold"), fg="red")
        self.lbl_left_hint.pack(side=tk.LEFT, padx=30)

        # 固定在右側的保留提示
        self.lbl_right_hint = tk.Label(
            self.center_frame, text="✅\n(右滑)", font=("Arial", 40, "bold"), fg="green")
        self.lbl_right_hint.pack(side=tk.RIGHT, padx=30)

        # 中間圖片顯示區 (改用 place 以支援滑動)
        self.lbl_image = tk.Label(self.center_frame)
        self.lbl_image.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 綁定滑鼠拖曳事件 (滑動操作)
        self.lbl_image.bind("<ButtonPress-1>", self.on_drag_start)
        self.lbl_image.bind("<B1-Motion>", self.on_drag_motion)
        self.lbl_image.bind("<ButtonRelease-1>", self.on_drag_release)

        # 覆蓋層 (用於顯示 ✅ 或 ❌，初始為隱藏)
        self.lbl_overlay = tk.Label(root, font=("Arial", 150))

        # 底部控制與說明區
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        # 刪除按鈕 (靠左)
        self.btn_delete = tk.Button(
            self.bottom_frame, text="🗑️ 刪除 (←)", font=("Arial", 16, "bold"), fg="red", command=self.delete_image)
        self.btn_delete.pack(side=tk.LEFT, padx=50)

        # 保留按鈕 (靠右)
        self.btn_keep = tk.Button(
            self.bottom_frame, text="✅ 保留 (→)", font=("Arial", 16, "bold"), fg="green", command=self.keep_image)
        self.btn_keep.pack(side=tk.RIGHT, padx=50)

        # 復原提示 (置中)
        self.lbl_instruction = tk.Label(
            self.bottom_frame, text="💡 提示：左右滑動或使用方向鍵分類 | 按 Enter 重新命名 | 復原按 Ctrl+Z", font=("Arial", 12), fg="gray")
        self.lbl_instruction.pack(expand=True)

        # 垃圾桶計數器 (絕對定位於右下角)
        self.lbl_trash_count = tk.Label(
            root, text="🗑️ 待刪除: 0", font=("Arial", 12, "bold"), fg="gray")
        self.lbl_trash_count.place(
            relx=1.0, rely=1.0, anchor=tk.SE, x=-20, y=-20)

        # --- 綁定鍵盤事件 ---
        self.root.bind('<Left>', self.delete_image)
        self.root.bind('<Right>', self.keep_image)
        self.root.bind('<Control-z>', self.undo_action)
        self.root.bind('<Command-z>', self.undo_action)  # 支援 Mac 鍵盤
        self.root.bind('<Return>', self.rename_image)    # 綁定 Enter 鍵

        # 綁定視窗關閉事件，確保關閉時才真正將檔案丟入垃圾桶
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.last_folder = data.get("last_folder", "")
                    self.progress = data.get("progress", {})
                    return
            except Exception as e:
                print(f"讀取設定檔發生錯誤: {e}")
        self.last_folder = ""
        self.progress = {}

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"last_folder": self.last_folder,
                          "progress": self.progress}, f, ensure_ascii=False)
        except Exception as e:
            print(f"儲存設定檔發生錯誤: {e}")

    def reset_progress(self):
        if messagebox.askyesno("確認重置", "確定要清除所有資料夾的整理進度嗎？\n\n(這將會刪除隱藏的設定檔，一切從頭開始，但不會刪除您的實體圖片)"):
            self.progress = {}
            self.last_folder = ""
            try:
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)
                messagebox.showinfo("成功", "所有進度已重置！")
                # 如果當前有載入圖片，將畫面切回第一張
                if self.image_list:
                    self.current_index = 0
                    self.show_image()
            except Exception as e:
                messagebox.showerror("錯誤", f"無法刪除設定檔: {e}")

    def select_folder(self):
        kwargs = {}
        if self.last_folder and os.path.exists(self.last_folder):
            kwargs['initialdir'] = self.last_folder

        folder_path = filedialog.askdirectory(**kwargs)
        if folder_path:
            self.last_folder = folder_path
            self.save_config()

            # 支援的圖片格式
            valid_ext = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
            files = [f for f in os.listdir(
                folder_path) if f.lower().endswith(valid_ext)]
            files.sort()  # 按照字母排序，確保重新開啟時順序一致

            self.image_list = [os.path.join(folder_path, f) for f in files]

            if not self.image_list:
                messagebox.showinfo("提示", "該資料夾內沒有找到支援的圖片。")
                return

            self.current_index = 0
            # 讀取這個資料夾上次的進度
            last_file = self.progress.get(folder_path)
            if last_file:
                for i, f in enumerate(files):
                    if f == last_file:
                        self.current_index = i + 1  # 找到上次處理的最後一張，從下一張開始
                        break
                    elif f > last_file:
                        self.current_index = i  # 如果上次那張被刪掉了，就從字母順序大於它的第一張開始
                        break

                # 詢問使用者要繼續還是從頭開始
                if self.current_index >= len(self.image_list):
                    prompt = "此資料夾的圖片已全數整理完畢。\n\n要從頭重新整理嗎？"
                else:
                    prompt = f"此資料夾已整理至第 {self.current_index}/{len(self.image_list)} 張。\n\n要從上次中斷處繼續(No)，還是從頭開始(Yes)？"

                restart = messagebox.askyesno(
                    "找到整理進度", prompt, default=messagebox.NO)
                if restart:
                    self.current_index = 0
                    del self.progress[folder_path]
                    self.save_config()

            self.show_image()

    def show_image(self):
        # 確保圖片在正中央 (重置可能存在的滑動偏移)
        self.lbl_image.place(relx=0.5, x=0, rely=0.5, anchor=tk.CENTER)

        # 檢查是否已經處理完所有圖片
        if self.current_index < len(self.image_list):
            img_path = self.image_list[self.current_index]

            try:
                # 讀取圖片並縮放以適合視窗
                img = Image.open(img_path)
                # 根據相機的 EXIF 資訊自動將照片轉正 (避免手機直拍照變成橫的)
                img = ImageOps.exif_transpose(img)
                # 使用 thumbnail 可以保持圖片的長寬比
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(img)
                self.lbl_image.config(image=photo)
                self.lbl_image.image = photo  # 必須保留引用，否則會被垃圾回收機制清掉

                # 更新狀態列
                filename = os.path.basename(img_path)
                self.lbl_status.config(
                    text=f"進度: {self.current_index + 1} / {len(self.image_list)}  |  目前檔案: {filename}")

            except Exception as e:
                print(f"讀取圖片發生錯誤 {img_path}: {e}")
                filename = os.path.basename(img_path)
                self.lbl_status.config(text=f"⚠️ 無法讀取圖片，自動跳過: {filename}")
                self.root.after(800, self.keep_image)  # 顯示警告 800 毫秒後跳過
        else:
            self.lbl_image.config(image='')
            self.lbl_status.config(text="🎉 所有圖片已整理完畢！")
            messagebox.showinfo("🎉 任務完成", "太棒了！資料夾內的圖片已全數檢視完畢！ ✨")

    def show_overlay(self, text, fg_color):
        self.lbl_overlay.config(text=text, fg=fg_color)
        self.lbl_overlay.place(relx=0.5, x=0, rely=0.45, anchor=tk.CENTER)
        self.root.update_idletasks()

    def hide_overlay(self):
        self.lbl_overlay.place_forget()

    def update_trash_count(self):
        self.lbl_trash_count.config(text=f"🗑️ 待刪除: {len(self.trash_queue)}")

    def on_drag_start(self, event):
        if self.is_processing or not self.image_list or self.current_index >= len(self.image_list):
            return
        self.drag_start_x = event.x_root

    def on_drag_motion(self, event):
        if self.is_processing or not self.image_list or not hasattr(self, 'drag_start_x'):
            return
        dx = event.x_root - self.drag_start_x
        self.lbl_image.place(relx=0.5, x=dx, rely=0.5, anchor=tk.CENTER)

        # 動態顯示提示圖示
        if dx > 50:
            self.lbl_overlay.config(text="✅", fg="green")
            self.lbl_overlay.place(relx=0.5, x=dx, rely=0.45, anchor=tk.CENTER)
        elif dx < -50:
            self.lbl_overlay.config(text="❌", fg="red")
            self.lbl_overlay.place(relx=0.5, x=dx, rely=0.45, anchor=tk.CENTER)
        else:
            self.hide_overlay()

    def on_drag_release(self, event):
        if self.is_processing or not self.image_list or not hasattr(self, 'drag_start_x'):
            return
        dx = event.x_root - self.drag_start_x
        del self.drag_start_x

        self.hide_overlay()

        if dx > 150:
            self.keep_image()
        elif dx < -150:
            self.delete_image()
        else:
            # 沒超過閾值，彈回中央
            self.lbl_image.place(relx=0.5, x=0, rely=0.5, anchor=tk.CENTER)

    def rename_image(self, event=None):
        if self.is_processing or not self.image_list or self.current_index >= len(self.image_list):
            return

        current_path = self.image_list[self.current_index]
        folder_path, old_filename = os.path.split(current_path)
        name, ext = os.path.splitext(old_filename)

        # 彈出對話框讓使用者輸入新檔名
        new_name = simpledialog.askstring(
            "重新命名", f"請輸入新的檔案名稱 (不含副檔名 {ext})：",
            initialvalue=self.last_rename_name or name, parent=self.root)

        if new_name and new_name != name:
            # 拒絕包含路徑分隔符的檔名，防止意外移動到其他目錄
            if os.sep in new_name or ('/' in new_name) or ('\\' in new_name):
                messagebox.showerror("錯誤", "檔名不可包含路徑分隔符 (/ 或 \\)！")
                return
            new_name = new_name.strip()
            if not new_name:
                return
            new_filename = new_name + ext
            new_path = os.path.join(folder_path, new_filename)

            if os.path.exists(new_path):
                messagebox.showerror("錯誤", f"檔名 {new_filename} 已經存在！")
                return

            try:
                os.rename(current_path, new_path)
                self.last_rename_name = new_name
                # 更新內部清單，避免後續操作出錯
                self.image_list[self.current_index] = new_path
                self.show_image()  # 刷新狀態列顯示的新檔名
            except Exception as e:
                messagebox.showerror("錯誤", f"重新命名失敗：{e}")

    def keep_image(self, event=None):
        if self.is_processing:
            return
        if self.image_list and self.current_index < len(self.image_list):
            self.is_processing = True
            self.show_overlay("✅", "green")
            self.root.after(150, self._process_keep)  # 顯示 150 毫秒後切換

    def _process_keep(self):
        img_path = self.image_list[self.current_index]
        self.history.append(('KEEP', self.current_index))
        self.current_index += 1

        # 紀錄進度為剛處理完的這張照片
        self.progress[self.last_folder] = os.path.basename(img_path)

        self.hide_overlay()
        self.update_trash_count()
        self.show_image()
        self.save_config()
        self.is_processing = False

    def delete_image(self, event=None):
        if self.is_processing:
            return
        if self.image_list and self.current_index < len(self.image_list):
            self.is_processing = True
            self.show_overlay("❌", "red")
            self.root.after(150, self._process_delete)

    def _process_delete(self):
        img_path = self.image_list[self.current_index]
        self.history.append(('DELETE', img_path, self.current_index))
        self.trash_queue.append(img_path)
        self.image_list.pop(self.current_index)

        self.progress[self.last_folder] = os.path.basename(img_path)

        self.hide_overlay()
        self.update_trash_count()
        self.show_image()
        self.save_config()
        self.is_processing = False

    def undo_action(self, event=None):
        if self.is_processing or not self.history:
            return  # 沒有可以復原的步驟

        action = self.history.pop()

        if action[0] == 'KEEP':
            self.current_index = action[1]
        elif action[0] == 'DELETE':
            img_path = action[1]
            idx = action[2]
            self.image_list.insert(idx, img_path)
            self.trash_queue.remove(img_path)
            self.current_index = idx

        # 復原時，進度退回上一張
        if self.current_index > 0:
            prev_img_path = self.image_list[self.current_index - 1]
            self.progress[self.last_folder] = os.path.basename(prev_img_path)
        else:
            if self.last_folder in self.progress:
                del self.progress[self.last_folder]

        self.update_trash_count()
        self.show_image()

    def on_closing(self):
        # 程式關閉時，統一將待刪除的檔案移至垃圾桶
        if self.trash_queue:
            msg = f"本次整理共有 {len(self.trash_queue)} 張圖片即將被移至資源回收桶 🗑️\n\n確定要完成並離開嗎？"
            # 彈出確認視窗，如果使用者按否 (No) 則什麼都不做，程式繼續執行
            if messagebox.askyesno("🚪 確認離開", msg):
                self.save_config()
                for img_path in self.trash_queue:
                    try:
                        send2trash(img_path)
                    except Exception as e:
                        print(f"無法刪除檔案 {img_path}: {e}")
                self.root.destroy()
        else:
            self.save_config()
            self.root.destroy()


if __name__ == "__main__":
    print("模組載入成功，正在啟動圖形介面...")
    root = tk.Tk()

    # 設定程式的視窗圖示 (支援 PyInstaller 打包後的路徑讀取)
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(application_path, "fire.png")
    if os.path.exists(icon_path):
        try:
            icon_img = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon_img)
        except Exception as e:
            print(f"載入圖示發生錯誤: {e}")

    app = PicTinderApp(root)
    # 讓視窗一啟動就獲得焦點，確保鍵盤事件能立刻生效
    root.focus_force()
    root.mainloop()
