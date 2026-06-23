"""
Instituto Tecnológico de Costa Rica
Escuela de Ingeniería en Computadores
Curso: Fundamentos de Sistemas Computacionales
Año: 2026
Grupo: 05
Estudiantes: Fabián Salazar Bañes, Lucrecia Soto Aguilar
Título de la asignación. Proyecto 1: Stranger TEC
Requerimientos del sistema: Tkinter, conexión a la rasp, biblioteca pyserial instalada
"""

# IMPORTACIÓN DE BIBLIOTECAS
import tkinter as tk
from tkinter import messagebox
import random, serial, threading, time
from PIL import Image, ImageTk
import os

# CONFIGURACIÓN DE COLORES
NEGRO = "#000000"
ROJO = "#FF0000"
GRIS = "#505050"
TEXTO = "#FFFFFF"

# CONFIGURACIÓN DE FUENTES
FUENTE_TITULO = ("Times New Roman", 34, "bold")
FUENTE_SUB = ("Fixedsys", 18, "bold")
FUENTE_NORMAL = ("Fixedsys", 14)
FUENTE_INPUT = ("Garamond", 28, "bold")

# CONFIGURACIÓN DE HARDWARE Y CONEXIÓN SERIAL

# Se intenta abrir conexión serial USB con la Raspberry Pi Pico
try:
    
    # COM3 = puerto serial usado en Windows
    # 115200 = velocidad de transmisión
    # timeout = tiempo máximo de espera
    ser = serial.Serial('COM3', 115200, timeout=1) #Ajustar puerto según sistema operativo
    
    # Mensaje de éxito en consola
    print(">>> Conexión USB exitosa.") #Mensaje de éxito en conexión serial

# Captura cualquier error durante la conexión
except Exception as e: #Manejo de error en caso de falla en conexión serial
    
    # Si falla, la variable queda vacía
    ser = None
    
    # Se imprime el error exacto
    print(f">>> Error Serial: {e}") #Mensaje de error detallado en caso de falla en conexión serial

# FUNCIÓN PARA ENVIAR DATOS A LA RASP
def enviar_a_pico(comando):
    
    # Verifica que exista conexión y esté abierta
    if ser and ser.is_open:

        try:
            # Envía el comando seguido de salto de línea
            ser.write(f"{comando}\n".encode())

        except:
            # Error genérico de envío
            print("Error USB") #Mensaje de error en caso de falla al enviar datos a través de la conexión serial

# VARIABLES DEL JUEGO
# Lista de palabras usadas durante las rondas
palabras = ["HOLA", "TECNICO", "RADIO", "MORSE", "CODIGO", "PICO", "LUCES", "ESTUDIANTE", "LOGICA", "RECEPTOR"]

# Mezcla aleatoriamente las palabras
random.shuffle(palabras)

# Variables globales para controlar la velocidad del código Morse, ronda actual, jugador actual y puntajes
velocidad_actual = 0.15; ronda_actual = 1; jugador_actual = 1; puntajes = {1: 0, 2: 0}

# Variables globales para almacenar la palabra objetivo actual, el modo de juego seleccionado, y el tiempo de inicio del turno
palabra_objetivo = ""; modo_juego = ""; tiempo_inicio = 0

# Variable global para almacenar el tiempo utilizado por el jugador 1 en su turno
tiempo_j1 = 0

# Variable global para almacenar el multiplicador de dificultad
multiplicador_dificultad = 1.0

# CONFIGURACIÓN DE LA VENTANA PRINCIPAL

ventana = tk.Tk()
ventana.state("zoomed")
ventana.title("StrangerTEC - Torneo Universitario") #Título de la ventana
ventana.config(bg=NEGRO)

# CARGA DE IMAGEN DE FONDO

# Obtiene la ruta donde está el archivo actual
ruta_actual = os.path.dirname(__file__)

# Construye la ruta completa de la imagen
ruta_imagen = os.path.join(ruta_actual, "fondo.jpg")

# Abre la imagen
imagen = Image.open(ruta_imagen)

# Redimensiona la imagen
imagen = imagen.resize((1920, 1080))

# Convierte la imagen para tkinter
fondo = ImageTk.PhotoImage(imagen)

# Label que contiene el fondo
label_fondo = tk.Label(ventana, image=fondo)

# Coloca el fondo ocupando toda la ventana
label_fondo.place(x=0, y=0, relwidth=1, relheight=1)

