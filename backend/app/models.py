from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base

class Athlete(Base):
    __tablename__ = 'athletes'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=True)
    sport = Column(String(80), nullable=False)
    injury_history = Column(Text, default='None')
    created_at = Column(DateTime, default=datetime.utcnow)
    videos = relationship('Video', back_populates='athlete', cascade='all, delete-orphan')
    analyses = relationship('Analysis', back_populates='athlete', cascade='all, delete-orphan')

class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String(40), default='Uploaded')
    athlete = relationship('Athlete', back_populates='videos')
    analyses = relationship('Analysis', back_populates='video', cascade='all, delete-orphan')

class Analysis(Base):
    __tablename__ = 'analyses'
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    movement_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    recommendation = Column(Text, default='Maintain good warm-up, technique and recovery habits.')
    created_at = Column(DateTime, default=datetime.utcnow)
    athlete = relationship('Athlete', back_populates='analyses')
    video = relationship('Video', back_populates='analyses')
    biomechanics = relationship('Biomechanics', back_populates='analysis', cascade='all, delete-orphan', uselist=False)

class Biomechanics(Base):
    __tablename__ = 'biomechanics'
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), nullable=False, unique=True)
    knee_angle = Column(Float, nullable=True)
    hip_angle = Column(Float, nullable=True)
    ankle_angle = Column(Float, nullable=True)
    movement_quality = Column(Float, nullable=False)
    frames_processed = Column(Integer, default=0)
    pose_detection_rate = Column(Float, default=0)
    analysis = relationship('Analysis', back_populates='biomechanics')
