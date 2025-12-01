# actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import random
import os
import re

logger = logging.getLogger(__name__)

# ============================================================
#   EXTRAER NÚMEROS DESDE TEXTO
# ============================================================
def parse_number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    try:
        s = str(value).replace(",", ".")
        m = re.search(r"(\d+(\.\d+)?)", s)
        if m:
            return float(m.group(1))
    except:
        pass

    return None


# ============================================================
#   ACTION: CALCULAR IMC
# ============================================================
class ActionCalcularIMC(Action):
    def name(self) -> Text:
        return "action_calcular_imc"

    def run(self, dispatcher, tracker, domain):

        peso_slot = tracker.get_slot("peso")
        altura_slot = tracker.get_slot("altura")
        nombre = tracker.get_slot("nombre") or "amigo"

        logger.info(f"[action_calcular_imc] peso_slot={peso_slot} altura_slot={altura_slot} nombre={nombre}")

        peso = parse_number(peso_slot)
        altura = parse_number(altura_slot)

        if peso is None or altura is None:
            dispatcher.utter_message(
                text="No entendí tu peso o tu altura. Dímelos nuevamente ejemplo: 58 kg, 1.64 m"
            )
            return []

        # Si mandan centímetros
        if altura > 3:
            altura = altura / 100.0

        if peso <= 0 or altura <= 0:
            dispatcher.utter_message(text="Los valores deben ser positivos.")
            return []

        imc = peso / (altura ** 2)
        imc_str = f"{imc:.2f}"

        if imc < 18.5:
            interpretacion = "Tu IMC está bajo. Podrías necesitar comer un poquito más para crecer fuerte."
        elif imc < 25:
            interpretacion = "¡Tu IMC es saludable! Sigue así."
        else:
            interpretacion = "Tu IMC está un poco alto. Te recomiendo moverte más y comer saludable."

        logger.info(f"[action_calcular_imc] imc={imc_str} interpretacion={interpretacion}")

        return [
            SlotSet("peso", peso),
            SlotSet("altura", altura),
            SlotSet("imc", imc_str),
            SlotSet("interpretacion", interpretacion),
        ]


# ============================================================
#   ACTION: RECOMENDAR PLATO
# ============================================================
class ActionRecomendarPlato(Action):
    def name(self) -> Text:
        return "action_recomendar_plato"

    def run(self, dispatcher, tracker, domain):

        tiempo = tracker.get_slot("tiempo_comida")
        nombre = tracker.get_slot("nombre") or "amigo"

        if not tiempo:
            dispatcher.utter_message(text="¿Para qué tiempo de comida deseas la recomendación?")
            return []

        tiempo_norm = str(tiempo).lower().strip()
        tiempo_norm = (
            tiempo_norm.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("mañana", "manana")
        )

        archivos = {
            "desayuno": "desayuno.txt",
            "almuerzo": "almuerzo.txt",
            "cena": "cena.txt",
            "media manana": "media_manana.txt",
            "media tarde": "media_tarde.txt"
        }

        archivo = archivos.get(tiempo_norm)
        if not archivo:
            dispatcher.utter_message(text="Ese tiempo de comida no existe.")
            return []

        actions_dir = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(actions_dir)
        ruta = os.path.join(root, "data", "datasets", archivo)

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                platos = [line.strip() for line in f if line.strip()]
        except:
            dispatcher.utter_message(text="Error cargando el menú.")
            return []

        if not platos:
            dispatcher.utter_message(text="No tengo platos disponibles ahora mismo.")
            return []

        plato = random.choice(platos)

        dispatcher.utter_message(
            text=f"¡{nombre}! Te recomiendo esta combinación para {tiempo}:\n\n🍽️ {plato}\n\n¿Te gusta esta combinación?"
        )

        return [SlotSet("plato_recomendado", plato)]


# ============================================================
#   ACTION: MANEJAR CONFIRMACIÓN O RECHAZO
# ============================================================
class ActionManejarConfirmacionPlato(Action):

    def name(self):
        return "action_manejar_confirmacion_plato"

    def run(self, dispatcher, tracker, domain):

        intent = tracker.latest_message.get("intent", {}).get("name")
        tiempo = tracker.get_slot("tiempo_comida")
        nombre = tracker.get_slot("nombre") or "amigo"
        anterior = tracker.get_slot("plato_recomendado")

        if intent == "afirmar":
            dispatcher.utter_message(
                text=f"¡Perfecto {nombre}! Me alegra que te guste. ¡Disfruta tu comida!"
            )
            return [SlotSet("plato_confirmado", True)]

        elif intent == "negar":

            # Cargar archivo del tiempo de comida
            tiempo_norm = str(tiempo).lower().strip().replace("mañana", "manana")

            archivos = {
                "desayuno": "desayuno.txt",
                "almuerzo": "almuerzo.txt",
                "cena": "cena.txt",
                "media manana": "media_manana.txt",
                "media tarde": "media_tarde.txt"
            }

            archivo = archivos.get(tiempo_norm)
            if not archivo:
                dispatcher.utter_message(text="No sé qué menú usar.")
                return []

            actions_dir = os.path.dirname(os.path.abspath(__file__))
            root = os.path.dirname(actions_dir)
            ruta = os.path.join(root, "data", "datasets", archivo)

            with open(ruta, "r", encoding="utf-8") as f:
                platos = [p.strip() for p in f if p.strip()]

            # eliminar el anterior
            opciones = [p for p in platos if p != anterior]

            if not opciones:
                dispatcher.utter_message(
                    text="Ya te mostré todas las opciones  ¿Quieres repetir la misma o elegir otro tiempo de comida?"
                )
                return []

            nuevo = random.choice(opciones)

            dispatcher.utter_message(
                text=f"Ok {nombre}, te propongo esta otra opción:\n\n {nuevo}\n\n¿Te gusta esta combinación?"
            )

            return [SlotSet("plato_recomendado", nuevo)]

        else:
            dispatcher.utter_message(text="No entendí, ¿te gusta esta combinación? Responde sí o no.")
            return []
