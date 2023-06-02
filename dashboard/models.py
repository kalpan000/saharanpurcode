from bdb import effective
import datetime
from xmlrpc.client import boolean
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ForeignKey
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.forms import CharField, DecimalField
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from matplotlib.backend_bases import LocationEvent
from numpy import integer
from psqlextra.types import PostgresPartitioningMethod
from psqlextra.models import PostgresPartitionedModel
from uptime import uptime

# Create your models here.
#AKRITI MODELS

class SaveXYZ(models.Model):
    ipaddress = models.CharField(max_length=100 , blank=True, null=False)
    subnet = models.CharField(max_length=100 , blank=True, null=False)
    gateway = models.CharField(max_length=100 , blank=True, null=False)
    dns1 = models.CharField(max_length=100 , blank=True, null=False)
    dns2 = models.CharField(max_length=100 , blank=True, null=False)
    def __str__(self):
        return str(self.ipaddress)

class StartApp(models.Model):
    is_start = models.BooleanField(default=False)
    nfs_host = models.CharField(max_length=100, blank=True, null=True)
    nfs_user = models.CharField(max_length=100, blank=True, null=True)
    nfs_pwd = models.CharField(max_length=100, blank=True, null=True)
    nfs_loc = models.CharField(max_length=100, blank=True, null=True)
    nfs_file = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return str(self.is_start)
    
class TempIPDevice(models.Model):
    host = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    action = models.BooleanField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    def __str__(self):
        return str(self.host)
