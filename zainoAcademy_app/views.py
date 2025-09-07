from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from .models import Periodo, Usuario, TipoUsuario, Boletin, Materia, Estudiante_Curso, Estudiantes, Actividad, Actividad_Entrega, MaterialApoyo, Asistencia, Profesores, Estado_Actividad, Estado_Asistencia, Curso, Directivos, Matricula, Acudiente, Asistencia, Estudiantes
from datetime import date
import json, io
from .forms import  UsuarioForm, EstudiantesForm, DirectivosForm, AcudienteForm, MatriculaForm, CursoForm, MateriaForm
from .models import Boletin
from .forms import BoletinForm
from django.views.decorators.http import require_GET, require_POST


#Paginas Estaticas:
def inicio(request):
    return render (request, "staticPage/index.html")

def nosotros(request):
    return render (request, "staticPage/nosotros.html")

def contacto(request):
    return render (request, "staticPage/contacto.html")

def precios(request):
    return render (request, "staticPage/precio.html")



def redirect_to_login(request):
    return redirect('login')


def login_view(request):
    mensaje = ''
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        contraseña = request.POST.get('contraseña', '').strip()

        try:
            usuario = Usuario.objects.get(correo=correo, Us_contraseña=contraseña)
            
            # Guardamos el usuario en sesión
            request.session['usuario_id'] = usuario.Us_id
            request.session['tipo_usuario'] = usuario.TipoUsuario.TusTiposUsuario
            request.session['usuario_nombre'] = usuario.Us_nombre

            # Redirigir según tipo de usuario
            tipo_id = usuario.TipoUsuario.Tus_id

            if tipo_id == 2:  # estudiante
                return redirect('dashboard_estudiantes')
            elif tipo_id == 1:  # profesor
                return redirect('dashboard_profesores')
            elif tipo_id == 3:  # directivo
                return redirect('dashboard_directivos')
            elif tipo_id == 4:  # acudiente
                return redirect('dashboard_acudientes')
            else:
                mensaje = 'Tipo de usuario no válido'

        except Usuario.DoesNotExist:
            mensaje = 'Correo o contraseña incorrectos'

    return render(request, 'registration/login.html', {'mensaje': mensaje})

