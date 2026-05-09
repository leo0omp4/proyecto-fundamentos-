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

#Importación de bibliotecas
import tkinter as tk
from tkinter import messagebox
import random, serial, threading, time
from PIL import Image, ImageTk

NEGRO = "#000000"
ROJO = "#FF0000"
GRIS = "#505050"
TEXTO = "#FFFFFF"

FUENTE_TITULO = ("Times New Roman", 34, "bold")
FUENTE_SUB = ("Fixedsys", 18, "bold")
FUENTE_NORMAL = ("Fixedsys", 14)
FUENTE_INPUT = ("Garamond", 28, "bold")

#Configuración de hardware, intento de conexión serial con la Rasp para comunicación USB 
try:
    ser = serial.Serial('COM3', 115200, timeout=1) #Ajustar puerto según sistema operativo
    print(">>> Conexión USB exitosa.") #Mensaje de éxito en conexión serial
except Exception as e: #Manejo de error en caso de falla en conexión serial
    ser = None #Variable ser se establece como None para indicar que no hay conexión serial
    print(f">>> Error Serial: {e}") #Mensaje de error detallado en caso de falla en conexión serial

#Función para enviar comandos a la Rasp a través de la USB
def enviar_a_pico(comando):
    if ser and ser.is_open: #Verificación de que la conexión serial está abierta antes de intentar enviar datos
        try:
            ser.write(f"{comando}\n".encode()) #Envío del comando a través de la conexión serial
        except:
            print("Error USB") #Mensaje de error en caso de falla al enviar datos a través de la conexión serial

#Lógica de juego
palabras = ["HOLA", "TECNICO", "RADIO", "MORSE", "CODIGO", "PICO", "LUCES", "ESTUDIANTE", "LOGICA", "RECEPTOR"] #Lista de palabras definidas para el juego
random.shuffle(palabras) #Mezcla aleatoria de palabras para cada partida
velocidad_actual = 0.15; ronda_actual = 1; jugador_actual = 1; puntajes = {1: 0, 2: 0} #Variables globales para controlar la velocidad del código Morse, ronda actual, jugador actual y puntajes
palabra_objetivo = ""; modo_juego = ""; tiempo_inicio = 0 #Variables globales para almacenar la palabra objetivo actual, el modo de juego seleccionado, y el tiempo de inicio del turno
tiempo_j1 = 0 #Variable global para almacenar el tiempo utilizado por el jugador 1 en su turno
multiplicador_dificultad = 1.0 #Variable global para almacenar el multiplicador de dificultad

ventana = tk.Tk()
ventana.state("zoomed")
ventana.title("StrangerTEC - Torneo Universitario") #Título de la ventana
ventana.config(bg=NEGRO)

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

subtitulo = tk.Label(
    ventana,
    text="MORSE COMMUNICATION SYSTEM",
    font=("Tahoma", 12),
    fg=ROJO,
    bg=NEGRO
)
subtitulo.pack()

label_info = tk.Label(
    ventana,
    text="SELECCIONE UN MODO",
    font=FUENTE_SUB,
    fg=TEXTO,
    bg=NEGRO
)
label_info.pack(pady=20)

label_palabra = tk.Label(
    ventana,
    text="",
    font=("Georgia", 48, "bold"),
    fg=ROJO,
    bg=NEGRO
)
label_palabra.pack(pady=30)

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

label_puntajes = tk.Label(
    ventana,
    text="J1: 0 pts | J2: 0 pts",
    font=("Garamond", 18, "bold"),
    fg=ROJO,
    bg=NEGRO
)
label_puntajes.pack(pady=10)

#Canvas para mostrar el estado del reloj de tiempo durante el turno de cada jugador (luz roja cuando el tiempo está corriendo, gris cuando está detenido)
canvas_timer = tk.Canvas(
    ventana,
    width=50,
    height=50,
    bg=NEGRO,
    highlightthickness=0
)
canvas_timer.pack(pady=5)

luz_timer = canvas_timer.create_oval(10, 10, 30, 30, fill="#444") 

label_timer_status = tk.Label(
    ventana,
    text="RELOJ DETENIDO",
    font=("Garamond", 11, "bold"),
    fg=ROJO,
    bg=NEGRO
)
label_timer_status.pack()

#Funciones para manejo de configuración del torneo, reinicio manual del juego, inicio de rondas, verificación de progreso del jugador, y mostrar resultados finales al concluir el torneo
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

    tk.Frame(vent_config, height=2, bd=1, relief="sunken").pack(fill="x", padx=20, pady=10)

    tk.Label(vent_config, text="Multiplicador de Dificultad:", font=("Fixedsys", 12, "bold")).pack(pady=5)
    
    def actualizar_mult(val):
        global multiplicador_dificultad
        multiplicador_dificultad = float(val)

    escala_dif = tk.Scale(vent_config, from_=0.5, to=3.0, resolution=0.1, 
                          orient="horizontal", command=actualizar_mult, length=250)
    escala_dif.set(multiplicador_dificultad) 
    escala_dif.pack(pady=10)
    
    tk.Button(vent_config, text="Cerrar y Guardar", command=vent_config.destroy, bg="#3498DB", fg="white").pack(pady=20)

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