class Product(models.Model):
    name = models.CharField(max_length=300)
    is_favorite = models.BooleanField(default=False)
    username = models.CharField(max_length=1000, default="" , blank=True, null=True)
    password = models.CharField(max_length=1000, default="" , blank=True , null=True)
    cameraname = models.CharField(max_length=1000, default="" , blank=True , null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.name

class CameraMonitor(models.Model):
    url = models.CharField(max_length=300)
    is_favorite = models.BooleanField(default=False)
    username = models.CharField(max_length=1000, default="" , blank=True, null=True)
    password = models.CharField(max_length=1000, default="" , blank=True , null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.url

class TerminalLog(models.Model):
    cmd = models.CharField(max_length=200)
    output = models.TextField()
    device = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.cmd)

class WebsiteLinks(models.Model):
    website_name = models.CharField(max_length=300,unique=True)
    website_up = models.TextField(default=timezone.now,blank=True)
    response_time = models.TextField(blank=True)
    repeat = models.IntegerField(default=0, blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.website_name

# class DC(models.Model):
#     datat_center_tag = models.CharField(max_length=50) 
#     data_center_name = models.CharField(max_length=50)
#     sqr_mtr = models.CharField(max_length=50)
#     address = models.CharField(max_length=100)
#     country = models.CharField(max_length=100)
#     statte = models.CharField(max_length=50)
#     capacity = models.CharField(max_length=50)
#     name = models.CharField(max_length=50)
#     email = models.CharField(max_length=50)
#     phone = models.CharField(max_length=50)
#     contact = models.CharField(max_length=50)

#     def __str__(self):
#         return self.data_center_name

#AKRITI MODELS


# class DataCenCountterCountry(models.Model):
#     data_center_name = models.CharField(max_length=100)
#     sqr_mtr = models.CharField(max_length=50, default="", blank=True, null=True)
#     address = models.CharField(max_length=100)
#     country_name = models.CharField(max_length=100)
#     capacity = models.CharField(max_length=50)
#     country_code = models.CharField(max_length=5, unique=True)
#     other_info = models.TextField(default="", blank=True, null=True)
     
#     def __str__(self):
#         return self.data_center_name
    

class DataCenterState(models.Model):
    state_name = models.CharField(max_length = 100 , default="" , blank=True , null=True)
    state_code = models.CharField(max_length = 100 , default="" , blank=True , null=True)
    data_center_name = models.CharField(max_length = 100 , default="" , blank=True , null=True)
    address = models.CharField(max_length = 100 , default="" , blank=True , null=True)
    capacity = models.CharField(max_length = 100 , default="" , blank=True , null=True)
    sqr_mtr = models.PositiveIntegerField(default=0, blank=True, null=True)
    # country = models.ForeignKey(DataCenterCountry, on_delete=models.CASCADE)
    other_info = models.TextField(default="", blank=True, null=True)
    link_dc = models.URLField(default="https://www.google.com/")
    
    def __str__(self):
        return self.state_name

    

# class DeviceEquipement(models.Model):
#     device_assest_tag = models.CharField(max_length=15, unique=True, error_messages={'unique': "Device already exists."})
#     make_and_model = models.CharField(max_length=50)
#     size = models.CharField(max_length=50)
#     device_serial_no = models.IntegerField(default=0)
#     wattage = models.CharField(max_length=50)
#     type = models.CharField(max_length=50)
#     no_of_power_supplies = models.CharField(max_length=50)
#     no_of_ports = models.IntegerField()
#     special_notes = models.TextField()

#     def __str__(self):
#         return self.device_assest_tag

class UserProfile(models.Model):
    # User - name, email, first_name, Last_name, last_seen, new_registration, group
    # UserProfile - phone, address, Security Question, 
    STAFF_TYPE_CHOICE = (
    ('STAFF','STAFF'),
    ('ADMIN', 'ADMIN'),
    ('SUPERADMIN','SUPERADMIN'),
    ('DC','DC'),
    )

    new_user = models.BooleanField(default=True)
    bio = models.TextField(default = "NO BIO")
    user = models.OneToOneField(User, blank = True, null = True, on_delete=models.CASCADE)
    master_password = models.CharField(default="Test@123", max_length=100)
    pic = models.ImageField(upload_to='profile_pic' ,blank=True, null=True)
    staff_type = models.CharField(max_length=100, choices=STAFF_TYPE_CHOICE, default="STAFF",)
    def save(self, *args, **kwargs):                                                     
        self.master_password = make_password(self.master_password, None, 'pbkdf2_sha1')  
        super(UserProfile, self).save(*args, **kwargs)                                   
    def __str__(self):
        return self.user.username
    

# class Person(models.Model):
#     name = models.CharField(max_length=30)
#     email = models.EmailField(blank=True, null=True)
#     birth_date = models.DateField()
#     location = models.CharField(max_length=100, blank=True, null=True)

#     def __str__(self):
#         return self.name



# class Post(models.Model):
#     Postname = models.CharField(max_length=30)
#     Postemail = models.EmailField(blank=True, null=True)
#     date = models.DateField()
#     location = models.CharField(max_length=100, blank=True, null=True)


# class Employee(models.Model):
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=60)
#     email = models.EmailField(blank=True, null=True)
#     day_started = models.DateField()
#     location = models.CharField(max_length=100, blank=True, null=True)


# class PagePermissionForGroup(models.Model):
#     groupname=models.ForeignKey(Group,on_delete=models.CASCADE, blank=True, null=True)
#     name_of_page= models.CharField(max_length=30)
#     all_perm=models.BooleanField(default=False)
#     read_perm=models.BooleanField(default=False)
#     write_perm=models.BooleanField(default=False)
#     delete_perm=models.BooleanField(default=False)
#     update_perm=models.BooleanField(default=False)
#     patch_perm=models.BooleanField(default=False)

#     def __str__(self):
#         return self.name_of_page



class addDataCenter(models.Model):
    dataCenterTag =models.CharField(max_length = 30, blank=True, null=True)
    DataCenterName=models.CharField(max_length = 30, blank=True, null=True)
    sqr_mtr = models.PositiveIntegerField(default=0, blank=True, null=True)
    Add_country =models.CharField(max_length=30, blank=True, null=True)
    Add_state = models.CharField(max_length=255, blank=True, null=True)
    Address=models.CharField(max_length=100, blank=True, null=True)
    Contact=models.CharField(max_length=100, blank=True, null=True)
    PersonalDet_fname=models.CharField( max_length=128, blank=True, null=True )
    PersonalDet_email=models.EmailField(max_length=100, blank=True, null=True)
    phone=models.CharField(max_length=50, blank=True, null=True)
    Capacity_in_MW=models.FloatField(default=0, blank=True, null=True)
    def __str__(self):
        return self.DataCenterName

class addDataCenterRow(models.Model):
    data_center = models.ForeignKey(addDataCenter, blank = True, null = True, on_delete=models.CASCADE)
    RackRow=models.CharField(max_length=10, blank=True, null=True)
    Row_Label_Tag=models.CharField(max_length = 30, blank=True, null=True)
    RowColor = models.CharField(max_length=10, blank=True, null=True)
    def __str__(self):
        return str(self.data_center) +" - "+ self.RackRow

class AddDataCenterRackcabinet(models.Model):
    datacenter = models.ForeignKey(addDataCenter, blank = True, null = True, on_delete=models.CASCADE)
    date_center_row = models.ForeignKey(addDataCenterRow, blank = True, null = True, on_delete=models.CASCADE)
    # RackRow=models.CharField(max_length=1, blank=True, null=True)
    Rack_Label_Tag=models.CharField(max_length=100, blank=True, null=True)
    RowColor = models.CharField(max_length=10, blank=True, null=True)
    Rack_Type= models.CharField(max_length=50, blank=True, null=True)
    Rack_Type_Information=models.IntegerField(default=0, blank=True, null=True)
    Special_Notes=models.CharField(max_length=200)
    is_delete = models.BooleanField(default=False)
    device_height_array = models.TextField(blank=True, null=True, default='0')
    def __str__(self):
        return self.Rack_Label_Tag

# @receiver(pre_save, sender=User)
# def user_to_inactive(sender, instance, **kwargs):
#     if instance._state.adding is True:
#         instance.is_active = False

class AddDevice(models.Model):
    datacenter = models.ForeignKey(addDataCenter, blank = True, null = True, on_delete=models.CASCADE)
    date_center_row = models.ForeignKey(addDataCenterRow, blank = True, null = True, on_delete=models.CASCADE)
    device_height = models.IntegerField(blank=True, null=True)
    data_center_rack = models.ForeignKey(AddDataCenterRackcabinet, blank = True, null = True, on_delete=models.CASCADE)
    Device_Asset_Tag=models.CharField(max_length=50 ,blank=True, null=True)
    Device_Description=models.CharField(max_length=200 ,blank=True, null=True)
    Unit_Location=models.IntegerField(blank=True, null=True)
    type_of_device = models.CharField(max_length=300 ,blank=True, null=True)

    network_device_category = models.CharField(max_length=50, blank=True, null=True)
    network_sub_category = models.CharField(max_length=50, blank=True, null=True)
    network_number_of_ports = models.IntegerField(blank=True, null=True)
    network_uplink_ports_wan = models.IntegerField(blank=True, null=True)
    network_connection_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    network_connection_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    network_connection_type_both = models.CharField(max_length=50, blank=True, null=True)

    security_device_category = models.CharField(max_length=50, blank=True, null=True)
    security_number_of_ports_lan = models.IntegerField(blank=True, null=True)
    security_network_uplink_ports_wan = models.IntegerField(blank=True, null=True)
    security_connection_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    security_connection_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    security_connection_type_both = models.CharField(max_length=50, blank=True, null=True)

    patch_position = models.CharField(max_length=50, blank=True, null=True)
    patch_port = models.IntegerField(blank=True, null=True) 

    server_number_of_ports = models.IntegerField(blank=True, null=True)
    server_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    server_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    server_type_both = models.CharField(max_length=50, blank=True, null=True)

    chassis_number_of_blades = models.IntegerField(blank=True, null=True)
    chassis_total_blades_slots = models.IntegerField(blank=True, null=True)
    chassis_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    chassis_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    chassis_type_both = models.CharField(max_length=50, blank=True, null=True)

    load_number_of_ports = models.IntegerField(blank=True, null=True)
    load_uplink_ports_wan = models.IntegerField(blank=True, null=True)
    load_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    load_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    # load_type_both = models.CharField(max_length=50, blank=True, null=True)

    storage_number_of_controllers = models.IntegerField(blank=True, null=True)
    storage_number_of_disks = models.IntegerField(blank=True, null=True)
    storage_capicity_range = models.IntegerField(blank=True, null=True)
    storage_capicity_input = models.CharField(max_length=50, blank=True, null=True)
    storage_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    storage_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    storage_type_both = models.CharField(max_length=50, blank=True, null=True)


    tapelib_number_of_magazine = models.IntegerField(blank=True, null=True)
    tapelib_number_io_station = models.IntegerField(blank=True, null=True)
    tapelib_type = models.CharField(max_length=50, blank=True, null=True)
    tapelib_number_tape_capacity = models.IntegerField(blank=True, null=True)
    tapelib_storage_capacity = models.CharField(max_length=50, blank=True, null=True)
    tapelib_space_occupied = models.IntegerField(blank=True, null=True)

    pdu_category = models.CharField(max_length=50, blank=True, null=True)
    pdu_port = models.IntegerField(blank=True, null=True)
    pdu_type = models.CharField(max_length=50, blank=True, null=True)
    pdu_position = models.CharField(max_length=50, blank=True, null=True)

    # PDU from PDU Form
    # pdudevice = models.CharField(max_length=50, blank=True, null=True)
    # pdu_type = models.CharField(max_length=50, blank=True, null=True)
    # pdu_port = models.IntegerField(blank=True, null=True)
    # device = models.CharField(max_length=50, blank=True, null=True)
    # device_port = models.IntegerField(blank=True, null=True)
    # End

    ups_max_loads = models.CharField(max_length=50, blank=True, null=True)
    ups_number_of_power_ports = models.CharField(max_length=50, blank=True, null=True)


    IP_Address_col1=models.PositiveIntegerField(default=1, blank=True, null=True)
    IP_Address_col2=models.PositiveIntegerField(default=1, blank=True, null=True)
    IP_Address_col3=models.PositiveIntegerField(default=1, blank=True, null=True)
    IP_Address_col4=models.PositiveIntegerField(default=1, blank=True, null=True)
    
    deviceMake = models.CharField(max_length=200 ,blank=True, null=True)
    deviceModel = models.CharField(max_length=200 ,blank=True, null=True)
    installDate = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    expiryDate = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    deviceOwner = models.CharField(max_length=200 ,blank=True, null=True)
    ownerDesc = models.CharField(max_length=200 ,blank=True, null=True)
    deviceport = models.IntegerField(blank=True, null=True)
    deviceWatt = models.FloatField(blank=True, default=0.0)
    deviceSupplies = models.IntegerField(blank=True, null=True)
    
    Special_Notes=models.CharField(max_length=200 ,blank=True, null=True)
    power_left = models.BooleanField(default=True)
    power_right = models.BooleanField(default=True)

    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.Device_Asset_Tag

    def ip(self):
        return f"{self.IP_Address_col1}.{self.IP_Address_col2}.{self.IP_Address_col3}.{self.IP_Address_col4}"

    @property
    def remaining_days(self):
        remaining = (self.expiryDate - datetime.datetime.now().date()).days
        return remaining

class DeviceTemplate(models.Model):
    datacenter = models.CharField(max_length=50 ,blank=True, null=True)
    date_center_row = models.CharField(max_length=50 ,blank=True, null=True)
    device_height = models.IntegerField(blank=True, null=True)
    data_center_rack = models.CharField(max_length=50 ,blank=True, null=True)
    Device_Asset_Tag=models.CharField(max_length=50 ,blank=True, null=True)
    Device_Description=models.CharField(max_length=200 ,blank=True, null=True)
    Unit_Location=models.PositiveIntegerField(default=1, blank=True, null=True)
    type_of_device = models.CharField(max_length=300 ,blank=True, null=True)

    network_device_category = models.CharField(max_length=50, blank=True, null=True)
    network_sub_category = models.CharField(max_length=50, blank=True, null=True)
    network_number_of_ports = models.IntegerField(blank=True, null=True)
    network_uplink_ports_wan = models.IntegerField(blank=True, null=True)
    network_connection_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    network_connection_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    network_connection_type_both = models.CharField(max_length=50, blank=True, null=True)

    security_device_category = models.CharField(max_length=50, blank=True, null=True)
    security_number_of_ports_lan = models.IntegerField(blank=True, null=True)
    security_network_uplink_ports_wan = models.IntegerField(blank=True, null=True)
    security_connection_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    security_connection_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    security_connection_type_both = models.CharField(max_length=50, blank=True, null=True)

    patch_position = models.CharField(max_length=50, blank=True, null=True)
    patch_port = models.IntegerField(blank=True, null=True)
    patch_category_type_inter = models.CharField(max_length=50, blank=True, null=True)
    patch_category_type_cross = models.CharField(max_length=50, blank=True, null=True)
    patch_category_type_isp = models.CharField(max_length=50, blank=True, null=True)
    patch_category_type_other = models.CharField(max_length=50, blank=True, null=True)
    path_number_of_ports = models.IntegerField(blank=True, null=True)

    server_number_of_ports = models.IntegerField(blank=True, null=True)
    server_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    server_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    server_type_both = models.CharField(max_length=50, blank=True, null=True)

    chassis_number_of_blades = models.IntegerField(blank=True, null=True)
    chassis_total_blades_slots = models.IntegerField(blank=True, null=True)
    chassis_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    chassis_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    chassis_type_both = models.CharField(max_length=50, blank=True, null=True)

    load_number_of_ports = models.IntegerField(blank=True, null=True)
    load_uplink_ports_wan = models.IntegerField(blank=True, null=True)
    load_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    load_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    # load_type_both = models.CharField(max_length=50, blank=True, null=True)

    storage_number_of_controllers = models.IntegerField(blank=True, null=True)
    storage_number_of_disks = models.IntegerField(blank=True, null=True)
    storage_capicity_range = models.IntegerField(blank=True, null=True)
    storage_capicity_input = models.CharField(max_length=50, blank=True, null=True)
    storage_type_fibre = models.CharField(max_length=50, blank=True, null=True)
    storage_type_ehthernet = models.CharField(max_length=50, blank=True, null=True)
    storage_type_both = models.CharField(max_length=50, blank=True, null=True)


    tapelib_number_of_magazine = models.IntegerField(blank=True, null=True)
    tapelib_number_io_station = models.IntegerField(blank=True, null=True)
    tapelib_type = models.CharField(max_length=50, blank=True, null=True)
    tapelib_number_tape_capacity = models.IntegerField(blank=True, null=True)
    tapelib_storage_capacity = models.CharField(max_length=50, blank=True, null=True)
    tapelib_space_occupied = models.IntegerField(blank=True, null=True)

    pdu_category = models.CharField(max_length=50, blank=True, null=True)
    pdu_number_of_power_ports = models.CharField(max_length=50, blank=True, null=True)
    pdu_type = models.CharField(max_length=50, blank=True, null=True)
    pdu_position = models.CharField(max_length=50, blank=True, null=True)

    ups_max_loads = models.CharField(max_length=50, blank=True, null=True)
    ups_number_of_power_ports = models.CharField(max_length=50, blank=True, null=True)


    IP_Address_col1=models.PositiveIntegerField(default=1, blank=True, null=True)
    IP_Address_col2=models.PositiveIntegerField(default=1, blank=True, null=True)
    IP_Address_col3=models.PositiveIntegerField(default=1, blank=True, null=True)
    IP_Address_col4=models.PositiveIntegerField(default=1, blank=True, null=True)
    
    deviceMake = models.CharField(max_length=200 ,blank=True, null=True)
    deviceModel = models.CharField(max_length=200 ,blank=True, null=True)
    installDate = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    expiryDate = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    deviceOwner = models.CharField(max_length=200 ,blank=True, null=True)
    ownerDesc = models.CharField(max_length=200 ,blank=True, null=True)
    deviceport = models.IntegerField(blank=True, null=True)
    deviceWatt = models.FloatField(blank=True, default=0.0)
    deviceSupplies = models.IntegerField(blank=True, null=True)
    
    Special_Notes=models.CharField(max_length=200 ,blank=True, null=True)
    status = models.BooleanField(default=True)

    templatename = models.CharField(max_length=200 ,blank=True, null=True)

    def __str__(self):
        return str(self.templatename)
    
class DeviceDetails(models.Model):
    device = models.ForeignKey(AddDevice, blank = True, null = True, on_delete=models.CASCADE)
    power_on = models.BooleanField(default=False)
    power_off = models.BooleanField(default=False)
    patchpanel_incoming = models.IntegerField(blank=True, null=True)
    patchpanel_outgoing = models.IntegerField(blank=True, null=True)


# class RR(models.Model):
#     RackRow = models.CharField(max_length=50)
#     rack_label = models.CharField(max_length=50)
#     rack_label_colour = models.CharField(max_length=50)
#     assest_tag = models.CharField(max_length=15, unique=True)
#     make_and_model = models.CharField(max_length=50)
#     rack_type = models.CharField(max_length=50)
#     client_department = models.CharField(max_length=50)
#     patch_panels = models.CharField(max_length=50)
#     power_load = models.CharField(max_length=50)
#     special_notes = models.TextField()

#     def __str__(self):
#         return self.assest_tag
class DeviceSetting(models.Model):
    is_blink = models.BooleanField(default=True)
    cpu_threshold = models.FloatField(default=80)
    usedRam = models.FloatField(default=80)
    usedSMemory = models.FloatField(default=80)
    usedStorage = models.FloatField(default=80)
    iowait = models.FloatField(default=50)
    temperature = models.FloatField(default=85)
    footer = models.CharField(default="Made with <img src='/static/dashboard/images/heart.png'> in <img src='/static/dashboard/images/india.png'>", max_length=200)
    country = models.CharField(max_length=50, blank=True, null=True, default="india")
    def __str__(self):
        return str(self.is_blink)

class SnmpDeviceSetting(models.Model):
    ip = models.CharField(max_length=50)
    cpu_threshold = models.FloatField(default=40)
    usedRam = models.FloatField(default=50)
    usedSMemory = models.FloatField(default=20)
    usedStorage = models.FloatField(default=50)
    def __str__(self):
        return str(self.ip)

class Notif(models.Model):
    # user = models.ForeignKey(User, blank = True, null = True, on_delete=models.CASCADE)
    # name = models.CharField(max_length=50,blank=True, null=True)
    parent = models.CharField(max_length=50,blank=True, null=True)
    title = models.CharField(max_length=50,blank=True, null=True)
    data = models.TextField(max_length=50,blank=True, null=True)
    content = models.TextField(max_length=100,blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_delete = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_raised = models.BooleanField(default=False)
    SEVERITY_CHOICES = (
    ("high", "High"),
    ("medium", "Medium"),
    ("low", "Low"),
    ("predictive", "Predictive"),
    ("future", "Future"),
    )
    severity = models.CharField(max_length=50, choices=SEVERITY_CHOICES, default = 'low')
    def __str__(self):
        return self.title

class PatchPanel(models.Model):
    rack = models.ForeignKey(AddDataCenterRackcabinet, blank = True, null = True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    incoming = models.BooleanField(default=False)
    outgoing = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class PatchPanelPort(models.Model):
    patchpanel = models.ForeignKey(AddDevice, blank = True, null = True, on_delete=models.CASCADE, related_name="patchpanel")
    device = models.ForeignKey(AddDevice, blank = True, null = True, on_delete=models.CASCADE)
    # rack = 
    port = models.IntegerField(blank=True, null=True)
    information = models.CharField(max_length=50, blank=True, null=True)
    #dropdown of incom outgo
    in_out = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.patchpanel)
class PduPortForm(models.Model):
    rack = models.ForeignKey(AddDataCenterRackcabinet, blank = True, null = True, on_delete=models.CASCADE)
    pdudevice = models.ForeignKey(AddDevice, blank = True, null = True, on_delete=models.CASCADE, related_name="pdudevice")
    pdu_type = models.CharField(max_length=50, blank=True, null=True)
    pdu_port = models.IntegerField(blank=True, null=True)
    device = models.ForeignKey(AddDevice, blank = True, null = True, on_delete=models.CASCADE)
    device_port = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.pdu_type)

# class Uptime(models.Model):
#     startingTime=models.DateTimeField()

# class ProcessUtil(models.Model):
#     time=models.DateTimeField(auto_now_add=True)
#     utilpercentage=models.FloatField(default=0.0)

#     def __str__(self):
#         return str(self.utilpercentage)


# class Browser(models.Model):
#     chrome=models.FloatField(default=0.0)
#     firefox=models.FloatField(default=0.0)
#     mozilla=models.FloatField(default=0.0)
#     safari=models.FloatField(default=0.0)
#     others=models.FloatField(default=0.0)

# class Series(models.Model):
#     series1=models.FloatField(default=0.0)
#     series2=models.FloatField(default=0.0)



# class Test1(models.Model):
#     testname=models.CharField(max_length=20 , default=True)
    

# class gitTest(models.Model):
#     series1=models.FloatField(default=0.0)
#     series2=models.FloatField(default=0.0)

# class ServerData(models.Model):
#     user_id = models.ForeignKey(User , on_delete=models.CASCADE)
#     server_data = models.CharField(max_length=30000)
#     function_name = models.CharField(max_length=100 , default="config")
#     date_time = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return str(self.date_time)

class DeviceCapibility(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    ip = models.CharField(max_length=50, blank=True, null=True)
    user = models.CharField(max_length=50, blank=True, null=True)
    pwd = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated = models.DateTimeField(auto_now=False,blank=True,null=True)
    is_snmp = models.BooleanField(default=False, )
    is_netconf = models.BooleanField(default=False)
    is_restconf = models.BooleanField(default=False)

    snmp = models.TextField(blank=True, null=True)
    commString = models.CharField(max_length=50, blank=True, null=True)
    snmpv3user = models.CharField(max_length=50, blank=True, null=True)
    snmpv3auth = models.CharField(max_length=50, blank=True, null=True)
    snmpv3pass = models.CharField(max_length=50, blank=True, null=True)
    netconf = models.TextField(blank=True, null=True)
    restconf = models.TextField(blank=True, null=True)
    schedule = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    is_fav = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    dbuser = models.CharField(max_length=50, blank=True, null=True)
    dbpwd = models.CharField(max_length=50, blank=True, null=True)
    dbname = models.CharField(max_length=50, blank=True, null=True)
    dbport = models.CharField(max_length=50, blank=True, null=True, default=5432)

    def __str__(self):
        return self.ip

class ContactUs(models.Model):
    fname = models.CharField(max_length=50, blank=True, null=True)
    lname = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    msg = models.TextField(blank=True, null=True)
    def __str__(self):
        return "Message from "+self.fname

class RaiseTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, blank=True, null=True)
    img = models.ImageField(upload_to='ticket/', blank=True, null=True)
    subject = models.CharField(max_length=50)
    msg = models.TextField()
    admin_response = models.CharField(max_length=500, blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="assigned_users", blank=True, null=True)
    accepted = models.BooleanField(default=False)
    is_aprove = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return "Message from " + str(self.id)
    

class AnsibleOutput(models.Model):
    result = models.CharField(max_length=10000)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date_time)


