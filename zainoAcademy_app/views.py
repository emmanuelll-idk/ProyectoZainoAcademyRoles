#
# Nombre del archivo: views.py 
# Descripción: Este archivo realiza las vistas entre la base y los templates
# Autor: Gabriela Muñoz Acero
# Fecha de creación: 2025-02-02 
# # Última modificación: 2025-09-08
#NOTAS: Se realizco migracion de los archivos y vistas por acudinetes


#Importaciones de libreias y otros archivos
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Periodo, Usuario, TipoUsuario, Boletin, Materia, Estudiante_Curso, Estudiantes, Actividad, Actividad_Entrega, MaterialApoyo, Asistencia, Profesores, Estado_Actividad, Estado_Asistencia, Curso, Directivos, Matricula, Acudiente, Asistencia, Estudiantes, Actividad_EntregaArchivo
from datetime import date
import json, io
import logging
from .forms import  UsuarioForm, EstudiantesForm, DirectivosForm, AcudienteForm, MatriculaForm, CursoForm, MateriaForm, BoletinForm, MaterialApoyoForm

# Para los reportes de estudiantes

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.utils import timezone

# Importaciones Stefany

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Count
from django.utils.timezone import localtime
from collections import defaultdict



#Paginas Estaticas y paginas de inicio:
def inicio(request):
    return render (request, "staticPage/index.html")

def nosotros(request):
    return render (request, "staticPage/nosotros.html")


# Configurar logging
logger = logging.getLogger(__name__)

