from app import db
from datetime import datetime

class Image(db.Model):
    __tablename__ = 'images'

    id            = db.Column(db.Integer, primary_key=True)
    filename      = db.Column(db.String(255), nullable=False)
    filepath      = db.Column(db.String(512), nullable=False)
    captured_at   = db.Column(db.DateTime, default=datetime.utcnow)
    is_meteor     = db.Column(db.Boolean, default=False)
    cnn_confidence= db.Column(db.Float, default=0.0)
    sdr_confirmed = db.Column(db.Boolean, default=False)
    uploaded_to_s3= db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id':            self.id,
            'filename':      self.filename,
            'filepath':      self.filepath,
            'captured_at':   self.captured_at.isoformat(),
            'is_meteor':     self.is_meteor,
            'cnn_confidence':self.cnn_confidence,
            'sdr_confirmed': self.sdr_confirmed,
            'uploaded_to_s3':self.uploaded_to_s3,
        }

class SystemStatus(db.Model):
    __tablename__ = 'system_status'

    id             = db.Column(db.Integer, primary_key=True)
    capture_active = db.Column(db.Boolean, default=False)
    start_time     = db.Column(db.String(10), default='20:00')
    end_time       = db.Column(db.String(10), default='06:00')
    last_updated   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'capture_active': self.capture_active,
            'start_time':     self.start_time,
            'end_time':       self.end_time,
            'last_updated':   self.last_updated.isoformat(),
        }