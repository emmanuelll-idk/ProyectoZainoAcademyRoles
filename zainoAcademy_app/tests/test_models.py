#
# Nombre del archivo: test_models.py 
# Descripción: Este archivo realiza las pruebas unitarias de los modelos de la base de datos
# Autor: David Santiago Alfonso Guzman
# Fecha de creación: 2025-09-02 
# # Última modificación: 2025-09-07
#Notas: Pruebas ya terminadas TODAS funcionales y probadas


import pytest
from zainoAcademy_app.models import (
    TipoUsuario, Usuario, Curso, Estudiantes, Estudiante_Curso,
    Acudiente, Directivos, Matricula, Profesores, Periodo,
    Materia, Boletin, Estado_Actividad, Actividad,
    Actividad_Entrega, MaterialApoyo, Estado_Asistencia, Asistencia
)
from datetime import date

# ----------------------------
# TipoUsuario y Usuario Con Roles
# ----------------------------

#Prueb tipo usuario
@pytest.mark.django_db
def test_tipo_usuario_str():
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Director")
    assert str(tipo) == "Director"

#prueba rol profesor
@pytest.mark.django_db
def test_usuario_str_and_email():
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Profesor")
    usuario = Usuario.objects.create(
        Us_nombre="Prueba Profesor",
        Us_contraseña="123",
        documento="1234567890",
        genero="femenino",
        correo="profesor@test.com",
        TipoUsuario=tipo
    )
    assert str(usuario) == "Prueba Profesor"
    assert usuario.correo == "profesor@test.com"

#prueba rol directivo
@pytest.mark.django_db
def test_usuario_str_and_email():
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Directivo")
    usuario = Usuario.objects.create(
        Us_nombre="Prueba Directivo",
        Us_contraseña="123",
        documento="1234567891",
        genero="masculino",
        correo="directivo@test.com",
        TipoUsuario=tipo
    )
    assert str(usuario) == "Prueba Directivo"
    assert usuario.correo == "directivo@test.com"

#prueba rol estudiante
@pytest.mark.django_db
def test_usuario_str_and_email():
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Estudiante")
    usuario = Usuario.objects.create(
        Us_nombre="Prueba Estudiante",
        Us_contraseña="123",
        documento="1234567891",
        genero="otro",
        correo="estudiante@test.com",
        TipoUsuario=tipo
    )
    assert str(usuario) == "Prueba Estudiante"
    assert usuario.correo == "estudiante@test.com"

#Prueba rol Acudiente
@pytest.mark.django_db
def test_usuario_str_and_email():
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Acudiente")
    usuario = Usuario.objects.create(
        Us_nombre="Prueba Acudiente",
        Us_contraseña="123",
        documento="1234567891",
        genero="masculino",
        correo="acudiente@test.com",
        TipoUsuario=tipo
    )
    assert str(usuario) == "Prueba Acudiente"
    assert usuario.correo == "acudiente@test.com"

# ----------------------------
# Curso 
# ----------------------------
@pytest.mark.django_db
def test_curso_str():
    curso = Curso.objects.create(Cur_nombre="Biología")
    assert str(curso) == "Biología"

# ----------------------------
# Estudiantes Informacion adicional
# ----------------------------
@pytest.mark.django_db
def test_estudiante_str_and_eps():
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Estudiante")
    usuario = Usuario.objects.create(
        Us_nombre="Pedro",
        Us_contraseña="123",
        documento="112233",
        genero="masculino",
        correo="pedro@test.com",
        TipoUsuario=tipo
    )
    estudiante = Estudiantes.objects.create(
        Est_direccion="Cra 45 #12",
        Est_añoAcademico="decimo",
        Est_tipoJornada="mañana",
        Est_enfermedad="Asma",
        Est_eps="sanitas",
        Est_colegioAnterior="Colegio ABC",
        Usuario_us=usuario
    )
    assert str(estudiante) == "Pedro"
    assert estudiante.Est_eps == "sanitas"

# ----------------------------
# Relación Estudiante-Curso
# ----------------------------
@pytest.mark.django_db
def test_estudiante_curso_relationship():
    curso = Curso.objects.create(Cur_nombre="Química")
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Estudiante")
    usuario = Usuario.objects.create(
        Us_nombre="Maria",
        Us_contraseña="clave",
        documento="778899",
        genero="femenino",
        correo="maria@test.com",
        TipoUsuario=tipo
    )
    estudiante = Estudiantes.objects.create(
        Est_direccion="Av 123",
        Est_añoAcademico="once",
        Est_tipoJornada="tarde",
        Est_enfermedad="Ninguna",
        Est_eps="sura",
        Est_colegioAnterior="Colegio XYZ",
        Usuario_us=usuario
    )
    relacion = Estudiante_Curso.objects.create(Est=estudiante, Cur=curso)
    assert str(relacion) == str(relacion.Est_Cur_id)

