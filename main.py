import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from enum import Enum
import threading

# Enumeraciones para Prioridad y Estado
class Prioridad(Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    PERSONALIZADA = "Personalizada"

class Estado(Enum):
    PENDIENTE = "Pendiente"
    COMPLETADA = "Completada"

# Clase Tarea
class Tarea:
    def __init__(self, nombre, prioridad, estado=Estado.PENDIENTE, fecha_creacion=None, recordatorio=None):
        self.nombre = nombre
        self.prioridad = prioridad
        self.estado = estado
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.recordatorio = recordatorio

# Aplicación principal
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Tareas")
        self.geometry("700x500")
        self.resizable(False, False)

        self.tareas = []  # Lista de tareas
        self.filtro_prioridad = None  # Filtro de prioridad actual
        self.historial = []  # Lista de tareas completadas (historial)

        self._crear_interfaz()
        self._iniciar_recordatorios()

    def _crear_interfaz(self):
        # Cabecera
        header = tk.Label(self, text="Lista de Tareas", font=("Arial", 16, "bold"))
        header.pack(pady=10)

        # Barra de búsqueda
        self.entry_busqueda = tk.Entry(self, width=30)
        self.entry_busqueda.pack(pady=5)
        self.entry_busqueda.bind("<KeyRelease>", self._buscar_tareas)

        # Frame para el ListView
        self.tree = ttk.Treeview(self, columns=("Nombre", "Prioridad", "Estado", "Fecha", "Recordatorio"), show="headings")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Prioridad", text="Prioridad")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Fecha", text="Fecha de Creación")
        self.tree.heading("Recordatorio", text="Recordatorio")
        self.tree.column("Nombre", width=150)
        self.tree.column("Prioridad", width=80)
        self.tree.column("Estado", width=100)
        self.tree.column("Fecha", width=120)
        self.tree.column("Recordatorio", width=120)
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Pie de Página
        self.pie = tk.Label(self, text="Total de tareas: 0 | Tareas completadas: 0", font=("Arial", 10))
        self.pie.pack(pady=5)

        # Botones
        botones_frame = tk.Frame(self)
        botones_frame.pack(pady=10)

        btn_agregar = tk.Button(botones_frame, text="Agregar Tarea", command=self._mostrar_formulario)
        btn_agregar.grid(row=0, column=0, padx=5)

        btn_completar = tk.Button(botones_frame, text="Completar Tarea", command=self._completar_tarea)
        btn_completar.grid(row=0, column=1, padx=5)

        btn_eliminar = tk.Button(botones_frame, text="Eliminar Tarea", command=self._eliminar_tarea)
        btn_eliminar.grid(row=0, column=2, padx=5)

        btn_historial = tk.Button(botones_frame, text="Ver Historial", command=self._mostrar_historial)
        btn_historial.grid(row=0, column=3, padx=5)

        # Ordenamiento
        btn_ordenar_fecha = tk.Button(botones_frame, text="Ordenar por Fecha", command=self._ordenar_por_fecha)
        btn_ordenar_fecha.grid(row=0, column=4, padx=5)

        btn_ordenar_prioridad = tk.Button(botones_frame, text="Ordenar por Prioridad", command=self._ordenar_por_prioridad)
        btn_ordenar_prioridad.grid(row=0, column=5, padx=5)

    def _actualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for tarea in self.tareas:
            if self.filtro_prioridad and tarea.prioridad != self.filtro_prioridad:
                continue
            recordatorio = tarea.recordatorio.strftime("%Y-%m-%d %H:%M") if tarea.recordatorio else ""
            self.tree.insert(
                "", "end",
                values=(
                    tarea.nombre,
                    tarea.prioridad.value,
                    tarea.estado.value,
                    tarea.fecha_creacion.strftime("%Y-%m-%d %H:%M"),
                    recordatorio,
                ),
            )

        total = len(self.tareas)
        completadas = sum(1 for tarea in self.tareas if tarea.estado == Estado.COMPLETADA)
        self.pie.config(text=f"Total de tareas: {total} | Tareas completadas: {completadas}")

    def _mostrar_formulario(self):
        form = tk.Toplevel(self)
        form.title("Agregar Tarea")
        form.geometry("300x300")
        form.resizable(False, False)

        tk.Label(form, text="Nombre:").pack(pady=5)
        nombre_entry = tk.Entry(form)
        nombre_entry.pack(pady=5)

        tk.Label(form, text="Prioridad:").pack(pady=5)
        prioridades = [p.value for p in Prioridad]
        prioridad_combo = ttk.Combobox(form, values=prioridades, state="readonly")
        prioridad_combo.pack(pady=5)
        prioridad_combo.current(0)

        tk.Label(form, text="Recordatorio (minutos desde ahora):").pack(pady=5)
        recordatorio_entry = tk.Entry(form)
        recordatorio_entry.pack(pady=5)

        def agregar():
            nombre = nombre_entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío")
                return
            prioridad = Prioridad[prioridad_combo.get().upper()]
            recordatorio_min = recordatorio_entry.get().strip()
            recordatorio = datetime.now() + timedelta(minutes=int(recordatorio_min)) if recordatorio_min else None
            nueva_tarea = Tarea(nombre, prioridad, recordatorio=recordatorio)
            self.tareas.append(nueva_tarea)
            self._actualizar_lista()
            form.destroy()

        tk.Button(form, text="Guardar", command=agregar).pack(pady=20)

    def _completar_tarea(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "No se seleccionó ninguna tarea")
            return

        for item in seleccion:
            nombre = self.tree.item(item, "values")[0]
            for tarea in self.tareas:
                if tarea.nombre == nombre and tarea.estado == Estado.PENDIENTE:
                    tarea.estado = Estado.COMPLETADA
                    self.historial.append(tarea)
        self._actualizar_lista()

    def _eliminar_tarea(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "No se seleccionó ninguna tarea")
            return

        if messagebox.askyesno("Eliminar Tarea", "¿Está seguro de eliminar la tarea seleccionada?"):
            for item in seleccion:
                nombre = self.tree.item(item, "values")[0]
                self.tareas = [tarea for tarea in self.tareas if tarea.nombre != nombre]
            self._actualizar_lista()

    def _ordenar_por_fecha(self):
        self.tareas.sort(key=lambda tarea: tarea.fecha_creacion)
        self._actualizar_lista()

    def _ordenar_por_prioridad(self):
        prioridad_orden = {Prioridad.ALTA: 1, Prioridad.MEDIA: 2, Prioridad.BAJA: 3, Prioridad.PERSONALIZADA: 4}
        self.tareas.sort(key=lambda tarea: prioridad_orden.get(tarea.prioridad, 0))
        self._actualizar_lista()

    def _buscar_tareas(self, event):
        query = self.entry_busqueda.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for tarea in self.tareas:
            if query in tarea.nombre.lower():
                self.tree.insert(
                    "", "end",
                    values=(
                        tarea.nombre,
                        tarea.prioridad.value,
                        tarea.estado.value,
                        tarea.fecha_creacion.strftime("%Y-%m-%d %H:%M"),
                        tarea.recordatorio.strftime("%Y-%m-%d %H:%M") if tarea.recordatorio else "",
                    ),
                )

    def _mostrar_historial(self):
        historial_window = tk.Toplevel(self)
        historial_window.title("Historial de Tareas Completadas")
        historial_window.geometry("400x300")
        tk.Label(historial_window, text="Historial de Tareas Completadas", font=("Arial", 14)).pack(pady=10)
        for tarea in self.historial:
            tk.Label(historial_window, text=f"- {tarea.nombre} ({tarea.fecha_creacion.strftime('%Y-%m-%d')})").pack()

    def _iniciar_recordatorios(self):
        def verificar_recordatorios():
            while True:
                for tarea in self.tareas:
                    if tarea.recordatorio and tarea.estado == Estado.PENDIENTE and tarea.recordatorio <= datetime.now():
                        tarea.estado = Estado.COMPLETADA
                        self.historial.append(tarea)
                        messagebox.showinfo("Recordatorio", f"Es hora de completar la tarea: {tarea.nombre}")
                        self._actualizar_lista()
                self.after(60000, verificar_recordatorios)
        
        hilo = threading.Thread(target=verificar_recordatorios, daemon=True)
        hilo.start()

# Ejecución de la aplicación
if __name__ == "__main__":
    app = App()
    app.mainloop()