# TÍTULO PRINCIPAL
titulo = tk.Label(
    ventana,
    text="STRANGERTEC",
    font=FUENTE_TITULO,
    fg=ROJO,
    bg=NEGRO
)
titulo.pack(pady=(20, 5))

linea = tk.Frame(
    ventana,
    bg="#AA0000",
    height=2,
    width=500
)

linea.place(relx=0.5, y=90, anchor="center")

# SUBTÍTULO
subtitulo = tk.Label(
    ventana,
    text="MORSE COMMUNICATION SYSTEM",
    font=("Tahoma", 12),
    fg=ROJO,
    bg=NEGRO
)
subtitulo.pack()

# LABEL DE INFORMACIÓN
label_info = tk.Label(
    ventana,
    text="SELECCIONE UN MODO",
    font=FUENTE_SUB,
    fg=TEXTO,
    bg=NEGRO
)
label_info.pack(pady=20)

# LABEL PARA MOSTRAR PALABRAS DEL JUEGO
label_palabra = tk.Label(
    ventana,
    text="",
    font=("Georgia", 48, "bold"),
    fg=ROJO,
    bg=NEGRO
)
label_palabra.pack(pady=30)

# CAJA DE TEXTO DONDE EL JUGADOR ESCRIBE
entrada = tk.Entry(
    ventana,
    font=FUENTE_INPUT,
    justify="center",
    bg=GRIS,
    fg=ROJO,
    insertbackground=ROJO,
    relief="flat",
    width=20
)
entrada.pack(pady=20)

# LABEL DE PUNTAJES
label_puntajes = tk.Label(
    ventana,
    text="J1: 0 pts | J2: 0 pts",
    font=("Garamond", 18, "bold"),
    fg=ROJO,
    bg=NEGRO
)
label_puntajes.pack(pady=10)

# CANVAS DEL TEMPORIZADOR
canvas_timer = tk.Canvas(
    ventana,
    width=50,
    height=50,
    bg=NEGRO,
    highlightthickness=0
)
canvas_timer.pack(pady=5)

# LUZ INDICADORA DEL TIEMPO
    # Dibuja un círculo dentro del canvas que cambia de color según el estado
luz_timer = canvas_timer.create_oval(10, 10, 30, 30, fill="#444") 

# LABEL DE ESTADO DEL RELOJ
label_timer_status = tk.Label(
    ventana,
    text="RELOJ DETENIDO",
    font=("Garamond", 11, "bold"),
    fg=ROJO,
    bg=NEGRO
)
label_timer_status.pack()
lf_modulos = tk.LabelFrame(
    ventana,
    text="Incrementador en 5",
    font= "Arial, 20",
    fg=ROJO,
    bg=GRIS,             # Fondo gris
    padx=10,
    pady=10,
    width=300,           # Ancho estático
    height=200           # Alto estático
)
lf_modulos.pack_propagate(False)
lbl_info = tk.Label(
    lf_modulos,
    text="...",
    font=FUENTE_NORMAL,
    fg=TEXTO,
    bg=GRIS,
    justify="left"
)
lbl_info.pack(fill="both", expand=True, padx=5, pady=5)

# Funciones para manejo de configuración del torneo, reinicio manual del juego, inicio de rondas, verificación de progreso del jugador, y mostrar resultados finales al concluir el torneo
def abrir_configuracion():
    vent_config = tk.Toplevel(ventana)
    vent_config.title("Ajustes de Torneo")
    vent_config.geometry("400x450")
    vent_config.grab_set()

    #Configuración de velocidad
    tk.Label(vent_config, text="Velocidad del Código (s):", font=("Fixedsys", 12, "bold")).pack(pady=5)
    lbl_v = tk.Label(vent_config, text=f"{velocidad_actual}s")
    lbl_v.pack()
    
    #Función para cambiar la velocidad del sonido
    def cambiar_v():
        global velocidad_actual
        velocidad_actual = 0.10 if velocidad_actual == 0.15 else (0.25 if velocidad_actual == 0.10 else 0.15)
        lbl_v.config(text=f"{velocidad_actual}s")
        enviar_a_pico(f"SPD:{velocidad_actual}")
    
    tk.Button(vent_config, text="Cambiar Velocidad", command=cambiar_v).pack(pady=5)

    # LÍNEA DIVISORIA
    tk.Frame(vent_config, height=2, bd=1, relief="sunken").pack(fill="x", padx=20, pady=10)

    # CONFIGURACIÓN DE DIFICULTAD
    tk.Label(vent_config, text="Multiplicador de Dificultad:", font=("Fixedsys", 12, "bold")).pack(pady=5)

    # FUNCIÓN PARA ACTUALIZAR DIFICULTAD
    def actualizar_mult(val):
        global multiplicador_dificultad
        multiplicador_dificultad = float(val)

    escala_dif = tk.Scale(vent_config, from_=0.5, to=3.0, resolution=0.1, 
                          orient="horizontal", command=actualizar_mult, length=250)
    escala_dif.set(multiplicador_dificultad) 
    escala_dif.pack(pady=10)
    
    # BOTÓN PARA CERRAR CONFIGURACIÓN
    tk.Button(vent_config, text="Cerrar y Guardar", command=vent_config.destroy, bg="#3498DB", fg="white").pack(pady=20)

