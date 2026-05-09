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

#Importación de bibliotecas
from machine import Pin, PWM #Control de hardware (GPIO, PWM)
import time #Manejo de tiempos
import sys #Interacción con la consola (lectura de comandos desde PC)
import select #Para lectura no bloqueante de stdin (comandos desde PC)

btn = Pin(16, Pin.IN, Pin.PULL_UP) #Botón con resistencia pull-up interna
buzzer = PWM(Pin(5)) #Buzzer conectado al pin 5, controlado por PWM para generar tonos
buzzer.duty_u16(0) #Inicialmente apagado (duty cycle 0)

# CONFIGURACIÓN DE FILAS DE LUCES
fila_sup = Pin(15, Pin.OUT) #fila superior de luces
fila_mid = Pin(14, Pin.OUT) #fila media de luces
fila_inf = Pin(13, Pin.OUT) #fila inferior de luces

# CONFIGURACIÓN DE COMUNICACIÓN CON REGISTROS
clk_pin = Pin(26, Pin.OUT) #pin de reloj para comunicación SPI
data_pin = Pin(27, Pin.OUT) #pin de datos para comunicación SPI

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
MORSE_REV = {v: k for k, v in MORSE_CODE.items()} #Diccionario inverso para traducción de caracteres a código Morse

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

# FUNCIÓN DE PULSO DE RELOJ
def pulso_reloj():
    clk_pin.value(1)
    time.sleep_us(100)
    clk_pin.value(0)
    time.sleep_us(100)

# FUNCIÓN PARA APAGAR TODAS LAS LUCES
def limpiar():
    fila_sup.value(0); fila_mid.value(0); fila_inf.value(0)
    data_pin.value(0)
    for _ in range(16): pulso_reloj()

# FUNCIÓN PARA MOSTRAR UNA LETRA
def mostrar_letra(letra_txt):
    coord = LIGHT_MAP.get(letra_txt.upper())
    if coord:
        limpiar()
        pin_f, col_idx = coord
        pin_f.value(1)
        for i in range(16):
            data_pin.value(1 if (15 - i) == col_idx else 0)
            pulso_reloj()

# FUNCIÓN PARA REPRODUCIR MORSE EN BUZZER
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

# SONIDO DE ÉXITO
def sonido_exito():
    for freq in [1000, 1500]:
        buzzer.freq(freq); buzzer.duty_u16(32768); time.sleep(0.15)
        buzzer.duty_u16(0); time.sleep(0.05)

# SONIDO DE ERROR
def sonido_error():
    buzzer.freq(200); buzzer.duty_u16(32768); time.sleep(0.6); buzzer.duty_u16(0)

# SONIDO DE FIN DE RONDA
def sonido_fin_ronda():
    for freq in [1200, 800]:
        buzzer.freq(freq); buzzer.duty_u16(32768); time.sleep(0.3)
    buzzer.duty_u16(0)

# VARIABLES DE CONTROL DEL SISTEMA
buffer_morse = ""
ultimo_cambio = time.ticks_ms()
estado_anterior = 1
letra_iluminada = False

# LIMPIEZA INICIAL
limpiar()

# BUCLE PRINCIPAL DEL SISTEMA
while True:

    # RECEPCIÓN DE COMANDOS DESDE LA PC
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        comando = sys.stdin.readline().strip()

        # REPRODUCCIÓN DE MORSE
        if comando.startswith("PLAY:"):
            sonar_solo_buzzer(comando[5:])

        # CAMBIO DE VELOCIDAD
        elif comando.startswith("SPD:"):
            velocidad_punto = float(comando[4:])

        # MOSTRAR LETRAS
        elif comando.startswith("LUZ:"):
            mostrar_letra(comando[4:])
            letra_iluminada = True

        # SONIDOS ESPECIALES
        elif comando == "WIN":
            sonido_exito()
        elif comando == "LOSE":
            sonido_error()
        elif comando == "ROUND_END":
            sonido_fin_ronda()
            limpiar()
        elif comando == "OFF":
            limpiar()

    # LECTURA DEL BOTÓN
    estado_actual = btn.value()
    ahora = time.ticks_ms()
    duracion = time.ticks_diff(ahora, ultimo_cambio)

    # DETECCIÓN DE CAMBIO DE ESTADO
    if estado_actual != estado_anterior:

        # CUANDO SE PRESIONA EL BOTÓN
        if estado_actual == 0: 
            if letra_iluminada:
                limpiar()
                letra_iluminada = False
        
        # CUANDO SE SUELTA EL BOTÓN
        elif estado_actual == 1:
            if duracion > 40:
                buffer_morse += "." if duracion < 250 else "-"
        
        ultimo_cambio = ahora
        estado_anterior = estado_actual
        time.sleep_ms(10)

    # DETECCIÓN DE FIN DE LETRA
    if estado_actual == 1 and buffer_morse != "" and duracion > 600:
        letra = MORSE_CODE.get(buffer_morse, "?")
        print(f"KEY:{letra}") 
        mostrar_letra(letra)
        letra_iluminada = True
        buffer_morse = ""
        ultimo_cambio = ahora