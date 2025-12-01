from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QTextCursor, QIcon
import requests
import sys

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

def enviar_mensaje_a_rasa(mensaje, usuario="usuario1"):
    payload = {"sender": usuario, "message": mensaje}
    try:
        response = requests.post(RASA_URL, json=payload, timeout=5)
        response.raise_for_status()
        respuestas = response.json()
        textos = [r["text"] for r in respuestas if "text" in r]
        return "\n".join(textos)
    except requests.exceptions.RequestException as e:
        return f"Error al conectarse con Rasa: {e}"

class ChatGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VitaKids - Chat Infantil Saludable")
        self.setGeometry(100, 100, 600, 800)

        # ======== FONDO PRINCIPAL =========
        self.setStyleSheet("background-color: #fca311;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # ========= TÍTULO =========
        header = QLabel("VitaKids")
        header.setFont(QFont("Arial Rounded MT Bold", 32))   # MÁS GRANDE
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: black;")
        main_layout.addWidget(header)

        # ========= FRUTAS =========
        frutas_layout = QHBoxLayout()
        frutas_layout.setSpacing(40)
        frutas_layout.setAlignment(Qt.AlignCenter)

        frutas = ["Imagenes/fruta1.png", "Imagenes/fruta2.png", "Imagenes/fruta3.png"]

        for fruta in frutas:
            img = QLabel()
            pix = QPixmap(fruta).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img.setPixmap(pix)
            frutas_layout.addWidget(img)

        main_layout.addLayout(frutas_layout)

        # ========= IMAGEN CENTRAL (MASCOTA) =========
        self.mascota = QLabel()
        pixmap_mascota = QPixmap("Imagenes/mascota_vitakids.png")
        pixmap_mascota = pixmap_mascota.scaled(210, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # MÁS GRANDE

        self.mascota.setPixmap(pixmap_mascota)
        self.mascota.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.mascota)

        # ========= AREA DEL CHAT =========
        self.chat_frame = QFrame()
        self.chat_frame.setStyleSheet("""
            background-color: #FFF4CC;   /* Amarillo pálido bonito */
            border-radius: 15px; 
        """)
        chat_layout = QVBoxLayout(self.chat_frame)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            background-color: #FFF4CC;
            color: black;
            border: none;
            padding: 10px;
        """)
        self.chat_area.setFont(QFont("Arial", 12))

        chat_layout.addWidget(self.chat_area)
        main_layout.addWidget(self.chat_frame, stretch=1)

        # ========= INPUT ==========
        input_container = QFrame()
        input_container.setStyleSheet("""
            background-color: white;
            border-radius: 20px;
            padding: 5px;
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.input_msg = QLineEdit()
        self.input_msg.setPlaceholderText("Escribe tu mensaje...")
        self.input_msg.setStyleSheet("color: black;")   # PLACEHOLDER Y TEXTO NEGRO
        self.input_msg.setFont(QFont("Arial", 12))
        self.input_msg.returnPressed.connect(self.enviar_mensaje)

        # ========= BOTÓN ENVIAR ICONO ==========
        self.btn_enviar = QPushButton()
        self.btn_enviar.setIcon(QIcon("Imagenes/icono_enviar.png"))  # Usa un icono claro
        self.btn_enviar.setStyleSheet("border: none;")
        self.btn_enviar.setFixedSize(45, 45)
        self.btn_enviar.clicked.connect(self.enviar_mensaje)

        input_layout.addWidget(self.input_msg)
        input_layout.addWidget(self.btn_enviar)

        main_layout.addWidget(input_container)

        self.setLayout(main_layout)

        # Mensaje inicial
        self.agregar_mensaje("Bot", "¡Hola! Estoy listo para ayudarte.")

    # ========= BURBUJAS DEL CHAT ================
    def agregar_mensaje(self, remitente, mensaje):
        if remitente == "Bot":
            estilo = "background-color:#FFE9A3;"  # Amarillo más fuerte, suave
        else:
            estilo = "background-color:#FFD3B4; text-align:right;"  # Salmón suave

        self.chat_area.append(
            f"<p style='{estilo} padding:8px; border-radius:12px;'>"
            f"<b>{remitente}:</b> {mensaje}</p>"
        )
        self.chat_area.moveCursor(QTextCursor.End)

    def enviar_mensaje(self):
        mensaje_usuario = self.input_msg.text().strip()
        if not mensaje_usuario:
            return

        self.agregar_mensaje("Tú", mensaje_usuario)
        self.input_msg.clear()

        respuesta = enviar_mensaje_a_rasa(mensaje_usuario)
        self.agregar_mensaje("Bot", respuesta)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ChatGUI()
    gui.show()
    sys.exit(app.exec())
