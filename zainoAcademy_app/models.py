#
# Nombre del archivo: models.py 
# Descripción: Este archivo realiza los modelos para usar en todo el sistema
# Autor: David Santiago Alfonso Guzman
# Fecha de creación: 2025-02-02 
# # Última modificación: 2025-09-07
#NOTAS: 

from django.db import models

class TipoUsuario(models.Model):
    Tus_id = models.AutoField(primary_key=True)
    TusTiposUsuario = models.CharField(max_length=30)

    class Meta:
        db_table = 'TipoUsuario'
    
    def __str__(self):
        return self.TusTiposUsuario

class Usuario(models.Model): 
    Us_id = models.AutoField(primary_key=True)
    Us_nombre = models.CharField(max_length=30)
    Us_contraseña = models.CharField(max_length=30)
    fecha_registro = models.DateField(auto_now_add=True)
    documento = models.CharField(max_length=30)
    
    # CAMBIO AQUÍ - Reemplazar esta línea:
    # genero = models.CharField(max_length=30)
    
    # POR ESTA:
    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('prefiero_no_decir', 'Prefiero no decir'),
    ]
    genero = models.CharField(
        max_length=30,
        choices=GENERO_CHOICES,
        blank=False
    )
    
    correo = models.EmailField(unique=True)
    TipoUsuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE) 

    class Meta:
        db_table = 'usuario'
    def __str__(self):
        return self.Us_nombre
class Curso(models.Model):  
    Cur_id = models.AutoField(primary_key=True)  
    Cur_nombre = models.CharField(max_length=100) 

    class Meta:
        db_table = 'curso'
    def __str__(self):  
        return self.Cur_nombre

class Estudiantes(models.Model):
    Est_id = models.AutoField(primary_key=True) 
    Est_direccion = models.CharField(max_length=100)
    
    # CAMBIO 1: Grado académico
    GRADO_CHOICES = [
        ('transicion', 'Transición'),
        ('primero', 'Primero'),
        ('segundo', 'Segundo'),
        ('tercero', 'Tercero'),
        ('cuarto', 'Cuarto'),
        ('quinto', 'Quinto'),
        ('sexto', 'Sexto'),
        ('septimo', 'Séptimo'),
        ('octavo', 'Octavo'),
        ('noveno', 'Noveno'),
        ('decimo', 'Décimo'),
        ('once', 'Once'),
    ]
    Est_añoAcademico = models.CharField(
        max_length=30,
        choices=GRADO_CHOICES,
        verbose_name="Grado académico"
    )
    
    # CAMBIO 2: Tipo de jornada
    JORNADA_CHOICES = [
        ('mañana', 'Mañana'),
        ('tarde', 'Tarde'),
        ('noche', 'Noche'),
        ('completa', 'Jornada Completa'),
        ('sabatina', 'Sabatina'),
        ('dominical', 'Dominical'),
    ]
    Est_tipoJornada = models.CharField(
        max_length=30,
        choices=JORNADA_CHOICES,
        verbose_name="Tipo de jornada"
    )
    
    Est_enfermedad = models.CharField(max_length=30)
    
    # CAMBIO 3: EPS de Colombia
    EPS_CHOICES = [
        ('nueva_eps', 'Nueva EPS'),
        ('sanitas', 'Sanitas'),
        ('sura', 'Sura'),
        ('compensar', 'Compensar'),
        ('famisanar', 'Famisanar'),
        ('salud_total', 'Salud Total'),
        ('coomeva', 'Coomeva'),
        ('medimas', 'Medimás'),
        ('colsanitas', 'Colsanitas'),
        ('cafesalud', 'Cafesalud'),
        ('golden_group', 'Golden Group'),
        ('aliansalud', 'Aliansalud'),
        ('mutual_ser', 'Mutual Ser'),
        ('coosalud', 'Coosalud'),
        ('capresoca', 'Capresoca'),
        ('comfenalco', 'Comfenalco'),
        ('ecoopsos', 'Ecoopsos'),
        ('emssanar', 'Emssanar'),
        ('salud_vida', 'Salud Vida'),
        ('otra', 'Otra'),
    ]
    Est_eps = models.CharField(
        max_length=30,
        choices=EPS_CHOICES,
        verbose_name="EPS"
    )
    
    Est_colegioAnterior = models.CharField(max_length=30)
    Usuario_us = models.ForeignKey(Usuario, on_delete=models.CASCADE) 

    class Meta:
        db_table = 'estudiantes'
    def __str__(self):
        return f"{self.Usuario_us.Us_nombre}"

