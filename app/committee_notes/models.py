from app import db

class CommitteeNotes(db.Model):
	__tablename__ = 'committee_notes'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	description = db.Column(db.String)
	author = db.Column(db.ForeignKey('users.id'))
	committee = db.Column(db.ForeignKey('committees.id'))
	created_at = db.Column(db.DateTime, server_default= db.func.now())
