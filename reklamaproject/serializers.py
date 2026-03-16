from rest_framework import serializers
from .models import (Advertisement, Station, MetroLine, Position, AdvertisementArchive, 
                     Ijarachi, Turi, ShartnomaSummasi, ShartnomaSummasiArchive,Depo, HarakatTarkibi, TarkibPosition, TarkibShartnomaSummasi,TarkibAdvertisementArchiveShartnomaSummasi,
                     TarkibAdvertisement, TarkibAdvertisementArchive)
from rest_framework.fields import CurrentUserDefault
from datetime import date, timedelta,datetime
from rest_framework import status
from rest_framework.response import Response

from django_filters import rest_framework as filters
from decimal import Decimal
class MetroLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetroLine
        fields = ['id', 'name', ]



class StationSerializer(serializers.ModelSerializer):
    line_name = serializers.CharField(source='line.name', read_only=True)

    class Meta:
        model = Station
        fields = ['id', 'name','line', 'line_name', 'schema_image']




class TuriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turi
        fields = ['id', 'qurilmaturi']



class AdvertisementNestedSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="user.username", read_only=True)
    station = serializers.CharField(source='position.station.name', read_only=True)
    position_number = serializers.IntegerField(source='position.number', read_only=True)
    
    class Meta:
        model = Advertisement
        fields = [
            "id", "Reklama_nomi", "Qurilma_turi", "Shartnoma_raqami",
            "Shartnoma_muddati_boshlanishi", "Shartnoma_tugashi",
            "O_lchov_birligi", "Qurilma_narxi", "Egallagan_maydon",
            "Shartnoma_summasi", "position", "position_number", 
            "station", "photo", "created_at", "created_by"
        ]


class IjarachiSerializers(serializers.ModelSerializer):
    reklamalari = AdvertisementNestedSerializer(source="advertisement_set", many=True, read_only=True)
    
    
    
    class Meta:
        model = Ijarachi
        fields = ['id', 'name',"logo", "contact_number", "reklamalari"]




class ShartnomaSummasiSerializer(serializers.ModelSerializer):
    advertisement_id = serializers.PrimaryKeyRelatedField(
        queryset=Advertisement.objects.all(), source='advertisement'
    )

    class Meta:
        model = ShartnomaSummasi
        fields = ['id', 'advertisement_id', 'Shartnomasummasi','comment', 'created_at']


class ShartnomaSummasiArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShartnomaSummasiArchive
        fields = ['id', 'Shartnomasummasi', 'comment','created_at']