class SSHServers(models.Model):
    host = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    packages = models.CharField(max_length=2000)

    def __str__(self):
        return str(self.host)


class Cabels(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.name)

class ApplianceDataCollection(PostgresPartitionedModel):
    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["created_at"]
    data = models.CharField(blank=True, null=True, max_length=50)
    type = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.type

class DashboardDataCollection(models.Model):
    data = models.CharField(blank=True, null=True, max_length=50)
    type = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.type

class TestModal(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    value = models.IntegerField()
    type = models.TextField(max_length=100 , default="" , null=True,blank=True)
    valueArr = models.TextField(max_length=10000 , default="" , null=True , blank=True)
    def __str__(self):
        return str(self.created_at)
    

class SNMPDataCollection(PostgresPartitionedModel):
    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["created_at"]

    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    ip = models.TextField(max_length=50 , default="")
    name = models.TextField(max_length=100 , default="")
    description = models.TextField(max_length=100 , default="")
    contact = models.TextField(max_length=100 , default="")
    location = models.TextField(max_length=100 , default="")
    oid = models.TextField(max_length=100 , default="")
    uptime = models.IntegerField(default=0)

    # cpu 
    cpu = models.TextField(max_length=100 , default="")
    ram = models.TextField(max_length=100 , default="")
    virtual = models.TextField(max_length=100 , default="")
    storage = models.TextField(max_length=100 , default="")
    interfaces = models.TextField(default="")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.ip)


