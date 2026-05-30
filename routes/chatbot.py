from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, send_file
from extensions import db
from models import User, Conversation, Message
from chatbot_core import generate_response
import csv
import io
from datetime import datetime, timezone

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chatbot")
def chatbot():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.pop("username", None)
        return redirect(url_for("auth.login"))

    conversations = Conversation.query.filter_by(user_id=user.id).order_by(Conversation.updated_at.desc()).all()
    active_conversation = conversations[0] if conversations else None
    messages = active_conversation.messages if active_conversation else []

    return render_template(
        "chatbot.html",
        conversations=conversations,
        active_conversation=active_conversation,
        messages=messages
    )


@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    message = data.get("message", "").strip()
    conversation_id = data.get("conversation_id")

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    conversation = None
    if conversation_id:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()

    if not conversation:
        title = " ".join(message.split())[:40]
        conversation = Conversation(title=title or "New Chat", user_id=user.id)
        db.session.add(conversation)
        db.session.flush()

    user_msg = Message(
        conversation_id=conversation.id,
        user_id=user.id,
        role="user",
        content=message
    )
    db.session.add(user_msg)

    # After getting bot_data, save emotion to conversation
    bot_data = generate_response(message)
    reply_text = bot_data.get("reply", "Sorry, I could not generate a reply.")
    emotion = bot_data.get("emotion", "neutral")

    bot_msg = Message(
        conversation_id=conversation.id,
        user_id=user.id,
        role="assistant",
        content=reply_text
    )
    db.session.add(bot_msg)

    conversation.title = conversation.title or (" ".join(message.split())[:40] or "New Chat")
    conversation.last_emotion = emotion  # ✅ NEW — persist emotion
    db.session.commit()

    return jsonify({
        "reply": reply_text,
        "emotion": emotion,
        "conversation_id": conversation.id
    })


@chatbot_bp.route("/chat/history/<int:conversation_id>")
def chat_history(conversation_id):
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.pop("username", None)
        return redirect(url_for("auth.login"))

    conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
    if not conversation:
        flash("Conversation not found.", "error")
        return redirect(url_for("chatbot.chatbot"))

    conversations = Conversation.query.filter_by(user_id=user.id).order_by(Conversation.updated_at.desc()).all()

    return render_template(
        "chatbot.html",
        conversations=conversations,
        active_conversation=conversation,
        messages=conversation.messages
    )


@chatbot_bp.route("/chat/export/<string:format>")
def export_chat(format):
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.pop("username", None)
        return redirect(url_for("auth.login"))

    if format not in ("txt", "csv"):
        flash("Invalid export format.", "error")
        return redirect(url_for("chatbot.chatbot"))

    conversations = Conversation.query.filter_by(user_id=user.id)\
        .order_by(Conversation.created_at.asc()).all()

    if format == "txt":
        output = io.StringIO()
        output.write(f"MindCare AI — Chat History\n")
        output.write(f"User: {user.fullname} (@{user.username})\n")
        output.write(f"Exported on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")
        output.write("=" * 60 + "\n\n")

        for convo in conversations:
            output.write(f"Conversation: {convo.title}\n")
            output.write(f"Date: {convo.created_at.strftime('%Y-%m-%d')}\n")
            output.write("-" * 40 + "\n")
            for msg in convo.messages:
                role  = "You" if msg.role == "user" else "MindCare AI"
                time  = msg.created_at.strftime("%H:%M")
                output.write(f"[{time}] {role}: {msg.content}\n")
            output.write("\n")

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/plain",
            as_attachment=True,
            download_name=f"mindcare_chat_{user.username}.txt"
        )

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Conversation", "Date", "Time", "Role", "Message"])

        for convo in conversations:
            for msg in convo.messages:
                writer.writerow([
                    convo.title,
                    msg.created_at.strftime("%Y-%m-%d"),
                    msg.created_at.strftime("%H:%M"),
                    "User" if msg.role == "user" else "Assistant",
                    msg.content
                ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"mindcare_chat_{user.username}.csv"
        )