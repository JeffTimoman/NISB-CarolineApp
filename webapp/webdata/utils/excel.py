import openpyxl
from datetime import datetime


def _cell(ws, coord):
	"""Helper: safe cell value extraction."""
	cell = ws[coord]
	return cell.value if cell is not None else None


def _col_row(ws, col, row):
	return _cell(ws, f"{col}{row}")


def _try_parse_date(val):
	if val is None:
		return None
	if isinstance(val, datetime):
		return val
	if isinstance(val, str):
		s = val.strip()
		# try several common formats
		fmts = [
			"%Y-%m-%d %H:%M:%S",
			"%Y-%m-%d",
			"%d/%m/%Y",
			"%d-%m-%Y",
			"%m/%d/%Y",
			"%d %b %Y",
			"%b %d, %Y",
			"%d %B %Y",
		]
		for f in fmts:
			try:
				return datetime.strptime(s, f)
			except Exception:
				continue
	# fallback: return None
	return None


def parse_ip_allocation_excel(path):
	"""Parse the specified Excel file and return a dict with:
	{ start_ip, provider, details: [ {location,address,lat,long,pic_bca,pic_bca_phone,online_date}, ... ] }

	The function expects the layout described by the user:
	  - F3: start_ip
	  - F4: provider
	  - Rows starting at 7: C=location, D=address, E=lat, F=long, G=pic_bca, H=phone, I=online_date
	"""
	wb = openpyxl.load_workbook(path, data_only=True)
	ws = wb.active

	start_ip = _col_row(ws, 'F', 3)
	provider = _col_row(ws, 'F', 4)

	details = []
	row = 7
	while True:
		loc = _col_row(ws, 'C', row)
		# stop when location and address and lat are all empty (tunable)
		addr = _col_row(ws, 'D', row)
		lat = _col_row(ws, 'E', row)
		long = _col_row(ws, 'F', row)
		pic = _col_row(ws, 'G', row)
		phone = _col_row(ws, 'H', row)
		online_raw = _col_row(ws, 'I', row)

		if all([v is None or (isinstance(v, str) and v.strip() == '') for v in (loc, addr, lat, long, pic, phone, online_raw)]):
			break

		online_date = _try_parse_date(online_raw)

		details.append({
			'location': loc,
			'address': addr,
			'lat': str(lat) if lat is not None else None,
			'long': str(long) if long is not None else None,
			'pic_bca': pic,
			'pic_bca_phone': phone,
			'online_date': online_date,
		})

		row += 1

	return {
		'start_ip': start_ip,
		'provider': provider,
		'details': details,
	}
