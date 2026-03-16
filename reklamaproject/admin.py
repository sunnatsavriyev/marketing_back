from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import MetroLine, Station, Position, Advertisement, AdvertisementArchive, Ijarachi,TarkibShartnomaSummasi, Turi, ShartnomaSummasi,HarakatTarkibi, TarkibPosition, TarkibAdvertisement, TarkibAdvertisementArchive,Depo

@admin.register(MetroLine)
class MetroLineAdmin(admin.ModelAdmin):
    list_display = ['id', 'name',]
    search_fields = ['name', ]
    verbose_name = _("Metro liniyasi")
    verbose_name_plural = _("Metro liniyalari")

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'line','schema_image_display']
    list_filter = ['line']
    search_fields = ['name',]
    verbose_name = _("Bekat")
    verbose_name_plural = _("Bekatlar")
    def schema_image_display(self, obj):
        if obj.schema_image:
            return f"<img src='{obj.schema_image.url}' width='100' height='60' />"
        return "Yo'q"
    schema_image_display.allow_tags = True
    schema_image_display.short_description = "Sxema rasmi"

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['id', 'station', 'number', 'created_at', 'created_by']
    list_filter = ['station','created_by']
    search_fields = ['station__name',]
    verbose_name = _("Joylashuv")
    verbose_name_plural = _("Joylashuvlar")
    
    
    
@admin.register(Ijarachi)
class IjarachiAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'contact_number', 'logo_display']
    search_fields = ['name', 'contact_number']
    verbose_name = _("Ijarachi")
    verbose_name_plural = _("Ijarachilar")

    def logo_display(self, obj):
        if obj.logo:
            return f"<img src='{obj.logo.url}' width='60' height='40' />"
        return "Yo'q"
    logo_display.allow_tags = True
    logo_display.short_description = "Logo"



@admin.register(ShartnomaSummasi)
class ShartnomaSummasiAdmin(admin.ModelAdmin):
    list_display = ['id', 'Shartnomasummasi', 'comment','created_at']
    search_fields = ['Shartnomasummasi']
    verbose_name = _("Shartnomasummasi")
    verbose_name_plural = _("Shartnomasummalari")



@admin.register(Turi)
class TuriAdmin(admin.ModelAdmin):
    list_display = ['id', 'qurilmaturi']
    search_fields = ['qurilmaturi']
    verbose_name = _(" qurilmaturi")
    verbose_name_plural = _("Qurilma turlari")


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = [
        'Reklama_nomi', 'get_ijarachi_name', 'get_ijarachi_contact',
        'get_station', 'Qurilma_turi',
        'Shartnoma_raqami', 'Shartnoma_muddati_boshlanishi',
        'Shartnoma_tugashi', 'O_lchov_birligi',
        'Qurilma_narxi', 'Egallagan_maydon', 'Shartnoma_summasi',
        'Shartnoma_fayl',
    ]
    list_filter = ['Ijarachi', 'Qurilma_turi']
    search_fields = ['Reklama_nomi', 'Shartnoma_raqami', 'Ijarachi__name']
    verbose_name = _("Reklama")
    verbose_name_plural = _("Reklamalar")

    @admin.display(description=_("Bekat"))
    def get_station(self, obj):
        if obj.position and obj.position.station:
            return obj.position.station.name
        return "-"

    @admin.display(description=_("Ijarachi nomi"))
    def get_ijarachi_name(self, obj):
        return obj.Ijarachi.name if obj.Ijarachi else "-"

    @admin.display(description=_("Ijarachi telefon"))
    def get_ijarachi_contact(self, obj):
        return obj.Ijarachi.contact_number if obj.Ijarachi else "-"