# FUNCIÓN PARA REINICIAR EL JUEGO MANUALMENTE
def resetear_juego_manual():
    global ronda_actual, jugador_actual, puntajes, palabras
    ronda_actual = 1
    jugador_actual = 1
    puntajes = {1: 0, 2: 0}
    random.shuffle(palabras) 
    label_puntajes.config(text="J1: 0 pts | J2: 0 pts")
    label_info.config(text="Juego reiniciado. Seleccione un modo.")
    label_palabra.config(text="")
    entrada.delete(0, tk.END)
    entrada.unbind("<KeyRelease>")
    canvas_timer.itemconfig(luz_timer, fill="gray")
    print(">>> Puntajes y rondas reseteados manualmente.")

# FUNCIÓN PARA INICIAR UNA NUEVA RONDA
def iniciar_ronda(nuevo_modo=None):

    # Variables globales que serán modificadas
    global ronda_actual, jugador_actual, palabra_objetivo, tiempo_inicio, modo_juego
    
    # Si se recibe un modo nuevo, se actualiza
    if nuevo_modo: modo_juego = nuevo_modo

    # Si se superan las 10 rondas termina el juego
    if ronda_actual > 10: mostrar_resultados(); return
    
    if jugador_actual == 1:
        palabra_objetivo = palabras[ronda_actual - 1] 
    
    # Actualiza texto informativo
    label_info.config(text=f"RONDA {ronda_actual}/10 | Turno: JUGADOR {jugador_actual}")
    
    # Limpia entrada anterior
    entrada.delete(0, tk.END)
    entrada.focus()
    
    # MODO ESCUCHA Y TRANSMISIÓN
    if modo_juego == "escucha y transmisión":
        label_palabra.config(text="PRESTA ATENCIÓN")

        # Envía la palabra a la pico a través del buzzer
        ventana.after(500, lambda: enviar_a_pico(f"PLAY:{palabra_objetivo}"))
    
    # En modo simple muestra la palabra directamente
    else: 
        label_palabra.config(text=palabra_objetivo)

    # Reinicia temporizador
    tiempo_inicio = 0 

    # Apaga indicador del reloj
    canvas_timer.itemconfig(luz_timer, fill="gray")

    # Actualiza estado visual
    label_timer_status.config(text="Reloj detenido", fg="gray")
    
