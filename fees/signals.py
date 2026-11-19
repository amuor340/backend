from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import FeePayment, StudentFee


def recalculate_student_fee(student_fee_id):
    try:
        student_fee = StudentFee.objects.get(pk=student_fee_id)
    except StudentFee.DoesNotExist:
        return

    total_paid = FeePayment.objects.filter(
        student_fee_id=student_fee_id,
        payment_status=FeePayment.PaymentStatus.SUCCESS,
    ).aggregate(total=Sum("amount"))["total"] or 0

    # QuerySet.update avoids triggering model save hooks unnecessarily.
    StudentFee.objects.filter(pk=student_fee_id).update(
        amount_paid=total_paid,
        balance=student_fee.total_fee - total_paid,
    )


@receiver(post_save, sender=FeePayment)
def update_student_fee_after_payment_save(sender, instance, **kwargs):
    recalculate_student_fee(instance.student_fee_id)


@receiver(post_delete, sender=FeePayment)
def update_student_fee_after_payment_delete(sender, instance, **kwargs):
    recalculate_student_fee(instance.student_fee_id)
