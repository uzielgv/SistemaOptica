from django.db import models

class Categoria(models.Model):
    categoria_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

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
    producto_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField()

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
        managed = False

    def __str__(self):
        return self.nombre
    
class Movimiento(models.Model):
    movimiento_id = models.AutoField(primary_key=True)
    
    producto = models.ForeignKey(
        Producto,
        db_column='producto_id',
        on_delete=models.CASCADE
    )

    tipo = models.CharField(max_length=10)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(db_column='fecha_movimiento')

    class Meta:
        db_table = 'movimientos_inventario'