from websocket import WebSocket
from .detection import FaceDetection


class FaceService:
    """
    Class for face authorization and detection tasks
    """

    def __init__(self):
        self.detection = FaceDetection()

    async def detect_face(self, websocket: WebSocket) -> None:
        """
        Method for detecting face. ONLY FOR TESTING PURPOSES
        :param websocket: WebSocket with client face images
        :return: None
        """
        await self.detection.detect_face(websocket)
        await websocket.close()
        return
