from django.db import models

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'categorias'
        managed = False

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    proveedor_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'proveedores'
        managed = False

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField()
    marca = models.CharField(max_length=100, null=True, blank=True)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        db_column='categoria_id'
    )
    
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        db_column='proveedor_id'
    )

    class Meta:
        db_table = 'productos'

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField()

    class Meta:
        db_table = 'usuarios'
        managed = False

    def __str__(self):
        return self.username

class Paciente(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=200)
    domicilio = models.TextField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    pasatiempos = models.TextField(null=True, blank=True)
    eliminado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pacientes'

class HistoriaClinica(models.Model):
    id = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(
        'Paciente', 
        on_delete=models.CASCADE,
        db_column='paciente_id'
    )
    uso_previo_lentes = models.BooleanField(default=False)
    tiempo_uso = models.CharField(max_length=100, null=True, blank=True)
    graduacion_micas = models.TextField(null=True, blank=True)
    antecedentes_familiares = models.TextField(null=True, blank=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'historia_clinica'

class ServicioMedico(models.Model):
    id = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(
        'Paciente', 
        on_delete=models.CASCADE,
        db_column='paciente_id'
    )
    usuario = models.ForeignKey(
        'Usuario', 
        on_delete=models.CASCADE,
        db_column='usuario_id'
    )
    tipo_servicio = models.CharField(max_length=100)
    presion_arterial = models.CharField(max_length=20, null=True, blank=True)
    glucosa = models.CharField(max_length=20, null=True, blank=True)
    signos_vitales_otros = models.TextField(null=True, blank=True)
    detalle_mica = models.JSONField(null=True, blank=True)
    fecha_servicio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'servicios_medicos'

class Venta(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, db_column='usuario_id')
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, db_column='paciente_id', null=True, blank=True)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField()

    class Meta:
        db_table = 'ventas'
        managed = False

class DetalleVenta(models.Model):
    id = models.AutoField(primary_key=True)
    venta = models.ForeignKey('Venta', on_delete=models.CASCADE, db_column='venta_id')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, db_column='producto_id')
    cantidad = models.IntegerField()
    precio_unitario_aplicado = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_ventas'
        managed = False

class MovimientoInventario(models.Model):
    id = models.AutoField(primary_key=True)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, db_column='producto_id')
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, db_column='usuario_id')
    tipo = models.CharField(max_length=10)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=255, null=True, blank=True)
    fecha_movimiento = models.DateTimeField()

    class Meta:
        db_table = 'movimientos_inventario'
        managed = False