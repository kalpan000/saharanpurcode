from numpy import source
from rest_framework import serializers
from dashboard.models import *

class DeviceCapabilitiSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceCapibility
        fields = ["id","name", "ip", "user", "pwd", "created", "updated", "is_snmp", "commString"]

class CCTVSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id","name", "username", "password", "cameraname", "created_at"]

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteLinks
        fields = ["id","website_name", "created_at"]

class DeviceSerializer(serializers.ModelSerializer):
    dcname = serializers.StringRelatedField(read_only=True,source="datacenter")
    rowname = serializers.StringRelatedField(read_only=True,source="date_center_row")
    rackname = serializers.StringRelatedField(read_only=True,source="data_center_rack")
    ip = serializers.ReadOnlyField()
    class Meta:
        model = AddDevice
        fields = ["id","dcname","datacenter","rowname","date_center_row","device_height","rackname","data_center_rack","Device_Asset_Tag","Unit_Location","type_of_device","ip"]