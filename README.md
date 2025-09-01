<p align="center">
  <!-- Example using free icons (you can replace with your own logo in /assets/logo.png) -->
  <img src="https://img.icons8.com/fluency/96/visible.png" width="80"/>
  <img src="https://img.icons8.com/fluency/96/hand.png" width="80"/>
  <img src="https://img.icons8.com/fluency/96/happy.png" width="80"/>
</p>

<h1 align="center">Eye-Hand-Emotion Tracker 👁️✋😊</h1>

---

- `main.py` → the full tracking logic (eyes, hands, emotions).  
- `requirements.txt` → dependencies for installation.  

---

## ✨ Features  

- **Eye Control**  
  - Close right eye → Open Google Chrome  
  - Close left eye → Open File Explorer  
  - Close both eyes → Restart PC (optional, configurable)  

- **Hand Gestures (MediaPipe Hands)**  
  - 👍 Thumbs Up  
  - 👎 Thumbs Down  
  - ✋ Open Palm  
  - ✌️ Peace (V-sign)  
  - ✊ Fist  
  - 👌 OK Sign  

- **Emotion Detection (FER)**  
  - Detects real-time emotions: Happy, Sad, Angry, Neutral, etc.  
  - Displays predictions with confidence score  

---

## 🛠️ Installation  

1. Clone the repo:  
   ```bash
   git clone https://github.com/Ahmad-GoCode/eye-hand-emotion-tracker.git
   cd eye-hand-emotion-tracker

pip install -r requirements.txt

python main.py
