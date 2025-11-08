from flask import Blueprint, request, url_for, redirect, render_template, flash
from flask import url_for, redirect, request, jsonify, current_app
from werkzeug.utils import secure_filename
from webdata import db, Config
from webdata.models import SummaryBandwith
from webdata.utils.ocr import ocr_image, parse_ocr_result
from webdata.utils.pdf import combine_pdfs, convert_pdf_to_png_parallel

import shutil
import os
import csv
import re
import uuid
import concurrent.futures
summary_bandwith = Blueprint('summary_bandwith', __name__)

# ... (upload_file function remains the same) ...
@summary_bandwith.route("/upload_file", methods=["POST"])
def upload_file():
    # ... NO CHANGES NEEDED HERE ...
    files = request.files.getlist('pdf')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No selected file', 'details': 'No file was selected.'}), 400

    allowed_exts = ['.pdf']
    allowed_mimes = ['application/pdf']

    pdf_folder = os.path.join(current_app.static_folder, Config.PDF_FOLDER_PATH)
    os.makedirs(pdf_folder, exist_ok=True)

    saved_pdf_paths = []
    original_filenames = []

    for file in files:
        original_filename = secure_filename(file.filename)
        file_ext = os.path.splitext(original_filename)[1].lower()
        if file_ext not in allowed_exts or file.mimetype not in allowed_mimes:
            return jsonify({'error': 'Invalid file type', 'details': f'File {original_filename} is not a valid PDF.'}), 400
        uuid_filename = f"{uuid.uuid4()}{file_ext}"
        pdf_path = os.path.join(pdf_folder, uuid_filename)
        file.save(pdf_path)
        print(f"Saved file: {pdf_path}, size: {os.path.getsize(pdf_path)} bytes")
        saved_pdf_paths.append(pdf_path)
        original_filenames.append(original_filename)

    # Combine if more than one
    if len(saved_pdf_paths) > 1:
        combined_uuid = f"{uuid.uuid4()}.pdf"
        combined_pdf_path = os.path.join(pdf_folder, combined_uuid)
        try:
            combine_pdfs(saved_pdf_paths, combined_pdf_path)
        except Exception as e:
            return jsonify({'error': 'PDF combine error', 'details': str(e)}), 400
        pdf_filename = combined_uuid
        pdf_original_name = ', '.join(original_filenames)
        for p in saved_pdf_paths:
            os.remove(p)
    else:
        pdf_filename = os.path.basename(saved_pdf_paths[0])
        pdf_original_name = original_filenames[0]

    generation = SummaryBandwith(
        pdf_filename=pdf_filename,
        pdf_original_name=pdf_original_name
    )
    db.session.add(generation)
    db.session.commit()

    return jsonify({'id': generation.id})


@summary_bandwith.route("/generate_csv", methods=["POST"])
def generate_csv():
    data = request.get_json()
    generation_id = data.get('id')
    if not generation_id:
        return jsonify({'error': 'Missing id', 'details': 'No generation ID provided.'}), 400

    generation = SummaryBandwith.query.get(generation_id)
    if not generation:
        return jsonify({'error': 'Not found', 'details': f'No generation found for ID {generation_id}.'}), 404

    pdf_folder = os.path.join(current_app.static_folder, Config.PDF_FOLDER_PATH)
    temp_folder = os.path.join(current_app.static_folder, Config.TEMP_FOLDER)
    csv_folder = os.path.join(current_app.static_folder, Config.CSV_FOLDER_PATH)
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(csv_folder, exist_ok=True)

    pdf_path = os.path.join(pdf_folder, generation.pdf_filename)
    png_out_dir = os.path.join(temp_folder, str(generation_id))
    # This is already created by the parallel function, but exist_ok=True is safe
    os.makedirs(png_out_dir, exist_ok=True)

    try:
        # MODIFICATION 1: Call the new parallel function
        convert_pdf_to_png_parallel(pdf_path, png_out_dir)

        png_files = sorted(
            [f for f in os.listdir(png_out_dir) if f.lower().endswith('.png')],
            key=lambda x: int(re.search(r'(\d+)', x).group(1)) if re.search(r'(\d+)', x) else x
        )

        # Create a list of full paths for the OCR process
        png_paths = [os.path.join(png_out_dir, f) for f in png_files]
        ocr_results = []

        # MODIFICATION 2: Parallelize the OCR step as well
        print(f"Starting parallel OCR for {len(png_paths)} images...")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # executor.map will run ocr_image on each path in parallel
            # and return the raw text results in order.
            raw_texts = executor.map(ocr_image, png_paths)

            # Now parse the results sequentially (parsing is fast)
            for text in raw_texts:
                try:
                    parsed = parse_ocr_result(text)
                    ocr_results.append(parsed)
                    # This print can be noisy in parallel, but useful for debugging
                    # print(f"OCR parsed successfully: {parsed.get('Title', 'No Title')}")
                except Exception as e:
                    print(f"OCR parse error: {e}")

        print("Finished OCR and parsing.")

        csv_filename = f"{generation_id}.csv"
        csv_path = os.path.join(csv_folder, csv_filename)
        if ocr_results:
            # Filter out any "Not Available" results if you don't want them in the final CSV
            # valid_results = [r for r in ocr_results if r.get('Title') != 'Not Available']
            # if not valid_results:
            #    return jsonify({'error': 'No valid OCR results', 'details': 'OCR did not return any parsable data.'}), 500

            headers = list(ocr_results[0].keys())
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(ocr_results) # writerows is more efficient
        else:
            return jsonify({'error': 'No OCR results', 'details': 'OCR did not return any results.'}), 500

        generation.csv_filename = csv_filename
        db.session.commit()

        return jsonify({'csv_filename': csv_filename, 'id': generation_id})
    except Exception as e:
        # Use traceback for better debugging in your server logs
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'CSV generation failed', 'details': str(e)}), 500
    finally:
        # Cleanup temp folder
        if os.path.exists(png_out_dir):
            shutil.rmtree(png_out_dir, ignore_errors=True)

# ... (detail function remains the same) ...
@summary_bandwith.route("/detail", methods=["GET"])
def detail():
    generation_id = request.args.get('id')  # Get 'id' from query parameters
    if not generation_id:
        return "Missing generation ID", 400

    generation = SummaryBandwith().query.get(generation_id)
    if not generation:
        return "Generation not found", 404

    return render_template('summary_bandwith/detail.html', generation=generation)