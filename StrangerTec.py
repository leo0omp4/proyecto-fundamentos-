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
import tkinter as tk
from tkinter import messagebox
import random, serial, threading, time

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

ventana = tk.Tk() #Creación de la ventana principal del juego utilizando Tkinter
ventana.state("zoomed") #Maximización de la ventana
ventana.title("StrangerTEC - Torneo Universitario") #Título de la ventana

label_info = tk.Label(ventana, text="Seleccione un modo", font=("Arial", 20)) #Indicación de selección de modo de juego
label_info.pack(pady=20)
label_palabra = tk.Label(ventana, text="", font=("Arial", 48, "bold"), fg="#2C3E50") #Etiqueta para mostrar la palabra objetivo
label_palabra.pack(pady=30)
entrada = tk.Entry(ventana, font=("Arial", 30), justify="center") #Campo de entrada para que el jugador escriba su intento de adivinar la palabra objetivo
entrada.pack(pady=20)

label_puntajes = tk.Label(ventana, text="J1: 0 pts | J2: 0 pts", font=("Arial", 18), fg="#34495E") #Etiqueta para mostrar los puntajes de los jugadores
label_puntajes.pack(pady=10)

#Canvas para mostrar el estado del reloj de tiempo durante el turno de cada jugador (luz roja cuando el tiempo está corriendo, gris cuando está detenido)
canvas_timer = tk.Canvas(ventana, width=40, height=40, highlightthickness=0) 
canvas_timer.pack(pady=5)
luz_timer = canvas_timer.create_oval(10, 10, 30, 30, fill="gray") 
label_timer_status = tk.Label(ventana, text="Reloj detenido", font=("Arial", 10), fg="gray")
label_timer_status.pack()

#Funciones para manejo de configuración del torneo, reinicio manual del juego, inicio de rondas, verificación de progreso del jugador, y mostrar resultados finales al concluir el torneo
def abrir_configuracion():
    vent_config = tk.Toplevel(ventana)
    vent_config.title("Ajustes de Torneo")
    vent_config.geometry("400x450")
    vent_config.grab_set()

    tk.Label(vent_config, text="Velocidad del Código (s):", font=("Arial", 12, "bold")).pack(pady=5)
    lbl_v = tk.Label(vent_config, text=f"{velocidad_actual}s")
    lbl_v.pack()
    
    def cambiar_v():
        global velocidad_actual
        velocidad_actual = 0.10 if velocidad_actual == 0.15 else (0.25 if velocidad_actual == 0.10 else 0.15)
        lbl_v.config(text=f"{velocidad_actual}s")
        enviar_a_pico(f"SPD:{velocidad_actual}")
    
    tk.Button(vent_config, text="Cambiar Velocidad", command=cambiar_v).pack(pady=5)

    tk.Frame(vent_config, height=2, bd=1, relief="sunken").pack(fill="x", padx=20, pady=10)

    tk.Label(vent_config, text="Multiplicador de Dificultad:", font=("Arial", 12, "bold")).pack(pady=5)
    
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
    
    if modo_juego == "escucha":
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

            if modo_juego == "transmision":
                ventana.after(500, lambda: enviar_a_pico("ROUND_END"))

            if modo_juego == "escucha":
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

f_botones = tk.Frame(ventana); f_botones.pack(side="bottom", pady=50)

tk.Button(f_botones, text="MODO TRANSMISIÓN", bg="#2ECC71", fg="white", font=("Arial", 14, "bold"),
          command=lambda: [iniciar_ronda("transmision"), entrada.bind("<KeyRelease>", verificar_progreso)], 
          width=20, height=2).grid(row=0, column=0, padx=20)

tk.Button(f_botones, text="MODO ESCUCHA", bg="#F39C12", fg="white", font=("Arial", 14, "bold"),
          command=lambda: [threading.Thread(target=lambda: iniciar_ronda("escucha")).start(), 
                          entrada.bind("<KeyRelease>", verificar_progreso)], 
          width=20, height=2).grid(row=0, column=1, padx=20)

tk.Button(ventana, text="⚙ Ajustes", command=abrir_configuracion).place(relx=0.02, rely=0.02)
tk.Button(ventana, text="🔄 Resetear Juego", command=resetear_juego_manual, 
          bg="#E74C3C", fg="white", font=("Arial", 10, "bold")).place(relx=0.08, rely=0.02)

def escuchar_serial():
    while ser and ser.is_open:
        try:
            linea = ser.readline().decode('utf-8').strip()
            if linea.startswith("KEY:"):
                letra = linea.split(":")[1]
                ventana.after(0, lambda l=letra: insertar_letra(l))
        except: break

def insertar_letra(l):
    if l:
        entrada.insert(tk.END, l)
        verificar_progreso(None)

hilo_lectura = threading.Thread(target=escuchar_serial, daemon=True)
hilo_lectura.start()

ventana.mainloop()