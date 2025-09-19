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
    path('acudientes/perfil/', views.ver_perfil_acudientes, name='ver_perfil_acudientes'),
    path('acudientes/dashboard_acudientes/', views.dashboard_acudientes_calendar, name="dashboard_acudientes"),
    path('acudientes/actividades_list/', views.actividades_list_acudientes, name='actividades_list_acudientes'),
    path('acudientes/asistencia_list/', views.asistencia_list_acudientes, name='asistencia_list_acudientes'),
    path("acudientes/asistencia/reporte/<int:periodo_id>/", views.generar_reporte_asistencia_acudientes_pdf, name="reporte_asistencia_acudientes"),

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
    path('cambiar_contraseña/', views.reset_password, name='reset_password'),


    #Profesores
    path('profesores/actividades/crear/<int:bol_id>/', views.actividad_profesores_crear_actividad, name='actividad_profesores_crear_actividad'),
    path('profesores/perfil/', views.ver_perfil_profesores, name='ver_perfil_profesores'),
    path('profesores/actividades/lista/', views.actividad_profesores_lista, name='actividad_profesores_lista'),
    path('profesores/actividades/consultar/', views.actividad_profesores_consultar, name='actividad_profesores_consultar'),
    path('profesores/actividades/cursos/<int:periodo_id>/', views.actividad_profesores_consultar_cursos, name='actividad_profesores_consultar_cursos'),
    path("profesores/asistencia/cursos/", views.asistencia_profesores_cursos, name="asistencia_profesores_cursos"),
    path("profesores/asistencia/cursos/<int:periodo_id>/", views.asistencia_profesores_cursos_periodo, name="asistencia_profesores_cursos_periodo"),
    path('profesores/asistencia/consultar/<int:bol_id>/', views.asistencia_profesores_consultar, name='asistencia_profesores_consultar'),
    path('profesores/asistencia/añadir/<int:bol_id>/', views.asistencia_profesores_añadir, name='asistencia_profesores_añadir'),
    path("profesores/actividades/guardar/<int:bol_id>/", views.guardar_calificaciones, name="guardar_calificaciones"),
    path('profesores/actividades/cursos/<int:periodo_id>/',views.actividad_profesores_consultar_cursos,name='actividad_profesores_consultar_cursos'),
    path('profesores/actividades/calificaciones/<int:act_id>/', views.actividad_profesores_calificaciones, name='actividad_profesores_calificaciones'),
    path('profesores/actividades/calificaciones/curso/<int:bol_id>/', views.actividades_por_curso_materia, name='actividades_por_curso_materia'),
    path('profesores/materialApoyo/subir/<int:bol_id>/', views.materialApoyo_subir, name='materialApoyo_subir'),
    path('profesores/materialApoyo/consultar/<int:bol_id>/', views.materialApoyo_consultar, name='materialApoyo_consultar'),
    path("profesores/materialApoyo/editar/<int:Mate_id>/", views.materialApoyo_editar, name="materialApoyo_editar"),
    path('profesores/materialApoyo/eliminar/<int:Mate_id>/', views.materialApoyo_eliminar, name='materialApoyo_eliminar'),
    path('profesores/materialApoyo/confirmar-eliminar/<int:id>/', views.materialApoyo_confirmar_eliminar, name='materialApoyo_confirmar_eliminar'),
    path('profesores/reportes/', views.reportes_profesores, name='reportes_profesores'),
    path('profesores/reportes/descargar/<int:periodo_id>/', views.reportes_profesores_descargar, name='reportes_profesores_descargar'),
    path('profesores/reportes/asistencias/pdf/<int:periodo_id>/', views.generar_reporte_asistencias_pdf, name='reporte_asistencias_pdf'),
    path('profesores/reportes/rendimiento/pdf/<int:periodo_id>/', views.generar_reporte_rendimiento_pdf, name='reporte_rendimiento_pdf'),
    path('profesores/notificaciones/', views.notificaciones_profesores, name='notificaciones_profesores'),
    path('profesores/actividades/editar/<int:act_id>/', views.actividad_profesores_editar, name='actividad_profesores_editar'),
    path('profesores/actividades/eliminar/<int:act_id>/', views.actividad_profesores_eliminar, name='actividad_profesores_eliminar'),
    path('materialApoyo/consultar/<int:bol_id>/', views.materialApoyo_consultar, name='materialApoyo_consultar'),
    path('materialApoyo/editar/<int:Mate_id>/', views.materialApoyo_editar, name='materialApoyo_editar'),
    path('materialApoyo/eliminar/<int:Mate_id>/', views.materialApoyo_eliminar, name='materialApoyo_eliminar'),
    path('materialApoyo/confirmar_eliminar/<int:Mate_id>/', views.materialApoyo_confirmar_eliminar, name='materialApoyo_confirmar_eliminar'),
    path('profesores/actividades/calificar/<int:curso_id>/', views.lista_actividades_calificar, name='lista_actividades_calificar'),


    path('profesores/editar_perfil/', views.editar_perfil_profesores, name='editar_perfil_profesores'),

    
    path('profesores/actualizar_perfil/', views.actualizar_perfil_profesores, name='actualizar_perfil_profesores'),
    path('profesores/dashboard_profesores/', views.dashboard_profesores_calendar, name="dashboard_profesores"),

    #Directivos
    path('directivos/',views.dashboard_directivos, name='dashboard_directivo'),
    path('dirrectivos/notificaciones/',views.notificaciones_directivos, name='notificaciones_directivos'),
    path('dirrectivos/periodo/',views.periodo_crear_directivos, name='periodo_directivos'),
    path('directivos/dashboard_directivos/', views.dashboard_directivos_calendar, name="dashboard_directivos"),
    path('directivos/editar_perfil/', views.editar_perfil_directivos, name='editar_perfil_directivos'),
    path('directivos/perfil/', views.ver_perfil_directivos, name='ver_perfil_directivos'),

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
path('directivos/periodo/', views.periodo_crear_directivos, name='periodo_directivos'),
path('directivos/periodo/consultar/', views.periodo_consultar_directivos, name='periodo_directivos_consultar'),
path('directivos/periodo/editar/<int:id>/', views.editar_periodo, name='editar_periodo'),
path('directivos/periodo/eliminar/<int:id>/', views.eliminar_periodo, name='eliminar_periodo'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)