# FUNCIÓN PARA VERIFICAR EL PROGRESO DEL JUGADOR
def verificar_progreso(event):
    # Variables globales modificables
    global jugador_actual, ronda_actual, tiempo_j1, tiempo_inicio, puntajes
    
    # Obtiene texto ingresado y lo convierte a mayúscula
    intento = entrada.get().upper()
    
    # CONTROL DE LONGITUD DEL TEXTO
    # Si el usuario escribe más letras de las necesarias
    if len(intento) > len(palabra_objetivo):

        # Elimina caracteres sobrantes
        entrada.delete(len(palabra_objetivo), tk.END)

        # Ajusta variable intento
        intento = intento[:len(palabra_objetivo)]

    # ENVÍO DE LETRAS A LA RASP

    # Verifica que exista texto válido
    if intento and (event is None or (hasattr(event, 'char') and (event.char.isalnum() or event.char in "+-"))):
        
        # Envía última letra escrita
        enviar_a_pico(f"LUZ:{intento[-1]}")
    
    # INICIO DEL TEMPORIZADOR

    # Cuando se escribe la primera letra
    if len(intento) == 1 and tiempo_inicio == 0:

        # Guarda tiempo inicial
        tiempo_inicio = time.time()
        
        # Cambia color del reloj a rojo
        canvas_timer.itemconfig(luz_timer, fill="#E74C3C") 
        
        # Cambia estado visual
        label_timer_status.config(text="¡TIEMPO CORRIENDO!", fg="#E74C3C")

    # SI TODAVÍA NO TERMINA LA PALABRA
    if not intento or len(intento) < len(palabra_objetivo):
        return
    
    # CUANDO EL JUGADOR COMPLETA LA PALABRA
    if len(intento) == len(palabra_objetivo):

        # Desactiva escritura temporalmente
        entrada.unbind("<KeyRelease>") 
        
        # CÁLCULO DE TIEMPO Y PUNTAJE

        # Calcula tiempo total usado
        tiempo_final = time.time() - tiempo_inicio

        # Cuenta letras correctas
        aciertos = sum(1 for i in range(len(palabra_objetivo)) if intento[i] == palabra_objetivo[i])
        
        # Bono basado en velocidad
        bono_velocidad = max(10, int(100 - tiempo_final))
        
        # Fórmula del puntaje bas
        puntos_base = int((aciertos / len(palabra_objetivo)) * bono_velocidad * multiplicador_dificultad)
        
        # TURNO DEL JUGADOR 1
        if jugador_actual == 1:
            tiempo_j1 = tiempo_final
            puntajes[1] += puntos_base
            label_info.config(text=f"¡TURNO COMPLETADO J1! Sigue Jugador 2...")
            
            if aciertos > 0: enviar_a_pico("WIN")
            else: enviar_a_pico("LOSE")

            ventana.after(1000, lambda: enviar_a_pico("OFF")) 

            jugador_actual = 2
            ventana.after(1500, lambda: [iniciar_ronda(), entrada.bind("<KeyRelease>", verificar_progreso)])
        
        # TURNO DEL JUGADOR 2
        else:
            multiplicador = 1.0
            if 0 < tiempo_final < tiempo_j1:
                multiplicador = tiempo_j1 / tiempo_final
            
            if multiplicador > 3.0: multiplicador = 3.0
            puntajes[2] += int(puntos_base * multiplicador)

            if aciertos > 0: enviar_a_pico("WIN")
            else: enviar_a_pico("LOSE")

            # FINAL DE RONDA EN MODO SIMPLE
            if modo_juego == "simple":
                ventana.after(500, lambda: enviar_a_pico("ROUND_END"))
            
            # MOSTRAR RESPUESTA EN MODO ESCUCHA
            if modo_juego == "escucha y transmisión":
                label_palabra.config(text=f"ERA: {palabra_objetivo}", fg="#E67E22")

            label_puntajes.config(text=f"J1: {puntajes[1]} pts | J2: {puntajes[2]} pts")
            
            jugador_actual = 1
            ronda_actual += 1
            label_info.config(text=f"¡FIN DE RONDA {ronda_actual-1}!")
            
            ventana.after(2500, lambda: [iniciar_ronda(), 
                                         entrada.bind("<KeyRelease>", verificar_progreso),
                                         label_palabra.config(fg="#2C3E50")])

# FUNCIÓN PARA MOSTRAR RESULTADOS FINALES
def mostrar_resultados():
    final_msg = f"TORNEO FINALIZADO\n\nJ1: {puntajes[1]} pts\nJ2: {puntajes[2]} pts"
    messagebox.showinfo("Resultados", final_msg)
    label_palabra.config(text="FIN DE PARTIDA")
    label_info.config(text="Presione 'Resetear Juego' para una nueva partida")
    entrada.delete(0, tk.END)
    entrada.unbind("<KeyRelease>")

# FUNCIÓN PARA APLICAR ESTILO A BOTONES
def estilo_boton(btn, color):
    btn.config(
        bg=color,
        fg="white",
        activebackground=ROJO,
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Fixedsys", 13, "bold"),
        padx=10,
        pady=10
    )

# FRAME CONTENEDOR DE BOTONES
f_botones = tk.Frame(
    ventana,
    bg=NEGRO
); f_botones.pack(side="bottom", pady=50)

# BOTÓN DE MODO SIMPLE
btn_simple = tk.Button(
    f_botones,
    text="MODO SIMPLE",
    command=lambda: [
        iniciar_ronda("simple"),
        entrada.bind("<KeyRelease>", verificar_progreso)
    ],
    width=20,
    height=2
)

estilo_boton(btn_simple, "#145A32")
btn_simple.grid(row=0, column=0, padx=20)