class SNMPInterfaceDataCollection(PostgresPartitionedModel):
    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["created_at"]
        
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    ip = models.TextField(max_length=50 , default="")
    name = models.TextField(max_length=100 , default="")
    description = models.TextField(max_length=100 , default="")
    mac = models.TextField(max_length=50 , default="")
    admin = models.TextField(max_length=10 , default="")
    port = models.TextField(max_length=10 , default="")
    inbound = models.FloatField(default=0)
    outbound = models.FloatField(default=0)
    mtu = models.IntegerField(default=0)
    speed = models.FloatField(default=0)
    errorin = models.IntegerField(default=0)
    errorout = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.ip)
# 10 , 10 , 60 , 20 , 40 , 60 = 200 / 6 =

class License(models.Model):
    key = models.CharField(max_length=50, unique=True)
    duration = models.IntegerField()
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(auto_now=False)
    status = models.BooleanField(default=False)
    def __str__(self):
        return str(self.key)

class MyDevice(models.Model):
    ip = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    contact = models.CharField(max_length=500, blank=True, null=True)
    Location = models.CharField(max_length=50, blank=True, null=True)
    type_of_device = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return str(self.ip)

class MyDeviceSNMPData(models.Model):
    device = models.ForeignKey(MyDevice, on_delete=models.CASCADE)
    uptime = models.BigIntegerField(default=0)
    storage_total = models.FloatField(default=0)
    storage_used = models.FloatField(default=0)
    storage_available = models.FloatField(default=0)
    ram_total = models.FloatField(default=0)
    ram_used = models.FloatField(default=0)
    ram_available = models.FloatField(default=0)
    swap_total = models.FloatField(default=0)
    swap_used = models.FloatField(default=0)
    swap_available = models.FloatField(default=0)
    cpu = models.CharField(max_length=500, default="") 
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.device)

