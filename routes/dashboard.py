from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from sqlalchemy import func
from extensions import db
from models import User, Conversation, Message, MoodLog
from datetime import datetime, timezone, timedelta
import json

dashboard_bp = Blueprint("dashboard", __name__)

WELLNESS_TIPS = {
    "joy": [
        "You're in a great headspace! Use this energy to do something creative today.",
        "Happiness is contagious — reach out to a friend and share your good mood.",
        "Celebrate small wins. You deserve to acknowledge how far you've come.",
        "Channel your positive energy into a new hobby or skill you've been meaning to try.",
    ],
    "love": [
        "Feeling connected is powerful. Take a moment to express gratitude to someone you care about.",
        "Love starts with self-care. Do one kind thing for yourself today.",
        "Write down three things you appreciate about the people in your life.",
        "A warm conversation with someone close can lift your whole day.",
    ],
    "sadness": [
        "It's okay to feel sad. Give yourself permission to rest and be gentle with yourself.",
        "Try journaling your thoughts — writing can help process difficult emotions.",
        "Step outside for a short walk. Fresh air and movement can shift your mood gently.",
        "Reach out to someone you trust. You don't have to carry this alone.",
    ],
    "anger": [
        "Take 5 slow, deep breaths before responding to anything that's frustrating you.",
        "Physical movement helps release tension — try a short walk or stretching.",
        "Write down what's bothering you without filtering. Sometimes anger has a message.",
        "Give yourself space before reacting. A brief pause can prevent regret.",
    ],
    "fear": [
        "Ground yourself: name 5 things you can see, 4 you can touch, 3 you can hear.",
        "Break what's worrying you into small, manageable steps. Focus on just the next one.",
        "Fear often shrinks when we talk about it. Consider sharing with someone you trust.",
        "Remind yourself of a past challenge you overcame. You are more resilient than you think.",
    ],
    "neutral": [
        "Take a few minutes today to practice deep breathing — inhale slowly, hold, exhale gently.",
        "Hydrate, stretch, and step away from your screen for 5 minutes. Your body will thank you.",
        "A short mindfulness exercise can reset your focus and reduce background stress.",
        "Check in with yourself: how are you really feeling today? Awareness is the first step.",
    ],
    "crisis": [
        "You are not alone. Please reach out to AASRA at 91-9820466627 or a trusted person near you.",
        "Your life has value. Take it one moment at a time and seek support today.",
    ],
    "sensitive": [
        "It's okay to set boundaries in conversations. Your comfort matters.",
        "Focus on what you can control today and let go of what you cannot.",
    ],
}

DEFAULT_TIPS = WELLNESS_TIPS["neutral"]

# Numeric score for each emotion (for chart Y-axis)
EMOTION_SCORE = {
    "joy":      5,
    "love":     4,
    "neutral":  3,
    "fear":     2,
    "sadness":  2,
    "anger":    1,
    "crisis":   1,
    "sensitive": 3,
}

EMOTION_LABEL = {
    1: "Distressed",
    2: "Low",
    3: "Neutral",
    4: "Good",
    5: "Joyful",
}


def get_tips_for_user(user):
    last_conv = (
        Conversation.query
        .filter_by(user_id=user.id)
        .order_by(Conversation.updated_at.desc())
        .first()
    )
    if not last_conv:
        return DEFAULT_TIPS, "neutral"
    emotion = getattr(last_conv, "last_emotion", None) or "neutral"
    tips = WELLNESS_TIPS.get(emotion, DEFAULT_TIPS)
    return tips, emotion


def get_mood_trend(user, days=14):
    since = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.session.query(
            func.date(Conversation.updated_at).label("day"),
            Conversation.last_emotion
        )
        .filter(
            Conversation.user_id == user.id,
            Conversation.updated_at >= since,
            Conversation.last_emotion != None
        )
        .order_by(
            func.date(Conversation.updated_at).asc(),
            Conversation.updated_at.desc()
        )
        .all()
    )

    seen = {}
    for row in rows:
        day_str = str(row.day)
        if day_str not in seen:
            seen[day_str] = row.last_emotion

    labels, scores, emotions = [], [], []

    for i in range(days):
        day = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).date()
        day_str = str(day)
        label = day.strftime("%b %d")
        emotion = seen.get(day_str)
        score = EMOTION_SCORE.get(emotion, None) if emotion else None
        labels.append(label)
        scores.append(score)
        emotions.append(emotion or "")

    # ✅ NEW — tells the template whether there is anything to plot
    has_data = any(s is not None for s in scores)

    return {
        "labels":       json.dumps(labels),
        "scores":       json.dumps(scores),
        "emotions":     json.dumps(emotions),
        "emotion_label": json.dumps(EMOTION_LABEL),
        "has_data":     has_data,   # ✅ NEW
    }


@dashboard_bp.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.pop("username", None)
        return redirect(url_for("auth.login"))

    # Usage stats
    total_sessions = Conversation.query.filter_by(user_id=user.id).count()
    total_messages = Message.query.filter_by(user_id=user.id, role="user").count()
    days_active = db.session.query(
        func.count(func.distinct(func.date(Message.created_at)))
    ).filter(Message.user_id == user.id, Message.role == "user").scalar() or 0
    first_conv = Conversation.query.filter_by(user_id=user.id)\
        .order_by(Conversation.created_at.asc()).first()
    member_since = (
        (datetime.now(timezone.utc) - first_conv.created_at.replace(tzinfo=timezone.utc)).days
        if first_conv else 0
    )

    first_name = user.fullname.split()[0] if user.fullname else user.username

    stats = {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "days_active": days_active,
        "member_since": member_since,
    }

    # Wellness tips
    tips, last_emotion = get_tips_for_user(user)

    # Mood trend chart
    mood_chart = get_mood_trend(user, days=14)

    return render_template(
        "dashboard.html",
        username=first_name,
        stats=stats,
        tips=tips,
        last_emotion=last_emotion,
        mood_chart=mood_chart,
    )


@dashboard_bp.route("/mood-checkin", methods=["POST"])
def mood_checkin():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    from flask import request as req
    data  = req.get_json() or {}
    mood  = data.get("mood", "").strip()
    note  = data.get("note", "").strip()[:200]

    if not mood:
        return jsonify({"error": "Mood is required"}), 400

    VALID_MOODS = {"happy", "sad", "anxious", "calm", "angry", "tired"}
    if mood not in VALID_MOODS:
        return jsonify({"error": "Invalid mood"}), 400

    # Allow only one check-in per day
    from sqlalchemy import func as sqlfunc
    today = datetime.now(timezone.utc).date()
    existing = MoodLog.query.filter(
        MoodLog.user_id == user.id,
        sqlfunc.date(MoodLog.logged_at) == today
    ).first()

    if existing:
        return jsonify({
            "status": "already_logged",
            "message": "You've already checked in today.",
            "mood": existing.mood
        }), 200

    log = MoodLog(user_id=user.id, mood=mood, note=note or None)
    db.session.add(log)
    db.session.commit()

    return jsonify({"status": "success", "mood": mood}), 201


@dashboard_bp.route("/mood-checkin/today", methods=["GET"])
def mood_checkin_today():
    """Returns today's check-in so the dashboard can restore state on reload."""
    if "username" not in session:
        return jsonify({"mood": None}), 200

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        return jsonify({"mood": None}), 200

    from sqlalchemy import func as sqlfunc
    today = datetime.now(timezone.utc).date()
    existing = MoodLog.query.filter(
        MoodLog.user_id == user.id,
        sqlfunc.date(MoodLog.logged_at) == today
    ).first()

    return jsonify({"mood": existing.mood if existing else None}), 200