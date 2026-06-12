Python 3.14.4 (tags/v3.14.4:23116f9, Apr  7 2026, 14:10:54) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
"""
Instituto Tecnológico de Costa Rica
Escuela de Ingeniería en Computadores
Curso: Fundamentos de Sistemas Computacionales
Año: 2026
Grupo: 05
Estudiantes: Fabián Salazar Bañes, Lucrecia Soto Aguilar
Título de la asignación. Proyecto 2: Extensión Stranger TEC
"""

# Importación de bibliotecas
from machine import Pin, PWM # Control de hardware (GPIO, PWM)
import time # Manejo de tiempos
import sys # Interacción con la consola (lectura de comandos desde PC)
import select # Para lectura no bloqueante de stdin (comandos desde PC)

# ==========================================
# CONFIGURACIÓN PROYECTO 1
# ==========================================
btn = Pin(16, Pin.IN, Pin.PULL_UP) # Botón con resistencia pull-up interna
buzzer = PWM(Pin(5)) # Buzzer controlado por PWM
buzzer.duty_u16(0) 

fila_sup = Pin(15, Pin.OUT) 
fila_mid = Pin(14, Pin.OUT) 
fila_inf = Pin(13, Pin.OUT) 
clk_pin = Pin(26, Pin.OUT) 
data_pin = Pin(27, Pin.OUT) 

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
MORSE_REV = {v: k for k, v in MORSE_CODE.items()}

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

velocidad_punto = 0.15

# ==========================================
# NUEVA CONFIGURACIÓN: PROYECTO 2
# ==========================================
# Switch de habilitación (0 = encendido si se conecta a GND con PULL_UP)
switch_incremento = Pin(17, Pin.IN, Pin.PULL_UP)

# Pines para los 4 LEDs del circuito sumador físicos (devolución del hardware)
# Organizados en una lista desde el LSB (índice 0) hasta el MSB (índice 3)
leds_sumador = [
    Pin(18, Pin.OUT),  # LED 0 (LSB - Bit menos significativo: vale 1)
    Pin(19, Pin.OUT),  # LED 1 (Bit intermedio: vale 2)
    Pin(20, Pin.OUT),  # LED 2 (Bit intermedio: vale 4)
    Pin(21, Pin.OUT)   # LED 3 (MSB - Bit más significativo: vale 8)
]

def actualizar_leds_sumador(resultado_suma):
    """Enciende los LEDs basándose en el número binario calculado"""
    for i in range(4):
        # Extrae el bit en la posición i usando corrimiento y una máscara de 1
        bit = (resultado_suma >> i) & 1
        leds_sumador[i].value(bit)

def apagar_leds_sumador():
    """Apaga las 4 luces del circuito incremento 5"""
    for led in leds_sumador:
        led.value(0)

# ==========================================
# FUNCIONES DE CONTROL DE LUCES MAQUETA
# ==========================================
def pulso_reloj():
    clk_pin.value(1)
    time.sleep_us(100)
    clk_pin.value(0)
    time.sleep_us(100)

def limpiar():
    fila_sup.value(0); fila_mid.value(0); fila_inf.value(0)
    data_pin.value(0)
    for _ in range(16): pulso_reloj()
    apagar_leds_sumador()  # Aseguramos apagar todo en limpiezas globales

def mostrar_letra(letra_txt):
    coord = LIGHT_MAP.get(letra_txt.upper())
    if coord:
        limpiar()
        pin_f, col_idx = coord
        pin_f.value(1)
        for i in range(16):
            data_pin.value(1 if (15 - i) == col_idx else 0)
            pulso_reloj()

# ==========================================
# FUNCIONES DE AUDIO
# ==========================================
def sonar_solo_buzzer(palabra):
    for letra in palabra:
        codigo = MORSE_REV.get(letra.upper(), "")
        for sym in codigo:
            buzzer.freq(2000)
            buzzer.duty_u16(32768)
            time.sleep(velocidad_punto if sym == '.' else velocidad_punto * 3)
            buzzer.duty_u16(0)
            time.sleep(0.1)
        time.sleep(0.4)

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

buffer_morse = ""
ultimo_cambio = time.ticks_ms()
estado_anterior = 1
letra_iluminada = False

limpiar()

# ==========================================
# BUCLE PRINCIPAL
# ==========================================
while True:
    # 1. Monitoreo de comandos entrantes desde la PC
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        comando = sys.stdin.readline().strip()
        if comando.startswith("PLAY:"):
            sonar_solo_buzzer(comando[5:])
        elif comando.startswith("SPD:"):
            velocidad_punto = float(comando[4:])
        elif comando.startswith("LUZ:"):
            mostrar_letra(comando[4:])
            letra_iluminada = True
        elif comando == "WIN":
            sonido_exito()
        elif comando == "LOSE":
            sonido_error()
        elif comando == "ROUND_END":
            sonido_fin_ronda()
            limpiar()
        elif comando == "OFF":
            limpiar()

    # 2. Lectura del botón físico de Morse
    estado_actual = btn.value()
    ahora = time.ticks_ms()
    duracion = time.ticks_diff(ahora, ultimo_cambio)

    if estado_actual != estado_anterior:
        if estado_actual == 0: # Botón presionado
            buzzer.freq(2000)
            buzzer.duty_u16(32768)
            if letra_iluminada:
                limpiar()
                letra_iluminada = False
        elif estado_actual == 1: # Botón liberado
            buzzer.duty_u16(0)
            if duracion > 40:
                buffer_morse += "." if duracion < 250 else "-"
        
        ultimo_cambio = ahora
        estado_anterior = estado_actual
        time.sleep_ms(10)

    # 3. Procesamiento de letra cuando hay silencio (Fin de pulsaciones)
    if estado_actual == 1 and buffer_morse != "" and duracion > 600:
        letra = MORSE_CODE.get(buffer_morse, "?")
        
...         # Enviamos la tecla detectada a la PC de forma normal
...         print(f"KEY:{letra}") 
...         mostrar_letra(letra)
...         letra_iluminada = True
...         
...         # --- LOGICA DEL PROYECTO 2 ---
...         # Verificamos si el switch de incremento está activo (0 significa activado por PULL_UP)
...         if switch_incremento.value() == 0 and letra != "?":
...             # 1. Obtener valor ASCII
...             valor_ascii = ord(letra.upper())
...             
...             # 2. Aislar los 4 bits menos significativos con la máscara de bits
...             cuatro_bits = valor_ascii & 0x0F # Equivale a 'valor_ascii & 15'
...             
...             # 3. Sumar 5 (Operación del circuito combinatorio simulada/asociada)
...             resultado_suma = cuatro_bits + 5
...             
...             # Nota: Dado que 15 + 5 = 20, para evitar desbordar los 4 LEDs, 
...             # limitamos la visualización física al rango de 4 bits (0 a 15) aplicando una máscara.
...             resultado_visual = resultado_suma & 0x0F 
...             
...             # 4. Modificar los LEDs físicos de salida
...             actualizar_leds_sumador(resultado_visual)
...             
...             # 5. Informar a la PC el resultado para la comparación de software y pantalla
...             print(f"SUMA_F_ASCII:{cuatro_bits}")
...             print(f"SUMA_F_OUT:{resultado_visual}")
...         else:
...             apagar_leds_sumador()
...         # -----------------------------
...         
...         buffer_morse = ""
