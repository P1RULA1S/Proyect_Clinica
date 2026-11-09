from datetime import datetime
from pathlib import Path

import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget,
)

from database import CAPTURES_DIR, Captura, create_session
from services.camera import CameraManager
from services.patient_service import cargar_paciente, buscar_por_cedula, guardar_paciente
from services.reportes import generar_pdf


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Termografia Medica")
        self.resize(1280, 850)
        self.patient_id = None
        self.frames = {}
        self.capture_paths = []
        self.fields = {}
        self.checkboxes = {}
        self._build_style()
        self._build_ui()
        self.camera_manager = CameraManager({"Frontal": 0, "Izquierda": 1, "Derecha": 2})
        self.camera_manager.start(self._on_frame, self._on_camera_error)

    def _build_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #f8fafc; font-family: Segoe UI; }
            QTabWidget::pane { border: 1px solid #e2e8f0; background: white; }
            QTabBar::tab { background: #e2e8f0; color: #475569; padding: 11px 22px; font-weight: bold; }
            QTabBar::tab:selected { background: white; color: #0f172a; border-bottom: 2px solid #0ea5e9; }
            QGroupBox { color: #334155; font-weight: bold; background: white; border: 1px solid #e2e8f0; border-radius: 6px; margin-top: 12px; padding: 16px; }
            QGroupBox::title { subcontrol-origin: margin; padding: 0 6px; color: #0284c7; }
            QLineEdit, QComboBox, QTextEdit { padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; background: #f8fafc; color: #0f172a; }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border: 1px solid #0ea5e9; background: white; }
            QCheckBox { color: #334155; spacing: 7px; }
            QPushButton { background: #0ea5e9; color: white; padding: 10px 16px; border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background: #0284c7; }
            QPushButton:disabled { background: #94a3b8; }
            QLabel { color: #334155; }
        """)

    def _build_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self._build_capture_tab(), "Captura y busqueda")
        tabs.addTab(self._build_form_tab(), "Historia clinica")
        self.tabs = tabs
        self.setCentralWidget(tabs)

    def _build_capture_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        search_box = QGroupBox("Paciente")
        search_layout = QVBoxLayout(search_box)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cedula o CURP")
        self.search_input.returnPressed.connect(self.search_patient)
        search_button = QPushButton("Buscar paciente")
        search_button.clicked.connect(self.search_patient)
        new_button = QPushButton("Nuevo paciente")
        new_button.clicked.connect(self.new_patient)
        self.status_label = QLabel("Busque un paciente o registre uno nuevo.")
        self.status_label.setWordWrap(True)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(new_button)
        search_layout.addWidget(self.status_label)
        search_layout.addStretch()

        camera_box = QGroupBox("Camara termica")
        camera_layout = QGridLayout(camera_box)
        self.camera_labels = {}
        for column, name in enumerate(("Frontal", "Izquierda", "Derecha")):
            label = QLabel("Sin senal")
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumSize(280, 220)
            label.setStyleSheet("background: #0f172a; color: white;")
            self.camera_labels[name] = label
            camera_layout.addWidget(QLabel(name), 0, column)
            camera_layout.addWidget(label, 1, column)
        capture_button = QPushButton("Capturar las camaras")
        capture_button.clicked.connect(self.capture_frames)
        report_button = QPushButton("Generar informe PDF")
        report_button.clicked.connect(self.generate_report)
        camera_layout.addWidget(capture_button, 2, 0, 1, 2)
        camera_layout.addWidget(report_button, 2, 2)
        layout.addWidget(search_box, 1)
        layout.addWidget(camera_box, 3)
        return tab

    def _build_form_tab(self):
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(14)
        grid.addWidget(self._build_main_data(), 0, 0)
        grid.addWidget(self._build_characteristics(), 1, 0)
        grid.addWidget(self._build_symptoms(), 0, 1)
        grid.addWidget(self._build_genetics(), 1, 1)
        grid.addWidget(self._build_notes(), 0, 2, 2, 1)
        actions = QHBoxLayout()
        save_button = QPushButton("Guardar historia clinica")
        save_button.clicked.connect(self.save_patient)
        clear_button = QPushButton("Limpiar formulario")
        clear_button.clicked.connect(self.new_patient)
        actions.addStretch()
        actions.addWidget(clear_button)
        actions.addWidget(save_button)
        grid.addLayout(actions, 2, 0, 1, 3)
        scroll.setWidget(container)
        layout = QVBoxLayout(tab)
        layout.addWidget(scroll)
        return tab

    def _build_main_data(self):
        box = QGroupBox("Datos principales")
        form = QFormLayout(box)
        for key, label in (("cedula", "Cedula / CURP"), ("nombre_completo", "Nombre completo"), ("edad", "Edad"), ("peso", "Peso (kg)"), ("estatura", "Estatura (m)"), ("ritmo_cardiaco", "Ritmo cardiaco"), ("presion", "Presion")):
            field = QLineEdit()
            self.fields[key] = field
            form.addRow(label, field)
        return box

    def _build_characteristics(self):
        box = QGroupBox("Caracteristicas fisicas")
        form = QFormLayout(box)
        for key, label, values in (("tamano_seno", "Tamano", ["", "A", "B", "C", "D", "DD"]), ("tipo_somatico", "Tipo somatico", ["", "Ectomorfo", "Mesomorfo", "Endomorfo"]), ("ciclo_menstrual", "Ciclo menstrual", ["", "Menstruacion", "Fase folicular", "Ovulacion", "Fase lutea", "Asintomatica"])):
            field = QComboBox()
            field.addItems(values)
            self.fields[key] = field
            form.addRow(label, field)
        for key, label in (("terapia_hormonal", "Terapia hormonal"), ("lactancia", "Lactancia"), ("anticonceptivos", "Anticonceptivos")):
            check = QCheckBox(label)
            self.checkboxes[key] = check
            form.addRow(check)
        return box

    def _build_symptoms(self):
        box = QGroupBox("Sintomas y molestias")
        layout = QGridLayout(box)
        for index, (key, label) in enumerate((("molestia_masa", "Masa o protuberancia"), ("molestia_hinchazon", "Hinchazon"), ("molestia_dolor", "Dolor"), ("secrecion_sanguinolenta", "Secrecion sanguinolenta"), ("piel_enrojecimiento_seno", "Enrojecimiento en piel"))):
            check = QCheckBox(label)
            self.checkboxes[key] = check
            layout.addWidget(check, index // 2, index % 2)
        return box

    def _build_genetics(self):
        box = QGroupBox("Carga genetica")
        layout = QVBoxLayout(box)
        for key, label in (("gen_abuela_materna", "Abuela materna"), ("gen_abuela_paterna", "Abuela paterna"), ("gen_mama", "Madre"), ("gen_hermana", "Hermana")):
            check = QCheckBox(label)
            self.checkboxes[key] = check
            layout.addWidget(check)
        return box

    def _build_notes(self):
        box = QGroupBox("Diagnostico y observaciones")
        layout = QVBoxLayout(box)
        self.fields["diagnostico_dx"] = QTextEdit()
        self.fields["observaciones"] = QTextEdit()
        self.fields["diagnostico_dx"].setMaximumHeight(120)
        layout.addWidget(QLabel("Diagnostico"))
        layout.addWidget(self.fields["diagnostico_dx"])
        layout.addWidget(QLabel("Observaciones"))
        layout.addWidget(self.fields["observaciones"])
        return box

    def _on_frame(self, name, frame):
        self.frames[name] = frame
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = image.shape
        qimage = QImage(image.data, width, height, channels * width, QImage.Format_RGB888)
        self.camera_labels[name].setPixmap(QPixmap.fromImage(qimage).scaled(300, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _on_camera_error(self, message):
        self.status_label.setText(message)

    def search_patient(self):
        cedula = self.search_input.text().strip()
        if not cedula:
            self.status_label.setText("Ingrese una cedula o CURP.")
            return
        patient = buscar_por_cedula(cedula)
        if patient is None:
            self.new_patient()
            self.fields["cedula"].setText(cedula)
            self.status_label.setText("Paciente nuevo. Complete la historia clinica.")
            self.tabs.setCurrentIndex(1)
            return
        self.patient_id = patient.id
        self._load_values(cargar_paciente(patient.id))
        self.status_label.setText(f"Paciente encontrado: {patient.nombre_completo}")
        self.tabs.setCurrentIndex(1)

    def _load_values(self, values):
        for key, value in values.items():
            control = self.fields.get(key) or self.checkboxes.get(key)
            if isinstance(control, QLineEdit):
                control.setText("" if value is None else str(value))
            elif isinstance(control, QTextEdit):
                control.setPlainText(value or "")
            elif isinstance(control, QComboBox):
                control.setCurrentText(value or "")
            elif isinstance(control, QCheckBox):
                control.setChecked(bool(value))

    def _collect_values(self):
        values = {}
        for key, control in self.fields.items():
            if isinstance(control, QLineEdit):
                text = control.text().strip()
                values[key] = text or None
            elif isinstance(control, QTextEdit):
                values[key] = control.toPlainText().strip() or None
            elif isinstance(control, QComboBox):
                values[key] = control.currentText() or None
        for key, control in self.checkboxes.items():
            values[key] = control.isChecked()
        for key in ("edad", "ritmo_cardiaco"):
            if values[key]:
                values[key] = int(values[key])
        for key in ("peso", "estatura"):
            if values[key]:
                values[key] = float(values[key])
        return values

    def save_patient(self):
        try:
            values = self._collect_values()
            if not values.get("cedula") or not values.get("nombre_completo"):
                raise ValueError("Cedula y nombre completo son obligatorios.")
            self.patient_id = guardar_paciente(self.patient_id, values)
            self.status_label.setText("Historia clinica guardada correctamente.")
            QMessageBox.information(self, "Guardado", "La historia clinica se guardo correctamente.")
        except (ValueError, TypeError) as error:
            QMessageBox.warning(self, "Datos invalidos", str(error))
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la historia clinica: {error}")

    def new_patient(self):
        self.patient_id = None
        self.capture_paths = []
        self._load_values({key: False for key in self.checkboxes})
        self._load_values({key: "" for key in self.fields})

    def capture_frames(self):
        if not self.patient_id:
            QMessageBox.warning(self, "Paciente requerido", "Guarde o busque un paciente antes de capturar.")
            return
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        session = create_session()
        try:
            self.capture_paths = []
            for name, frame in self.camera_manager.capture().items():
                path = Path(CAPTURES_DIR) / f"paciente_{self.patient_id}_{name.lower()}_{stamp}.jpg"
                if cv2.imwrite(str(path), frame):
                    session.add(Captura(paciente_id=self.patient_id, camara=name, ruta_archivo=str(path)))
                    self.capture_paths.append(str(path))
            session.commit()
            self.status_label.setText(f"Capturas guardadas: {len(self.capture_paths)}")
        except Exception as error:
            session.rollback()
            QMessageBox.critical(self, "Error de captura", str(error))
        finally:
            session.close()

    def generate_report(self):
        if not self.patient_id:
            QMessageBox.warning(self, "Paciente requerido", "Busque o guarde un paciente antes de generar el informe.")
            return
        try:
            path = generar_pdf(self.patient_id, self._collect_values(), self.capture_paths)
            QMessageBox.information(self, "Informe generado", f"Informe guardado en:\n{path}")
        except Exception as error:
            QMessageBox.critical(self, "Error de informe", str(error))

    def closeEvent(self, event):
        self.camera_manager.stop()
        event.accept()
