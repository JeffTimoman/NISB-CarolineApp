from flask import Blueprint, request, url_for, redirect, render_template, flash
from flask import url_for, redirect, request, jsonify, current_app
from werkzeug.utils import secure_filename
from webdata import db, Config

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

	filename = secure_filename(file.filename)

	# ensure excel folder exists (use project root from Config)
	excel_folder = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), Config.EXCEL_FOLDER_PATH)
	os.makedirs(excel_folder, exist_ok=True)

	saved_path = os.path.join(excel_folder, filename)
	file.save(saved_path)

	try:
		parsed = parse_ip_allocation_excel(saved_path)
	except Exception as e:
		return jsonify({'success': False, 'message': f'Failed to parse excel: {str(e)}'}), 400

	# Build models
	ipalloc = IpAllocation(
		start_ip=parsed.get('start_ip'),
		provider=parsed.get('provider'),
		original_excel_name=file.filename,
		excel_filename=filename,
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


@ip_allocation.route('/detail')
def detail():
	"""Render detail page for a saved IpAllocation. Query param: id"""
	from flask import render_template, request, abort
	from webdata.models import IpAllocation

	alloc_id = request.args.get('id')
	if not alloc_id:
		abort(400, description='Missing id')

	ipalloc = IpAllocation.query.filter_by(id=alloc_id).first()
	if not ipalloc:
		abort(404, description='IpAllocation not found')

	# ensure details sorted by order
	details = sorted(ipalloc.details, key=lambda d: (d.order or 0))

	return render_template('ip_allocation/detail.html', ipalloc=ipalloc, details=details)