def iniciar_ronda(nuevo_modo=None):
    global ronda_actual, jugador_actual, palabra_objetivo, tiempo_inicio, modo_juego
    if nuevo_modo: modo_juego = nuevo_modo
    if ronda_actual > 10: mostrar_resultados(); return
    
    if jugador_actual == 1:
        palabra_objetivo = palabras[ronda_actual - 1] 
    
    label_info.config(text=f"RONDA {ronda_actual}/10 | Turno: JUGADOR {jugador_actual}")
    
    entrada.delete(0, tk.END)
    entrada.focus()
    
    if modo_juego == "escucha y transmisión":
        label_palabra.config(text="PRESTA ATENCIÓN")
        ventana.after(500, lambda: enviar_a_pico(f"PLAY:{palabra_objetivo}"))
    else: 
        label_palabra.config(text=palabra_objetivo)
        
    tiempo_inicio = 0 
    canvas_timer.itemconfig(luz_timer, fill="gray")
    label_timer_status.config(text="Reloj detenido", fg="gray")
    
def verificar_progreso(event):
    global jugador_actual, ronda_actual, tiempo_j1, tiempo_inicio, puntajes
    
    intento = entrada.get().upper()
    
    if len(intento) > len(palabra_objetivo):
        entrada.delete(len(palabra_objetivo), tk.END)
        intento = intento[:len(palabra_objetivo)]

    if intento and (event is None or (hasattr(event, 'char') and (event.char.isalnum() or event.char in "+-"))):
        enviar_a_pico(f"LUZ:{intento[-1]}")
        
    if len(intento) == 1 and tiempo_inicio == 0:
        tiempo_inicio = time.time()
        canvas_timer.itemconfig(luz_timer, fill="#E74C3C") 
        label_timer_status.config(text="¡TIEMPO CORRIENDO!", fg="#E74C3C")

    if not intento or len(intento) < len(palabra_objetivo):
        return

    if len(intento) == len(palabra_objetivo):
        entrada.unbind("<KeyRelease>") 
        
        tiempo_final = time.time() - tiempo_inicio
        aciertos = sum(1 for i in range(len(palabra_objetivo)) if intento[i] == palabra_objetivo[i])
        
        bono_velocidad = max(10, int(100 - tiempo_final))
        puntos_base = int((aciertos / len(palabra_objetivo)) * bono_velocidad * multiplicador_dificultad)
        
        if jugador_actual == 1:
            tiempo_j1 = tiempo_final
            puntajes[1] += puntos_base
            label_info.config(text=f"¡TURNO COMPLETADO J1! Sigue Jugador 2...")
            
            if aciertos > 0: enviar_a_pico("WIN")
            else: enviar_a_pico("LOSE")

            ventana.after(1000, lambda: enviar_a_pico("OFF")) 

            jugador_actual = 2
            ventana.after(1500, lambda: [iniciar_ronda(), entrada.bind("<KeyRelease>", verificar_progreso)])
            
        else:
            multiplicador = 1.0
            if 0 < tiempo_final < tiempo_j1:
                multiplicador = tiempo_j1 / tiempo_final
            
            if multiplicador > 3.0: multiplicador = 3.0
            puntajes[2] += int(puntos_base * multiplicador)

            if aciertos > 0: enviar_a_pico("WIN")
            else: enviar_a_pico("LOSE")

            if modo_juego == "simple":
                ventana.after(500, lambda: enviar_a_pico("ROUND_END"))

            if modo_juego == "escucha y transmisión":
                label_palabra.config(text=f"ERA: {palabra_objetivo}", fg="#E67E22")

            label_puntajes.config(text=f"J1: {puntajes[1]} pts | J2: {puntajes[2]} pts")
            
            jugador_actual = 1
            ronda_actual += 1
            label_info.config(text=f"¡FIN DE RONDA {ronda_actual-1}!")
            
            ventana.after(2500, lambda: [iniciar_ronda(), 
                                         entrada.bind("<KeyRelease>", verificar_progreso),
                                         label_palabra.config(fg="#2C3E50")])

def mostrar_resultados():
    final_msg = f"TORNEO FINALIZADO\n\nJ1: {puntajes[1]} pts\nJ2: {puntajes[2]} pts"
    messagebox.showinfo("Resultados", final_msg)
    label_palabra.config(text="FIN DE PARTIDA")
    label_info.config(text="Presione 'Resetear Juego' para una nueva partida")
    entrada.delete(0, tk.END)
    entrada.unbind("<KeyRelease>")

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

f_botones = tk.Frame(
    ventana,
    bg=NEGRO
); f_botones.pack(side="bottom", pady=50)

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

btn_config = tk.Button(
    ventana,
    text="⚙ AJUSTES",
    command=abrir_configuracion
)

estilo_boton(btn_config, "#1F618D")
btn_config.place(relx=0.02, rely=0.02)

btn_reset = tk.Button(
    ventana,
    text="🔄 RESET",
    command=resetear_juego_manual
)

estilo_boton(btn_reset, "#922B21")
btn_reset.place(relx=0.12, rely=0.02)

def escuchar_serial():
    while ser and ser.is_open:
        try:
            linea = ser.readline().decode('utf-8').strip()

            if linea.startswith("KEY:"):

                # SOLO bloquear:
                # escucha y transmisión + jugador 1
                if modo_juego == "escucha y transmisión" and jugador_actual == 1:
                    continue

                letra = linea.split(":")[1]
                ventana.after(0, lambda l=letra: insertar_letra(l))

        except:
            break

def insertar_letra(l):
    if l:
        entrada.insert(tk.END, l)
        verificar_progreso(None)

hilo_lectura = threading.Thread(target=escuchar_serial, daemon=True)
hilo_lectura.start()

ventana.mainloop()