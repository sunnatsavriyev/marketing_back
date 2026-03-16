from django.db import models
from django.contrib.auth import get_user_model
from .validators import validate_file_extension
import logging
from django.core.validators import FileExtensionValidator
logger = logging.getLogger(__name__)
from django.utils import timezone
User = get_user_model()

class MetroLine(models.Model):
    name = models.CharField(max_length=100, unique=True,null=True)

    def __str__(self):
        return str(self.name or "No name")

 

class Station(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    line = models.ForeignKey(MetroLine, on_delete=models.SET_NULL, related_name='stations', null=True, blank=True)
    schema_image = models.FileField(
        upload_to='station_schemas/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
        null=True,
        blank=True,
        help_text="Bekat sxemasi (rasm yoki PDF)"
    )
    def __str__(self):
        return f"{self.name} ({self.line.name})" if self.line and self.line.name else self.name or "No name"



class Position(models.Model):
    station = models.ForeignKey(Station, on_delete=models.SET_NULL,null=True, related_name='positions')
    number = models.PositiveIntegerField(help_text="Joy raqami, masalan: 1, 2, 3")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"{self.station.name} - Joy #{self.number}" if self.station else f"Joy #{self.number}"

    class Meta:
        unique_together = ('station', 'number')
        verbose_name = "Pozitsiya"
        verbose_name_plural = "Pozitsiyalar"


class Depo(models.Model):
    nomi = models.CharField(max_length=100, unique=True,help_text="TCH-1, TCH-2 va hokazo")

    def __str__(self):
        return self.nomi


class HarakatTarkibi(models.Model):
    depo = models.ForeignKey(Depo, on_delete=models.CASCADE, related_name='haraka_tarkiblari')
    tarkib = models.CharField(max_length=100, unique=True,help_text="0001-0002-0003-0004")
    schema_image = models.FileField(
        upload_to='haraka_tarkibi_schemas/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
        null=True,
        blank=True, 
        help_text="Bekat sxemasi (rasm yoki PDF)"
    )

    def __str__(self):
        return self.tarkib



class TarkibPosition(models.Model): 
    harakat_tarkibi = models.ForeignKey(
        HarakatTarkibi, 
        on_delete=models.CASCADE, 
        related_name='tarkib_positions'
    )
    position = models.CharField(max_length=100, help_text="Pozitsiya raqami, masalan: 1, 2, 3",)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField( default=timezone.now)
    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['harakat_tarkibi', 'position'], name='unique_position_per_tarkib')
        ]

    def __str__(self):
        return f"{self.harakat_tarkibi.tarkib} - Pozitsiya #{self.position}"


class Ijarachi(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_number = models.CharField(max_length=20)
    logo = models.ImageField(upload_to='ijarachi_logos/', null=True, blank=True)
    
    def __str__(self):
        return self.name
    

class Turi(models.Model):
    qurilmaturi = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.qurilmaturi



class ShartnomaSummasi(models.Model):
    advertisement = models.ForeignKey(
        "Advertisement",
        on_delete=models.CASCADE,
        related_name="tolovlar",
        null=True,  
        blank=True 
    )
    Shartnomasummasi = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.advertisement.Reklama_nomi} → {self.Shartnomasummasi}"



class ShartnomaSummasiArchive(models.Model):
    archive = models.ForeignKey(
        "AdvertisementArchive",
        on_delete=models.CASCADE,
        related_name='tolovlar'
    )
    Shartnomasummasi = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.archive.Reklama_nomi} → {self.Shartnomasummasi}"




class TarkibShartnomaSummasi(models.Model):
    Shartnomasummasi = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    reklama = models.ForeignKey('TarkibAdvertisement', on_delete=models.SET_NULL, null=True, blank=True, related_name='tarkibtolovlar')
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reklama} → {self.Shartnomasummasi}"



class TarkibAdvertisementArchiveShartnomaSummasi(models.Model):
    reklama_archive = models.ForeignKey(
    'TarkibAdvertisementArchive',
        on_delete=models.CASCADE,
        related_name='tarkibtolovlar'
    )
    Shartnomasummasi = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reklama_archive} → {self.Shartnomasummasi}"