# BOTÓN DE MODO ESCUCHA Y TRANSMISIÓN
btn_morse = tk.Button(
    f_botones,
    text="ESCUCHA Y TRANSMISIÓN",
    command=lambda: [
        threading.Thread(
            target=lambda: iniciar_ronda("escucha y transmisión")
        ).start(),
        entrada.bind("<KeyRelease>", verificar_progreso)
    ],
    width=25,
    height=2
)

estilo_boton(btn_morse, "#7D6608")
btn_morse.grid(row=0, column=1, padx=20)

# BOTÓN DE CONFIGURACIÓN
btn_config = tk.Button(
    ventana,
    text="⚙ AJUSTES",
    command=abrir_configuracion
)

estilo_boton(btn_config, "#1F618D")
btn_config.place(relx=0.02, rely=0.02)

# BOTÓN DE RESETEO
btn_reset = tk.Button(
    ventana,
    text="🔄 RESET",
    command=resetear_juego_manual
)

estilo_boton(btn_reset, "#922B21")
btn_reset.place(relx=0.12, rely=0.02)

# FUNCIÓN PARA ESCUCHAR DATOS SERIAL
def escuchar_serial():
    while ser and ser.is_open:
        try:
            linea = ser.readline().decode('utf-8').strip()
            
            # ---> AGREGA ESTA LÍNEA PARA MONITOREAR TODO EN LA CONSOLA DE LA PC
            if linea:
                print(f"DEBUG SERIAL -> Llegó desde la Pico: '{linea}'")

            if linea == "SWITCH:ON":
                # lift() fuerza al componente a ponerse en la capa de más arriba (al frente del fondo)
                ventana.after(0, lambda: lf_modulos.lift())
                # place() lo ubica centrado abajo (relx=0.5, rely=0.85)
                ventana.after(0, lambda: lf_modulos.place(relx=0.2, rely=0.4, anchor="center"))
                print(">>> Módulos de control habilitados.")
                continue
            elif linea == "SWITCH:OFF":
                # place_forget() lo oculta de forma segura
                ventana.after(0, lambda: lf_modulos.place_forget())
                continue
                
            if linea.startswith("KEY:"):
                if modo_juego == "escucha y transmisión" and jugador_actual == 1:
                    continue

                letra = linea.split(":")[1].split("|")[0].strip()
                ventana.after(0, lambda l=letra: insertar_letra(l))

                # ====================================================================
                # LOGICA DE PROCESAMIENTO BINARIO PARA EL LABELFRAME
                # ====================================================================
                try:
                    val_ascii = ord(letra)
                    val_bin = bin(val_ascii)[2:] # Quita el '0b'
                    
                    # Últimos 4 dígitos del binario original
                    ultimos_4_orig = val_bin[-4:] if len(val_bin) >= 4 else val_bin.zfill(4)
                    
                    # Convertir los últimos 4 dígitos a entero, sumar 5 y pasar de nuevo a binario
                    entero_ultimos_4 = int(ultimos_4_orig, 2)
                    suma_5 = entero_ultimos_4 + 5
                    bin_suma_5 = bin(suma_5)[2:]
                    
                    # Últimos 4 dígitos del nuevo número sumado
                    ultimos_4_nuev = bin_suma_5[-4:] if len(bin_suma_5) >= 4 else bin_suma_5.zfill(4)
                    
                    # Estructurar el bloque de texto
                    texto_completo = (
                        f"Letra: {letra}\n"
                        f"ASCII: {val_ascii}\n"
                        f"Binario: {val_bin}\n"
                        f"Ultimos 4 bits: {ultimos_4_orig}\n"
                        f"incremento de 5: {bin_suma_5}\n"
                        f"Últimos 4 bits: {ultimos_4_nuev}"
                    )
                    
                    # Actualizar el componente visual de forma segura
                    ventana.after(0, lambda t=texto_completo: lbl_info.config(text=t))
                except Exception as e:
                    print(f"Error procesando datos de la letra: {e}")

        except:
            break

# FUNCIÓN PARA INSERTAR LETRAS EN EL ENTRY
def insertar_letra(l):
    if l:
        entrada.insert(tk.END, l)
        verificar_progreso(None)

# HILO DE LECTURA SERIAL
hilo_lectura = threading.Thread(target=escuchar_serial, daemon=True)
hilo_lectura.start()

# EJECUCIÓN PRINCIPAL DEL PROGRAMA
ventana.mainloop()