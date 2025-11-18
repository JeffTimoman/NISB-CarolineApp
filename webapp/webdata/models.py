from webdata import db
import uuid
from datetime import datetime


def default_name():
    return f"Summary Bandwith - {datetime.now().strftime('%d:%m:%y %H:%M')}"


def default_ipalloc_name():
    return f"IP Allocation - {datetime.now().strftime('%d:%m:%y %H:%M')}"

class SummaryBandwith(db.Model):
    __tablename__ = "summarybandwiths"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(100), default=default_name)
    pdf_filename = db.Column(db.String(100))
    pdf_original_name = db.Column(db.String(4000))
    csv_filename = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
class IpAllocation(db.Model):
    __tablename__ = "ipallocations"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(200), default=default_ipalloc_name)
    start_ip = db.Column(db.String(50))
    provider = db.Column(db.String(100))
    details = db.relationship("IpAllocationDetail", backref="ipallocation", cascade="all, delete-orphan", lazy=True)
    
    original_excel_name = db.Column(db.String(4000))
    excel_filename = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
class IpAllocationDetail(db.Model):
    __tablename__ = "ipallocationdetails"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    ip_allocation_id = db.Column(db.String(36), db.ForeignKey("ipallocations.id", ondelete='CASCADE'))
    order = db.Column(db.Integer)
    
    # Given in excel
    location = db.Column(db.String(100))
    address = db.Column(db.String(200))
    lat = db.Column(db.String(50))
    long = db.Column(db.String(50))
    pic_bca = db.Column(db.String(100))
    pic_bca_phone = db.Column(db.String(50))
    online_date = db.Column(db.DateTime, nullable=True)
    
    
    #Default to be filled
    mask = db.Column(db.String(10), default="/29")
    bandwidth = db.Column(db.String(50), default="64 Kbps")
    quota = db.Column(db.String(50), default="1 Gb")
    
    start_ip = db.Column(db.String(50), default="-")
    end_ip = db.Column(db.String(50), default="-")
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    
    
    
    
# class GenerationDetail(db.Model):
#     __tablename__ = "generationdetails"
#     id = db.Column(db.String(36), primary_key=True, default=lambda:str(uuid.uuid4()), unique=True, nullable=False)    
#     generation_id = db.Column(db.String(36), db.ForeignKey("generations.id", ondelete='CASCADE'))
#     order = db.Column(db.Integer)

#     title = db.Column(db.String(100))
#     time_range = db.Column(db.String(100))
#     source_device = db.Column(db.String(100))
#     source_device_ip = db.Column(db.String(50))
#     in_interface = db.Column(db.String(50))
#     description = db.Column(db.String(200))
#     speed = db.Column(db.String(50))
#     dest_subnet = db.Column(db.String(50))
#     dest_mask = db.Column(db.String(10))
#     peak_traffic_rate = db.Column(db.String(50))
#     peak_traffic_time = db.Column(db.String(50))
#     average_traffic = db.Column(db.String(50))
#     average_data = db.Column(db.String(50))

'''
{'Title': 'BCA Finance Cabang Denpasar 1', 'Time Range': 'Jul 22, 2025, 8:00 AM WIB - 5:00 PM WIB', 'Source Device': 'A04-KUT-R1.intra.bca.co.id', 'Source Device IP': '10.96.33.139', 'In Interface': 'Tunnel10', 'Description': '*** MPLS INDOSAT ***', 'Speed': '30 Mbps', 'Dest Subnet': '10.97.51.0/24', 'Dest Mask': '24', 'Peak Traffic Rate': '7.71Mbps', 'Peak Traffic Time': '9:20 AM for 1m', 'Average Traffic': '389.67kbps', 'Average Data': '1.47 GB'}'''

'''
ocr_dict = {
    'Title': 'BCA Finance Cabang Denpasar 1',
    'Time Range': 'Jul 22, 2025, 8:00 AM WIB - 5:00 PM WIB',
    'Source Device': 'A04-KUT-R1.intra.bca.co.id',
    'Source Device IP': '10.96.33.139',
    'In Interface': 'Tunnel10',
    'Description': '*** MPLS INDOSAT ***',
    'Speed': '30 Mbps',
    'Dest Subnet': '10.97.51.0/24',
    'Dest Mask': '24',
    'Peak Traffic Rate': '7.71Mbps',
    'Peak Traffic Time': '9:20 AM for 1m',
    'Average Traffic': '389.67kbps',
    'Average Data': '1.47 GB'
}

detail = GenerationDetail(
    title=ocr_dict['Title'],
    time_range=ocr_dict['Time Range'],
    source_device=ocr_dict['Source Device'],
    source_device_ip=ocr_dict['Source Device IP'],
    in_interface=ocr_dict['In Interface'],
    description=ocr_dict['Description'],
    speed=ocr_dict['Speed'],
    dest_subnet=ocr_dict['Dest Subnet'],
    dest_mask=ocr_dict['Dest Mask'],
    peak_traffic_rate=ocr_dict['Peak Traffic Rate'],
    peak_traffic_time=ocr_dict['Peak Traffic Time'],
    average_traffic=ocr_dict['Average Traffic'],
    average_data=ocr_dict['Average Data'],
    # generation_id=...,
    # order=...,
)
db.session.add(detail)
db.session.commit()
'''