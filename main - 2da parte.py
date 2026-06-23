"""
Instituto Tecnológico de Costa Rica
Escuela de Ingeniería en Computadores
Curso: Fundamentos de Sistemas Computacionales
Año: 2026
Grupo: 05
Estudiantes: Fabián Salazar Bañes, Lucrecia Soto Aguilar
Título de la asignación. Proyecto 1: Stranger TEC
Requerimientos del sistema: Tkinter, conexión a la rasp
"""

# Importación de bibliotecas
from machine import Pin, PWM # Control de hardware (GPIO, PWM)
import time # Manejo de tiempos
import sys # Interacción con la consola (lectura de comandos desde PC)
import select # Para lectura no bloqueante de stdin (comandos desde PC)

# CONFIGURACIÓN DE COMPONENTES ORIGINALES
btn = Pin(16, Pin.IN, Pin.PULL_UP) # Botón con resistencia pull-up interna
buzzer = PWM(Pin(5)) # Buzzer controlado por PWM para generar tonos
buzzer.duty_u16(0) # Inicialmente apagado

# CONFIGURACIÓN DE FILAS DE LUCES ORIGINALES
fila_sup = Pin(15, Pin.OUT)
fila_mid = Pin(14, Pin.OUT)
fila_inf = Pin(13, Pin.OUT)

# CONFIGURACIÓN DE COMUNICACIÓN CON REGISTROS ORIGINALES
clk_pin = Pin(26, Pin.OUT)
data_pin = Pin(27, Pin.OUT)

# ====================================================================
# NUEVA CONFIGURACIÓN DE PINES ( CIRCUITO DE LA SEGUNDA IMAGEN )
# ====================================================================
switch_hab = Pin(19, Pin.IN, Pin.PULL_UP) # Switch deslizante
data_p2 = Pin(20, Pin.OUT)                # Datos registro 2
clear_p2 = Pin(21, Pin.OUT)               # Clear registro 2
clk_p2 = Pin(22, Pin.OUT)                 # Reloj registro 2
# ====================================================================

# DICCIONARIO DE CÓDIGO MORSE
MORSE_CODE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
    '----.': '9', '.-.-.': '+', '-....-': '-'
}

# DICCIONARIO INVERSO
MORSE_REV = {v: k for k, v in MORSE_CODE.items()}

# MAPA DE LUCES
LIGHT_MAP = {
    'A': (fila_sup, 0), 'B': (fila_mid, 0), 'C': (fila_sup, 1), 'D': (fila_mid, 1),
    'E': (fila_sup, 2), 'F': (fila_mid, 2), 'G': (fila_sup, 3), 'H': (fila_mid, 3),
    'I': (fila_sup, 4), 'J': (fila_mid, 4), 'K': (fila_sup, 5), 'L': (fila_mid, 5),
    'M': (fila_sup, 6), 'N': (fila_mid, 6), 'O': (fila_sup, 7), 'P': (fila_mid, 7),
    'Q': (fila_sup, 8), 'R': (fila_mid, 8), 'S': (fila_sup, 9), 'T': (fila_mid, 9),
    'U': (fila_sup, 10), 'V': (fila_mid, 10), 'W': (fila_sup, 11), 'X': (fila_mid, 11),
    'Y': (fila_sup, 12), 'Z': (fila_mid, 12), '0': (fila_inf, 0), '1': (fila_inf, 1),
    '2': (fila_inf, 2), '3': (fila_inf, 3), '4': (fila_inf, 4), '5': (fila_inf, 5),
    '6': (fila_inf, 6), '7': (fila_inf, 7), '8': (fila_inf, 8), '9': (fila_inf, 9),
    '+': (fila_inf, 11), '-': (fila_inf, 12)
}

# CONFIGURACIÓN DE VELOCIDAD MORSE
velocidad_punto = 0.15

