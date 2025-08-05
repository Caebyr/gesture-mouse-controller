Gesture-Based Mouse Controller

Overview:
This is a Python project that enables mouse control using hand gestures in real-time. It uses a webcam to detect hand positions and perform mouse operations like moving, clicking, and scrolling.

Libraries Required:
- opencv-python
- mediapipe
- numpy
- pynput
- pyautogui

Installation Steps:
1. Install Python 3.11 or lower.
2. Run the following command to install dependencies:
   pip install -r requirements.txt

Dataset:
No static dataset is required. The program uses real-time webcam input.

How to Run:
->USING PYTHON 3.11 OR LOWER: 
1. Make sure your webcam is connected.
2. Run the Python script:
   python your_script_name.py
3. Use gestures:
   - Index + Thumb: Single/Double Click
   - Middle + Thumb: Scroll Down
   - Ring + Thumb: Scroll Up
4. Press 'q' to exit.

->USING PYTHON 3.12 OR HIGHER(in VScode):
1. Make sure your webcam is connected.
2. Install python 3.11 on your computer.
3. Create virtual environment with Python 3.11 (py -3.11 -m venv mediapipe_env)
4. Activate it ,you'll see the environment name in your prompt:
   .\mediapipe_env\Scripts\Activate

   - If you face an error while doing so , follow these steps:
       (i.) Check current execution policy:
            Get-ExecutionPolicy
       (ii.) Set execution policy to allow local scripts
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
       (iii.) Or for just this session
            Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
       (iv.) Now, try activating again.

5. Install your packages:
   pip install mediapipe opencv-python pynput numpy
6. Run the Python script:
   python your_script_name.py
7. Use gestures:
   - Index + Thumb: Single/Double Click
   - Middle + Thumb: Scroll Down
   - Ring + Thumb: Scroll Up
8. Press 'q' to exit.