class MyDeviceSNMPInterface(models.Model):
    deviceData = models.ForeignKey(MyDeviceSNMPData, on_delete=models.CASCADE)
    ifindex = models.BigIntegerField(default=0)
    inOctect = models.BigIntegerField(default=0)
    outOctect = models.BigIntegerField(default=0)
    inErr = models.BigIntegerField(default=0)
    name = models.CharField(max_length=500, default="")
    outErr = models.BigIntegerField(default=0)
    mtu = models.BigIntegerField(default=0)
    speed = models.BigIntegerField(default=0)
    mac = models.CharField(max_length=500, default="")
    adminstatus = models.CharField(max_length=50, default="down")
    operstatus = models.CharField(max_length=50, default="down")
    description = models.CharField(max_length=500, default="")
    def __str__(self):
        return str(self.deviceData)


class AssetPage(models.Model):
    def __str__(self):
        return str(self.id)

class NetworkSummary(models.Model):
    def __str__(self):
        return str(self.id)
        
class ServerSummary(models.Model):
    def __str__(self):
        return str(self.id)

class DatabaseSummary(models.Model):
    def __str__(self):
        return str(self.id)

class StorageSummary(models.Model):
    def __str__(self):
        return str(self.id)
        
class CCTV(models.Model):
    def __str__(self):
        return str(self.id)

class WebMonitoring(models.Model):
    def __str__(self):
        return str(self.id)

class Reports(models.Model):
    def __str__(self):
        return str(self.id)

class APM(models.Model):
    def __str__(self):
        return str(self.id)

class Settings(models.Model):
    def __str__(self):
        return str(self.id)

class Dashboard(models.Model):
    def __str__(self):
        return str(self.id)

class Appliance(models.Model):
    def __str__(self):
        return str(self.id)

class Topology(models.Model):
    type = models.CharField(max_length=50, default="topo2")