# FUNCIÓN DE PULSO DE RELOJ (ORIGINAL)
def pulso_reloj():
    clk_pin.value(1)
    time.sleep_us(100)
    clk_pin.value(0)
    time.sleep_us(100)

# FUNCIÓN PARA APAGAR TODAS LAS LUCES (ORIGINAL)
def limpiar():
    fila_sup.value(0); fila_mid.value(0); fila_inf.value(0)
    data_pin.value(0)
    for _ in range(16): pulso_reloj()

# FUNCIÓN PARA MOSTRAR UNA LETRA (ORIGINAL)
def mostrar_letra(letra_txt):
    coord = LIGHT_MAP.get(letra_txt.upper())
    if coord:
        limpiar()
        pin_f, col_idx = coord
        pin_f.value(1)
        for i in range(16):
            data_pin.value(1 if (15 - i) == col_idx else 0)
            pulso_reloj()

# FUNCIÓN PARA REPRODUCIR MORSE EN BUZZER (ORIGINAL)
def sonar_solo_buzzer(palabra):
    for letra in palabra:
        codigo = MORSE_REV.get(letra.upper(), "")
        for sym in codigo:
            buzzer.freq(800)
            buzzer.duty_u16(32768)
            time.sleep(velocidad_punto if sym == '.' else velocidad_punto * 3)
            buzzer.duty_u16(0)
            time.sleep(0.1)
        time.sleep(0.4)

# SONIDOS ESPECIALES (ORIGINALES)
def sonido_exito():
    for freq in [1000, 1500]:
        buzzer.freq(freq); buzzer.duty_u16(32768); time.sleep(0.15)
        buzzer.duty_u16(0); time.sleep(0.05)

def sonido_error():
    buzzer.freq(200); buzzer.duty_u16(32768); time.sleep(0.6); buzzer.duty_u16(0)

def sonido_fin_ronda():
    for freq in [1200, 800]:
        buzzer.freq(freq); buzzer.duty_u16(32768); time.sleep(0.3)
    buzzer.duty_u16(0)


# ====================================================================
# NUEVA FUNCIÓN: CONTROL DEL SEGUNDO REGISTRO DE DESPLAZAMIENTO
# ====================================================================
# ====================================================================


# VARIABLES DE CONTROL DEL SISTEMA ORIGINAL
buffer_morse = ""
ultimo_cambio = time.ticks_ms()
estado_anterior = 1
letra_iluminada = False

# ====================================================================
# NUEVAS VARIABLES DE CONTROL PARA EL SWITCH
# ====================================================================
clear_p2.value(1) # Desactivar el reset físico (asumiendo que clear es activo en bajo)
estado_switch_anterior = switch_hab.value() # Guardar el estado inicial del switch
# ====================================================================

# LIMPIEZA INICIAL DE LUCES PRINCIPALES
limpiar()


# --- FUNCIONES ---
# ... (asegúrate de que tus otras funciones estén aquí) ...

def enviar_patron_p2(numero):
    """
    Extrae los 4 bits menos significativos y los posiciona
    exactamente en tus pasos físicos: Q0, Q1, Q4, Q5.
    """
    # Extracción limpia de los 4 bits del ASCII
    b0 = (numero >> 0) & 1  # Bit 0
    b1 = (numero >> 1) & 1  # Bit 1
    b2 = (numero >> 2) & 1  # Bit 2
    b3 = (numero >> 3) & 1  # Bit 3
    
    patron = [0] * 8
    patron[5] = b0  # LED 1 -> Q0
    patron[4] = b1  # LED 2 -> Q1
    patron[1] = b2  # LED 3 -> Q4
    patron[0] = b3  # LED 4 -> Q5
    
    clear_p2.value(1)
    
    # Envío de los 8 bits en reversa a alta velocidad sin desplazamientos extra
    for i in range(7, -1, -1):
        data_p2.value(patron[i])
        clk_p2.value(1)
        time.sleep_us(10)
        clk_p2.value(0)
        time.sleep_us(10)