class AdvertisementSerializer(serializers.ModelSerializer):
    station = serializers.CharField(source='position.station.name', read_only=True)
    position_number = serializers.IntegerField(source='position.number', read_only=True)
    created_by = serializers.CharField(source="user.username", read_only=True) 
    photo = serializers.ImageField(use_url=True)
    # Reklama ko'rishda barcha pozitsiyalar bo'lishi mumkin
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all())
    Ijarachi = serializers.PrimaryKeyRelatedField(
        queryset=Ijarachi.objects.all(),
        required=False,
        allow_null=True
    )
    tolovlar = ShartnomaSummasiSerializer(many=True, read_only=True)
    jami_tolov = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    
    Shartnoma_muddati_boshlanishi = serializers.DateField(format="%d-%m-%Y")
    Shartnoma_tugashi = serializers.DateField(format="%d-%m-%Y")
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    # READ uchun nested obyekt
    ijarachi = IjarachiSerializers(source="Ijarachi", read_only=True)
    ijarachi_contact = serializers.CharField(source="Ijarachi.contact_number", read_only=True)
    ijarachi_logo = serializers.ImageField(source="Ijarachi.logo", read_only=True)
    ijarachi_name = serializers.CharField(source="Ijarachi.name", read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            'id', 'user', 'position', 'station', 'position_number',
            'Reklama_nomi', 
            'Qurilma_turi',
            'Ijarachi',          # id bilan yuboriladi
            'ijarachi',          # nested obyekt (name, contact_number, logo)
            'ijarachi_contact',
            'ijarachi_name',
            'ijarachi_logo', 
            'Shartnoma_raqami',
            'Shartnoma_muddati_boshlanishi', 'Shartnoma_tugashi',
            'O_lchov_birligi', 
            'Qurilma_narxi', 'Egallagan_maydon', 'Shartnoma_summasi',
            'Shartnoma_fayl', 'photo', 'created_at',
            'created_by',
            'tolovlar',
            'jami_tolov',
        ]
        read_only_fields = ['user']
        
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Jami hisoblash (bazadagi Shartnoma_summasi bilan moslashgan)
        total = sum(t.Shartnomasummasi for t in instance.tolovlar.all())
        data['jami_tolov'] = total
        return data
    
    def get_position_number(self, obj):
        return obj.position.number if obj.position else None
        
    def get_ijarachi(self, obj):
        if obj.Ijarachi:
            return obj.Ijarachi.name
        return None
    
    def get_ijarachi_contact(self, obj):
        if obj.Ijarachi:
            return obj.Ijarachi.contact_number
        return None
    
    def get_ijarachi_logo(self, obj):
        if obj.Ijarachi:
            return obj.Ijarachi.logo
        return None

    def get_station(self, obj):
        if obj.position and obj.position.station:
            return obj.position.station.name
        return None
    
    def get_status(self, obj):
        today = date.today()
        if obj.Shartnoma_tugashi and obj.Shartnoma_tugashi < today:
            return "tugagan"
        elif obj.Shartnoma_tugashi and obj.Shartnoma_tugashi <= today + timedelta(days=7):
            return "7_kunda_tugaydigan"
        return ""




# Reklama YARATISH uchun — faqat advertisement bo'sh joylar
class CreateAdvertisementSerializer(AdvertisementSerializer):
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.none(),
        required=True,
        allow_null=False
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            current_position = self.instance.position
            bosh_joylar = Position.objects.filter(advertisement__isnull=True)
            if current_position:
                bosh_joylar = bosh_joylar | Position.objects.filter(pk=current_position.pk)
            self.fields['position'].queryset = bosh_joylar.distinct()
        else:
            self.fields['position'].queryset = Position.objects.filter(advertisement__isnull=True)

    def validate(self, attrs):
        if 'position' not in attrs or attrs['position'] is None:
            raise serializers.ValidationError({
                'position': "Joy tanlanishi shart."
            })
        return attrs

 

   
class UpdateAdvertisementSerializer(serializers.ModelSerializer):
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        required=False
    )

    # ForeignKey integer qabul qiladi
    Ijarachi = serializers.IntegerField(write_only=True, required=False)
    ijarachi = IjarachiSerializers(read_only=True)

    # Date fields
    Shartnoma_muddati_boshlanishi = serializers.DateField(
        required=False, input_formats=["%Y-%m-%d", "%d-%m-%Y"]
    )
    Shartnoma_tugashi = serializers.DateField(
        required=False, input_formats=["%Y-%m-%d", "%d-%m-%Y"]
    )

    # Multi-file qabul qilish uchun MUST USE ListField
    photo = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )
    Shartnoma_fayl = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )

    class Meta:
        model = Advertisement
        fields = [
            'position', 'Reklama_nomi', 'Qurilma_turi',
            'Ijarachi', 'ijarachi',
            'Shartnoma_raqami', 'Shartnoma_muddati_boshlanishi',
            'Shartnoma_tugashi', 'O_lchov_birligi', 'Qurilma_narxi',
            'Egallagan_maydon', 'Shartnoma_summasi',
            'Shartnoma_fayl', 'photo'
        ]

    def validate(self, attrs):
        

        return attrs

    def update(self, instance, validated_data):
        
        

        # Foreign key update
        ijarachi_id = validated_data.pop("Ijarachi", None)
        if ijarachi_id:
            instance.Ijarachi_id = ijarachi_id

        # Normal fields
        simple_fields = [
            'position', 'Reklama_nomi', 'Qurilma_turi',
            'Shartnoma_raqami', 'Shartnoma_muddati_boshlanishi',
            'Shartnoma_tugashi', 'O_lchov_birligi', 'Qurilma_narxi',
            'Egallagan_maydon', 'Shartnoma_summasi'
        ]

        for field in simple_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        # Multi file update
        if "photo" in self.initial_data:
            photos = self.initial_data.getlist("photo")
            if photos:
                instance.photo = photos[0]  # bitta rasm emas, yangi birinchi rasmni qo'yamiz

        if "Shartnoma_fayl" in self.initial_data:
            files = self.initial_data.getlist("Shartnoma_fayl")
            if files:
                instance.Shartnoma_fayl = files[0]

        instance.save()
        return instance



