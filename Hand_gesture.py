import cv2
import numpy as np
import mediapipe as mp
from pynput.mouse import Button, Controller as MouseController
import time

class GestureMouseController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hand_detector = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.8
        )
        self.drawing_utils = mp.solutions.drawing_utils
        
        self.mouse_control = MouseController()
        
        self.display_width, self.display_height = self._get_screen_dimensions()
        
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.previous_cursor_x, self.previous_cursor_y = 0, 0
        self.smoothing_factor = 3
        
        self.was_pinching_before = False
        self.last_click_timestamp = 0
        self.double_click_time_window = 0.4
        
        self.is_scrolling_downward = False
        self.is_scrolling_upward = False
        self.scroll_timing = 0
        
        self.motion_threshold = 5
        self.last_stable_position = (0, 0)
        self.stability_start_time = 0
        self.required_stability_duration = 0.1
        
        self.INDEX_TIP = 8
        self.THUMB_TIP = 4
        self.MIDDLE_TIP = 12
        self.RING_TIP = 16
        
        self.PINCH_DISTANCE_THRESHOLD = 35
        
        print(f"System Display Resolution: {self.display_width}x{self.display_height}")
        print("Gesture Mouse Controller Initialized")
        print("Controls:")
        print("- Index + Thumb: Single/Double Click")
        print("- Middle + Thumb: Scroll Down")
        print("- Ring + Thumb: Scroll Up")
        print("- Press 'q' to quit")
    
    def _get_screen_dimensions(self):
        try:
            import tkinter as tk
            root = tk.Tk()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return width, height
        except:
            return 1920, 1080
    
    def _calculate_distance(self, point1, point2):
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def _is_cursor_stable(self, current_position):
        distance_moved = self._calculate_distance(current_position, self.last_stable_position)
        current_time = time.time()
        
        if distance_moved < self.motion_threshold:
            if self.stability_start_time == 0:
                self.stability_start_time = current_time
            cursor_is_stable = (current_time - self.stability_start_time) > self.required_stability_duration
        else:
            self.stability_start_time = 0
            cursor_is_stable = False
        
        self.last_stable_position = current_position
        return cursor_is_stable
    
    def _smooth_cursor_movement(self, raw_x, raw_y):
        smoothed_x = self.previous_cursor_x + (raw_x - self.previous_cursor_x) / self.smoothing_factor
        smoothed_y = self.previous_cursor_y + (raw_y - self.previous_cursor_y) / self.smoothing_factor
        
        self.previous_cursor_x, self.previous_cursor_y = smoothed_x, smoothed_y
        return smoothed_x, smoothed_y
    
    def _handle_click_gestures(self, fingertip_distances, cursor_position, is_stable):
        current_time = time.time()
        index_thumb_distance = fingertip_distances['index_thumb']
        
        is_currently_pinching = index_thumb_distance < self.PINCH_DISTANCE_THRESHOLD
        
        if is_currently_pinching and not self.was_pinching_before and is_stable:
            time_since_last_click = current_time - self.last_click_timestamp
            
            if time_since_last_click < self.double_click_time_window:
                self.mouse_control.click(Button.left, 2)
                print(f"Double click executed at ({cursor_position[0]:.0f}, {cursor_position[1]:.0f})")
                self.last_click_timestamp = 0
            else:
                self.mouse_control.click(Button.left, 1)
                self.last_click_timestamp = current_time
                print(f"Single click executed at ({cursor_position[0]:.0f}, {cursor_position[1]:.0f})")
        
        self.was_pinching_before = is_currently_pinching
        return is_currently_pinching
    
    def _handle_scroll_gestures(self, fingertip_distances):
        current_time = time.time()
        middle_thumb_distance = fingertip_distances['middle_thumb']
        ring_thumb_distance = fingertip_distances['ring_thumb']
        
        if middle_thumb_distance < self.PINCH_DISTANCE_THRESHOLD:
            if not self.is_scrolling_downward:
                self.is_scrolling_downward = True
                self.scroll_timing = current_time
            elif current_time - self.scroll_timing > 0.1:
                self.mouse_control.scroll(0, -3)
                self.scroll_timing = current_time
        else:
            self.is_scrolling_downward = False
        
        if ring_thumb_distance < self.PINCH_DISTANCE_THRESHOLD:
            if not self.is_scrolling_upward:
                self.is_scrolling_upward = True
                self.scroll_timing = current_time
            elif current_time - self.scroll_timing > 0.1:
                self.mouse_control.scroll(0, 3)
                self.scroll_timing = current_time
        else:
            self.is_scrolling_upward = False
        
        return middle_thumb_distance < self.PINCH_DISTANCE_THRESHOLD, ring_thumb_distance < self.PINCH_DISTANCE_THRESHOLD
    
    def _draw_visual_feedback(self, frame, hand_landmarks, fingertip_distances, cursor_stable, is_clicking, is_scrolling_down, is_scrolling_up):
        frame_height, frame_width = frame.shape[:2]
        
        landmark_pixels = []
        for landmark in hand_landmarks.landmark:
            x_pixel = int(landmark.x * frame_width)
            y_pixel = int(landmark.y * frame_height)
            landmark_pixels.append((x_pixel, y_pixel))
        
        self.drawing_utils.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        if is_clicking:
            cv2.circle(frame, landmark_pixels[self.INDEX_TIP], 15, (0, 255, 0), cv2.FILLED)
            if time.time() - self.last_click_timestamp < self.double_click_time_window and self.last_click_timestamp > 0:
                cv2.putText(frame, "Double Click Ready", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if is_scrolling_down:
            cv2.circle(frame, landmark_pixels[self.MIDDLE_TIP], 15, (255, 0, 0), cv2.FILLED)
            cv2.putText(frame, "Scrolling Down", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        if is_scrolling_up:
            cv2.circle(frame, landmark_pixels[self.RING_TIP], 15, (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, "Scrolling Up", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        stability_color = (0, 255, 0) if cursor_stable else (0, 0, 255)
        stability_text = "Cursor Stable" if cursor_stable else "Cursor Moving"
        cv2.putText(frame, stability_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, stability_color, 2)
        
        instructions = [
            "Index+Thumb: Click/Double-click",
            "Middle+Thumb: Scroll Down", 
            "Ring+Thumb: Scroll Up",
            "Press 'q' to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            y_position = frame_height - 80 + (i * 20)
            cv2.putText(frame, instruction, (10, y_position), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def run(self):
        try:
            while True:
                success, camera_frame = self.camera.read()
                if not success:
                    print("Failed to read from camera")
                    break
                
                camera_frame = cv2.flip(camera_frame, 1)
                frame_height, frame_width = camera_frame.shape[:2]
                
                rgb_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
                detection_results = self.hand_detector.process(rgb_frame)
                
                if detection_results.multi_hand_landmarks:
                    primary_hand = detection_results.multi_hand_landmarks[0]
                    
                    hand_points = []
                    for landmark in primary_hand.landmark:
                        pixel_x = int(landmark.x * frame_width)
                        pixel_y = int(landmark.y * frame_height)
                        hand_points.append((pixel_x, pixel_y))
                    
                    index_tip = hand_points[self.INDEX_TIP]
                    thumb_tip = hand_points[self.THUMB_TIP]
                    middle_tip = hand_points[self.MIDDLE_TIP]
                    ring_tip = hand_points[self.RING_TIP]
                    
                    screen_x = np.interp(index_tip[0], (0, frame_width), (0, self.display_width))
                    screen_y = np.interp(index_tip[1], (0, frame_height), (0, self.display_height))
                    
                    cursor_x, cursor_y = self._smooth_cursor_movement(screen_x, screen_y)
                    
                    self.mouse_control.position = (cursor_x, cursor_y)
                    
                    current_cursor_position = (cursor_x, cursor_y)
                    cursor_is_stable = self._is_cursor_stable(current_cursor_position)
                    
                    distances = {
                        'index_thumb': self._calculate_distance(index_tip, thumb_tip),
                        'middle_thumb': self._calculate_distance(middle_tip, thumb_tip),
                        'ring_thumb': self._calculate_distance(ring_tip, thumb_tip)
                    }
                    
                    is_clicking = self._handle_click_gestures(distances, current_cursor_position, cursor_is_stable)
                    is_scrolling_down, is_scrolling_up = self._handle_scroll_gestures(distances)
                    
                    self._draw_visual_feedback(camera_frame, primary_hand, distances, cursor_is_stable, 
                                             is_clicking, is_scrolling_down, is_scrolling_up)
                
                else:
                    self.was_pinching_before = False
                    self.is_scrolling_downward = False
                    self.is_scrolling_upward = False
                    self.stability_start_time = 0
                
                cv2.imshow("Gesture Mouse Controller", camera_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nShutting down gesture mouse controller...")
        
        finally:
            self.camera.release()
            cv2.destroyAllWindows()
            print("Gesture mouse controller stopped.")

if __name__ == "__main__":
    controller = GestureMouseController()
    controller.run()