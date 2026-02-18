# Air Canvas - Draw with Hand Gestures ✋🎨

**Air Canvas** is an interactive drawing application that lets you create art using hand gestures tracked through your webcam. No physical tools needed - just your hand and creativity!

![Air Canvas Demo](https://img.shields.io/badge/Python-3.8%2B-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-green)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red)

## 🌟 Features

- **✨ Full-Screen Canvas**: Large, responsive drawing area with dark background for vivid colors
- **🖐️ Hand Gesture Control**: Intuitive gestures for drawing, erasing, and controlling the app
- **🎨 Multiple Colors**: 8 colors including Red, Green, Blue, Yellow, Orange, Purple, White, and Eraser
- **📏 Multiple Brush Sizes**: Small, medium, and large brush sizes
- **↩️ Undo/Redo**: Full undo/redo support for your drawing strokes
- **📹 Live Camera Preview**: Small picture-in-picture window showing hand tracking in real-time
- **📊 Gesture Guide Bar**: Bottom bar showing all available gestures with visual feedback
- **🎯 Smooth Drawing**: Anti-aliased lines with real-time performance (30+ FPS)
- **🖱️ Toolbar**: Color palette and control buttons for backup manual control

## 🎮 Gesture Controls

| Gesture | Action | Description |
|---------|--------|-------------|
| ☝️ **Index Finger Up** | Draw | Draw on canvas following your fingertip |
| ✌️ **Index + Middle Up** | Move/Navigate | Move cursor without drawing (selection mode) |
| ✊ **Fist** | Pause | Stop drawing temporarily |
| 👍 **Thumb Up** | Undo | Undo the last stroke |
| 🤙 **Pinky Up** | Redo | Redo the last undone stroke |
| 🖐️ **Open Palm** | Clear | Clear the entire canvas |
| 🤟 **3 Fingers Up** | Change Color | Cycle through the color palette |

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Webcam/Camera
- Operating System: Windows, macOS, or Linux

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/aadeshshukla/Project-expo-.git
   cd Project-expo-
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 How to Run

### Full Application (with hand tracking)

Simply run the main application file:

```bash
python air_canvas.py
```

### Demo Mode (without camera/hand tracking)

If you don't have a camera or want to test the interface, run the demo:

```bash
python demo.py
```

The demo allows you to:
- Draw with your mouse
- Test all UI features
- Try undo/redo functionality
- Explore the color palette

### Keyboard Shortcuts

- **Q** or **ESC**: Quit the application
- **C**: Clear the canvas
- **U**: Undo last stroke
- **R**: Redo last undone stroke

### Mouse Controls

- **Click on color swatches**: Select a color
- **Click on toolbar buttons**: Use Undo, Redo, or Clear functions

## 📁 Project Structure

```
Project-expo-/
├── README.md                  # This file - project documentation
├── requirements.txt           # Python dependencies
├── air_canvas.py             # Main application entry point
├── hand_tracker.py           # Hand detection and gesture recognition module
├── canvas.py                 # Canvas drawing logic (strokes, undo/redo, colors)
├── ui_elements.py            # UI components (toolbar, camera preview)
├── gesture_guide.py          # Gesture guide bar rendering
├── config.py                 # Configuration constants (colors, sizes, thresholds)
└── utils.py                  # Utility functions
```

## 🛠️ Tech Stack

- **Python 3.8+**: Core programming language
- **OpenCV (cv2)**: Computer vision and image processing
- **MediaPipe**: Google's ML framework for hand landmark detection
- **NumPy**: Numerical computations and array operations

## 🎨 Architecture

The application follows a modular design:

1. **hand_tracker.py**: Uses MediaPipe Hands to detect hand landmarks and recognize gestures
2. **canvas.py**: Manages drawing strokes, colors, brush sizes, and undo/redo functionality
3. **ui_elements.py**: Renders toolbar, color palette, and camera preview window
4. **gesture_guide.py**: Displays the gesture guide bar at the bottom of the screen
5. **config.py**: Centralizes all configuration constants
6. **utils.py**: Provides utility functions for drawing and calculations
7. **air_canvas.py**: Main application that orchestrates all components

## 🔧 Configuration

You can customize the application by editing `config.py`:

- Canvas size and colors
- Camera resolution and preview size
- Hand tracking confidence thresholds
- Brush sizes and drawing parameters
- UI colors and dimensions
- Performance settings (FPS target, frame skipping)

## 🐛 Troubleshooting

### MediaPipe Installation Issues ⚠️

**Problem**: "Hand tracking is not available" or MediaPipe import errors

**Background**: MediaPipe 0.10+ introduced breaking changes that removed the `solutions` API. This affects compatibility with many hand tracking libraries.

**Solutions**:

**Option 1: Install compatible packages (Recommended)**
```bash
pip install opencv-python numpy
pip install mediapipe cvzone
```
Note: This may work but could show warnings due to API changes.

**Option 2: Use Python 3.11 or earlier**
If you're on Python 3.12+, consider using Python 3.11 where older MediaPipe versions might be available.

**Option 3: Run in Demo Mode**
The application will run in demo mode without hand tracking if MediaPipe is not available. You can still:
- Use mouse to click toolbar buttons
- Test the canvas drawing functionality
- Use keyboard shortcuts (C for clear, U for undo, R for redo)

**Check your installation**:
```bash
python -c "import mediapipe; print(mediapipe.__version__)"
python -c "from hand_tracker import HandTracker; t = HandTracker()"
```

### Camera Not Found

**Problem**: "Failed to open camera" error

**Solutions**:
- Check if your webcam is properly connected
- Try changing `CAMERA_INDEX` in `config.py` (try 0, 1, or 2)
- Grant camera permissions to your terminal/Python
- Close other applications using the camera

### Low FPS / Performance Issues

**Problem**: Application is laggy or slow

**Solutions**:
- Reduce camera resolution in `config.py` (e.g., 320x240)
- Close other resource-intensive applications
- Ensure good lighting for better hand detection
- Try reducing `MAX_UNDO_STACK_SIZE` in `config.py`
- Enable `FRAME_SKIP` in `config.py` (set to 1 or 2)

### Hand Not Detected

**Problem**: Hand gestures not recognized

**Solutions**:
- Ensure good, even lighting
- Keep your hand within the camera frame
- Avoid busy backgrounds - use a plain background if possible
- Lower `MEDIAPIPE_DETECTION_CONFIDENCE` in `config.py`
- Make sure your palm is facing the camera
- Try moving your hand closer to or farther from the camera

### Gesture Recognition Issues

**Problem**: Gestures not working as expected

**Solutions**:
- Make gestures clear and distinct
- Hold each gesture for a moment before changing
- Increase `GESTURE_SMOOTHING_FRAMES` for more stable detection
- Adjust `FINGER_TIP_THRESHOLD` in `config.py`
- Ensure fingers are fully extended for "up" gestures

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💻 Author

Created by [@aadeshshukla](https://github.com/aadeshshukla)

## 🙏 Acknowledgments

- **MediaPipe** by Google for excellent hand tracking
- **OpenCV** community for comprehensive computer vision tools
- All contributors and users of this project

## 📸 Screenshots

The application features:
- A large, dark canvas for drawing
- Top toolbar with color palette and control buttons
- Small camera preview window in the top-right corner showing hand tracking
- Bottom gesture guide bar showing available gestures
- Real-time FPS and status information

## 🚨 Known Issues

### MediaPipe Compatibility

- **MediaPipe 0.10+** removed the `solutions` API that many hand tracking projects depend on
- The project includes fallback modes to handle this gracefully
- Hand tracking may not work out-of-the-box depending on your Python version
- The application can run in demo mode using mouse/keyboard controls if hand tracking is unavailable

### Python Version Compatibility

- Best results with Python 3.8-3.11
- Python 3.12+ may have limited MediaPipe version options
- All other features work regardless of Python version

## 💡 Tips for Best Results

- **Lighting**: Ensure good, even lighting for optimal hand detection
- **Background**: Use a plain, contrasting background behind your hand
- **Distance**: Keep your hand 1-2 feet from the camera
- **Gestures**: Make clear, distinct gestures and hold them for a moment
- **Performance**: Close other applications to ensure smooth 30+ FPS

---

**Enjoy creating art with your hands! ✋🎨**