class PositionSerializer(serializers.ModelSerializer):
    station = serializers.CharField(source="station.name", read_only=True)
    station_id = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
        source="station",
        write_only=True
    )
    advertisement = AdvertisementSerializer(read_only=True)
    status = serializers.SerializerMethodField()
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Position
        fields = [
            'id', 'station', 'station_id', 'number',
            'advertisement', 'status',
            'created_at', 'created_by'
        ]

    def get_status(self, obj):
        return getattr(obj, "advertisement", None) is not None

    def update(self, instance, validated_data):
        # update paytida station o‘zgarmasligi kerak
        validated_data.pop("station", None)
        return super().update(instance, validated_data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method in ("PUT", "PATCH"):
            self.fields.pop("station_id", None)




class AdvertisementArchiveSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    line_name = serializers.CharField(source='line.name', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    created_by = serializers.CharField(source="user.username", read_only=True)
    Ijarachi = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Ijarachi.objects.all()
    )
    position_number = serializers.SerializerMethodField(read_only=True)
    tolovlar = ShartnomaSummasiArchiveSerializer(many=True, read_only=True)
    jami_tolov = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    # GET javobida esa to‘liq Ijarachi obyektini qaytaradi
    ijarachi = IjarachiSerializers(source='Ijarachi', read_only=True)
    ijarachi_contact = serializers.CharField(source='Ijarachi.contact_number', read_only=True)
    ijarachi_logo = serializers.ImageField(source='Ijarachi.logo', read_only=True)  
    ijarachi_name = serializers.CharField(source='Ijarachi.name', read_only=True)

    class Meta:
        model = AdvertisementArchive
        fields = '__all__'
        
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['jami_tolov'] = sum(Decimal(t['Shartnomasummasi']) for t in data.get('tolovlar', []))
        return data
    
    def get_position_number(self, obj):
        return obj.position.number if obj.position else None
    
    
    def get_ijarachi(self, obj):
        if obj.Ijarachi:
            return obj.Ijarachi.name
        return None
    
    def get_ijarachi_contact(self, obj):
        if obj.Ijarachi:
            return obj.Ijarachi.contact_number
        return None
    
    def get_ijarachi_logo(self, obj):
        if obj.Ijarachi:
            return obj.Ijarachi.logo
        return None

    def get_station_name(self, obj):
        try:
            return obj.position.station.name
        except AttributeError:
            return None


class ExportAdvertisementSerializer(serializers.Serializer):
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all())

    def validate_position(self, value):
        if not value:
            raise serializers.ValidationError("Joy tanlanishi shart.")
        return value


class CountSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.IntegerField()
    color = serializers.CharField()

class AdvertisementStatisticsSerializer(serializers.Serializer):
    top_5_ads = AdvertisementSerializer(many=True)
    last_10_ads = AdvertisementSerializer(many=True)
    top_5_stations = serializers.ListField(
        child=serializers.DictField()
    )
    counts = CountSerializer(many=True)
    
    
    
    
    
