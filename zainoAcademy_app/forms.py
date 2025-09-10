#
# Nombre del archivo: forms.py 
# Descripción: Este archivo realiza los formularios para depues usarlos en los templates necesesarios
# Autor: Emmanuel Lopez 
# Fecha de creación: 2025-02-18 
# # Última modificación: 2025-09-05 


from django import forms
from .models import (
    TipoUsuario, Usuario, Curso, Estudiantes, Acudiente, Directivos, 
    Matricula, Profesores, Actividad, MaterialApoyo, 
    Materia, Asistencia, Boletin, Periodo
)
from django.forms import ModelChoiceField


# USUARIOS
class TipoUsuarioForm(forms.ModelForm):
    class Meta:
        model = TipoUsuario
        fields = '__all__'

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'fecha_registro': forms.DateInput(attrs={'type': 'date'}),
            'genero': forms.Select(attrs={'class': 'form-control'})  # AÑADIR ESTA LÍNEA
        }
        labels = {
            'Us_nombre': 'Nombre Completo de Usuario',
            'Us_contraseña': 'Contraseña de Usuario',
            'TipoUsuario': 'Tipo de Usuario',
            'genero': 'Género'  # AÑADIR ESTA LÍNEA
        }

class EstudiantesForm(forms.ModelForm):
    class Meta:
        model = Estudiantes
        exclude = ['Usuario_us']
        widgets = {
            'Est_direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'Est_añoAcademico': forms.Select(attrs={'class': 'form-control'}),  # NUEVO
            'Est_tipoJornada': forms.Select(attrs={'class': 'form-control'}),   # NUEVO
            'Est_enfermedad': forms.TextInput(attrs={'class': 'form-control'}),
            'Est_eps': forms.Select(attrs={'class': 'form-control'}),           # NUEVO
            'Est_colegioAnterior': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'Est_direccion': 'Dirección de Estudiante',
            'Est_añoAcademico': 'Grado académico',          # ACTUALIZADO
            'Est_tipoJornada': 'Tipo de jornada',       
            'Est_enfermedad': 'Enfermedad',
            'Est_eps': 'EPS',                           
            'Est_colegioAnterior': 'Colegio anterior',
        }

class AcudienteForm(forms.ModelForm):
    class Meta:
        model = Acudiente
        fields = ['Usuario_Us', 'Estudiantes_Est']
        widgets = {
            'Usuario_Us': forms.Select(attrs={'class': 'form-control'}),
            'Estudiantes_Est': forms.CheckboxSelectMultiple(),  # Para ManyToMany
        }
        labels = {
            'Usuario_Us': 'Usuario',
            'Estudiantes_Est': 'Estudiantes a cargo'
        }

class DirectivosForm(forms.ModelForm):
    class Meta:
        model = Directivos
        exclude = ['Dir_id', 'Us']  # ✅ EXCLUIR TAMBIÉN EL CAMPO Us
        widgets = {
            'Dir_cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'Dir_telefono': forms.TextInput(attrs={'class': 'form-control'})
        }
        labels = {
            'Dir_cargo': 'Cargo de Directivo',
            'Dir_telefono': 'Teléfono de Directivo'
        }

class ProfesoresForm(forms.ModelForm):
    class Meta:
        model = Profesores
        exclude = ['Pro_id', 'Us'] 