@admin.register(AdvertisementArchive)
class AdvertisementArchiveAdmin(admin.ModelAdmin):
    list_display = [
        'Reklama_nomi', 'Qurilma_turi', 'Shartnoma_raqami',
        'Shartnoma_muddati_boshlanishi', 'Shartnoma_tugashi',
        'O_lchov_birligi', 'Qurilma_narxi',
        'Shartnoma_summasi', 'Shartnoma_fayl',
        'user', 'created_at'
    ]
    search_fields = ['Reklama_nomi', 'Shartnoma_raqami']
    list_filter = ['created_at', 'user']

    readonly_fields = [
        'original_ad', 'user', 'line', 'station', 'position',
        'Reklama_nomi', 'Qurilma_turi', 'Ijarachi',
        'Shartnoma_raqami',
        'Shartnoma_muddati_boshlanishi', 'Shartnoma_tugashi',
        'O_lchov_birligi', 'Qurilma_narxi',
        'Egallagan_maydon', 'Shartnoma_summasi', 'Shartnoma_fayl',
        'photo', 'created_at'
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
    
 
 
@admin.register(Depo)
class DepoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nomi']
    search_fields = ['nomi']
    verbose_name = _("Depo")
    verbose_name_plural = _("Depolar")
    
    
@admin.register(HarakatTarkibi)
class HarakatTarkibiAdmin(admin.ModelAdmin):
    list_display = ['id', 'tarkib', 'depo']
    search_fields = ['tarkib', 'depo__nomi']
    list_filter = ['depo']
    verbose_name = _("Harakat tarkibi")
    verbose_name_plural = _("Harakat tarkiblari")


@admin.register(TarkibPosition)
class TarkibPositionAdmin(admin.ModelAdmin):
    list_display = ['id', 'harakat_tarkibi', 'position']
    search_fields = ['haraka_tarkibi__tarkib', 'position']
    list_filter = ['harakat_tarkibi']
    verbose_name = _("Tarkib pozitsiyasi")
    verbose_name_plural = _("Tarkib pozitsiyalari")



@admin.register(TarkibShartnomaSummasi)
class TarkibShardnomaSummasiAdmin(admin.ModelAdmin):
    list_display = ['id', 'Shartnomasummasi', 'reklama','comment']
    search_fields = ['reklama__Reklama_nomi', 'Shartnomasummasi']
    verbose_name = _("Harakat tarkibi shartnoma summasi")
    verbose_name_plural = _("Harakat tarkibi shartnoma summalari")



@admin.register(TarkibAdvertisement)
class TarkibAdvertisementAdmin(admin.ModelAdmin):
    list_display = [
        'Reklama_nomi', 'get_ijarachi_name', 'get_ijarachi_contact',
        'get_position', 'Qurilma_turi',
        'Shartnoma_raqami', 'Shartnoma_muddati_boshlanishi',
        'Shartnoma_tugashi', 'O_lchov_birligi',
        'Qurilma_narxi', 'Egallagan_maydon', 'Shartnoma_summasi',
        'Shartnoma_fayl',
    ]
    list_filter = ['Ijarachi', 'Qurilma_turi', 'position__harakat_tarkibi']
    search_fields = ['Reklama_nomi', 'Shartnoma_raqami', 'Ijarachi__name']
    verbose_name = _("Harakat tarkibi reklama")
    verbose_name_plural = _("Harakat tarkibi reklamalar")

    @admin.display(description=_("Pozitsiya"))
    def get_position(self, obj):
        if obj.position:
            return str(obj.position)
        return "-"

    @admin.display(description=_("Ijarachi nomi"))
    def get_ijarachi_name(self, obj):
        return obj.Ijarachi.name if obj.Ijarachi else "-"

    @admin.display(description=_("Ijarachi telefon"))
    def get_ijarachi_contact(self, obj):
        return obj.Ijarachi.contact_number if obj.Ijarachi else "-"


@admin.register(TarkibAdvertisementArchive)
class TarkibAdvertisementArchiveAdmin(admin.ModelAdmin):
    list_display = [
        'Reklama_nomi', 'Qurilma_turi', 'Shartnoma_raqami',
        'Shartnoma_muddati_boshlanishi', 'Shartnoma_tugashi',
        'O_lchov_birligi', 'Qurilma_narxi',
        'Shartnoma_summasi', 'Shartnoma_fayl',
        'user', 'created_at'
    ]
    search_fields = ['Reklama_nomi', 'Shartnoma_raqami']
    list_filter = ['created_at', 'user', 'depo']
    readonly_fields = [
        'original_ad', 'user', 'depo', 'tarkib', 'position',
        'Reklama_nomi', 'Qurilma_turi', 'Ijarachi',
        'Shartnoma_raqami',
        'Shartnoma_muddati_boshlanishi', 'Shartnoma_tugashi',
        'O_lchov_birligi', 'Qurilma_narxi',
        'Egallagan_maydon', 'Shartnoma_summasi', 'Shartnoma_fayl',
        'photo', 'created_at'
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    
    