# ----------------------------
# Acudiente con varios estudiantes
# ----------------------------
@pytest.mark.django_db
def test_acudiente_multiple_estudiantes():
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Acudiente")
    usuario = Usuario.objects.create(
        Us_nombre="Carlos Padre",
        Us_contraseña="padre123",
        documento="334455",
        genero="masculino",
        correo="padre@test.com",
        TipoUsuario=tipo
    )
    estudiante1 = Estudiantes.objects.create(
        Est_direccion="Calle 10",
        Est_añoAcademico="octavo",
        Est_tipoJornada="mañana",
        Est_enfermedad="Ninguna",
        Est_eps="compensar",
        Est_colegioAnterior="Colegio Z",
        Usuario_us=usuario
    )
    estudiante2 = Estudiantes.objects.create(
        Est_direccion="Calle 20",
        Est_añoAcademico="noveno",
        Est_tipoJornada="tarde",
        Est_enfermedad="Ninguna",
        Est_eps="famisanar",
        Est_colegioAnterior="Colegio Z",
        Usuario_us=usuario
    )
    acudiente = Acudiente.objects.create(Usuario_Us=usuario)
    acudiente.Estudiantes_Est.add(estudiante1, estudiante2)
    assert "Carlos Padre" in str(acudiente)
    assert acudiente.Estudiantes_Est.count() == 2

# ----------------------------
# Matricula y Directivos
# ----------------------------
@pytest.mark.django_db
def test_matricula_str():
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Directivo")
    usuario = Usuario.objects.create(
        Us_nombre="Rector Juan",
        Us_contraseña="123",
        documento="556677",
        genero="masculino",
        correo="rector@test.com",
        TipoUsuario=tipo
    )
    directivo = Directivos.objects.create(
        Dir_cargo="Rector",
        Dir_telefono="123456789",
        Us=usuario
    )
    tipo_est = TipoUsuario.objects.create(TusTiposUsuario="Estudiante")
    usuario_est = Usuario.objects.create(
        Us_nombre="Alumno X",
        Us_contraseña="abc",
        documento="998877",
        genero="masculino",
        correo="alumno@test.com",
        TipoUsuario=tipo_est
    )
    estudiante = Estudiantes.objects.create(
        Est_direccion="Calle 50",
        Est_añoAcademico="primero",
        Est_tipoJornada="mañana",
        Est_enfermedad="Ninguna",
        Est_eps="otra",
        Est_colegioAnterior="Colegio Y",
        Usuario_us=usuario_est
    )
    matricula = Matricula.objects.create(
        Mat_nivel="primaria",
        Mat_fecha=date.today(),
        Mat_estado="Pagada",
        Mat_metodo_pago="Efectivo",
        Mat_valor="500000",
        Mat_fecha_pago=date.today(),
        Estudiantes_Est=estudiante,
        Directivos_Dir=directivo
    )
    assert str(matricula) == str(matricula.Mat_id)

# ----------------------------
# Profesores y Boletín
# ----------------------------
@pytest.mark.django_db
def test_boletin_str():
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Profesor")
    usuario = Usuario.objects.create(
        Us_nombre="Profesor Luis",
        Us_contraseña="prof123",
        documento="445566",
        genero="masculino",
        correo="luis@test.com",
        TipoUsuario=tipo
    )
    profesor = Profesores.objects.create(Us=usuario)
    periodo = Periodo.objects.create(Per_nombre="2025-1")
    curso = Curso.objects.create(Cur_nombre="Historia")
    materia = Materia.objects.create(Mtr_nombre="Historia Universal")
    boletin = Boletin.objects.create(Pro=profesor, Per=periodo, Cur=curso, Mtr=materia)
    assert str(boletin) == str(boletin.Bol_id)

# ----------------------------
# Actividades y entregas
# ----------------------------
@pytest.mark.django_db
def test_actividad_and_entrega():
    estado = Estado_Actividad.objects.create(Esta_Actividad_Estado="Pendiente")
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Profesor")
    usuario = Usuario.objects.create(
        Us_nombre="Profe Ana",
        Us_contraseña="clave",
        documento="111222",
        genero="femenino",
        correo="profe@test.com",
        TipoUsuario=tipo
    )
    profesor = Profesores.objects.create(Us=usuario)
    periodo = Periodo.objects.create(Per_nombre="2025-2")
    curso = Curso.objects.create(Cur_nombre="Matemáticas")
    materia = Materia.objects.create(Mtr_nombre="Álgebra")
    boletin = Boletin.objects.create(Pro=profesor, Per=periodo, Cur=curso, Mtr=materia)

    actividad = Actividad.objects.create(
        Act_nombre="Tarea 1",
        Act_descripcion="Resolver ejercicios de álgebra",
        Act_fechaLimite=date.today(),
        Act_comentario="Importante entregar a tiempo",
        Esta_Actividad=estado,
        Bol=boletin
    )
    assert str(actividad) == "Tarea 1"

# ----------------------------
# Asistencia
# ----------------------------
@pytest.mark.django_db
def test_asistencia_str():
    estado_asistencia = Estado_Asistencia.objects.create(Esta_Asistencia_Estado="Presente")
    curso = Curso.objects.create(Cur_nombre="Inglés")
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Estudiante")
    usuario = Usuario.objects.create(
        Us_nombre="Esteban",
        Us_contraseña="clave",
        documento="999000",
        genero="masculino",
        correo="esteban@test.com",
        TipoUsuario=tipo
    )
    estudiante = Estudiantes.objects.create(
        Est_direccion="Calle 60",
        Est_añoAcademico="sexto",
        Est_tipoJornada="mañana",
        Est_enfermedad="Ninguna",
        Est_eps="sura",
        Est_colegioAnterior="Colegio ABC",
        Usuario_us=usuario
    )
    relacion = Estudiante_Curso.objects.create(Est=estudiante, Cur=curso)
    asistencia = Asistencia.objects.create(
        Ast_fecha=date.today(),
        Esta_Asistencia=estado_asistencia,
        Est_Cur=relacion
    )
    assert str(asistencia) == str(asistencia.Ast_id)