def contacto(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre', '').strip()
            email = request.POST.get('email', '').strip()
            mensaje = request.POST.get('mensaje', '').strip()
            
            print(f"DEBUG - Datos recibidos: nombre={nombre}, email={email}, mensaje={mensaje}")
            
            # Validaciones básicas
            if not all([nombre, email, mensaje]):
                return JsonResponse({
                    'success': False, 
                    'error': 'Todos los campos son obligatorios'
                })
            
            # Debug de configuración de email
            print(f"DEBUG - EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            print(f"DEBUG - EMAIL_HOST: {settings.EMAIL_HOST}")
            print(f"DEBUG - EMAIL_PORT: {settings.EMAIL_PORT}")
            print(f"DEBUG - EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
            
            # Enviar email al administrador
            admin_subject = f'Nuevo mensaje de contacto de {nombre}'
            admin_message = f'''
Has recibido un nuevo mensaje de contacto:

Nombre: {nombre}
Email: {email}
Mensaje: {mensaje}

---
Este mensaje fue enviado desde el formulario de contacto de ZainoAcademy.
            '''
            
            print("DEBUG - Intentando enviar email al administrador...")
            
            send_mail(
                subject=admin_subject,
                message=admin_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            
            print("DEBUG - Email al administrador enviado exitosamente")
            
            # Enviar email de confirmación al usuario
            user_subject = 'Hemos recibido tu mensaje - ZainoAcademy'
            user_message = f'''
Hola {nombre},

Hemos recibido tu mensaje y te contactaremos pronto.

Tu mensaje:
"{mensaje}"

Gracias por contactarnos.

Saludos,
Equipo ZainoAcademy
            '''
            
            print("DEBUG - Intentando enviar email de confirmación al usuario...")
            
            send_mail(
                subject=user_subject,
                message=user_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            
            print("DEBUG - Email de confirmación enviado exitosamente")
            
            return JsonResponse({
                'success': True, 
                'message': 'Mensaje enviado correctamente. Te contactaremos pronto.'
            })
            
        except Exception as e:
            # Log detallado del error
            error_msg = str(e)
            print(f"ERROR DETALLADO: {error_msg}")
            logger.error(f"Error enviando email: {error_msg}")
            
            # Diferentes tipos de errores comunes
            if "authentication" in error_msg.lower():
                return JsonResponse({
                    'success': False, 
                    'error': 'Error de autenticación con el servidor de correo'
                })
            elif "connection" in error_msg.lower():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se pudo conectar al servidor de correo'
                })
            elif "timeout" in error_msg.lower():
                return JsonResponse({
                    'success': False, 
                    'error': 'Tiempo de espera agotado. Inténtalo de nuevo.'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': f'Error técnico: {error_msg}'
                })
    
    return render(request, "staticPage/contacto.html")

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
                return redirect('dashboard_directivo')
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

def reset_password(request):
    exito = False  

    if request.method == "POST":
        correo = request.POST.get("correo")
        documento = request.POST.get("documento")
        nueva_contraseña = request.POST.get("new_password")
        confirmar_contraseña = request.POST.get("confirm_password")

        try:
            usuario = Usuario.objects.get(correo=correo, documento=documento)
        except Usuario.DoesNotExist:
            messages.error(request, "Correo o documento incorrecto.")
            return redirect("reset_password")

        if nueva_contraseña != confirmar_contraseña:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("reset_password")

        usuario.Us_contraseña = nueva_contraseña
        usuario.save()
        exito = True  

    return render(request, "registration/reset_password.html", {"exito": exito})

def dashboard_estudiantes(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    estudiante = get_object_or_404(Estudiantes, Usuario_us=usuario)

    cursos = Estudiante_Curso.objects.filter(Est=estudiante).select_related('Cur')
    curso_nombre = cursos[0].Cur.Cur_nombre if cursos.exists() else "Sin curso"

    boletines_qs = Boletin.objects.filter(
        Cur_id__in=cursos.values_list("Cur_id", flat=True)
    )

    actividades_qs = Actividad.objects.filter(Bol__in=boletines_qs).distinct()

    pendientes = []
    hoy = timezone.now().date()  

    for actividad in actividades_qs:
        if actividad.Act_fechaLimite >= hoy:
            entrega = Actividad_Entrega.objects.filter(Act=actividad, Est=estudiante).first()
            if not entrega or not entrega.archivos.exists():
                pendientes.append({
                    "actividad_obj": actividad,
                    "materia_obj": actividad.Bol.Mtr,
                    "periodo_obj": actividad.Bol.Per,
                    "estado": "Sin entregar"
                })

    pendientes_count = len(pendientes)

    return render(request, 'estudiantes/dashboard_estudiantes.html', {
        'usuario': usuario,
        'curso_nombre': curso_nombre,
        'pendientes': pendientes[:4],       
        'pendientes_count': pendientes_count, 
    })


def dashboard_directivos(request):
    usuario = get_usuario_from_session(request)

    # Traer las 5 matrículas más recientes
    matriculas_recientes = Matricula.objects.select_related("Estudiantes_Est", "Directivos_Dir")\
        .order_by('-Mat_fecha')[:5]

    return render(request, 'directivos/dashboard_directivos.html', {
        'usuario': usuario,
        'matriculas_recientes': matriculas_recientes
    })


def dashboard_directivos_calendar(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    # Aseguramos que fecha_registro no esté vacío
    if not usuario.fecha_registro:
        usuario.fecha_registro = date.today()
        usuario.save()

    today = date.today().isoformat()  # Para el input date

    return render(request, "directivos/dashboard_directivos.html", {
        "usuario": usuario,
        "today": today
    })

def editar_perfil_directivos(request):
    usuario = get_usuario_from_session(request)

    try:
        # Buscar el directivo asociado al usuario logueado
        directivo = Directivos.objects.get(Us=usuario)
    except Directivos.DoesNotExist:
        messages.error(request, "No se encontró el perfil de directivo asociado a este usuario.")
        return redirect("home")  # Ajusta la redirección a donde quieras enviar en caso de error

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        
        # Validar contraseña actual
        if current_password != usuario.Us_contraseña:  
            messages.error(request, "Contraseña actual incorrecta.")
            return redirect("editar_perfil_directivos")
        
        # Actualizar datos básicos
        usuario.Us_nombre = request.POST.get("username")
        usuario.correo = request.POST.get("email")

        # Actualizar contraseña si se proporciona una nueva
        new_password = request.POST.get("new_password")
        if new_password:
            usuario.Us_contraseña = new_password

        usuario.save()
        messages.success(request, "Perfil actualizado correctamente!")
        return redirect("editar_perfil_directivos")

    return render(request, 'directivos/editar_perfil_directivos.html', {
        'usuario': usuario,
        'directivo': directivo
    })

def ver_perfil_directivos(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'directivos/ver_perfil_directivos.html', {'usuario': usuario})

def dashboard_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/dashboard_acudientes.html', {'usuario': usuario})



# Vistas estudiantes:

def consultar_periodos(request):
    periodos = Periodo.objects.all().order_by('Per_id')
    return render(request, 'estudiantes/periodo_estudiantes.html', {'periodos': periodos})


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
    fecha_hoy = timezone.now().date()

    actividades_con_calificacion = []
    for actividad in actividades_qs:
        entrega = Actividad_Entrega.objects.filter(Act=actividad, Est=estudiante).first()
        fecha_vencida = actividad.Act_fechaLimite < fecha_hoy

        if not entrega or not entrega.archivos.exists():
            if fecha_vencida:
                estado = "Retrasado"
            else:
                estado = "Sin entregar"
        elif entrega.archivos.exists() and entrega.Act_calificacion is None:
            estado = "Entregado"
        elif entrega.Act_calificacion is not None:
            estado = "Calificado"

        actividades_con_calificacion.append({
            "actividad": actividad,
            "calificacion": entrega.Act_calificacion if entrega else None,
            "entrega": entrega,
            "estado": estado,
            "fecha_vencida": fecha_vencida
        })

    def ordenar(a):
        if a["estado"] == "Sin entregar" and not a["fecha_vencida"]:
            return 0
        elif a["estado"] == "Entregado" and not a["fecha_vencida"]:
            return 1
        elif a["estado"] == "Calificado":
            return 2
        elif a["estado"] == "Retrasado":
            return 3
        else:
            return 4

    actividades_con_calificacion.sort(key=ordenar)

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

    entrega, created = Actividad_Entrega.objects.get_or_create(
        Act=actividad,
        Est=estudiante
    )


    fecha_hoy = timezone.now().date()
    fecha_vencida = actividad.Act_fechaLimite < fecha_hoy 


    mensaje_exito = request.GET.get("mensaje", None)

    if request.method == "POST" and not fecha_vencida:
        eliminar_ids = request.POST.getlist("eliminar_archivo")
        if eliminar_ids:
            entrega.archivos.filter(id__in=eliminar_ids).delete()

        archivos = request.FILES.getlist("archivos_estudiante[]")
        if archivos:
            for archivo in archivos:
                Actividad_EntregaArchivo.objects.create(
                    entrega=entrega,
                    archivo=archivo
                )
            mensaje = "Actividad subida correctamente!"
        elif eliminar_ids:
            mensaje = "Archivos eliminados correctamente!"
        else:
            mensaje = None


        if mensaje:
            query_string = urlencode({'mensaje': mensaje})
            return redirect(f'/estudiantes/periodos/{Per_id}/materias/{Mtr_id}/actividad/{Act_id}/subir/?{query_string}')
        else:
            return redirect('subir_actividad_estudiante', Per_id=Per_id, Mtr_id=Mtr_id, Act_id=Act_id)

    return render(request, "estudiantes/actividad_estudiantes_subir.html", {
        "actividad": actividad,
        "materia": materia,
        "periodo": periodo,
        "entrega": entrega,
        "mensaje_exito": mensaje_exito,
        "fecha_vencida": fecha_vencida,
    })


def eliminar_archivo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            archivo_id = data.get("archivo_id")
            archivo = Actividad_EntregaArchivo.objects.get(pk=archivo_id)
            archivo.delete()
            return JsonResponse({"exito": True})
        except Actividad_EntregaArchivo.DoesNotExist:
            return JsonResponse({"exito": False, "error": "Archivo no encontrado"})
        except json.JSONDecodeError:
            return JsonResponse({"exito": False, "error": "Error al decodificar JSON"})
    return JsonResponse({"exito": False, "error": "Método no permitido"})


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

def consultar_reportes(request):
    periodos = Periodo.objects.all() 
    
    return render(request, 'estudiantes/reportes_estudiantes.html', {'periodos': periodos})

def reportes_estudiantes_descargar(request, Per_id):
    periodo = get_object_or_404(Periodo, pk=Per_id)


    context = {
        'periodo': periodo
    }

    return render(request, 'estudiantes/reportes_estudiantes_descargar.html', context)

def reporte_academico_pdf(request, periodo_id):
    periodo = get_object_or_404(Periodo, pk=periodo_id)

    usuario = get_usuario_from_session(request)
    estudiante = get_object_or_404(Estudiantes, Usuario_us=usuario)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="reporte_{estudiante.Usuario_us.Us_nombre}_{periodo.Per_nombre}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Reporte de Rendimiento Académico", styles['Title']))
    elements.append(Paragraph(f"Estudiante: {estudiante.Usuario_us.Us_nombre}", styles['Normal']))
    elements.append(Paragraph(f"Periodo: {periodo.Per_nombre}", styles['Normal']))
    elements.append(Spacer(1, 20))

    cursos = Estudiante_Curso.objects.filter(Est=estudiante).values_list("Cur", flat=True)
    boletines = Boletin.objects.filter(Per=periodo, Cur__in=cursos)

    for bol in boletines:
        elements.append(Paragraph(f"Curso - Materia: {bol.Cur.Cur_nombre} - {bol.Mtr.Mtr_nombre}", styles['Heading3']))

        actividades = Actividad.objects.filter(Bol=bol)
        data = [["Actividad", "Calificación", "Fecha Entrega"]]

        for act in actividades:
            entrega = Actividad_Entrega.objects.filter(Act=act, Est=estudiante).first()
            if entrega:
                calificacion = entrega.Act_calificacion if entrega.Act_calificacion is not None else "Sin calificar"
                fecha = entrega.Act_fecha_entrega.strftime("%d/%m/%Y")
                data.append([act.Act_nombre, calificacion, fecha])
            else:
                data.append([act.Act_nombre, "Sin entregas", "-"])

        table = Table(data, colWidths=[200, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e91d6")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

    doc.build(elements)

    return response


def editar_perfil_estudiantes(request):
    usuario = get_usuario_from_session(request)
    estudiante = Estudiantes.objects.get(Usuario_us=usuario)

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        
        if current_password != usuario.Us_contraseña:  
            messages.error(request, "Contraseña actual incorrecta.")
            return redirect("editar_perfil_estudiantes")
        
        usuario.Us_nombre = request.POST.get("username")
        usuario.correo = request.POST.get("email")

        new_password = request.POST.get("new_password")
        if new_password:
            usuario.Us_contraseña = new_password

        usuario.save()
        messages.success(request, "Perfil actualizado correctamente!")
        return redirect("editar_perfil_estudiantes")

    return render(request, 'estudiantes/editar_perfil_estudiantes.html', {'usuario': usuario})

def ver_perfil_estudiantes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'estudiantes/ver_perfil_estudiantes.html', {'usuario': usuario})


# Vistas Profesores:

def dashboard_profesores(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    profesor = usuario.profesores_set.first()
    hoy = timezone.localdate()

    actividades_abiertas = (
        Actividad.objects
        .filter(Bol__Pro=profesor, Act_fechaLimite__gte=hoy) 
        .annotate(total_entregas=Count('entregas'))
        .order_by('Act_fechaLimite')
    )

    return render(request, 'profesores/dashboard_profesores.html', {
        'usuario': usuario,
        'actividades_abiertas': actividades_abiertas,
    })

def ver_perfil_profesores(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'profesores/ver_perfil_profesores.html', {'usuario': usuario})

def actividad_profesores_calificaciones(request, act_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    actividad = get_object_or_404(Actividad, Act_id=act_id)

    try:
        profesor = Profesores.objects.get(Us=usuario)
    except Profesores.DoesNotExist:
        messages.error(request, "No tienes permisos de profesor.")
        return redirect('dashboard_profesores')

    entregas = Actividad_Entrega.objects.filter(Act=actividad).select_related("Est")
    for entrega in entregas:
        entrega.archivos_lista = Actividad_EntregaArchivo.objects.filter(entrega=entrega)

    if request.method == "POST":
        for entrega in entregas:
            calificacion = request.POST.get(f"calificacion_{entrega.id}")
            if calificacion:
                entrega.Act_calificacion = float(calificacion)
                entrega.save()
        messages.success(request, "Calificaciones guardadas correctamente.")
        return redirect(
            "actividad_profesores_consultar_cursos",
            periodo_id=actividad.Bol.Per.Per_id
        )

    estudiantes = Estudiantes.objects.filter(
        estudiante_curso__Cur=actividad.Bol.Cur
    ).distinct()

    context = {
        "actividad": actividad,
        "entregas": entregas,
        "usuario": usuario,
        "estudiantes": estudiantes,
        "curso": actividad.Bol.Cur,
        "materia": actividad.Bol.Mtr,
        "periodo_id": actividad.Bol.Per.Per_id,
    }
    return render(request, "profesores/actividades_por_curso_materia.html", context)

def actividades_por_curso_materia(request, bol_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    boletin = get_object_or_404(Boletin, Bol_id=bol_id)  

    curso = boletin.Cur
    materia = boletin.Mtr

    estudiantes_curso = Estudiantes.objects.filter(
        estudiante_curso__Cur=curso
    ).distinct()

    actividades = Actividad.objects.filter(Bol=boletin)

    entregas = Actividad_Entrega.objects.filter(
        Act__in=actividades,
        Est__in=estudiantes_curso
    ).select_related('Est', 'Act')

    return render(request, 'profesores/actividades_por_curso_materia.html', {
        'usuario': usuario,
        'curso': curso,
        'materia': materia,
        'actividades': actividades,
        'entregas': entregas,
        'estudiantes': estudiantes_curso,
        "periodo_id": boletin.Per_id,
    })



def guardar_calificaciones(request, bol_id):
    if request.method == "POST":
        bol = get_object_or_404(Boletin, Bol_id=bol_id)

        # obtenemos todas las entregas de ese boletín
        entregas_archivos = Actividad_EntregaArchivo.objects.filter(
            entrega__Act__Bol=bol
        ).select_related("entrega")

        for archivo_entrega in entregas_archivos:
            entrega = archivo_entrega.entrega
            # el input tiene el formato: calificacion_<id de la entrega>
            calificacion_key = f"calificacion_{entrega.id}"
            calificacion_valor = request.POST.get(calificacion_key)

            if calificacion_valor:
                try:
                    calificacion_valor = float(calificacion_valor)
                    # guardamos la nota en el objeto entrega (no en el archivo)
                    entrega.Act_calificacion = calificacion_valor
                    entrega.save()
                except ValueError:
                    continue  # si no es número, lo ignoramos

        messages.success(request, "✅ Calificaciones guardadas correctamente.")
        return redirect("actividad_profesores_consultar_cursos", periodo_id=bol.Per.Per_id)

    messages.error(request, "Método no permitido.")
    return redirect("dashboard_profesores")


def actividad_profesores_consultar_cursos(request, periodo_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    profesor = usuario.profesores_set.first()

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

    periodos = Periodo.objects.all()

    return render(request, 'profesores/actividad_profesores_consultar.html', {
        'usuario': usuario,
        'periodos': periodos
    })


def actividad_profesores_crear_actividad(request, bol_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario_custom = Usuario.objects.get(pk=usuario_id)
        profesor = Profesores.objects.get(Us_id=usuario_custom.Us_id)
    except (Usuario.DoesNotExist, Profesores.DoesNotExist):
        messages.error(request, "No se encontró información del profesor")
        return redirect('dashboard_profesores')
    
    boletin = get_object_or_404(Boletin, pk=bol_id, Pro_id=profesor.Pro_id)
    
    actividades = Actividad.objects.filter(Bol=boletin).select_related('Esta_Actividad')
    
    if request.method == 'POST':
        try:
            estado_pendiente = Estado_Actividad.objects.get(Esta_Actividad_Estado='Pendiente')
            
            
            Actividad.objects.create(
                Act_nombre=request.POST.get('Act_nombre'),
                Act_descripcion=request.POST.get('Act_descripcion'),
                Act_fechaLimite=request.POST.get('Act_fechaLimite'),
                Act_comentario=request.POST.get('Act_comentario', ''),
                Act_Archivo_Profesor=request.FILES.get('Act_Archivo_Profesor'),
                Bol=boletin,
                Esta_Actividad=estado_pendiente
            )
            
            messages.success(request, "Actividad creada exitosamente")
            # 👇 cambio importante: redirigir al dashboard
            return redirect('dashboard_profesores')
        except Exception as e:
            messages.error(request, f"Error al crear actividad: {str(e)}")
    
    context = {
        'boletin': boletin,
        'actividades': actividades,
        'usuario': usuario_custom
    }
    
    return render(request, 'profesores/actividad_profesores_crear_actividad.html', context)


def actividad_profesores_editar(request, act_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario_custom = Usuario.objects.get(pk=usuario_id)
        profesor = Profesores.objects.get(Us_id=usuario_custom.Us_id)
    except (Usuario.DoesNotExist, Profesores.DoesNotExist):
        messages.error(request, "No se encontró información del profesor")
        return redirect('dashboard_profesores')
    
    actividad = get_object_or_404(Actividad, pk=act_id, Bol__Pro_id=profesor.Pro_id)

    if request.method == 'POST':
        actividad.Act_nombre = request.POST.get('Act_nombre')
        actividad.Act_descripcion = request.POST.get('Act_descripcion')
        actividad.Act_fechaLimite = request.POST.get('Act_fechaLimite')
        actividad.Act_comentario = request.POST.get('Act_comentario', '')
        if request.FILES.get('Act_Archivo_Profesor'):
            actividad.Act_Archivo_Profesor = request.FILES.get('Act_Archivo_Profesor')
        
        actividad.save()
        messages.success(request, "Actividad actualizada exitosamente")
        return redirect('actividad_profesores_crear_actividad', bol_id=actividad.Bol.pk)

    context = {
        'actividad': actividad
    }
    return render(request, 'profesores/actividad_profesores_editar.html', context)

def actividad_profesores_eliminar(request, act_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario_custom = Usuario.objects.get(pk=usuario_id)
        profesor = Profesores.objects.get(Us_id=usuario_custom.Us_id)
    except (Usuario.DoesNotExist, Profesores.DoesNotExist):
        messages.error(request, "No se encontró información del profesor")
        return redirect('dashboard_profesores')
    
    actividad = get_object_or_404(Actividad, pk=act_id, Bol__Pro_id=profesor.Pro_id)
    bol_id = actividad.Bol.pk
    actividad.delete()
    messages.success(request, "Actividad eliminada exitosamente")
    return redirect('actividad_profesores_crear_actividad', bol_id=bol_id)


def actividad_profesores_lista(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    profesor = usuario.profesores_set.first()

    actividades = Actividad.objects.filter(Bol__Pro=profesor)

    return render(request, 'profesores/actividad_profesores_lista.html', {
        'usuario': usuario,
        'actividades': actividades
    })

def asistencia_profesores_añadir(request, bol_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    boletin = get_object_or_404(Boletin, Bol_id=bol_id)
    estudiantes_curso = Estudiante_Curso.objects.filter(
        Cur=boletin.Cur
    ).select_related("Est__Usuario_us")

    estados = Estado_Asistencia.objects.all()

    if request.method == 'POST':
        for ec in estudiantes_curso:
            estado_nombre = request.POST.get(f'estado_{ec.Est.Est_id}')
            comentario = request.POST.get(f'comentario_{ec.Est.Est_id}', "")

            if estado_nombre:
                estado_obj, _ = Estado_Asistencia.objects.get_or_create(
                    Esta_Asistencia_Estado=estado_nombre
                )

                asistencia = Asistencia.objects.create(
                    Ast_fecha=date.today(),
                    Est_Cur=ec,
                    Esta_Asistencia=estado_obj
                )

                if comentario.strip():
                    if "comentarios" not in request.session:
                        request.session["comentarios"] = {}
                    request.session["comentarios"][str(asistencia.Ast_id)] = comentario
                    request.session.modified = True

        return redirect('asistencia_profesores_consultar', bol_id=boletin.Bol_id)

    return render(request, 'profesores/asistencia_profesores_añadir.html', {
        'usuario': usuario,
        'boletin': boletin,
        'estudiantes_curso': estudiantes_curso,
        'estados': estados
    })

def asistencia_profesores_consultar(request, bol_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    boletin = get_object_or_404(Boletin, Bol_id=bol_id)
    estudiantes_curso = Estudiante_Curso.objects.filter(
        Cur=boletin.Cur
    ).select_related("Est__Usuario_us")

    asistencias = Asistencia.objects.filter(
        Est_Cur__in=estudiantes_curso
    ).select_related("Est_Cur__Est__Usuario_us", "Esta_Asistencia").order_by("Ast_fecha")

    comentarios_session = request.session.get("comentarios", {})

    if request.method == "POST":
        if "editar" in request.POST:
            ast_id = request.POST.get("asistencia_id")
            estado_nombre = request.POST.get("estado")
            comentario = request.POST.get("comentario", "")

            asistencia = get_object_or_404(Asistencia, Ast_id=ast_id)
            if estado_nombre:
                estado_obj = Estado_Asistencia.objects.get(Esta_Asistencia_Estado=estado_nombre)
                asistencia.Esta_Asistencia = estado_obj
                asistencia.Ast_fecha = date.today()
                asistencia.save()

            if comentario.strip():
                comentarios_session[str(asistencia.Ast_id)] = comentario
            else:
                comentarios_session.pop(str(asistencia.Ast_id), None)
            request.session["comentarios"] = comentarios_session
            request.session.modified = True

            return redirect("asistencia_profesores_consultar", bol_id=bol_id)

        if "eliminar" in request.POST:
            ast_id = request.POST.get("asistencia_id")
            asistencia = get_object_or_404(Asistencia, Ast_id=ast_id)
            asistencia.delete()
            comentarios_session.pop(str(ast_id), None)
            request.session["comentarios"] = comentarios_session
            request.session.modified = True
            return redirect("asistencia_profesores_consultar", bol_id=bol_id)

    asistencias_dict = defaultdict(dict)
    fechas = sorted(set(a.Ast_fecha for a in asistencias))

    for a in asistencias:
        estudiante = a.Est_Cur.Est.Usuario_us.Us_nombre
        comentario = comentarios_session.get(str(a.Ast_id), "")
        asistencias_dict[estudiante][a.Ast_fecha] = {
            "estado": a.Esta_Asistencia.Esta_Asistencia_Estado,
            "comentario": comentario
        }

    tabla_asistencias = []
    for ec in estudiantes_curso:
        fila = {"estudiante": ec.Est.Usuario_us.Us_nombre, "fechas": []}
        for f in fechas:
            datos = asistencias_dict.get(ec.Est.Usuario_us.Us_nombre, {}).get(f)
            fila["fechas"].append(datos)
        tabla_asistencias.append(fila)

    estados = Estado_Asistencia.objects.all()

    return render(request, "profesores/asistencia_profesores_consultar.html", {
        "usuario": usuario,
        "boletin": boletin,
        "tabla_asistencias": tabla_asistencias,
        "fechas": fechas,
        "estados": estados
    })


def lista_actividades_calificar(request, curso_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')
        
    curso = get_object_or_404(Curso, Cur_id=curso_id)
    
    try:
        profesor = Profesores.objects.get(Us=usuario)
    except Profesores.DoesNotExist:
        messages.error(request, "No tienes permisos de profesor.")
        return redirect('dashboard_profesores')
    
    actividades = Actividad.objects.filter(
        Bol__Pro=profesor,
        Bol__Cur=curso
    ).order_by('-Act_fechaLimite')
    
    # Obtener el periodo_id desde cualquier boletín del profesor y curso
    periodo_id = None
    boletin = Boletin.objects.filter(Pro=profesor, Cur=curso).first()
    if boletin:
        periodo_id = boletin.Per.Per_id
    
    for actividad in actividades:
        total_estudiantes = Estudiantes.objects.filter(
            estudiante_curso__Cur=curso
        ).distinct().count()
        
        # Conteo de entregas basado en Actividad_EntregaArchivo
        total_entregas = Actividad_EntregaArchivo.objects.filter(
            entrega__Act=actividad
        ).values('entrega').distinct().count()
        
        actividad.total_estudiantes = total_estudiantes
        actividad.total_entregas = total_entregas
    
    context = {
        'curso': curso,
        'actividades': actividades,
        'usuario': usuario,
        'periodo_id': periodo_id,
    }
    return render(request, 'profesores/lista_actividades_calificar.html', context)





def asistencia_profesores_cursos(request, periodo_id=None):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    profesor = usuario.profesores_set.first()
    periodos = Periodo.objects.all()

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
    for m in materiales:
        print(m.__dict__)
    boletin = Boletin.objects.get(Bol_id=bol_id)
    periodo_id = boletin.Per_id

    return render(request, "profesores/materialApoyo_consultar.html", {
        "materiales": materiales,
        "bol_id": bol_id,
        "periodo_id": periodo_id,
    })

def materialApoyo_editar(request, Mate_id):
    material = get_object_or_404(MaterialApoyo, Mate_id=Mate_id)

    if request.method == 'POST':
        form = MaterialApoyoForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Material actualizado exitosamente.')
                return redirect('materialApoyo_consultar', bol_id=material.Bol.Bol_id)
            except Exception as e:
                messages.error(request, f'Error al actualizar el material: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = MaterialApoyoForm(instance=material)

    context = {
        'form': form,
        'material': material,
        'boletin': material.Bol,
        'usuario': request.user
    }
    return render(request, 'profesores/materialApoyo_editar.html', context)

def materialApoyo_eliminar(request, Mate_id):
    material = get_object_or_404(MaterialApoyo, Mate_id=Mate_id)
    bol_id = material.Bol.Bol_id

    if request.method == 'POST':
        try:
            material.delete()
            messages.success(request, 'Material eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el material: {str(e)}')

    return redirect('materialApoyo_consultar', bol_id=bol_id)

def materialApoyo_confirmar_eliminar(request, Mate_id):
    material = get_object_or_404(MaterialApoyo, Mate_id=Mate_id)

    if request.method == 'POST':
        bol_id = material.Bol.Bol_id
        material.delete()
        messages.success(request, 'Material eliminado exitosamente.')
        return redirect('materialApoyo_consultar', bol_id=bol_id)

    context = {
        'material': material,
        'boletin': material.Bol,
        'usuario': request.user
    }

    return render(request, 'profesores/materialApoyo_confirmar_eliminar.html', context)

def notificaciones_profesores(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'profesores/notificaciones_profesores.html', {'usuario': usuario})

def reportes_profesores_descargar(request, periodo_id):
  usuario = get_usuario_from_session(request)
  if not usuario:
    return redirect('login')
  periodo = get_object_or_404(Periodo, Per_id=periodo_id)
  return render(request, 'profesores/reportes_profesores_descargar.html', {
    'usuario': usuario,
    'periodo': periodo
  })

def reportes_profesores(request):
    usuario = get_usuario_from_session(request)
    
    periodos = Periodo.objects.all().order_by('Per_id')
    
    return render(request, 'profesores/reportes_profesores.html', {
        'usuario': usuario,
        'periodos': periodos, 
    })

def generar_reporte_asistencias_pdf(request, periodo_id):
    """Genera un PDF con el reporte de asistencias de un periodo específico."""
    usuario = get_usuario_from_session(request)

    if not usuario:
        return redirect('login')

    profesor = usuario.profesores_set.first()
    if not profesor:
        return HttpResponse("No se encontró información del profesor", status=400)
    
    periodo = get_object_or_404(Periodo, Per_id=periodo_id)

    boletines = Boletin.objects.filter(
        Pro=profesor,
        Per=periodo
    ).select_related('Per', 'Cur', 'Mtr')

    if not boletines.exists():
        messages.error(request, f"No hay datos de asistencias para el periodo '{periodo.Per_nombre}'.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Reporte de Asistencias", styles["Title"]))
    elements.append(Paragraph(f"Profesor: {usuario.Us_nombre}", styles["Normal"]))
    elements.append(Paragraph(f"Período: {periodo.Per_nombre}", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    for boletin in boletines:
        elements.append(Paragraph(f"Curso: {boletin.Cur.Cur_nombre} - Materia: {boletin.Mtr.Mtr_nombre}", styles["Heading3"]))
        estudiantes_curso = Estudiante_Curso.objects.filter(Cur=boletin.Cur).select_related("Est__Usuario_us")
        asistencias = Asistencia.objects.filter(
            Est_Cur__in=estudiantes_curso
        ).select_related("Est_Cur__Est__Usuario_us", "Esta_Asistencia").order_by("Ast_fecha")
        
        if asistencias.exists():
            data = [["Estudiante", "Fecha", "Estado"]]
            for asistencia in asistencias:
                data.append([
                    asistencia.Est_Cur.Est.Usuario_us.Us_nombre,
                    asistencia.Ast_fecha.strftime("%d/%m/%Y"),
                    asistencia.Esta_Asistencia.Esta_Asistencia_Estado
                ])
            
            table = Table(data, colWidths=[200, 100, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e91d6")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f9f9f9")),
                ('FONTSIZE', (0,1), (-1,-1), 9),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 15))
        else:
            elements.append(Paragraph("No hay registros de asistencia para este curso.", styles["Normal"]))
            elements.append(Spacer(1, 15))
    
    doc.build(elements)
    buffer.seek(0)
    
    response = FileResponse(
        buffer, 
        as_attachment=True, 
        filename=f"Reporte_Asistencias_{usuario.Us_nombre.replace(' ', '_')}_{periodo.Per_nombre.replace(' ', '_')}.pdf"
    )
    return response


def generar_reporte_rendimiento_pdf(request, periodo_id):
    """Genera un PDF con el reporte de rendimiento académico de un periodo específico."""
    usuario = get_usuario_from_session(request)

    if not usuario:
        return redirect('login')

    profesor = usuario.profesores_set.first()
    if not profesor:
        return HttpResponse("No se encontró información del profesor", status=400)
    
    periodo = get_object_or_404(Periodo, Per_id=periodo_id)

    actividades = Actividad.objects.filter(
        Bol__Pro=profesor,
        Bol__Per=periodo
    ).select_related('Bol__Per', 'Bol__Cur', 'Bol__Mtr').prefetch_related('entregas__Est__Usuario_us')

    # Validación principal: si no hay actividades (y por lo tanto datos) para este periodo
    if not actividades.exists():
        messages.error(request, f"No hay datos de rendimiento académico para el periodo '{periodo.Per_nombre}'.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # Si hay datos, procede a generar el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Reporte de Rendimiento Académico", styles["Title"]))
    elements.append(Paragraph(f"Profesor: {usuario.Us_nombre}", styles["Normal"]))
    elements.append(Paragraph(f"Período: {periodo.Per_nombre}", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    materias_cursos = {}
    for actividad in actividades:
        key = f"{actividad.Bol.Cur.Cur_nombre} - {actividad.Bol.Mtr.Mtr_nombre}"
        if key not in materias_cursos:
            materias_cursos[key] = []
        materias_cursos[key].append(actividad)
    
    for materia_curso, actividades_mc in materias_cursos.items():
        elements.append(Paragraph(f"Curso - Materia: {materia_curso}", styles["Heading3"]))
        data = [["Actividad", "Estudiante", "Calificación", "Fecha Entrega"]]
        
        has_deliveries = False
        for actividad in actividades_mc:
            entregas = actividad.entregas.all()
            if entregas:
                has_deliveries = True
                for entrega in entregas:
                    calificacion = str(entrega.Act_calificacion) if entrega.Act_calificacion else "Sin calificar"
                    fecha_entrega = entrega.Act_fecha_entrega.strftime("%d/%m/%Y") if entrega.Act_fecha_entrega else "No entregada"
                    data.append([
                        actividad.Act_nombre,
                        entrega.Est.Usuario_us.Us_nombre,
                        calificacion,
                        fecha_entrega
                    ])
            else:
                data.append([actividad.Act_nombre, "Sin entregas", "-", "-"])
        
        if len(data) > 1:
            table = Table(data, colWidths=[120, 120, 80, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e91d6")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f9f9f9")),
                ('FONTSIZE', (0,1), (-1,-1), 8),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 15))
        else:
            elements.append(Paragraph("No hay actividades registradas para esta materia.", styles["Normal"]))
            elements.append(Spacer(1, 15))
    
    doc.build(elements)
    buffer.seek(0)
    
    response = FileResponse(
        buffer, 
        as_attachment=True, 
        filename=f"Reporte_Rendimiento_{usuario.Us_nombre.replace(' ', '_')}_{periodo.Per_nombre.replace(' ', '_')}.pdf"
    )
    return response

def editar_perfil_profesores(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'profesores/editar_perfil_profesores.html', {'usuario': usuario})

@csrf_exempt
def actualizar_perfil_profesores(request):
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

def dashboard_profesores_calendar(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    # Aseguramos que fecha_registro no esté vacío
    if not usuario.fecha_registro:
        usuario.fecha_registro = date.today()
        usuario.save()

    today = date.today().isoformat()  # Para el input date

    return render(request, "profesores/dashboard_profesores.html", {
        "usuario": usuario,
        "today": today
    })


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
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')
    
    # Obtener el directivo basado en el usuario de la sesión
    try:
        directivo = Directivos.objects.get(Us=usuario)
    except Directivos.DoesNotExist:
        messages.error(request, 'No se encontró un directivo asociado a este usuario.')
        return redirect('lista_matriculas')
    
    if request.method == 'POST':
        form = MatriculaForm(request.POST, request.FILES)
        
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        print("Form is valid:", form.is_valid())
        
        if form.is_valid():
            try:
                # Guardar la matrícula sin hacer commit
                matricula = form.save(commit=False)
                # Asignar automáticamente el directivo de la sesión
                matricula.Directivos_Dir = directivo
                # Asignar automáticamente la fecha actual
                matricula.Mat_fecha = date.today()
                matricula.save()
                
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
    
    context = {
        'form': form,
        'usuario': usuario,
        'directivo': directivo,  # Pasar el directivo al contexto
        'estudiantes_count': Estudiantes.objects.count(),
    }
    
    return render(request, 'directivos/matricula.html', context)
def editar_matricula(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')
    
    # Obtener el directivo basado en el usuario de la sesión
    try:
        directivo = Directivos.objects.get(Us=usuario)
    except Directivos.DoesNotExist:
        messages.error(request, 'No se encontró un directivo asociado a este usuario.')
        return redirect('lista_matriculas')
    
    if request.method == 'POST':
        form = MatriculaForm(request.POST, request.FILES, instance=matricula)
        
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        print("Form is valid:", form.is_valid())
        
        if form.is_valid():
            try:
                # Guardar la matrícula sin hacer commit
                matricula_actualizada = form.save(commit=False)
                # Mantener el directivo actual (no permitir cambiarlo)
                # matricula_actualizada.Directivos_Dir = directivo  # Opcional: forzar directivo de sesión
                matricula_actualizada.save()
                
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
    
    context = {
        'form': form,
        'matricula': matricula,
        'usuario': usuario,
        'directivo': directivo,  # Pasar el directivo al contexto
        'estudiantes_count': Estudiantes.objects.count(),
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
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    try:
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)
        print(f"✅ Acudiente encontrado: {acudiente}")
    except Acudiente.DoesNotExist:
        print("❌ Acudiente no encontrado")
        return redirect('login')

    # Obtener estudiantes a cargo (ManyToMany)
    estudiantes_a_cargo = acudiente.Estudiantes_Est.all()
    print(f"👥 Estudiantes a cargo: {estudiantes_a_cargo.count()}")

    if not estudiantes_a_cargo.exists():
        return render(request, 'acudientes/dashboard_acudientes.html', {
            'usuario': usuario,
            'pendientes': []
        })

    pendientes = []

    for estudiante in estudiantes_a_cargo:
        print(f"\n🎓 Procesando estudiante: {estudiante.Usuario_us.Us_nombre}")

        # Obtener cursos del estudiante
        estudiante_cursos = Estudiante_Curso.objects.filter(Est=estudiante)
        print(f"📚 Estudiante_Curso encontrados: {estudiante_cursos.count()}")

        for est_cur in estudiante_cursos:
            boletines = Boletin.objects.filter(Cur=est_cur.Cur)
            print(f"  📋 Boletines en el curso: {boletines.count()}")

            for boletin in boletines:
                actividades = Actividad.objects.filter(Bol=boletin)
                print(f"    📌 Actividades en el boletín: {actividades.count()}")

                for actividad in actividades:
                    print(f"      🔍 Actividad: {actividad.Act_nombre}")

                    try:
                        entrega = Actividad_Entrega.objects.get(Act=actividad, Est=estudiante)

                        if not entrega.archivos.exists():  # usa related_name="archivos"
                            pendientes.append({
                                "actividad": actividad.Act_nombre,
                                "materia": boletin.Mtr.Mtr_nombre,
                                "estado": "Pendiente",
                                "estudiante": estudiante.Usuario_us.Us_nombre
                            })
                            print("      ⚠️ PENDIENTE: sin archivo")
                        else:
                            print("      ✅ COMPLETA: con archivo")

                    except Actividad_Entrega.DoesNotExist:
                        pendientes.append({
                            "actividad": actividad.Act_nombre,
                            "materia": boletin.Mtr.Mtr_nombre,
                            "estado": "Pendiente",
                            "estudiante": estudiante.Usuario_us.Us_nombre
                        })
                        print("      ❌ No hay entrega registrada")

    # Limitar a 4 elementos
    pendientes_limitadas = pendientes[:4]

    return render(request, 'acudientes/dashboard_acudientes.html', {
        'usuario': usuario,
        'pendientes': pendientes_limitadas
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
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)
        
        estudiantes_a_cargo = acudiente.Estudiantes_Est.all()
        
        context = {
            'usuario': usuario,
            'estudiantes_a_cargo': estudiantes_a_cargo,
        }
        
        return render(request, 'acudientes/actividades_acudientes.html', context)
        
    except Acudiente.DoesNotExist:
        context = {
            'usuario': usuario,
            'estudiantes_a_cargo': [],
        }
        return render(request, 'acudientes/actividades_acudientes.html', context)


def asistencia_acudientes(request):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    # Obtener el acudiente con sus estudiantes
    try:
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)
        estudiantes_a_cargo = acudiente.Estudiantes_Est.all()
    except Acudiente.DoesNotExist:
        estudiantes_a_cargo = []

    return render(request, 'acudientes/asistencia_acudientes.html', {
        'usuario': usuario,
        'estudiantes_a_cargo': estudiantes_a_cargo
    })

def notificaciones_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/notificaciones_acudientes.html', {'usuario': usuario})

def editar_perfil_acudientes(request):
    usuario = get_usuario_from_session(request)

    try:
        # Buscar el acudiente asociado al usuario logueado
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)
    except Acudiente.DoesNotExist:
        messages.error(request, "No se encontró el perfil de acudiente asociado a este usuario.")
        return redirect("home")  # Ajusta la redirección a donde quieras enviar en caso de error

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        
        # Validar contraseña actual
        if current_password != usuario.Us_contraseña:  
            messages.error(request, "Contraseña actual incorrecta.")
            return redirect("editar_perfil_acudientes")
        
        # Actualizar datos básicos
        usuario.Us_nombre = request.POST.get("username")
        usuario.correo = request.POST.get("email")

        # Actualizar contraseña si se proporciona una nueva
        new_password = request.POST.get("new_password")
        if new_password:
            usuario.Us_contraseña = new_password

        usuario.save()
        messages.success(request, "Perfil actualizado correctamente!")
        return redirect("editar_perfil_acudientes")

    return render(request, 'acudientes/editar_perfil_acudientes.html', {
        'usuario': usuario,
        'acudiente': acudiente
    })

def ver_perfil_acudientes(request):
    usuario = get_usuario_from_session(request)
    return render(request, 'acudientes/ver_perfil_acudientes.html', {'usuario': usuario})

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

    try:
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)
        estudiantes = acudiente.Estudiantes_Est.all()
    except Acudiente.DoesNotExist:
        estudiantes = []

    periodos = Periodo.objects.all()  # 👈 para listar
    return render(request, 'acudientes/asistencia_list_acudientes.html', {
        'usuario': usuario,
        'estudiantes': estudiantes,
        'periodos': periodos,
    })

def generar_reporte_asistencia_acudientes_pdf(request, periodo_id):
    usuario = get_usuario_from_session(request)
    if not usuario:
        return redirect('login')

    try:
        acudiente = Acudiente.objects.get(Usuario_Us=usuario)
        estudiantes = acudiente.Estudiantes_Est.all()
    except Acudiente.DoesNotExist:
        return HttpResponse("No se encontró información de acudiente", status=400)

    periodo = get_object_or_404(Periodo, Per_id=periodo_id)

    # Buscar cursos de los estudiantes
    cursos = Estudiante_Curso.objects.filter(Est__in=estudiantes).select_related("Cur")

    asistencias = Asistencia.objects.filter(
        Est_Cur__in=cursos
    ).select_related("Est_Cur__Est__Usuario_us", "Esta_Asistencia").order_by("Ast_fecha")

    if not asistencias.exists():
        messages.error(request, f"No hay datos de asistencias para el periodo '{periodo.Per_nombre}'.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Reporte de Asistencias - Acudiente", styles["Title"]))
    elements.append(Paragraph(f"Acudiente: {usuario.Us_nombre}", styles["Normal"]))
    elements.append(Paragraph(f"Período: {periodo.Per_nombre}", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    data = [["Estudiante", "Fecha", "Estado"]]
    for asistencia in asistencias:
        data.append([
            asistencia.Est_Cur.Est.Usuario_us.Us_nombre,
            asistencia.Ast_fecha.strftime("%d/%m/%Y"),
            asistencia.Esta_Asistencia.Esta_Asistencia_Estado
        ])

    table = Table(data, colWidths=[200, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e91d6")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = FileResponse(
        buffer,
        as_attachment=True,
        filename=f"Asistencia_{usuario.Us_nombre}_{periodo.Per_nombre}.pdf"
    )
    return response


