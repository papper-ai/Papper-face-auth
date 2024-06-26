from ultralytics import YOLO
from asyncio.locks import Lock
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import cv2
from src.config import settings
import numpy as np


class CircleBorders(BaseModel):
    _r_min: int = int(275 / 1.5)
    _r_max: int = 275
    _center_x: int = 320
    _center_y: int = 320

    left_x_max: int = _center_x - _r_max
    left_x_min: int = _center_x - _r_min
    right_x_max: int = _center_x + _r_max
    right_x_min: int = _center_x + _r_min

    top_y_max: int = _center_y - _r_max
    top_y_min: int = _center_y - _r_min
    bottom_y_max: int = _center_y + _r_max
    bottom_y_min: int = _center_y + _r_min


class FaceDetection:
    """
    Class for face detection and cropping face from original frame
    """

    model = YOLO(settings.yolo_weights_path, verbose=True)
    model_lock = Lock
    borders = CircleBorders()

    def __init__(self):
        self.success_counter = 0

    async def detect_face(self, websocket: WebSocket) -> np.ndarray | None:
        """
        Method for detecting face and saving
        :param websocket: WebSocket with client images
        :return: ndarray with face or None
        """

        while True:
            try:
                # After DEBUG period delete it
                predicted_center_x, predicted_center_y, predicted_radius = 0, 0, 0

                action = ""
                text = ""
                x1, y1, x2, y2 = 0, 0, 0, 0

                bytes_img = await websocket.receive_bytes()
                arr_img = np.frombuffer(bytes_img, dtype=np.uint8)
                img = cv2.imdecode(arr_img, cv2.IMREAD_COLOR)
                frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                async with self.model_lock:
                    raw_results = self.model.predict(source=frame)[0]

                results = raw_results.boxes.data.cpu().numpy()

                if len(results) == 1:
                    x1, y1, x2, y2, conf, cls = results[0]

                    bbox_location_valid = await self.check_borders(x1, y1, x2, y2)
                    predicted_center_x, predicted_center_y, w, h = (
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        x2 - x1,
                        y2 - y1,
                    )
                    predicted_radius = w / 2 if w > h else h / 2

                    if bbox_location_valid:
                        self.success_counter += 1
                        action = "correct position"
                    else:
                        self.success_counter = 0
                        action = "incorrect position"
                else:
                    if len(results) == 0:
                        self.success_counter = 0
                        action = "no face"
                    else:
                        self.success_counter = 0
                        action = "multiple faces"

                if self.success_counter == 3:
                    text = "success"

                await websocket.send_json(
                    {
                        "action": action,
                        "text": text,
                        "radius": predicted_radius,
                        "center_point": (predicted_center_x, predicted_center_y),
                    }
                )

                if text == "success":
                    face_frame = frame[y1:y2, x1:x2]
                    return face_frame
            except WebSocketDisconnect:
                break
        return

    async def check_borders(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Method for checking predicted circle borders
        :param x1: Left upper corner x coordinate
        :param y1: Left upper corner y coordinate
        :param x2: Right lower corner x coordinate
        :param y2: Right lower corner y coordinate
        :return: Validation results
        """

        predicted_center_x, predicted_center_y, w, h = (
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            x2 - x1,
            y2 - y1,
        )
        predicted_radius = w / 2 if w > h else h / 2
        predicted_left_x, predicted_right_x = (
            predicted_center_x - predicted_radius,
            predicted_center_x + predicted_radius,
        )
        predicted_top_y, predicted_bottom_y = (
            predicted_center_y - predicted_radius,
            predicted_center_y + predicted_radius,
        )

        x_ok = (
            True
            if self.borders.left_x_max <= predicted_left_x <= self.borders.left_x_min
            and self.borders.right_x_max
            >= predicted_right_x
            >= self.borders.right_x_min
            else False
        )
        y_ok = (
            True
            if self.borders.top_y_max <= predicted_top_y <= self.borders.top_y_min
            and self.borders.bottom_y_max
            >= predicted_bottom_y
            >= self.borders.bottom_y_min
            else False
        )

        if x_ok and y_ok:
            return True
        else:
            return False
