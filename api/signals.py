from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Calificacion, CalificacionTributaria, Log, Auditoria

@receiver(post_save, sender=Calificacion)
def log_calificacion_save(sender, instance, created, **kwargs):
    """Registra la creación o actualización de una calificación"""
    accion = "Crear calificación" if created else "Actualizar calificación"
    with transaction.atomic():
        Log.objects.create(
            accion=accion,
            detalle=f"Calificación {instance.id} - Monto: {instance.monto_factor}",
            usuario=instance.usuario,
            calificacion=instance
        )

@receiver(pre_delete, sender=Calificacion)
def log_calificacion_delete(sender, instance, **kwargs):
    """Registra la eliminación de una calificación"""
    with transaction.atomic():
        Log.objects.create(
            accion="Eliminar calificación",
            detalle=f"Calificación {instance.id} eliminada",
            usuario=instance.usuario,
            calificacion=instance
        )

@receiver(post_save, sender=CalificacionTributaria)
def actualizar_calificacion_parent(sender, instance, created, **kwargs):
    """Actualiza la calificación padre cuando se modifica una tributaria"""
    with transaction.atomic():
        calificacion = instance.calificacion
        total_tributarias = CalificacionTributaria.objects.filter(
            calificacion=calificacion
        ).count()
        
        Auditoria.objects.create(
            tipo="Actualización automática",
            resultado="Éxito",
            observaciones=f"Actualización por cambio en tributaria {instance.id}",
            usuario=calificacion.usuario,
            calificacion=calificacion
        )