class Estudiante_Curso(models.Model):  
    Est_Cur_id = models.AutoField(primary_key=True)  
    Est = models.ForeignKey(Estudiantes, on_delete=models.CASCADE)
    Cur = models.ForeignKey(Curso, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Estudiante_Curso'
    def __str__(self):  
        return str(self.Est_Cur_id)

class Acudiente(models.Model):
    Acu_id = models.AutoField(primary_key=True)
    Usuario_Us = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    # Cambiar esta línea:
    # Estudiantes_Est = models.ForeignKey(Estudiantes, on_delete=models.CASCADE)
    # Por esta relación muchos-a-muchos:
    Estudiantes_Est = models.ManyToManyField(Estudiantes, related_name='acudientes')

    def __str__(self):
        return f"Acudiente {self.Usuario_Us.Us_nombre}"

class Directivos(models.Model):
    Dir_id = models.AutoField(primary_key=True) 
    Dir_cargo = models.CharField(max_length=50)
    Dir_telefono = models.CharField(max_length=30)
    Us = models.ForeignKey(Usuario, on_delete=models.CASCADE) 

    class Meta:
        db_table = 'directivos'
    def __str__(self):
        return self.Dir_cargo

class Matricula(models.Model):
    Mat_id = models.AutoField(primary_key=True) 
    
    # CAMBIO: Nivel académico con opciones predefinidas
    NIVEL_ACADEMICO_CHOICES = [
        ('transicion', 'Transición'),
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('media', 'Media'),
    ]
    Mat_nivel = models.CharField(
        max_length=50,
        choices=NIVEL_ACADEMICO_CHOICES,
        verbose_name="Nivel académico"
    )
    
    Mat_fecha = models.DateField()
    Mat_estado = models.CharField(max_length=30)
    Mat_metodo_pago = models.CharField(max_length=30)
    Mat_comprobante = models.FileField(upload_to='matricula/', null=True, blank=True)
    Mat_valor = models.CharField(max_length=30)
    Mat_fecha_pago = models.DateField()
    Estudiantes_Est = models.ForeignKey(Estudiantes,on_delete=models.CASCADE)
    Directivos_Dir = models.ForeignKey(Directivos, on_delete=models.CASCADE)

    class Meta:
        db_table = 'matricula'
    def __str__(self):
        return str(self.Mat_id)


class Profesores(models.Model):
    Pro_id = models.AutoField(primary_key=True)
    Us = models.ForeignKey(Usuario, on_delete=models.CASCADE)  

    class Meta:
        db_table = 'profesores'
    
    def __str__(self):
        return self.Us.Us_nombre



class Periodo(models.Model):
    Per_id = models.AutoField(primary_key=True) 
    Per_nombre = models.CharField(max_length=30) 

    class Meta:
        db_table = 'periodo'
    def __str__(self):
        return self.Per_nombre


class Materia(models.Model):
    Mtr_id = models.AutoField(primary_key=True)
    Mtr_nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'materia'
    def __str__(self):
        return self.Mtr_nombre

class Boletin(models.Model):
    Bol_id = models.AutoField(primary_key=True)
    Pro = models.ForeignKey(Profesores, on_delete=models.CASCADE)  
    Per = models.ForeignKey(Periodo, on_delete=models.CASCADE) 
    Cur = models.ForeignKey(Curso, on_delete=models.CASCADE) 
    Mtr = models.ForeignKey(Materia, on_delete=models.CASCADE) 

    class Meta:
        db_table = 'boletin'
    def __str__(self):
        return str(self.Bol_id)

class Estado_Actividad(models.Model):
    Esta_Actividad_id = models.AutoField(primary_key=True)
    Esta_Actividad_Estado = models.CharField(max_length=30)

    class Meta:
        db_table = 'estado_actividad'
    def __str__(self):
        return self.Esta_Actividad_Estado

class Actividad(models.Model):
    Act_id = models.AutoField(primary_key=True)
    Act_nombre = models.CharField(max_length=30)
    Act_descripcion = models.TextField()
    Act_fechaLimite = models.DateField()
    Act_comentario = models.CharField(max_length=100)
    Act_Archivo_Profesor = models.FileField(upload_to='archivos/profesores/', null=True, blank=True)
    Esta_Actividad = models.ForeignKey(Estado_Actividad, on_delete=models.CASCADE)
    Bol = models.ForeignKey(Boletin, on_delete=models.CASCADE)

    class Meta:
        db_table = 'actividad'

    def __str__(self):
        return self.Act_nombre

class Actividad_Entrega(models.Model):
    Act_Archivo_Estudiante = models.FileField(upload_to='archivos/estudiantes/')
    Act_fecha_entrega = models.DateField(auto_now_add=True)
    Act_calificacion = models.FloatField(null=True, blank=True)
    Act = models.ForeignKey('Actividad', on_delete=models.CASCADE)
    Est = models.ForeignKey('Estudiantes', on_delete=models.CASCADE)

    class Meta:
        db_table = 'actividad_entrega'
        unique_together = ('Act', 'Est')
    def __str__(self):
        return f"{self.Act} - {self.Est}"

class MaterialApoyo(models.Model):
    Mate_id = models.AutoField(primary_key=True)
    Mate_descripcion = models.CharField(max_length=100)
    Mate_titulo = models.CharField(max_length=100)
    Bol = models.ForeignKey(Boletin, on_delete=models.CASCADE)
    Mate_archivo = models.FileField(upload_to='materiales_apoyo/', null=True, blank=True) 

    class Meta:
        db_table = 'material_de_apoyo'

    def __str__(self):
        return self.Mate_titulo


class Estado_Asistencia(models.Model):
    Esta_Asistencia_id = models.AutoField(primary_key=True)
    Esta_Asistencia_Estado = models.CharField(max_length=30)

    class Meta:
        db_table = 'estado_asistencia'
    def __str__(self):
        return self.Esta_Asistencia_Estado


class Asistencia(models.Model):
    Ast_id = models.AutoField(primary_key=True)
    Ast_fecha = models.DateField()
    Esta_Asistencia = models.ForeignKey(Estado_Asistencia,on_delete=models.CASCADE)
    Est_Cur = models.ForeignKey(Estudiante_Curso,on_delete=models.CASCADE)

    class Meta:
        db_table = 'asistencia'
    def __str__(self):
        return str(self.Ast_id)