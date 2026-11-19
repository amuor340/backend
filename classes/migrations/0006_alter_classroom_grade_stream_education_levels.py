from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("classes", "0005_classroom_school_tenant_constraint"),
    ]

    operations = [
        migrations.AlterField(
            model_name="classroom",
            name="grade",
            field=models.CharField(
                max_length=20,
                choices=[
                ('Day Care', 'Day Care'),
                ('PP1', 'PP1'),
                ('PP2', 'PP2'),
                ('Grade 1', 'Grade 1'),
                ('Grade 2', 'Grade 2'),
                ('Grade 3', 'Grade 3'),
                ('Grade 4', 'Grade 4'),
                ('Grade 5', 'Grade 5'),
                ('Grade 6', 'Grade 6'),
                ('Grade 7', 'Grade 7'),
                ('Grade 8', 'Grade 8'),
                ('Grade 9', 'Grade 9'),
                ('Form 1', 'Form 1'),
                ('Form 2', 'Form 2'),
                ('Form 3', 'Form 3'),
                ('Form 4', 'Form 4'),
                ('P1', 'P1'),
                ('P2', 'P2'),
                ('P3', 'P3'),
                ('P4', 'P4'),
                ('P5', 'P5'),
                ('P6', 'P6'),
                ('P7', 'P7'),
                ('P8', 'P8'),
                ('S1', 'S1'),
                ('S2', 'S2'),
                ('S3', 'S3'),
                ('S4', 'S4'),
            ],
            ),
        ),
        migrations.AlterField(
            model_name="classroom",
            name="stream",
            field=models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F')]),
        ),
    ]
