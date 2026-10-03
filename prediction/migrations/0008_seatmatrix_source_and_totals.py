from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prediction", "0007_seatmatrix_unique_record"),
    ]

    operations = [
        migrations.AddField(
            model_name="seatmatrix",
            name="college_code",
            field=models.CharField(blank=True, db_index=True, default="", max_length=20),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="college_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="course_code",
            field=models.CharField(blank=True, db_index=True, default="", max_length=20),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="course_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="cap_seats",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="ms_seats",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="minority_seats",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="institute_seats",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="orphan_seats",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="ews_seats",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="pwd_seats",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="seatmatrix",
            name="def_seats",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="seatmatrix",
            name="category",
            field=models.CharField(db_index=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="seatmatrix",
            name="gender",
            field=models.CharField(db_index=True, max_length=10),
        ),
        migrations.AlterField(
            model_name="seatmatrix",
            name="district_type",
            field=models.CharField(db_index=True, max_length=20),
        ),
    ]