def get_usuario_from_session(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            return Usuario.objects.get(Us_id=usuario_id)
        except Usuario.DoesNotExist:
            return None
    return None

@csrf_exempt
def actualizar_perfil_acudientes(request):
    if request.method == 'POST':
        usuario = get_usuario_from_session(request)
        if not usuario:
            return JsonResponse({'error': 'Usuario no autenticado'}, status=403)

        try:
            data = json.loads(request.body.decode('utf-8'))

            usuario.Us_nombre = data.get('username', usuario.Us_nombre)
            usuario.correo = data.get('email', usuario.correo)
            usuario.Us_contraseña = data.get('password', usuario.Us_contraseña)

            # ✅ Solución: asegurarse de que fecha_registro tenga un valor
            if not usuario.fecha_registro:
                usuario.fecha_registro = date.today()

            usuario.save()

            # Actualizamos el nombre en la sesión
            request.session['usuario_nombre'] = usuario.Us_nombre

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def dashboard_estudiantes(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    estudiante = get_object_or_404(Estudiantes, Usuario_us=usuario)

    boletines_qs = Boletin.objects.filter(
        Cur_id__in=Estudiante_Curso.objects.filter(Est=estudiante).values_list("Cur_id", flat=True)
    )

    actividades_qs = Actividad.objects.filter(Bol__in=boletines_qs).distinct()

    pendientes = []
    for actividad in actividades_qs:
        entrega = Actividad_Entrega.objects.filter(Act=actividad, Est=estudiante).first()
        if not entrega or not entrega.Act_Archivo_Estudiante:  # no entregada
            pendientes.append({
                "actividad": actividad.Act_nombre,
                "materia": actividad.Bol.Mtr.Mtr_nombre,
                "estado": "Sin entregar"
            })

    return render(request, 'estudiantes/dashboard_estudiantes.html', {
        'usuario': usuario,
        'pendientes': pendientes[:4]  # limitar a 4 como en tu diseño
    })


def dashboard_directivos(request):
    return HttpResponse('<h1>Dashboard Directivos - Login Exitoso!</h1>')

def dashboard_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/dashboard_acudientes.html', {'usuario': usuario})

def actividades_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/actividades_acudientes.html', {'usuario': usuario})

def asistencia_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/asistencia_acudientes.html', {'usuario': usuario})

def notificaciones_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/notificaciones_acudientes.html', {'usuario': usuario})

def editar_perfil_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/editar_perfil_acudientes.html', {'usuario': usuario})



# Vistas estudiantes:

def consultar_periodos(request):
    periodos = Periodo.objects.all().order_by('Per_id')
    return render(request, 'estudiantes/periodo_estudiantes.html', {'periodos': periodos})

def consultar_reportes(request):
    return render(request, 'estudiantes/reportes_estudiantes.html')

def get_boletines_estudiante(usuario, periodo):
    estudiantes_qs = Estudiantes.objects.filter(Usuario_us = usuario) 
    cursos_ids = Estudiante_Curso.objects.filter(Est__in = estudiantes_qs).values_list('Cur_id', flat = True) # Est__in -> la __in es para cuando recibe listas de objetos, ej: [Est_id = 2, Est_id = 3] /// Guarda en una lista los Cur de Estudiante_Curso /// flat=true lo uso sólo cuando vaya a pedir una sola columna de mi lista
    boletines_qs = Boletin.objects.filter(Per=periodo, Cur_id__in = cursos_ids) # Boletin(Bol_id = 1, Cur=Curso (Cur_id = 2)), Per=Periodo(Per_id=2), Mtr = Materia(Mtr_id=5), Pro=Profesores(Pro_id=1))
    return boletines_qs


# estudiantes_qs = [ Estudiantes(Est_id=10, Usuario_us=7, Est_direccion="Calle 123", ...) ]
# cursos_ids = [2, 4]  // Sólo los cursos del estudiante por values_list, osino traería todos los campos de Estudiant_curso
# boletines_qs = [Boletin(1, Per=???, Cur=2, Mtr=5, Pro=1), Boletin(2, Per=???, Cur=4, Mtr=8, Pro=3)]


def materias_estudiantes(request, Per_id): # actividad_estudiantes(request, periodo_id=2)
    usuario = get_usuario_from_session(request) # usuario = [Usuario(id=7 , nombre="Emmanuel")]
    periodo = get_object_or_404(Periodo, pk=Per_id) # periodo = [Periodo(Per_id=2, Per_nombre="segundo")] /// get_object_or_404 -> trae todos los campos del objeto
    boletines_qs = get_boletines_estudiante(usuario,periodo) # Filtra estudiantes por usuario, después la PK del estudiante en Estudiante_Curso, después esos estudiantes de Estudiante_Curso los filtra en Boletin, con periodo y curso de la tabla Boletin
    materias_qs = Materia.objects.filter(Mtr_id__in=boletines_qs.values_list('Mtr_id', flat=True)).distinct() # distinct() -> Cuando quiero que la lista de values_list no repita algún resultado
        
    # print("Usuario:", usuario) Traer el único objeto de arriba
    # print("Estudiantes:", list(estudiantes_qs.values())) Traer todos los objetos de una lista o query set


    return render(request, 'estudiantes/actividad_estudiantes.html', {
    'periodo': periodo,
    'materias': materias_qs
    })

def actividades_estudiantes(request, Per_id, Mtr_id):
    usuario = get_usuario_from_session(request)
    periodo = get_object_or_404(Periodo, pk=Per_id)
    materia = get_object_or_404(Materia, pk=Mtr_id)

    boletines_qs = get_boletines_estudiante(usuario, periodo).filter(Mtr_id=materia)
    actividades_qs = Actividad.objects.filter(Bol__in=boletines_qs).distinct()

    estudiante = get_object_or_404(Estudiantes, Usuario_us=usuario)

    actividades_con_calificacion = []
    for actividad in actividades_qs:
        entrega = Actividad_Entrega.objects.filter(Act=actividad, Est=estudiante).first()
        actividades_con_calificacion.append({
            "actividad": actividad,
            "calificacion": entrega.Act_calificacion if entrega else None
        })

    return render(request, 'estudiantes/actividad_estudiantes_consultar.html', {
        "actividades": actividades_con_calificacion,
        "materia": materia,
        "periodo": periodo
    })

def subir_actividad_estudiante(request, Per_id, Mtr_id, Act_id):
    usuario = get_usuario_from_session(request)
    periodo = get_object_or_404(Periodo, pk=Per_id)
    materia = get_object_or_404(Materia, pk=Mtr_id)
    actividad = get_object_or_404(Actividad, pk=Act_id)

    estudiante = get_object_or_404(Estudiantes, Usuario_us=usuario)

    entrega = Actividad_Entrega.objects.filter(Act=actividad, Est=estudiante).first()

    if request.method == "POST":
        archivo = request.FILES.get("archivo_estudiante")
        if archivo:
            entrega, created = Actividad_Entrega.objects.update_or_create(
                Act=actividad,
                Est=estudiante,
                defaults={"Act_Archivo_Estudiante": archivo}
            )
            messages.success(request, "Actividad subida correctamente.")
        else:
            messages.error(request, "Debes seleccionar un archivo para subir.")

    return render(request, "estudiantes/actividad_estudiantes_subir.html", {
        "actividad": actividad,
        "materia": materia,
        "periodo": periodo,
        "entrega": entrega,
    })


def materiales_apoyo_estudiantes(request, Per_id, Mtr_id):
    usuario = get_usuario_from_session(request)
    periodo = get_object_or_404(Periodo, pk=Per_id)
    materia = get_object_or_404(Materia, pk=Mtr_id)

    boletines_qs = get_boletines_estudiante(usuario, periodo).filter(Mtr_id=materia)

    materiales_qs = MaterialApoyo.objects.filter(Bol__in=boletines_qs).distinct()

    return render(request, "estudiantes/material_de_apoyo_estudiantes.html", {
        "materiales": materiales_qs,
        "materia": materia,
        "periodo": periodo
    })


# Vistas Profesores:

def dashboard_profesores(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'profesores/dashboard_profesores.html', {'usuario': usuario})

def actividad_profesores_calificaciones(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'profesores/actividad_profesores_calificaciones.html', {'usuario': usuario})


def actividad_profesores_consultar_cursos(request, periodo_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    profesor = usuario.profesores_set.first()

    # Cursos + materias que el profesor tiene en ese periodo
    boletines = Boletin.objects.filter(Pro=profesor, Per_id=periodo_id).select_related('Cur', 'Mtr')

    return render(request, 'profesores/actividad_profesores_consultar_cursos.html', {
        'usuario': usuario,
        'boletines': boletines,
        'periodo_id': periodo_id
    })


def actividad_profesores_consultar(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    periodos = Periodo.objects.all()  # todos los periodos disponibles

    return render(request, 'profesores/actividad_profesores_consultar.html', {
        'usuario': usuario,
        'periodos': periodos
    })


def actividad_profesores_crear_actividad(request, bol_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    boletin = Boletin.objects.get(Bol_id=bol_id)  # el boletín viene de la URL
    estado = Estado_Actividad.objects.get_or_create(Esta_Actividad_Estado="Pendiente")[0]

    if request.method == 'POST':
        nombre = request.POST.get('Act_nombre')
        fecha = request.POST.get('Act_fechaLimite')
        descripcion = request.POST.get('Act_descripcion')
        archivo = request.FILES.get('Act_Archivo_Profesor')

        Actividad.objects.create(
            Act_nombre=nombre,
            Act_fechaLimite=fecha,
            Act_descripcion=descripcion,
            Act_Archivo_Profesor=archivo,
            Bol=boletin,
            Esta_Actividad=estado
        )

        return redirect('actividad_profesores_lista')  # redirigir a listado

    return render(request, 'profesores/actividad_profesores_crear_actividad.html', {
        'usuario': usuario,
        'boletin': boletin
    })

def actividad_profesores_lista(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    profesor = usuario.profesores_set.first()  # obtengo el profesor del usuario

    # ✅ Buscar actividades relacionadas con los boletines de ese profesor
    actividades = Actividad.objects.filter(Bol__Pro=profesor)

    return render(request, 'profesores/actividad_profesores_lista.html', {
        'usuario': usuario,
        'actividades': actividades
    })

def asistencia_profesores_añadir(request, bol_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    boletin = Boletin.objects.get(Bol_id=bol_id)
    estudiantes_curso = Estudiante_Curso.objects.filter(Cur=boletin.Cur).select_related("Est")

    if request.method == 'POST':
        for ec in estudiantes_curso:
            estado_nombre = request.POST.get(f'estado_{ec.Est.Est_id}')

            if estado_nombre:  # solo si se eligió algo
                # Buscar el estado en la tabla Estado_Asistencia
                estado_obj, _ = Estado_Asistencia.objects.get_or_create(Esta_Asistencia_Estado=estado_nombre)

                # Crear asistencia
                Asistencia.objects.create(
                    Ast_fecha=date.today(),
                    Est_Cur=ec,
                    Esta_Asistencia=estado_obj
                )

        return redirect('asistencia_profesores_consultar', bol_id=boletin.Bol_id)

    return render(request, 'profesores/asistencia_profesores_añadir.html', {
        'usuario': usuario,
        'boletin': boletin,
        'estudiantes': [ec.Est for ec in estudiantes_curso],  # pasamos solo los estudiantes
    })


def asistencia_profesores_consultar(request, bol_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    # Obtenemos el boletín
    boletin = Boletin.objects.get(Bol_id=bol_id)

    # Filtramos asistencias por los estudiantes de ese curso
    asistencias = Asistencia.objects.filter(
        Est_Cur__Cur=boletin.Cur
    ).select_related('Est_Cur')

    return render(request, 'profesores/asistencia_profesores_consultar.html', {
        'usuario': usuario,
        'asistencias': asistencias,
        'boletin': boletin,
    })


def asistencia_profesores_cursos(request, periodo_id=None):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    profesor = usuario.profesores_set.first()
    periodos = Periodo.objects.all()

    # Si ya eligió un periodo, buscamos sus cursos/materias en ese periodo
    boletines = []
    if periodo_id:
        boletines = Boletin.objects.filter(Pro=profesor, Per_id=periodo_id).select_related('Cur', 'Mtr')

    return render(request, 'profesores/asistencia_profesores_cursos.html', {
        'usuario': usuario,
        'periodos': periodos,
        'periodo_id': periodo_id,
        'boletines': boletines
    })

def materialApoyo_subir(request, bol_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    boletin = Boletin.objects.get(Bol_id=bol_id)

    if request.method == 'POST':
        titulo = request.POST.get('Mate_titulo')
        descripcion = request.POST.get('Mate_descripcion')
        archivo = request.FILES.get('Mate_archivo')

        MaterialApoyo.objects.create(
            Mate_titulo=titulo,
            Mate_descripcion=descripcion,
            Mate_archivo=archivo,
            Bol=boletin
        )

        return redirect('materialApoyo_consultar', bol_id=boletin.Bol_id)

    return render(request, 'profesores/materialApoyo_subir.html', {
        'usuario': usuario,
        'boletin': boletin
    })


def materialApoyo_consultar(request, bol_id):
    materiales = MaterialApoyo.objects.filter(Bol_id=bol_id)
    boletin = Boletin.objects.get(Bol_id=bol_id)
    periodo_id = boletin.Per_id  # obtiene el ID del periodo relacionado

    return render(request, "profesores/materialApoyo_consultar.html", {
        "materiales": materiales,
        "bol_id": bol_id,
        "periodo_id": periodo_id,
    })



def notificaciones_profesores(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'profesores/notificaciones_profesores.html', {'usuario': usuario})

def reportes_profesores_descargar(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'profesores/reportes_profesores_descargar.html', {'usuario': usuario})

def reportes_profesores(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'profesores/reportes_profesores.html', {'usuario': usuario})



#DIRECTIVOS SANTIAGO 

def get_cargo_directivo(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            directivo = Directivos.objects.get(Us_id=usuario_id)  # Buscar el directivo por su usuario
            return directivo.Dir_cargo
        except Directivos.DoesNotExist:
            return None
    return None


#--------------------------------------------
#Directivos
#----------------------------------------------
def dashboard_directivos(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'directivos/dashboard_directivos.html', {'usuario': usuario})
    

def dashboard_cargo_directivos(request):
    cargo = get_cargo_directivo(request)
    return render(request, 'directivos/dashboard_directivos.html', {'cargo' : cargo})




# ----------------------------
# USUARIO
# ----------------------------

def crear_usuario(request):
    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST)
        if usuario_form.is_valid():
            usuario = usuario_form.save()
            tipo_usuario_str = str(usuario.TipoUsuario).lower()
            
            if tipo_usuario_str == 'estudiante':
                return redirect('crear_estudiante', usuario_id=usuario.Us_id)
            elif tipo_usuario_str == 'directivo':
                return redirect('crear_directivo', usuario_id=usuario.Us_id)
            elif tipo_usuario_str == 'acudiente':
                return redirect('crear_acudiente', usuario_id=usuario.Us_id)
            elif tipo_usuario_str == 'profesor':
                # Crear automáticamente el registro en la tabla Profesores
                Profesores.objects.create(Us=usuario)
                messages.success(request, 'Usuario profesor registrado exitosamente.')
                return redirect('lista_usuarios')
            else:
                messages.success(request, 'Usuario registrado exitosamente.')
                return redirect('lista_usuarios')
    else:
        usuario_form = UsuarioForm()
    return render(request, 'directivos/usuario.html', {'usuario_form': usuario_form})


def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'directivos/usuario_form.html', {'usuarios': usuarios})


def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'directivos/editar_usuario.html', {'form': form, 'usuario': usuario})


def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('lista_usuarios')
    return render(request, 'directivos/eliminar_usuario.html', {'usuario': usuario})

# ----------------------------
# USUARIO + ESTUDIANTE
# ----------------------------


def crear_estudiante(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        estudiante_form = EstudiantesForm(request.POST)
        if estudiante_form.is_valid():
            estudiante = estudiante_form.save(commit=False)
            estudiante.Usuario_us = usuario   # ✅ ahora sí le pasas el objeto
            estudiante.save()
            messages.success(request, 'Datos del estudiante registrados correctamente.')
            return redirect('lista_usuarios')
    else:
        estudiante_form = EstudiantesForm()
    return render(request, 'directivos/crear_estudiante.html', {'estudiante_form': estudiante_form, 'usuario': usuario})




# ----------------------------
# USUARIO + DIRECTIVOS
# ----------------------------

def crear_directivo(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    
    if request.method == 'POST':
        directivo_form = DirectivosForm(request.POST)
        
        # Debug temporal - puedes comentar estas líneas después
        print("POST data:", request.POST)
        print("Form is valid:", directivo_form.is_valid())
        
        if directivo_form.is_valid():
            try:
                directivo = directivo_form.save(commit=False)
                directivo.Us = usuario  # Asignar el usuario al directivo
                directivo.save()
                messages.success(request, 'Datos del directivo registrados correctamente.')
                return redirect('lista_usuarios')
            except Exception as e:
                print(f"Error al guardar directivo: {e}")
                messages.error(request, f'Error al guardar el directivo: {str(e)}')
        else:
            # Mostrar errores del formulario
            print("Errores del formulario:", directivo_form.errors)
            for field, errors in directivo_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        directivo_form = DirectivosForm()
    
    return render(request, 'directivos/crear_directivo.html', {
        'directivo_form': directivo_form, 
        'usuario': usuario
    })

# ----------------------------
# USUARIO + ACUDIENTE
# ----------------------------

def crear_acudiente(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    return render(request, 'directivos/crear_acudiente.html', {'usuario': usuario})

@csrf_exempt
@require_POST
def crear_acudiente_con_estudiantes(request):  # CAMBIO: Nombre de función
    try:
        usuario_id = request.POST.get('usuario_id')
        estudiantes_ids = request.POST.getlist('estudiantes[]')  # CAMBIO: Obtener lista de estudiantes
        
        if not usuario_id or not estudiantes_ids:
            return JsonResponse({
                'success': False, 
                'error': 'Faltan datos: usuario_id o estudiantes_ids'
            })
        
        # Obtener el usuario
        usuario = get_object_or_404(Usuario, pk=usuario_id)
        
        # Crear o obtener el acudiente
        acudiente, created = Acudiente.objects.get_or_create(Usuario_Us=usuario)
        
        # CAMBIO: Limpiar relaciones anteriores (opcional)
        acudiente.Estudiantes_Est.clear()
        
        # CAMBIO: Agregar múltiples estudiantes a la relación ManyToMany
        estudiantes_asignados = []
        for est_id in estudiantes_ids:
            try:
                estudiante = Estudiantes.objects.get(pk=est_id)
                acudiente.Estudiantes_Est.add(estudiante)
                estudiantes_asignados.append(estudiante.Usuario_us.Us_nombre)
            except Estudiantes.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Acudiente registrado exitosamente para {len(estudiantes_asignados)} estudiantes',
            'estudiantes_asignados': estudiantes_asignados
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })


def crear_profesor(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        # Como el modelo Profesores solo tiene Us como campo adicional,
        # podemos crear directamente el registro
        profesor = Profesores.objects.create(Us=usuario)
        messages.success(request, 'Datos del profesor registrados correctamente.')
        return redirect('lista_usuarios')
    else:
        # Si el modelo Profesores tuviera más campos, usarías un formulario
        pass
    
    return render(request, 'directivos/crear_profesor.html', {'usuario': usuario})
# ----------------------------
# MATRICULA 
# ----------------------------

def lista_matriculas(request):
    matriculas = Matricula.objects.select_related(
        'Estudiantes_Est__Usuario_us', 
        'Directivos_Dir__Us'
    ).all()
    return render(request, 'directivos/matricula_form.html', {'matricula': matriculas})

def crear_matricula(request):
    if request.method == 'POST':
        # ⚠️ IMPORTANTE: Incluir request.FILES para el archivo
        form = MatriculaForm(request.POST, request.FILES)
        
        # Debugging temporal - puedes comentar estas líneas después
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        print("Form is valid:", form.is_valid())
        
        if form.is_valid():
            try:
                matricula = form.save()
                messages.success(request, f'Matrícula {matricula.Mat_id} registrada correctamente.')
                return redirect('lista_matriculas')
            except Exception as e:
                print(f"Error al guardar: {e}")
                messages.error(request, f'Error al guardar la matrícula: {str(e)}')
        else:
            # Mostrar errores del formulario
            print("Errores del formulario:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MatriculaForm()
    
    # Agregar información adicional para debugging
    context = {
        'form': form,
        'estudiantes_count': Estudiantes.objects.count(),
        'directivos_count': Directivos.objects.count(),
    }
    
    return render(request, 'directivos/matricula.html', context)

def editar_matricula(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    
    if request.method == 'POST':
        # ⚠️ IMPORTANTE: Incluir request.FILES para manejar archivos
        form = MatriculaForm(request.POST, request.FILES, instance=matricula)
        
        # Debug temporal - puedes comentar estas líneas después
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        print("Form is valid:", form.is_valid())
        
        if form.is_valid():
            try:
                matricula_actualizada = form.save()
                messages.success(request, f'Matrícula {matricula_actualizada.Mat_id} actualizada correctamente.')
                return redirect('lista_matriculas')
            except Exception as e:
                print(f"Error al actualizar matrícula: {e}")
                messages.error(request, f'Error al actualizar la matrícula: {str(e)}')
        else:
            # Mostrar errores del formulario
            print("Errores del formulario:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MatriculaForm(instance=matricula)
    
    # Agregar información adicional para debugging
    context = {
        'form': form,
        'matricula': matricula,  # ✅ Pasar la matrícula al contexto
        'estudiantes_count': Estudiantes.objects.count(),
        'directivos_count': Directivos.objects.count(),
    }
    
    return render(request, 'directivos/editar_matricula.html', context)

def eliminar_matricula(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)

    if request.method == 'POST':
        matricula.delete()
        messages.success(request, 'Matrícula eliminada correctamente.')
        return redirect('lista_matriculas')

    return render(request, 'directivos/eliminar_matricula.html', {'matricula': matricula})

# ----------------------------
# CURSO
# ----------------------------
# Buscar estudiantes por nombre o documento
@require_GET
def buscar_estudiantes(request):
    q = request.GET.get("q", "")
    
    # Si no hay query, devolver todos los estudiantes
    if not q:
        estudiantes = Estudiantes.objects.select_related('Usuario_us').all()
    else:
        estudiantes = Estudiantes.objects.filter(
            Usuario_us__Us_nombre__icontains=q
        ).select_related('Usuario_us') | Estudiantes.objects.filter(
            Usuario_us__documento__icontains=q
        ).select_related('Usuario_us')

    data = [
        {
            "id": e.Est_id,
            "nombre": e.Usuario_us.Us_nombre,
            "documento": e.Usuario_us.documento,
        }
        for e in estudiantes
    ]
    return JsonResponse(data, safe=False)



# Vista para mostrar el formulario de creación
def crear_curso(request):
    usuario = get_usuario_from_session(request)
    
    # Agregar información adicional para debugging como en matrícula
    context = {
        'usuario': usuario,
        'estudiantes_count': Estudiantes.objects.count(),
    }
    
    return render(request, "directivos/curso.html", context)


# Crear curso con estudiantes seleccionados
@csrf_exempt
def crear_curso_con_estudiantes(request):
    if request.method == "POST":
        try:
            nombre = request.POST.get("Cur_nombre")
            estudiantes_ids = request.POST.getlist("estudiantes[]")
            
            print(f"Nombre del curso: {nombre}")
            print(f"Estudiantes IDs: {estudiantes_ids}")
            
            if not nombre:
                return JsonResponse({"success": False, "error": "El nombre del curso es requerido"})
            
            if not estudiantes_ids:
                return JsonResponse({"success": False, "error": "Debe asignar al menos un estudiante"})
            
            # Crear el curso
            curso = Curso.objects.create(Cur_nombre=nombre)
            print(f"Curso creado con ID: {curso.Cur_id}")

            # Asignar estudiantes al curso
            estudiantes_asignados = []
            for est_id in estudiantes_ids:
                try:
                    estudiante = Estudiantes.objects.get(pk=est_id)
                    relacion = Estudiante_Curso.objects.create(Est=estudiante, Cur=curso)
                    estudiantes_asignados.append(estudiante.Usuario_us.Us_nombre)
                    print(f"Estudiante {estudiante.Usuario_us.Us_nombre} asignado al curso")
                except Estudiantes.DoesNotExist:
                    print(f"Estudiante con ID {est_id} no encontrado")
                    continue
                except Exception as e:
                    print(f"Error asignando estudiante {est_id}: {e}")
                    continue

            return JsonResponse({
                "success": True, 
                "curso_id": curso.Cur_id,
                "mensaje": f"Curso '{nombre}' creado con {len(estudiantes_asignados)} estudiantes",
                "estudiantes_asignados": estudiantes_asignados
            })

        except Exception as e:
            print(f"Error general: {e}")
            return JsonResponse({"success": False, "error": f"Error interno: {str(e)}"})

    return JsonResponse({"success": False, "error": "Método no permitido"})



def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'directivos/curso_form.html', {'cursos': cursos})

def editar_curso(request, id):
    curso = get_object_or_404(Curso, pk=id)
    usuario = get_usuario_from_session(request)
    
    context = {
        'curso': curso,
        'usuario': usuario,
        'estudiantes_count': Estudiantes.objects.count(),
    }
    
    return render(request, 'directivos/editar_curso.html', context)


@csrf_exempt
def actualizar_curso_con_estudiantes(request, curso_id):
    if request.method == "POST":
        try:
            curso = get_object_or_404(Curso, pk=curso_id)
            nombre = request.POST.get("Cur_nombre")
            estudiantes_ids = request.POST.getlist("estudiantes[]")
            
            print(f"Actualizando curso: {curso.Cur_nombre} -> {nombre}")
            print(f"Nuevos estudiantes IDs: {estudiantes_ids}")
            
            if not nombre:
                return JsonResponse({"success": False, "error": "El nombre del curso es requerido"})
            
            # Actualizar nombre del curso
            curso.Cur_nombre = nombre
            curso.save()

            # Eliminar todas las relaciones actuales
            Estudiante_Curso.objects.filter(Cur=curso).delete()
            print("Relaciones anteriores eliminadas")

            # Crear las nuevas relaciones
            estudiantes_asignados = []
            for est_id in estudiantes_ids:
                try:
                    estudiante = Estudiantes.objects.get(pk=est_id)
                    Estudiante_Curso.objects.create(Est=estudiante, Cur=curso)
                    estudiantes_asignados.append(estudiante.Usuario_us.Us_nombre)
                    print(f"Estudiante {estudiante.Usuario_us.Us_nombre} asignado al curso")
                except Estudiantes.DoesNotExist:
                    print(f"Estudiante con ID {est_id} no encontrado")
                    continue

            return JsonResponse({
                "success": True, 
                "curso_id": curso.Cur_id,
                "mensaje": f"Curso '{nombre}' actualizado con {len(estudiantes_asignados)} estudiantes",
                "estudiantes_asignados": estudiantes_asignados
            })

        except Exception as e:
            print(f"Error general: {e}")
            return JsonResponse({"success": False, "error": f"Error interno: {str(e)}"})

    return JsonResponse({"success": False, "error": "Método no permitido"})


@require_GET
def obtener_estudiantes_curso(request, curso_id):
    try:
        curso = get_object_or_404(Curso, pk=curso_id)
        relaciones = Estudiante_Curso.objects.filter(Cur=curso).select_related('Est__Usuario_us')
        
        data = [
            {
                "id": rel.Est.Est_id,
                "nombre": rel.Est.Usuario_us.Us_nombre,
                "documento": rel.Est.Usuario_us.documento,
            }
            for rel in relaciones
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def eliminar_curso(request, id):
    curso = get_object_or_404(Curso, pk=id)
    if request.method == 'POST':
        curso.delete()
        messages.success(request, 'Curso eliminado correctamente.')
        return redirect('lista_cursos')
    return render(request, 'directivos/eliminar_curso.html', {'curso': curso})


# ----------------------------
# MATERIA
# ----------------------------

def crear_materia(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia registrada exitosamente.')
            return redirect('lista_materias')
    else:
        form = MateriaForm()
    return render(request, 'directivos/materia.html', {'form': form})


def lista_materias(request):
    materias = Materia.objects.all()
    return render(request, "directivos/materia_form.html", {"materias": materias})


def editar_materia(request, id):
    materia = get_object_or_404(Materia, pk=id)
    if request.method == 'POST':
        form = MateriaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia actualizada.')
            return redirect('lista_materias')
    else:
        form = MateriaForm(instance=materia)
    return render(request, 'directivos/editar_materia.html', {'form': form})


def eliminar_materia(request, id):
    materia = get_object_or_404(Materia, pk=id)
    if request.method == 'POST':
        materia.delete()
        messages.success(request, 'Materia eliminada correctamente.')
        return redirect('lista_materias')
    return render(request, 'directivos/eliminar_materia.html', {'materia': materia})




#Directivo Notificaciones
def notificaciones_directivos(request):
    usuario = get_usuario_from_session(request)
    return render(request,'directivos/notificaciones_directivos.html',{'usuario' : usuario})

#--------------------------------------------------
#Periodo
#-------------------------------------------------
def periodo_crear_directivos(request):
    usuario = get_usuario_from_session(request)

    if request.method == 'POST':
        form = BoletinForm(request.POST)
        if form.is_valid():
            form.save()  # ← crea el registro en Boletín
            messages.success(request, 'Periodo asignado correctamente al boletín.')
            return redirect('periodo_directivos_consultar')
    else:
        form = BoletinForm()

    return render(request, 'directivos/periodo_directivos_crear.html', {
        'usuario': usuario,
        'form': form
    })

def periodo_consultar_directivos(request):
    usuario = get_usuario_from_session(request)
    boletines = Boletin.objects.select_related('Per','Pro__Us','Mtr','Cur').all()
    return render(request, 'directivos/periodo_directivos_consultar.html', {
        'usuario': usuario,
        'boletines': boletines
    })

# Agregar estas vistas al archivo views.py

def editar_periodo(request, id):
    """Vista para editar un boletín (periodo)"""
    boletin = get_object_or_404(Boletin, pk=id)
    usuario = get_usuario_from_session(request)
    
    if request.method == 'POST':
        form = BoletinForm(request.POST, instance=boletin)
        if form.is_valid():
            form.save()
            messages.success(request, 'Periodo actualizado correctamente.')
            return redirect('periodo_directivos_consultar')
        else:
            # Si hay errores en el formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = BoletinForm(instance=boletin)
    
    return render(request, 'directivos/editar_periodo.html', {
        'form': form,
        'boletin': boletin,
        'usuario': usuario
    })


def eliminar_periodo(request, id):
    """Vista para eliminar un boletín (periodo)"""
    boletin = get_object_or_404(Boletin, pk=id)
    usuario = get_usuario_from_session(request)
    
    if request.method == 'POST':
        # Antes de eliminar, verificar si hay actividades relacionadas
        actividades_relacionadas = Actividad.objects.filter(Bol=boletin).count()
        materiales_relacionados = MaterialApoyo.objects.filter(Bol=boletin).count()
        
        if actividades_relacionadas > 0 or materiales_relacionados > 0:
            messages.warning(
                request, 
                f'No se puede eliminar el periodo porque tiene {actividades_relacionadas} '
                f'actividades y {materiales_relacionados} materiales de apoyo asociados. '
                'Elimine primero estos elementos.'
            )
            return redirect('periodo_directivos_consultar')
        
        try:
            boletin.delete()
            messages.success(request, 'Periodo eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el periodo: {str(e)}')
        
        return redirect('periodo_directivos_consultar')
    
    return render(request, 'directivos/eliminar_periodo.html', {
        'boletin': boletin,
        'usuario': usuario
    })



#Acudiente

def dashboard_acudientes(request):
    try:
        usuario = get_usuario_from_session(request)
        if not usuario:
            return redirect('login')

        # traer acudiente y estudiantes a cargo
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)
        estudiantes_a_cargo = [acudiente.Estudiantes_Est]

        actividades_pendientes = []
        if estudiantes_a_cargo:
            actividades_pendientes = Actividad.objects.filter(
                Esta_Actividad_id=2,
                Bol__Cur__estudiante_curso__Est=estudiantes_a_cargo[0]
            ).select_related('Bol__Mtr', 'Esta_Actividad')

        context = {
            'usuario': usuario,
            'estudiantes_a_cargo': estudiantes_a_cargo,
            'actividades_pendientes': actividades_pendientes,
            'total_pendientes': len(actividades_pendientes),
        }
        return render(request, 'acudientes/dashboard_acudientes.html', context)

    except Exception as e:
        print(f"❌ Error en dashboard_acudientes: {e}")
        return render(request, 'acudientes/dashboard_acudientes.html', {
            'usuario': None,
            'estudiantes_a_cargo': [],
            'actividades_pendientes': [],
            'total_pendientes': 0,
        })


def dashboard_acudientes_calendar(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    # Aseguramos que fecha_registro no esté vacío
    if not usuario.fecha_registro:
        usuario.fecha_registro = date.today()
        usuario.save()

    today = date.today().isoformat()  # Para el input date

    return render(request, "acudientes/dashboard_acudientes.html", {
        "usuario": usuario,
        "today": today
    })

def actividades_acudientes(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')
    
    try:
        # Obtener el acudiente basado en el usuario de la sesión
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)
        
        # Obtener todos los estudiantes a cargo de este acudiente
        # Nota: Según tu modelo, un acudiente tiene UN estudiante (ForeignKey)
        # Si quieres que sea muchos estudiantes, deberías cambiar el modelo
        estudiantes_a_cargo = [acudiente.Estudiantes_Est]
        
        # Si quisieras múltiples estudiantes, usarías:
        # estudiantes_a_cargo = Acudiente.objects.filter(Usuario_Us=usuario).select_related('Estudiantes_Est')
        
        context = {
            'usuario': usuario,
            'estudiantes_a_cargo': estudiantes_a_cargo,
        }
        
        return render(request, 'acudientes/actividades_acudientes.html', context)
        
    except Acudiente.DoesNotExist:
        # Si no existe el acudiente, mostrar página sin estudiantes
        context = {
            'usuario': usuario,
            'estudiantes_a_cargo': [],
        }
        return render(request, 'acudientes/actividades_acudientes.html', context)

def asistencia_acudientes(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')
    
    try:
        # Obtener el acudiente basado en el usuario de la sesión
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)
        
        # Obtener todos los estudiantes a cargo de este acudiente
        estudiantes_a_cargo = [acudiente.Estudiantes_Est]
        
        # Si quisieras múltiples estudiantes, usarías:
        # estudiantes_a_cargo = Acudiente.objects.filter(Usuario_Us=usuario).select_related('Estudiantes_Est')
        
        context = {
            'usuario': usuario,
            'estudiantes_a_cargo': estudiantes_a_cargo,
        }
        
        return render(request, 'acudientes/asistencia_acudientes.html', context)
        
    except Acudiente.DoesNotExist:
        # Si no existe el acudiente, mostrar página sin estudiantes
        context = {
            'usuario': usuario,
            'estudiantes_a_cargo': [],
        }
        return render(request, 'acudientes/asistencia_acudientes.html', context)

def notificaciones_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/notificaciones_acudientes.html', {'usuario': usuario})

def editar_perfil_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/editar_perfil_acudientes.html', {'usuario': usuario})

def actividades_list_acudientes(request):
    usuario = get_usuario_from_session(request)
    estudiante_id = request.POST.get('student_id')  # Obtiene el ID del estudiante desde el formulario

    # Obtener el estudiante asociado al acudiente (solo si el estudiante existe)
    if estudiante_id:
        try:
            estudiante = Estudiantes.objects.get(Est_id=estudiante_id)
            # Usar solo 'Act' y 'Bol' en select_related
            actividades = Actividad_Entrega.objects.filter(Est=estudiante).select_related('Act', 'Act__Bol', 'Act__Esta_Actividad')
        except Estudiantes.DoesNotExist:
            actividades = []
    else:
        actividades = []

    return render(request, 'acudientes/actividades_list_acudientes.html', {
        'usuario': usuario,
        'actividades': actividades,
    })

def asistencia_list_acudientes(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    estudiante = None
    periodos = []

    try:
        # Obtener el acudiente asociado al usuario
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)

        # Tomar el estudiante a cargo (siempre 1 según tu modelo)
        estudiante = acudiente.Estudiantes_Est  

        if estudiante:
            # Guardamos en sesión por si se necesita luego
            request.session["student_id"] = estudiante.Est_id

            # Buscar periodos a los que pertenece este estudiante
            periodos = Periodo.objects.filter(
                boletin__Cur__estudiante_curso__Est=estudiante
            ).distinct()

    except Acudiente.DoesNotExist:
        pass

    return render(request, "acudientes/asistencia_list_acudientes.html", {
        "usuario": usuario,
        "estudiante": estudiante,
        "periodos": periodos
    })

def asistencia_pdf_acudientes(request):
    usuario = get_usuario_from_session(request)
    periodo_id = request.POST.get("periodo_id")
    estudiante_id = request.session.get("student_id")

    if not (periodo_id and estudiante_id):
        return HttpResponse("Faltan datos", status=400)

    try:
        # estudiante
        estudiante = Estudiantes.objects.get(Est_id=estudiante_id)
        # periodo
        periodo = Periodo.objects.get(Per_id=periodo_id)
        # estudiante_curso
        est_curso = Estudiante_Curso.objects.get(Est=estudiante)
    except (Estudiantes.DoesNotExist, Periodo.DoesNotExist, Estudiante_Curso.DoesNotExist):
        return HttpResponse("Datos no encontrados", status=404)

    # 🔎 Traer la asistencia real de ese estudiante y periodo
    asistencias = Asistencia.objects.filter(
        Est_Cur=est_curso,
        Est_Cur__Cur__boletin__Per=periodo   # ← ajusta si tu Periodo se relaciona distinto
    ).select_related("Esta_Asistencia").order_by("Ast_fecha")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # ====== Encabezado ======
    elements.append(Paragraph(f"Asistencia - {periodo.Per_nombre}", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Estudiante:</b> {estudiante.Usuario_us.Us_nombre}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # ====== Tabla ======
    data = [["Fecha", "Estado"]]  # cabecera
    if asistencias.exists():
        for a in asistencias:
            data.append([a.Ast_fecha.strftime("%Y-%m-%d"), a.Esta_Asistencia.Esta_Asistencia_Estado])
    else:
        data.append(["Sin registros", "-"])

    table = Table(data, colWidths=[200, 200])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e91d6")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 12),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#f9f9f9")),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Asistencia_{estudiante.Usuario_us.Us_nombre}.pdf")