# --- BUCLE PRINCIPAL ---
# (Tu código ahora debería encontrar la función sin problemas)

# BUCLE PRINCIPAL DEL SISTEMA
while True:
    estado_switch_actual = switch_hab.value()
    if estado_switch_actual != estado_switch_anterior:
        if estado_switch_actual == 0: 
            print("SWITCH:ON")
        else:
            enviar_patron_p2(0)  # <-- SE APAGAN LAS LUCES AL DESACTIVAR EL SWITCH
            print("SWITCH:OFF")
        
        estado_switch_anterior = estado_switch_actua

    # RECEPCIÓN DE COMANDOS DESDE LA PC (ORIGINAL)
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        comando = sys.stdin.readline().strip()

        if comando.startswith("PLAY:"):
            sonar_solo_buzzer(comando[5:])
        elif comando.startswith("SPD:"):
            try:
                velocidad_punto = float(comando[4:])
            except ValueError:
                pass
        elif comando.startswith("LUZ:"):
            letra_actual = comando[4:].upper()
            mostrar_letra(letra_actual)
            letra_iluminada = True
            
            if switch_hab.value() == 0:
                # 1. Obtener el ASCII de la letra
                valor_ascii = ord(letra_actual)
                # 2. Aislar los últimos 4 bits originales con una máscara AND (0x0F -> 1111)
                ultimos_4_orig = valor_ascii & 0x0F
                # 3. Sumar 5 al valor obtenido
                suma_incrementada = ultimos_4_orig + 5
                # 4. Enviar el nuevo valor resultante para posicionar los 4 bits en los LEDs físicos
                enviar_patron_p2(suma_incrementada)
        elif comando == "WIN":
            sonido_exito()
        elif comando == "LOSE":
            sonido_error()
        if comando == "ROUND_END":
            sonido_fin_ronda()
            limpiar()
            enviar_patron_p2(0)  # <-- APAGA LOS LEDS DEL REGISTRO AL FINAL DE LA RONDA
        elif comando == "OFF":
            limpiar()
            enviar_patron_p2(0)

    # LECTURA DEL BOTÓN (ORIGINAL)
    estado_actual = btn.value()
    ahora = time.ticks_ms()
    duracion = time.ticks_diff(ahora, ultimo_cambio)

    # DETECCIÓN DE CAMBIO DE ESTADO (ORIGINAL)
    if estado_actual != estado_anterior:
        if estado_actual == 0: 
            # El botón se presionó: Activa el buzzer (frecuencia 1000Hz, volumen medio)
            buzzer.freq(1000)
            buzzer.duty_u16(32768)
            
            if letra_iluminada:
                limpiar()
                letra_iluminada = False
        elif estado_actual == 1:
            # El botón se soltó: Apaga el buzzer por completo
            buzzer.duty_u16(0)
            
            if duracion > 40:
                buffer_morse += "." if duracion < 250 else "-"
        
        ultimo_cambio = ahora
        estado_anterior = estado_actual
        time.sleep_ms(10)

    # DETECCIÓN DE FIN DE LETRA (ORIGINAL)
    if estado_actual == 1 and buffer_morse != "" and duracion > 600:
        letra_actual = MORSE_CODE.get(buffer_morse, "?").upper()
        
        if letra_actual != "?":
            valor_ascii = ord(letra_actual)
            valor_binario = bin(valor_ascii)[2:]
            print(f"KEY:{letra_actual} | ASCII:{valor_ascii} | BIN:{valor_binario}")
            
            if switch_hab.value() == 0: 
                # Hacer exactamente el mismo cálculo matemático de bits
                ultimos_4_orig = valor_ascii & 0x0F
                suma_incrementada = ultimos_4_orig + 5
                enviar_patron_p2(suma_incrementada)
            
            mostrar_letra(letra_actual)
            letra_iluminada = True
        
        buffer_morse = ""
        ultimo_cambio = ahora
