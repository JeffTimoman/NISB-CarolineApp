from flask import Blueprint, request, url_for, redirect, render_template, flash, send_from_directory, abort, current_app
from flask import url_for, redirect, request, jsonify
from webdata import db
from webdata.models import SummaryBandwith
from webdata.config import Config
import os

main = Blueprint('main', __name__)

@main.route('/', methods=["GET"])
def index():
    return render_template("index.html")

@main.route('/history', methods=["GET"])
def history():
    return render_template("history.html")

@main.route('/api/summary_bandwiths', methods=["GET"])
def api_summary_bandwiths():
    # Get page and per_page from query string, default to 1 and 5
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    pagination = SummaryBandwith.query.order_by(SummaryBandwith.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = [{
        'id': s.id,
        'name': s.name,
        'pdf_filename': s.pdf_filename,
        'pdf_original_name': s.pdf_original_name,
        'csv_filename': s.csv_filename,
        'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': s.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
    } for s in pagination.items]
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

@main.route('/download/pdf/<id>')
def download_pdf(id):
    generation = SummaryBandwith.query.get_or_404(id)
    if not generation.pdf_filename:
        abort(404)
    pdf_path = os.path.join(current_app.static_folder, Config.PDF_FOLDER_PATH, generation.pdf_filename)
    if not os.path.exists(pdf_path):
        abort(404)
    # Send with original name
    return send_from_directory(
        directory=os.path.join(current_app.static_folder, Config.PDF_FOLDER_PATH),
        path=generation.pdf_filename,
        as_attachment=True,
        download_name=generation.pdf_original_name or generation.pdf_filename
    )

@main.route('/download/csv/<id>')
def download_csv(id):
    generation = SummaryBandwith.query.get_or_404(id)
    if not generation.csv_filename:
        abort(404)
    csv_path = os.path.join(current_app.static_folder, Config.CSV_FOLDER_PATH, generation.csv_filename)
    if not os.path.exists(csv_path):
        abort(404)

    safe_name = "".join(c for c in generation.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    download_name = f"{safe_name}.csv"
    return send_from_directory(
        directory=os.path.join(current_app.static_folder, Config.CSV_FOLDER_PATH),
        path=generation.csv_filename,
        as_attachment=True,
        download_name=download_name
    )

@main.route('/api/summary_bandwiths/<id>/name', methods=['PUT'])
def update_summary_bandwith_name(id):
    data = request.get_json()
    new_name = data.get('name')
    if not new_name or not new_name.strip():
        return jsonify({'error': 'Name is required'}), 400

    summary = SummaryBandwith.query.get(id)
    if not summary:
        return jsonify({'error': 'Not found'}), 404

    summary.name = new_name.strip()
    db.session.commit()
    return jsonify({'success': True, 'name': summary.name})