class TarkibAdvertisement(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,related_name='tarkib_advertisements', null=True, blank=True, )
    position = models.OneToOneField(TarkibPosition, on_delete=models.CASCADE, related_name='tarkib_advertisement', null=True, blank=True)
    Reklama_nomi = models.CharField(max_length=255, default='Reklama nomi',)
    Qurilma_turi = models.ForeignKey(Turi, on_delete=models.SET_NULL, null=True, blank=True)
    Ijarachi = models.ForeignKey(Ijarachi, on_delete=models.SET_NULL, null=True, blank=True)
    Shartnoma_raqami = models.CharField(max_length=100, help_text="Shartnoma raqami o'zbekcha", null=True, blank=True)
    Shartnoma_muddati_boshlanishi = models.DateField()
    Shartnoma_tugashi = models.DateField()
    O_lchov_birligi = models.CharField(max_length=50, choices=[
        ('dona', 'Dona'),
        ('kv_metr', 'Kv metr'),
        ('komplekt', 'Komplekt')
    ],
    default='dona',
    )
    
    Qurilma_narxi = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    Egallagan_maydon = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    Shartnoma_summasi = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    Shartnoma_fayl = models.FileField(upload_to='contracts/', default=None, validators=[validate_file_extension], null=True, blank=True)
    photo = models.ImageField(upload_to='ad_photos/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.Reklama_nomi and self.position:
            return f"{self.Reklama_nomi} ({self.position})"
        return self.Reklama_nomi or "TarkibAdvertisement"
    
    
    
    
class TarkibAdvertisementArchive(models.Model):
    original_ad = models.ForeignKey('TarkibAdvertisement', on_delete=models.SET_NULL, null=True, related_name='archives')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)
    depo = models.ForeignKey('Depo', on_delete=models.SET_NULL, null=True, blank=True)
    tarkib = models.ForeignKey('HarakatTarkibi', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(TarkibPosition, on_delete=models.SET_NULL, null=True, blank=True)
    Reklama_nomi = models.CharField(max_length=255)
    Qurilma_turi = models.ForeignKey(Turi, on_delete=models.SET_NULL, null=True, blank=True)
    Ijarachi = models.ForeignKey(Ijarachi, on_delete=models.SET_NULL, null=True, blank=True)
    Shartnoma_raqami= models.CharField(max_length=100, null=True, blank=True)
    Shartnoma_muddati_boshlanishi = models.DateField()
    Shartnoma_tugashi = models.DateField()
    O_lchov_birligi = models.CharField(max_length=50)
    Qurilma_narxi = models.DecimalField(max_digits=15, decimal_places=2)
    Egallagan_maydon = models.DecimalField(max_digits=10, decimal_places=2)
    Shartnoma_summasi = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    Shartnoma_fayl = models.FileField(upload_to='contracts_archive/', null=True, blank=True)
    photo = models.ImageField(upload_to='ad_photos_archive/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.Reklama_nomi} ({self.position})"
    


  
class Advertisement(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ads')
    position = models.OneToOneField(Position, on_delete=models.CASCADE, related_name='advertisement', null=True, blank=True)
    Reklama_nomi = models.CharField(max_length=255, default='Reklama nomi',)
    Qurilma_turi = models.ForeignKey(Turi, on_delete=models.SET_NULL, null=True, blank=True)
    Ijarachi = models.ForeignKey(Ijarachi, on_delete=models.SET_NULL, null=True, blank=True)
    Shartnoma_raqami = models.CharField(max_length=100, help_text="Shartnoma raqami o'zbekcha", null=True, blank=True)
    Shartnoma_muddati_boshlanishi = models.DateField()
    Shartnoma_tugashi = models.DateField()
    O_lchov_birligi = models.CharField(max_length=50, choices=[
        ('dona', 'Dona'),
        ('kv_metr', 'Kv metr'),
        ('komplekt', 'Komplekt')
    ],
    default='dona',
    )
    
    Qurilma_narxi = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    Egallagan_maydon = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    Shartnoma_summasi = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    Shartnoma_fayl = models.FileField(upload_to='contracts/', default=None, validators=[validate_file_extension], null=True, blank=True)
    photo = models.ImageField(upload_to='ad_photos/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.Reklama_nomi and self.position:
            return f"{self.Reklama_nomi} ({self.position})"
        return self.Reklama_nomi or "Advertisement"
    

class AdvertisementArchive(models.Model):
    original_ad = models.ForeignKey('Advertisement', on_delete=models.SET_NULL, null=True, related_name='archives')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    line = models.ForeignKey('MetroLine', on_delete=models.SET_NULL, null=True, blank=True)
    station = models.ForeignKey('Station', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    Reklama_nomi = models.CharField(max_length=255)
    Qurilma_turi = models.ForeignKey(Turi, on_delete=models.SET_NULL, null=True, blank=True)
    Ijarachi = models.ForeignKey(Ijarachi, on_delete=models.SET_NULL, null=True, blank=True)
    Shartnoma_raqami= models.CharField(max_length=100, null=True, blank=True)
    Shartnoma_muddati_boshlanishi = models.DateField()
    Shartnoma_tugashi = models.DateField()
    O_lchov_birligi = models.CharField(max_length=50)
    Qurilma_narxi = models.DecimalField(max_digits=15, decimal_places=2)
    Egallagan_maydon = models.DecimalField(max_digits=10, decimal_places=2)
    Shartnoma_summasi = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    Shartnoma_fayl = models.FileField(upload_to='contracts_archive/', null=True, blank=True)
    photo = models.ImageField(upload_to='ad_photos_archive/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.Reklama_nomi} ({self.position})"
    
