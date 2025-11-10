from flask import Blueprint, request, url_for, redirect, render_template, flash
from flask import url_for, redirect, request, jsonify, current_app
from werkzeug.utils import secure_filename
from webdata import db, Config
from webdata.models import IpAllocation

ip_allocation = Blueprint('ip_allocation', __name__)

@ip_allocation.route("/upload_file", methods=["POST"])
def upload_file():
	"""Handle uploaded Excel for IP allocation.

	Expects a file in the form field named 'file'.
	Reads:
	  - start_ip from cell F3
	  - provider from cell F4
	  - details from rows starting at row 7 with columns:
		  C: location, D: address, E: lat, F: long, G: pic_bca, H: phone, I: online_date

	Creates an IpAllocation and associated IpAllocationDetail records.
	Returns JSON with success or error message.
	"""
	from flask import current_app
	import os
	from webdata.models import IpAllocation, IpAllocationDetail
	from webdata.utils.excel import parse_ip_allocation_excel
	# validate file
	if 'file' not in request.files:
		return jsonify({'success': False, 'message': 'No file part in request'}), 400

	file = request.files['file']
	if file.filename == '':
		return jsonify({'success': False, 'message': 'No selected file'}), 400

	orig_filename = file.filename
	# create a safe original filename for extension extraction
	safe_orig = secure_filename(orig_filename)
	# generate a uuid filename to store on disk, keep original extension if present
	import uuid as _uuid
	_, ext = os.path.splitext(safe_orig)
	stored_filename = f"{str(_uuid.uuid4())}{ext}"

	# ensure excel folder exists (use project root from Config)
	excel_folder = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), Config.EXCEL_FOLDER_PATH)
	os.makedirs(excel_folder, exist_ok=True)

	saved_path = os.path.join(excel_folder, stored_filename)
	file.save(saved_path)

	try:
		parsed = parse_ip_allocation_excel(saved_path)
	except Exception as e:
		return jsonify({'success': False, 'message': f'Failed to parse excel: {str(e)}'}), 400

	# Build models
	ipalloc = IpAllocation(
		start_ip=parsed.get('start_ip'),
		provider=parsed.get('provider'),
		original_excel_name=orig_filename,
		excel_filename=stored_filename,
	)

	details = []
	for idx, d in enumerate(parsed.get('details', []), start=1):
		detail = IpAllocationDetail(
			order=idx,
			location=d.get('location'),
			address=d.get('address'),
			lat=d.get('lat'),
			long=d.get('long'),
			pic_bca=d.get('pic_bca'),
			pic_bca_phone=d.get('pic_bca_phone'),
			online_date=d.get('online_date'),
		)
		details.append(detail)

	# attach and commit
	ipalloc.details = details
	db.session.add(ipalloc)
	db.session.commit()

	# Prepare response including parsed extraction so frontend can show details
	response_parsed = {
		'success': True,
		'id': ipalloc.id,
		'message': 'Uploaded and saved successfully',
		'start_ip': parsed.get('start_ip'),
		'provider': parsed.get('provider'),
		'details': [],
	}

	from datetime import datetime
	for d in parsed.get('details', []):
		online = d.get('online_date')
		if isinstance(online, datetime):
			online_val = online.isoformat()
		else:
			online_val = online
		response_parsed['details'].append({
			'location': d.get('location'),
			'address': d.get('address'),
			'lat': d.get('lat'),
			'long': d.get('long'),
			'pic_bca': d.get('pic_bca'),
			'pic_bca_phone': d.get('pic_bca_phone'),
			'online_date': online_val,
		})

	return jsonify(response_parsed)


