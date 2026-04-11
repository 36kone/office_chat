from uuid import UUID
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Dict de user_id -> lista de WebSockets ativos (um usuário pode ter mais de uma aba aberta)
        self.active_connections: dict[UUID, list[WebSocket]] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: UUID, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_users(self, message: dict, user_ids: list[UUID]):
        """Envia uma mensagem JSON para uma lista específica de IDs de usuários."""
        for user_id in user_ids:
            if user_id in self.active_connections:
                for connection in self.active_connections[user_id]:
                    try:
                        await connection.send_json(message)
                    except Exception:
                        # Se falhar, a conexão provavelmente caiu, mas o disconnect vai cuidar disso.
                        pass


manager = ConnectionManager()
