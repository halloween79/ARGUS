from flask import Blueprint, render_template, jsonify, request, send_file
from app import db
from app.models import Image, SystemStatus
from datetime import datetime
import os, io, zipfile

main = Blueprint('main', __name__)

def get_or_create_status():
    status = SystemStatus.query.first()
    if not status:
        status = SystemStatus()
        db.session.add(status)
        db.session.commit()
    return status

# ── Page Routes ────────────────────────────────────────────
@main.route('/')
def home():
    status = get_or_create_status()
    last_image = Image.query.order_by(Image.captured_at.desc()).first()
    return render_template('home.html', status=status, last_image=last_image)

@main.route('/config')
def config():
    status = get_or_create_status()
    return render_template('config.html', status=status)

@main.route('/images')
def images():
    return render_template('images.html')

@main.route('/meteors')
def meteors():
    return render_template('meteors.html')

# ── REST API ───────────────────────────────────────────────
@main.route('/api/status')
def api_status():
    status = get_or_create_status()
    return jsonify(status.to_dict())

@main.route('/api/status', methods=['POST'])
def api_update_status():
    status = get_or_create_status()
    data = request.get_json()
    if 'capture_active' in data:
        status.capture_active = data['capture_active']
    if 'start_time' in data:
        status.start_time = data['start_time']
    if 'end_time' in data:
        status.end_time = data['end_time']
    status.last_updated = datetime.utcnow()
    db.session.commit()
    return jsonify(status.to_dict())

@main.route('/api/images')
def api_images():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    date_str = request.args.get('date', None)

    query = Image.query
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d')
            query = query.filter(
                db.func.date(Image.captured_at) == filter_date.date()
            )
        except ValueError:
            pass

    pagination = query.order_by(Image.captured_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'images':    [img.to_dict() for img in pagination.items],
        'total':     pagination.total,
        'pages':     pagination.pages,
        'page':      pagination.page,
    })

@main.route('/api/meteors')
def api_meteors():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    pagination = Image.query.filter(
        Image.cnn_confidence > 0.5
    ).order_by(Image.captured_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'images': [img.to_dict() for img in pagination.items],
        'total':  pagination.total,
        'pages':  pagination.pages,
        'page':   pagination.page,
    })

@main.route('/api/images/download-zip')
def download_zip():
    date_str = request.args.get('date', None)
    query    = Image.query
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d')
            query = query.filter(
                db.func.date(Image.captured_at) == filter_date.date()
            )
        except ValueError:
            pass

    images  = query.all()
    buf     = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for img in images:
            if os.path.exists(img.filepath):
                zf.write(img.filepath, img.filename)
    buf.seek(0)
    return send_file(buf, mimetype='application/zip',
                     as_attachment=True,
                     download_name='argus_images.zip')