@ip_allocation.route('/detail', methods=['GET'])
def detail():
	"""View-only detail page for a saved IpAllocation. Query param: id"""
	from flask import render_template, request, abort, url_for
	from webdata.models import IpAllocation
	import ipaddress

	alloc_id = request.args.get('id')
	if not alloc_id:
		abort(400, description='Missing id')

	ipalloc = IpAllocation.query.filter_by(id=alloc_id).first()
	if not ipalloc:
		abort(404, description='IpAllocation not found')

	details = sorted(ipalloc.details, key=lambda d: (d.order or 0))

	# Compute sequential start/end IPs for each detail based on ipalloc.start_ip and each detail.mask
	allocations = []
	try:
		current = ipaddress.IPv4Address(ipalloc.start_ip) if ipalloc.start_ip else None
	except Exception:
		current = None

	for d in details:
		assigned_start = None
		assigned_end = None
		gateway = None
		atm_start = None
		atm_end = None
		subnetmask = None
		prefix_int = None
		if current is not None:
			# determine prefix from mask (expect format like '/29' or '29')
			mask = (d.mask or '').strip()
			if mask.startswith('/'):
				prefix = mask[1:]
			else:
				prefix = mask
			try:
				prefix_int = int(prefix)
				# number of addresses in the block
				block_size = 2 ** (32 - prefix_int) if 0 <= prefix_int <= 32 else None
			except Exception:
				block_size = None

			if block_size:
				assigned_start = ipaddress.IPv4Address(int(current))
				assigned_end = ipaddress.IPv4Address(int(current) + block_size - 1)

				# compute network and hosts using ipaddress to get gateway and usable host ranges
				try:
					network = ipaddress.ip_network(f"{assigned_start}/{prefix_int}", strict=False)
					hosts = list(network.hosts())  # usable hosts
					if hosts:
						gateway = hosts[0]  # first usable as gateway
					if len(hosts) >= 2:
						atm_start = hosts[1]
						atm_end = hosts[-1]
					elif len(hosts) == 1:
						atm_start = hosts[0]
						atm_end = hosts[0]
					subnetmask = str(network.netmask)
				except Exception:
					gateway = None
					atm_start = None
					atm_end = None
					subnetmask = None

				# advance current to next address after this block
				current = ipaddress.IPv4Address(int(current) + block_size)

		allocations.append({
			'detail': d,
			'start_ip': str(assigned_start) if assigned_start is not None else None,
			'end_ip': str(assigned_end) if assigned_end is not None else None,
			'gateway': str(gateway) if gateway is not None else None,
			'atm_start': str(atm_start) if atm_start is not None else None,
			'atm_end': str(atm_end) if atm_end is not None else None,
			'subnetmask': subnetmask,
			'prefix': prefix_int,
		})

	return render_template('ip_allocation/detail.html', ipalloc=ipalloc, details=details, allocations=allocations)


@ip_allocation.route('/edit', methods=['GET', 'POST'])
def edit():
	"""Edit page for IpAllocation. GET shows editable form; POST saves changes."""
	from flask import render_template, request, abort, redirect, url_for, flash
	from webdata.models import IpAllocation
	from datetime import datetime

	alloc_id = request.args.get('id') or request.form.get('ipalloc_id')
	if not alloc_id:
		abort(400, description='Missing id')

	ipalloc = IpAllocation.query.filter_by(id=alloc_id).first()
	if not ipalloc:
		abort(404, description='IpAllocation not found')

	if request.method == 'POST':
		# update fields for each detail
		for d in ipalloc.details:
			prefix = f"{d.id}"
			d.location = request.form.get(f'location-{prefix}')
			d.address = request.form.get(f'address-{prefix}')
			d.lat = request.form.get(f'lat-{prefix}')
			d.long = request.form.get(f'long-{prefix}')
			d.pic_bca = request.form.get(f'pic_bca-{prefix}')
			d.pic_bca_phone = request.form.get(f'pic_bca_phone-{prefix}')
			mask = request.form.get(f'mask-{prefix}')
			if mask is not None:
				d.mask = mask
			d.bandwidth = request.form.get(f'bandwidth-{prefix}')
			d.quota = request.form.get(f'quota-{prefix}')
			# order can be provided by the form (order-<id>) when rows are reordered in the UI
			order_raw = request.form.get(f'order-{prefix}')
			if order_raw:
				try:
					d.order = int(order_raw)
				except Exception:
					pass

			online_raw = request.form.get(f'online_date-{prefix}')
			if online_raw:
				try:
					dt = datetime.fromisoformat(online_raw)
				except Exception:
					try:
						dt = datetime.strptime(online_raw, '%Y-%m-%dT%H:%M')
					except Exception:
						dt = None
				d.online_date = dt
			else:
				d.online_date = None

		db.session.commit()
		flash('Changes saved', 'success')
		return redirect(url_for('ip_allocation.detail') + '?id=' + alloc_id)

	# GET
	details = sorted(ipalloc.details, key=lambda d: (d.order or 0))
	return render_template('ip_allocation/edit.html', ipalloc=ipalloc, details=details)


@ip_allocation.route('/api/ip_allocations', methods=['GET'])
def api_ip_allocations():
	"""Return paginated IpAllocation items for the history UI.

	Query params: page (int), per_page (int)
	"""
	page = request.args.get('page', 1, type=int)
	per_page = request.args.get('per_page', 5, type=int)
	pagination = IpAllocation.query.order_by(IpAllocation.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
	items = [{
		'id': a.id,
		'start_ip': a.start_ip,
		'provider': a.provider,
		'original_excel_name': getattr(a, 'original_excel_name', None),
		'excel_filename': getattr(a, 'excel_filename', None),
		'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S') if getattr(a, 'created_at', None) else None,
		'updated_at': a.updated_at.strftime('%Y-%m-%d %H:%M:%S') if getattr(a, 'updated_at', None) else None,
	} for a in pagination.items]

	return jsonify({
		'items': items,
		'page': pagination.page,
		'pages': pagination.pages,
		'has_next': pagination.has_next,
		'has_prev': pagination.has_prev,
		'next_num': pagination.next_num,
		'prev_num': pagination.prev_num,
		'total': pagination.total
	})