# MATRÍCULA - MODIFICADO PARA SESIÓN Y SIN FECHA MANUAL
class MatriculaForm(forms.ModelForm):
    ESTADO_CHOICES = [
        ('', '---------'),
        ('activa', 'Activa'),
        ('pendiente', 'Pendiente'),
        ('cancelada', 'Cancelada')
    ]
    
    METODO_PAGO_CHOICES = [
        ('', '---------'),
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta de Crédito'),
        ('pse', 'PSE'),
        ('consignacion', 'Consignación')
    ]

    # Campo nivel académico
    Mat_nivel = forms.ChoiceField(
        choices=Matricula.NIVEL_ACADEMICO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Nivel académico'
    )

    Mat_estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado de la matrícula'
    )
    
    Mat_metodo_pago = forms.ChoiceField(
        choices=METODO_PAGO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Método de pago'
    )

    class Meta:
        model = Matricula
        fields = [
            'Estudiantes_Est',
            # REMOVIDO: 'Directivos_Dir' - se asignará automáticamente
            # REMOVIDO: 'Mat_fecha' - se asignará automáticamente con fecha actual
            'Mat_nivel',
            'Mat_estado',
            'Mat_metodo_pago',
            'Mat_comprobante',
            'Mat_valor',
            'Mat_fecha_pago'
        ]
        widgets = {
            'Estudiantes_Est': forms.Select(attrs={'class': 'form-control'}),
            # REMOVIDO: widget para Mat_fecha
            'Mat_fecha_pago': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'Mat_valor': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'class': 'form-control',
                'placeholder': 'Valor en pesos'
            }),
            'Mat_comprobante': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            })
        }
        labels = {
            'Estudiantes_Est': 'Estudiante',
            # REMOVIDO: 'Directivos_Dir': 'Directivo responsable',
            # REMOVIDO: 'Mat_fecha': 'Fecha de matrícula',
            'Mat_nivel': 'Nivel académico',
            'Mat_estado': 'Estado de la matrícula',
            'Mat_metodo_pago': 'Método de pago',
            'Mat_comprobante': 'Comprobante de pago',
            'Mat_valor': 'Valor de la matrícula',
            'Mat_fecha_pago': 'Fecha de pago'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # PERSONALIZAR EL QUERYSET DE ESTUDIANTES PARA MOSTRAR EL NOMBRE
        self.fields['Estudiantes_Est'].queryset = Estudiantes.objects.select_related('Usuario_us')
        self.fields['Estudiantes_Est'].empty_label = "-----------"
        
        # Para edición, hacer el comprobante opcional
        if 'instance' in kwargs and kwargs['instance']:
            # Modo edición - todos los campos opcionales
            for field_name, field in self.fields.items():
                if field_name != 'Mat_comprobante':
                    field.required = False
        else:
            # Modo creación - todos requeridos excepto comprobante
            for field_name, field in self.fields.items():
                if field_name != 'Mat_comprobante':
                    field.required = True

    def clean_Mat_valor(self):
        valor = self.cleaned_data.get('Mat_valor')
        if valor:
            try:
                float(valor)
                if float(valor) <= 0:
                    raise forms.ValidationError('El valor debe ser mayor que 0')
            except (ValueError, TypeError):
                raise forms.ValidationError('El valor debe ser un número válido')
        return valor
    
# CURSOS
class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['Cur_nombre']
        labels = {
            'Cur_nombre': 'Nombre Curso'
        }

# MATERIA 
class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = '__all__'

# BOLETÍN - CORREGIDO
class BoletinForm(forms.ModelForm):
    class Meta:
        model = Boletin
        fields = ['Per', 'Pro', 'Mtr', 'Cur']
        labels = {
            'Per': 'Periodo',
            'Pro': 'Profesor',
            'Mtr': 'Materia',
            'Cur': 'Curso',
        }
        widgets = {
            'Per': forms.Select(attrs={'class': 'form-control'}),
            'Pro': forms.Select(attrs={'class': 'form-control'}),
            'Mtr': forms.Select(attrs={'class': 'form-control'}),
            'Cur': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que todos los campos sean requeridos
        for field in self.fields.values():
            field.required = True

# CLASES DE ELECCIÓN PERSONALIZADAS (Opcionales - para mostrar mejores etiquetas)
class PeriodoChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.Per_nombre

class ProfesorChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.Us.Us_nombre

class MateriaChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.Mtr_nombre

class CursoChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.Cur_nombre
    
class MaterialApoyoForm(forms.ModelForm):
    class Meta:
        model = MaterialApoyo
        fields = ['Mate_titulo', 'Mate_descripcion', 'Mate_archivo']
        widgets = {
            'Mate_titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'Mate_descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'Mate_archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }