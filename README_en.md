[中文版](README.md)

# 🔥 PicTinder

A fast photo organization tool developed with Python and Tkinter. Easily clean up thousands of photos on your hard drive using intuitive Tinder-like "swipe left to delete, swipe right to keep" gestures!

## ✨ Features

- **Intuitive Swipe Operations**: Supports mouse dragging (Swipe left ❌ to delete, swipe right ✅ to keep).
- **Keyboard Shortcuts**: Use arrow keys for ultra-fast photo sorting.
- **Safe Deletion**: Photos marked for deletion don't disappear immediately; they are moved to the "Recycle Bin / Trash" when the program closes to prevent accidental deletion.
- **Auto-save Progress**: Automatically remembers your last processed photo position. Seamlessly resume sorting the next time you open the same folder.
- **Undo Support**: Made a mistake? No problem, easily undo the last action.
- **One-click Rename**: Press `Enter` at any time while browsing to rename the current photo.
- **Auto-rotation**: Reads EXIF data to automatically rotate vertical photos taken by mobile phones.

## 📝 Changelog

### v1.1.0 (2026-03-19)
- **Added "Reset Progress" Feature**: A new "🔄 Reset Progress" button allows clearing all saved sorting progress.
- **Enhanced Rename**: The rename function now remembers the last-used name and validates input to prevent invalid filenames.
- **Improved Progress Saving**: The app now asks whether to resume from the last session or start over when opening a folder.
- **Optimized Error Handling**: Now displays a warning and automatically skips corrupted or unreadable images.
- **More Robust Saving**: Progress is now saved after every keep/delete action.
- **UI Update**: The application title now displays the version number.

## 🛠️ System Requirements & Installation

This program is developed in Python. Please make sure you have Python 3.x installed on your system.

### 1. Install Tkinter (GUI Toolkit)
- **Windows**: Installed by default when installing Python (make sure tcl/tk is checked).
- **Mac**: If you encounter an error saying tkinter cannot be found, install it via Homebrew:
  ```bash
  brew install python-tk
  ```
- **Linux (Ubuntu/Debian)**: 
  ```bash
  sudo apt-get install python3-tk
  ```

### 2. Install Dependencies
Open your terminal and run the following command to install the required Python packages:

```bash
pip install Pillow send2trash
```
*Note: `Pillow` is used for image processing and resizing. `send2trash` is used to safely move files to the trash.*

## 🚀 How to Use

1. Run the program in your terminal:
   ```bash
   python PicTinder.py
   ```
2. Click **"選擇資料夾 (Step 0)" (Select Folder)** at the top left to choose a directory containing images.
3. Images will appear in the center of the screen. Start sorting!
4. When finished, click **"🚪 完成並離開" (Finish & Exit)** at the top right. The program will then move the files marked for deletion to the trash.

### ⌨️ Shortcuts

| Action | Mouse / Keyboard | Description |
| :--- | :--- | :--- |
| **Keep Photo** | `Drag Right` or `→ (Right Arrow)` | Keeps the photo and loads the next one |
| **Mark for Deletion** | `Drag Left` or `← (Left Arrow)` | Adds the photo to the deletion queue and loads the next one |
| **Undo** | `Ctrl + Z` or `Cmd + Z` | Returns to the previous photo |
| **Rename** | `Enter` | Opens a dialog box to modify the current photo's filename |

## 📂 Supported Image Formats

`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`

## ⚙️ Configuration File

The program will generate a hidden configuration file `~/.pictinder_config.json` in your user directory to record the last opened folder and the sorting progress of each folder. If you want to clear all progress, simply delete this file.