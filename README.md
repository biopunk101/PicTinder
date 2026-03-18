[English Version](README_en.md)

# 🔥 PicTinder

一個使用 Python 與 Tkinter 開發的快速圖片整理工具。透過類似 Tinder 的「左滑刪除、右滑保留」直覺操作，讓你輕鬆清理硬碟中成千上萬的照片！

## 📥 懶人下載 (Mac 專用)

如果您不想安裝 Python，可以直接到 **[Releases](https://github.com/biopunk101/PicTinder/releases)** 頁面下載打包好的 `PicTinder_Mac.zip`。解壓縮後即可直接點擊執行！

## ✨ 功能特色

- **直覺的滑動操作**：支援滑鼠拖曳（左滑 ❌ 刪除、右滑 ✅ 保留）。
- **快捷鍵支援**：可使用鍵盤方向鍵進行超快速的圖片分類。
- **安全刪除**：被標記刪除的圖片不會馬上消失，而是在關閉程式時統一移至「資源回收桶 / 垃圾桶」，避免誤刪。
- **自動儲存進度**：自動記憶上次整理到的圖片位置，下次開啟同一資料夾時可無縫接軌繼續整理。
- **支援復原 (Undo)**：按錯了？沒關係，支援退回上一步。
- **一鍵重新命名**：在瀏覽時隨時按下 `Enter` 鍵即可為圖片重新命名。
- **自動轉正**：讀取 EXIF 資訊，自動將手機拍攝的直立照片轉正。

## 🛠️ 系統需求與安裝

本程式使用 Python 開發，請確保您的系統已安裝 Python 3.x。

### 1. 安裝 Tkinter (視窗介面套件)
- **Windows**: 安裝 Python 時預設已勾選安裝 tcl/tk。
- **Mac**: 若執行時出現找不到 tkinter 的錯誤，請透過 Homebrew 安裝：
  ```bash
  brew install python-tk
  ```
- **Linux (Ubuntu/Debian)**: 
  ```bash
  sudo apt-get install python3-tk
  ```

### 2. 安裝依賴套件
開啟終端機，執行以下指令安裝必備的 Python 套件：

```bash
pip install Pillow send2trash
```
*註：`Pillow` 用於圖片處理與縮放，`send2trash` 用於將檔案安全地移至垃圾桶。*

## 🚀 如何使用

1. 在終端機中執行程式：
   ```bash
   python PicTinder.py
   ```
2. 點擊左上角的 **「選擇資料夾 (Step 0)」**，選取包含圖片的目錄。
3. 畫面中央會顯示圖片，開始進行整理！
4. 整理完畢後，點擊右上角的 **「🚪 完成並離開」**，程式會將標記為刪除的檔案移至垃圾桶。

### 📦 如何自行打包 (For Developers)
如果您想將此程式打包成 Mac 的 `.app` 執行檔，請安裝 `pyinstaller` 並執行以下指令：

```bash
pip install pyinstaller
pyinstaller --name "PicTinder" --windowed --icon=fire.png --add-data "fire.png:." PicTinder.py
```
打包完成後，執行檔會產生在 `dist/PicTinder.app` 目錄下。

### ⌨️ 快捷鍵一覽

| 操作 | 滑鼠 / 鍵盤 | 說明 |
| :--- | :--- | :--- |
| **保留圖片** | `向右拖曳` 或 `→ (右鍵)` | 圖片保留，自動載入下一張 |
| **標記刪除** | `向左拖曳` 或 `← (左鍵)` | 圖片加入待刪除佇列，自動載入下一張 |
| **復原 (Undo)** | `Ctrl + Z` 或 `Cmd + Z` | 退回上一張圖片 |
| **重新命名** | `Enter` | 彈出對話框修改目前圖片檔名 |

## 📂 支援的圖片格式

`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`

## ⚙️ 設定檔

程式會在使用者目錄下產生一個隱藏的設定檔 `~/.pictinder_config.json`，用於記錄最後開啟的資料夾以及各資料夾的整理進度。若想清除所有進度，直接刪除該檔案即可。