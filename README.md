# ✋ Virtual-Air-Writer

> Draw in the air using hand gestures — no touch required.

**Virtual-Air-Writer** is a real-time computer vision application that allows users to draw, write, and interact using hand gestures captured through a webcam. It combines MediaPipe hand tracking with OpenCV rendering to create a smooth and immersive drawing experience.

---

## 🚀 Overview

Turn your hand into a virtual pen and draw directly in the air:

* ✍️ Write and sketch using finger movements
* 🎨 Select colors with gesture-based interaction
* 🧽 Erase using intuitive hand gestures
* ⚡ Experience real-time, low-latency performance

---

## 📸 Demo

![Demo](assets/demo.png)

---

## ✨ Features

### 🖐️ Real-Time Hand Tracking

* Tracks **21 hand landmarks** using MediaPipe
* Accurate and stable detection
* Works in real-time via webcam

---

### 🧠 Gesture-Based Interaction

Built-in gesture recognition system:

* ☝️ **Draw Mode** → Index finger up
* ✊ **Hover Mode** → Fist or two fingers
* 🖐️ **Eraser Mode** → All fingers up
* ❌ **Idle Mode** → No valid gesture

---

### 🎨 Drawing Engine

* Smooth stroke rendering
* Continuous line tracking
* Adjustable brush thickness
* Multiple color options

---

### 🎛️ Interactive UI Overlay

* On-screen color palette
* Gesture-based color selection
* Pointer visualization (pen / eraser)
* Live status display

---

### ⚡ Performance Optimized

* Low latency processing
* Efficient frame handling using OpenCV
* Fullscreen immersive UI

---

## 🎮 Controls

| Gesture / Key           | Action           |
| ----------------------- | ---------------- |
| ☝️ Index Finger         | Draw             |
| ✊ Fist / ✌️ Two Fingers | Hover            |
| 🖐️ All Fingers         | Erase            |
| `C`                     | Clear Canvas     |
| `Q`                     | Quit Application |

---

## 🛠️ Tech Stack

* **Python**
* **OpenCV**
* **MediaPipe**
* **NumPy**

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Xenoncode-dev/Virtual-Air-Writer.git
cd Virtual-Air-Writer
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Run the application

```bash
python main.py
```

---

## ⚙️ Configuration

Customize application behavior by editing:

```
config.py
```

You can adjust:

* Camera resolution
* Brush thickness
* Colors
* Detection sensitivity

---

## 📦 Model Handling

* The required hand tracking model is automatically downloaded on first run
* Manual setup (optional):

```bash
python download_model.py
```

---

## 🎯 Future Improvements

* Multi-hand support
* Save drawings as images
* Gesture customization
* Shape recognition system

---

## 👨‍💻 Author

**Prakhar (xenondevhub)**
Developer | Computer Vision Enthusiast

---

## ⭐ Support

If you like this project:

* ⭐ Star the repo
* 🍴 Fork it
* 📢 Share it

---

> Built with computer vision and creativity 🚀