# Harakat tarkiblari uchun serializerlar 

class DepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depo
        fields = ['id', 'nomi']
        


class HarakatTarkibiSerializer(serializers.ModelSerializer):
    depo = serializers.StringRelatedField(read_only=True)
    depo_id = serializers.PrimaryKeyRelatedField(
        source='depo',  
        queryset=Depo.objects.all(),
        write_only=True  
    )
    
    class Meta:
        model = HarakatTarkibi
        fields = ['id', 'depo','depo_id', 'tarkib', 'schema_image']
        

class TarkibShartnomaSummasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarkibShartnomaSummasi
        fields = ['id', 'Shartnomasummasi', 'reklama', 'comment', 'created_at']
        read_only_fields = ['created_at']




class TarkibAdvertisementArchiveShartnomaSummasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarkibAdvertisementArchiveShartnomaSummasi
        fields = ['id', 'reklama_archive', 'Shartnomasummasi', 'comment', 'created_at']
        read_only_fields = ['created_at']


# ================== Advertisement ==================
class TarkibAdvertisementSerializer(serializers.ModelSerializer):
    station = serializers.CharField(source='position.station.name', read_only=True)
    position_number = serializers.IntegerField(source='position.number', read_only=True)
    created_by = serializers.CharField(source="user.username", read_only=True) 
    photo = serializers.ImageField(use_url=True)
    tarkib_nomi = serializers.CharField(
        source='position.harakat_tarkibi.tarkib',
        read_only=True
    )
    depo_nomi = serializers.CharField(
        source='position.harakat_tarkibi.depo.nomi',
        read_only=True
    )
    position = serializers.PrimaryKeyRelatedField(queryset=TarkibPosition.objects.all())
    Ijarachi = serializers.PrimaryKeyRelatedField(
        queryset=Ijarachi.objects.all(),
        required=False,
        allow_null=True
    )
    tolovlar = TarkibShartnomaSummasiSerializer(source='tarkibtolovlar', many=True, read_only=True)
    jami_tolov = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    
    Shartnoma_muddati_boshlanishi = serializers.DateField(format="%d-%m-%Y")
    Shartnoma_tugashi = serializers.DateField(format="%d-%m-%Y")
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    ijarachi = IjarachiSerializers(source="Ijarachi", read_only=True)
    ijarachi_contact = serializers.CharField(source="Ijarachi.contact_number", read_only=True)
    ijarachi_logo = serializers.ImageField(source="Ijarachi.logo", read_only=True)
    ijarachi_name = serializers.CharField(source="Ijarachi.name", read_only=True)

    class Meta:
        model = TarkibAdvertisement
        fields = [
            'id', 'user', 'position', 'station', 'position_number',
            'Reklama_nomi', 'Qurilma_turi','tarkib_nomi',
            'depo_nomi',
            'Ijarachi', 'ijarachi', 'ijarachi_contact', 'ijarachi_name', 'ijarachi_logo',
            'Shartnoma_raqami', 'Shartnoma_muddati_boshlanishi', 'Shartnoma_tugashi',
            'O_lchov_birligi', 'Qurilma_narxi', 'Egallagan_maydon', 'Shartnoma_summasi',
            'Shartnoma_fayl', 'photo', 'created_at', 'created_by',
            'tolovlar', 'jami_tolov',
        ]
        read_only_fields = ['user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        total = sum(t.Shartnomasummasi for t in instance.tarkibtolovlar.all())
        data['jami_tolov'] = total
        return data
    
    
    def get_ijarachi(self, obj):
        if obj.Ijarachi:
            return obj.Ijarachi.name
        return None
    
    def get_ijarachi_contact(self, obj):
        if obj.Ijarachi:
            return obj.Ijarachi.contact_number
        return None
    
    def get_ijarachi_logo(self, obj):
        if obj.Ijarachi:
            return obj.Ijarachi.logo
        return None

    def get_station(self, obj):
        if obj.position and obj.position.station:
            return obj.position.station.name
        return None
    
    def get_status(self, obj):
        today = date.today()
        if obj.Shartnoma_tugashi and obj.Shartnoma_tugashi < today:
            return "tugagan"
        elif obj.Shartnoma_tugashi and obj.Shartnoma_tugashi <= today + timedelta(days=7):
            return "7_kunda_tugaydigan"
        return ""


class CreateTarkibAdvertisementSerializer(TarkibAdvertisementSerializer):
    position = serializers.PrimaryKeyRelatedField(
        queryset=TarkibPosition.objects.none(),
        required=True,
        allow_null=False
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            current_position = self.instance.position
            bosh_joylar = TarkibPosition.objects.filter(tarkib_advertisement__isnull=True)
            if current_position:
                bosh_joylar = bosh_joylar | TarkibPosition.objects.filter(pk=current_position.pk)
            self.fields['position'].queryset = bosh_joylar.distinct()
        else:
            self.fields['position'].queryset = TarkibPosition.objects.filter(tarkib_advertisement__isnull=True)

    def validate(self, attrs):
        if 'position' not in attrs or attrs['position'] is None:
            raise serializers.ValidationError({'position': "Joy tanlanishi shart."})
        return attrs


class UpdateTarkibAdvertisementSerializer(serializers.ModelSerializer):
    position = serializers.PrimaryKeyRelatedField(
        queryset=TarkibPosition.objects.all(),
        required=False
    )
    Ijarachi = serializers.IntegerField(write_only=True, required=False)
    ijarachi = IjarachiSerializers(read_only=True)
    Shartnoma_muddati_boshlanishi = serializers.DateField(
        required=False, input_formats=["%Y-%m-%d", "%d-%m-%Y"]
    )
    Shartnoma_tugashi = serializers.DateField(
        required=False, input_formats=["%Y-%m-%d", "%d-%m-%Y"]
    )
    photo = serializers.ListField(child=serializers.FileField(), required=False)
    Shartnoma_fayl = serializers.ListField(child=serializers.FileField(), required=False)

    class Meta:
        model = TarkibAdvertisement
        fields = [
            'position', 'Reklama_nomi', 'Qurilma_turi',
            'Ijarachi', 'ijarachi',
            'Shartnoma_raqami', 'Shartnoma_muddati_boshlanishi', 'Shartnoma_tugashi',
            'O_lchov_birligi', 'Qurilma_narxi', 'Egallagan_maydon', 'Shartnoma_summasi',
            'Shartnoma_fayl', 'photo'
        ]

    def update(self, instance, validated_data):
        ijarachi_id = validated_data.pop("Ijarachi", None)
        if ijarachi_id:
            instance.Ijarachi_id = ijarachi_id

        for field in [
            'position', 'Reklama_nomi', 'Qurilma_turi',
            'Shartnoma_raqami', 'Shartnoma_muddati_boshlanishi',
            'Shartnoma_tugashi', 'O_lchov_birligi', 'Qurilma_narxi',
            'Egallagan_maydon', 'Shartnoma_summasi'
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        if "photo" in self.initial_data:
            photos = self.initial_data.getlist("photo")
            if photos:
                instance.photo = photos[0]

        if "Shartnoma_fayl" in self.initial_data:
            files = self.initial_data.getlist("Shartnoma_fayl")
            if files:
                instance.Shartnoma_fayl = files[0]

        instance.save()
        return instance


# ================== Position ==================
class TarkibPositionSerializer(serializers.ModelSerializer):
    harakat_tarkibi = serializers.CharField(
        source="harakat_tarkibi.tarkib",
        read_only=True
    )
    harakat_tarkibi_input = serializers.ChoiceField(
        choices=[],
        required=False  # PUTda majburiy emas
    )
    position = serializers.CharField(allow_blank=True, required=False)
    tarkib_advertisement = TarkibAdvertisementSerializer(read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = TarkibPosition
        fields = [
            'id',
            'harakat_tarkibi',
            'harakat_tarkibi_input',
            'position',
            'tarkib_advertisement',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['harakat_tarkibi_input'].choices = [
            (obj.tarkib, f"{obj.tarkib} ({obj.depo.nomi})")
            for obj in HarakatTarkibi.objects.select_related("depo")
        ]

    def to_internal_value(self, data):
        # Frontend array yuborsa stringga aylantirish
        if 'position' in data:
            if isinstance(data['position'], list) and data['position']:
                data['position'] = data['position'][0]
            elif data['position'] is None:
                data['position'] = ''
        return super().to_internal_value(data)

    def validate(self, attrs):
        # Debug: kelayotgan attrs ni print qilamiz
        print("Serializer validate attrs:", attrs)

        position = attrs.get("position", "")

        if self.instance is None:
            # CREATE
            harakat_tarkibi_input = attrs.get("harakat_tarkibi_input")
            if not position:
                raise serializers.ValidationError({"position": "Ushbu maydon to'ldirilishi shart."})
            if not harakat_tarkibi_input:
                raise serializers.ValidationError({"harakat_tarkibi_input": "Ushbu maydon to'ldirilishi shart."})
        else:
            # UPDATE - faqat position kerak
            if 'position' not in attrs or not position:
                raise serializers.ValidationError({"position": "Ushbu maydon to'ldirilishi shart."})

        return attrs

    def get_status(self, obj):
        return hasattr(obj, "tarkibadvertisement") and obj.tarkibadvertisement is not None

    def create(self, validated_data):
        tarkib_nomi = validated_data.pop("harakat_tarkibi_input")
        harakat = HarakatTarkibi.objects.get(tarkib=tarkib_nomi)
        validated_data["harakat_tarkibi"] = harakat
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Debug: kelayotgan validated_data ni print qilamiz
        print("Serializer update validated_data:", validated_data)

        position = validated_data.get('position')
        if position is not None:
            instance.position = position
            instance.save()
        return instance








# ================== Archive ==================
class TarkibAdvertisementArchiveSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    Ijarachi = serializers.SlugRelatedField(slug_field='name', queryset=Ijarachi.objects.all())
    position_number = serializers.SerializerMethodField()
    tarkib_nomi = serializers.CharField(
        source='position.harakat_tarkibi.tarkib',
        read_only=True
    )
    depo_nomi = serializers.CharField(
        source='position.harakat_tarkibi.depo.nomi',
        read_only=True)
    tolovlar = TarkibAdvertisementArchiveShartnomaSummasiSerializer(source='tarkibtolovlar', many=True, read_only=True)
    jami_tolov = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    ijarachi = IjarachiSerializers(source='Ijarachi', read_only=True)
    ijarachi_contact = serializers.CharField(source='Ijarachi.contact_number', read_only=True)
    ijarachi_logo = serializers.ImageField(source='Ijarachi.logo', read_only=True)
    ijarachi_name = serializers.CharField(source='Ijarachi.name', read_only=True)

    class Meta:
        model = TarkibAdvertisementArchive
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # jami_tolov hisoblash
        data['jami_tolov'] = sum(t['Shartnomasummasi'] for t in data.get('tarkibtolovlar', []))
        return data

    def get_position_number(self, obj):
        return obj.position.position if obj.position else None


class IjarachiUnifiedStatisticsQuerySerializer(serializers.Serializer):
    TYPE_CHOICES = (
        ('train', 'Train'),
        ('station', 'Station'),
    )
    type = serializers.ChoiceField(
        choices=TYPE_CHOICES,
        required=True,
        help_text="Statistika turi: 'train' (Tarkib) yoki 'station' (Station)"
    )
    pdf = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Agar True bo'lsa PDF hosil qilinadi"
    ) 
        

