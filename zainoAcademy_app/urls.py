#
# Nombre del archivo: urls.py 
# Descripción: Este archivo realiza la conexion entre los templates con las vistas
# Autor: Stefany Danciela Abril Samaca
# Fecha de creación: 2025-02-02 
# # Última modificación: 2025-09-04
#NOTAS: 

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.inicio, name='home'),
    path('nosotros/',views.nosotros, name='nosotros'),
    path('contacto/',views.contacto, name='contacto'),
    path('precios/',views.precios, name='precios'),
    path('login/', views.login_view, name='login'),

    # Dashboards
    path('estudiantes/', views.dashboard_estudiantes, name='dashboard_estudiantes'),
    path('profesores/', views.dashboard_profesores, name='dashboard_profesores'),
    path('directivos/', views.dashboard_directivos, name='dashboard_directivos'),
    path('acudientes/', views.dashboard_acudientes, name='dashboard_acudientes'),

    # Acudientes
    path('acudientes/actividades/', views.actividades_acudientes, name='actividades_acudientes'),
    path('acudientes/asistencia/', views.asistencia_acudientes, name='asistencia_acudientes'),
    path('acudientes/notificaciones/', views.notificaciones_acudientes, name='notificaciones_acudientes'),
    path('acudientes/editar_perfil/', views.editar_perfil_acudientes, name='editar_perfil_acudientes'),
    path('acudientes/actualizar_perfil/', views.actualizar_perfil_acudientes, name='actualizar_perfil_acudientes'),
    path('acudientes/dashboard_acudientes/', views.dashboard_acudientes_calendar, name="dashboard_acudientes"),
    path('acudientes/actividades_list/', views.actividades_list_acudientes, name='actividades_list_acudientes'),
    path('acudientes/asistencia_list/', views.asistencia_list_acudientes, name='asistencia_list_acudientes'),
    path('asistencia/pdf/', views.asistencia_pdf_acudientes, name='asistencia_pdf_acudientes'),

    #Estudiantes

    path('estudiantes/periodos/', views.consultar_periodos , name='consultar_periodos'),
    path('estudiantes/reportes/', views.consultar_reportes , name='consultar_reportes'),
    path('estudiantes/periodos/<int:Per_id>/', views.materias_estudiantes, name='materias_estudiante'), # Per_id, ese "periodo" es la variable que definí en mi template
    path('estudiantes/periodos/<int:Per_id>/materias/<int:Mtr_id>/', views.actividades_estudiantes, name='actividades_estudiantes'),
    path("estudiantes/periodos/<int:Per_id>/materias/<int:Mtr_id>/actividad/<int:Act_id>/subir/", views.subir_actividad_estudiante, name="subir_actividad_estudiante"),
    path("estudiantes/periodos/<int:Per_id>/materias/<int:Mtr_id>/materiales/", views.materiales_apoyo_estudiantes,name="materiales_apoyo_estudiantes"),
    path('estudiantes/reportes/descargar/<int:Per_id>/',views.reportes_estudiantes_descargar,name='reportes_estudiantes_descargar'),
    path("estudiantes/reportes/<int:periodo_id>/", views.reporte_academico_pdf, name="reporte_academico_pdf"),
    path('estudiantes/editar_perfil/', views.editar_perfil_estudiantes, name='editar_perfil_estudiantes'),
    path('perfil/', views.ver_perfil_estudiantes, name='ver_perfil_estudiantes'),
    path('eliminar-archivo/', views.eliminar_archivo, name='eliminar_archivo'),

    # Acudientes
    path('acudientes/actividades/', views.actividades_acudientes, name='actividades_acudientes'),
    path('acudientes/asistencia/', views.asistencia_acudientes, name='asistencia_acudientes'),
    path('acudientes/notificaciones/', views.notificaciones_acudientes, name='notificaciones_acudientes'),
    path('acudientes/editar_perfil/', views.editar_perfil_acudientes, name='editar_perfil_acudientes'),
    path('acudientes/actualizar_perfil/', views.actualizar_perfil_acudientes, name='actualizar_perfil_acudientes'),


    # Profesores:

    path('profesores/actividades/crear/<int:bol_id>/', views.actividad_profesores_crear_actividad, name='actividad_profesores_crear_actividad'),
    path('profesores/actividades/lista/', views.actividad_profesores_lista, name='actividad_profesores_lista'),
    path('profesores/actividades/consultar/', views.actividad_profesores_consultar, name='actividad_profesores_consultar'),
    path('profesores/actividades/cursos/<int:periodo_id>/', views.actividad_profesores_consultar_cursos, name='actividad_profesores_consultar_cursos'),
    path('profesores/asistencia/cursos/', views.asistencia_profesores_cursos, name='asistencia_profesores_cursos'),
    path("profesores/asistencia/cursos/<int:periodo_id>/", views.asistencia_profesores_cursos, name="asistencia_profesores_cursos_periodo"),
    path('profesores/asistencia/consultar/<int:bol_id>/', views.asistencia_profesores_consultar, name='asistencia_profesores_consultar'),
    path('profesores/asistencia/añadir/<int:bol_id>/', views.asistencia_profesores_añadir, name='asistencia_profesores_añadir'),
    path('profesores/actividades/calificaciones/',views.actividad_profesores_calificaciones, name="actividad_profesores_calificaciones"),
    path('profesores/materialApoyo/subir/<int:bol_id>/', views.materialApoyo_subir, name='materialApoyo_subir'),
    path('profesores/materialApoyo/consultar/<int:bol_id>/', views.materialApoyo_consultar, name='materialApoyo_consultar'),
    path('profesores/reportes/', views.reportes_profesores, name='reportes_profesores'),
    path('profesores/reportes/descargar/', views.reportes_profesores_descargar, name='reportes_profesores_descargar'),
    path('profesores/notificaciones/', views.notificaciones_profesores, name='notificaciones_profesores'),


    #Directivos
    path('directivos/',views.dashboard_directivos, name='dashboard_directivo'),
    path('dirrectivos/notificaciones/',views.notificaciones_directivos, name='notificaciones_directivos'),
    path('dirrectivos/periodo/',views.periodo_crear_directivos, name='periodo_directivos'),

    #Directivos Usuarios:
    path('usuario/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuario/', views.lista_usuarios, name='lista_usuarios'),
    path('usuario/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:usuario_id>/crear-estudiante/', views.crear_estudiante, name='crear_estudiante'),
    path('usuarios/<int:usuario_id>/crear-directivo/', views.crear_directivo, name='crear_directivo'),
    path('usuarios/<int:usuario_id>/crear-acudiente/', views.crear_acudiente, name='crear_acudiente'),
    path('crear_acudiente_con_estudiantes/', views.crear_acudiente_con_estudiantes, name='crear_acudiente_con_estudiantes'),
    path('usuario/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),

    #Directivos Matricula
    path('matricula/', views.lista_matriculas, name='lista_matriculas'),
    path('matricula/crear/', views.crear_matricula, name='crear_matricula'),
    path('matricula/eliminar/<int:pk>/', views.eliminar_matricula, name='eliminar_matricula'),
    path('matricula/editar/<int:pk>/', views.editar_matricula, name='editar_matricula'),

#Direcitvos Curso
    path("curso/", views.crear_curso, name="crear_curso"),
    path("curso/crear/", views.crear_curso_con_estudiantes, name="crear_curso_con_estudiantes"),
    path('curso/lista/', views.lista_cursos, name='lista_cursos'),
    path('curso/editar/<int:id>/', views.editar_curso, name='editar_curso'),
    path('curso/eliminar/<int:id>/', views.eliminar_curso, name='eliminar_curso'),
    path("curso/buscar-estudiantes/", views.buscar_estudiantes, name="buscar_estudiantes"),
    path('curso/actualizar/<int:curso_id>/', views.actualizar_curso_con_estudiantes, name='actualizar_curso_con_estudiantes'),
    path('curso/<int:curso_id>/estudiantes/', views.obtener_estudiantes_curso, name='obtener_estudiantes_curso'),
    path('buscar_estudiantes/', views.buscar_estudiantes, name='buscar_estudiantes'),
    path('crear_curso_con_estudiantes/', views.crear_curso_con_estudiantes, name='crear_curso_con_estudiantes'),

#Directivos Materia
    path('materia/', views.crear_materia, name='crear_materia'),
    path('materia/lista/', views.lista_materias, name='lista_materias'),
    path('materia/editar/<int:id>/', views.editar_materia, name='editar_materia'),
    path('materia/eliminar/<int:id>/', views.eliminar_materia, name='eliminar_materia'),

#Directivos Periodo
path('dirrectivos/periodo/', views.periodo_crear_directivos, name='periodo_directivos'),
path('dirrectivos/periodo/consultar/', views.periodo_consultar_directivos, name='periodo_directivos_consultar'),
path('directivos/periodo/editar/<int:id>/', views.editar_periodo, name='editar_periodo'),
path('directivos/periodo/eliminar/<int:id>/', views.eliminar_periodo, name='eliminar_periodo'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)