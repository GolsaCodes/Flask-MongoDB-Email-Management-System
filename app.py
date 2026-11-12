from __future__ import print_function
from flask import Flask, render_template, request, redirect, url_for 
from pymongo import MongoClient
from flask import render_template
from datetime import datetime
from flask import jsonify
import os


app = Flask(__name__)

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

db = client["G9"]
collection_sent = db["sent"]
collection_received = db["received"]



@app.route('/')
def gmail():
    return render_template("gmail.html")

#Using Aggregation to show sender's name,email content and date in received emails page
# Sorted by email date
@app.route('/inbox', methods=['GET'])
def inbox():
    pipeline = [
        {"$unwind": "$emails"},
        {"$sort": {"emails.email_date": -1}},
        {"$project": {"_id": 0, "id": "$emails.id", "sender": "$emails.sender.name",
                       "subject": "$emails.subject", "email_date": "$emails.email_date"}}
    ]
    inbox_data = list(collection_received.aggregate(pipeline))
    return render_template("inbox.html", inbox_data=inbox_data)


#Using Aggregation to check unread received emails
#sorted by the email date
@app.route('/unread_inbox', methods=['GET'])

def unread_inbox():
    pipeline = [
        {"$unwind": "$emails"},
        {"$match": {"emails.read": False}},  # Match only unread emails
        {"$sort": {"emails.email_date": -1}},
        {"$project": {
            "_id": 0,
            "id": "$emails.id",
            "sender": "$emails.sender.name",
            "subject": "$emails.subject",
            "email_date": "$emails.email_date"
        }}
    ]
    unread_data = list(collection_received.aggregate(pipeline))
    return render_template("unread_inbox.html", unread_data=unread_data)


#Using Aggregation to show receiver's name,email content and date in sent emails page
#Sorted by email date
#Only show 3 first emails at first and if the user wants, they can upload more emails
sent_offset = 0

@app.route('/sent', methods=['GET'])
def sent():
    global sent_offset
    pipeline = [
        {"$unwind": "$sent_emails"},
        {"$sort": {"sent_emails.email_date": -1}},
        {"$project": {"_id": 0, "id": "$sent_emails.id", "receiver_name": "$sent_emails.receiver.name",
                      "subject": "$sent_emails.subject", "email_date": "$sent_emails.email_date"}},
        {"$limit": 3} 
    ]
    sent_data = list(collection_sent.aggregate(pipeline))
    sent_offset += 3  # Update the offset
    return render_template("sent.html", sent_data=sent_data)


# Route to fetch more sent emails (next 3)
@app.route('/more_sent', methods=['GET'])
def more_sent():
    global sent_offset
    pipeline = [
        {"$unwind": "$sent_emails"},
        {"$sort": {"sent_emails.email_date": -1}},
        {"$project": {"_id": 0, "id": "$sent_emails.id", "receiver_name": "$sent_emails.receiver.name",
                      "subject": "$sent_emails.subject", "email_date": "$sent_emails.email_date"}},
        {"$skip": sent_offset},  
        {"$limit": 3}  
    ]
    sent_data = list(collection_sent.aggregate(pipeline))
    sent_offset += 3 
    return jsonify(sent_data)


@app.route('/report')
def report():
    # Perform aggregation to count received emails based on sender
    # And count sent emails based on receiver's name
    pipeline = [
        {"$unwind": "$emails"},
        {"$group": {"_id": "$emails.sender.name", "count": {"$sum": 1}}}
    ]
    sender_counts = list(collection_received.aggregate(pipeline))

    pipeline_unique_receivers = [
        {"$unwind": "$sent_emails"},
        {"$group": {"_id": "$sent_emails.receiver.name", "count": {"$sum": 1}}}
    ]

    unique_receivers_count = list(collection_sent.aggregate(pipeline_unique_receivers))
    return render_template("report.html", sender_counts=sender_counts,
                           unique_receivers_count=unique_receivers_count)



#Perform aggregation to show received emails based on the alphabetic order of senders 

@app.route('/alphabetic_report')
def alphabetic_report():

    pipeline = [
        {"$unwind": "$emails"},
        {"$sort": {"emails.sender.name": 1}},  # Sort by sender's name in ascending order
        {"$project": {"_id": 0, "id": "$emails.id", "sender": "$emails.sender.name",
                      "subject": "$emails.subject", "email_date": "$emails.email_date"}}
    ]

    alpha_order = list(collection_received.aggregate(pipeline))
    return render_template("alphabetic_report.html", alpha_order=alpha_order)



@app.route('/email_details/<int:email_id>')
def email_details(email_id):
    
    collection_received.update_one({"emails.id": email_id}, {"$set": {"emails.$.read": True}})
    for email_obj in collection_received.find({}):
        for email in email_obj['emails']:
            if email['id'] == email_id:
                sender_name = email['sender']['name']
                sender_email = email['sender']['email']
                receiver_name = email['receiver']['name']
                receiver_email = email['receiver']['email']
                email_date = email['email_date']
                email_content = email['email_content']

                return render_template("email_details.html", sender_name=sender_name, sender_email=sender_email,
                                       receiver_name=receiver_name, receiver_email=receiver_email,
                                       email_date=email_date, email_content=email_content)
    return "Email not found"


@app.route('/sent_email_details/<int:email_id>')
def sent_email_details(email_id):
    for email_obj in collection_sent.find({}):
        for email in email_obj['sent_emails']:
            if email['id'] == email_id:
                print(email)
                sender_name = email['sender']['name']
                sender_email = email['sender']['email']
                receiver_name = email['receiver']['name']
                receiver_email = email['receiver']['email']
                email_date = email['email_date']
                email_content = email['email_content']

                return render_template("sentEmailDet.html", sender_name=sender_name, sender_email=sender_email,
                                       receiver_name=receiver_name, receiver_email=receiver_email,
                                       email_date=email_date, email_content=email_content)
    return "Email not found"



@app.route('/new_email', methods=['GET', 'POST'])
def new_email():
    if request.method == 'POST':

        receiver_name = request.form.get('receiver_name')
        receiver_email = request.form.get('receiver_email')
        subject = request.form.get('subject')
        email_content = request.form.get('email_content')
        email_date = datetime.now()
        existing_data = list(collection_sent.find())
        if not existing_data:
            existing_data = [{'sent_emails': []}]

        last_email = existing_data[-1]['sent_emails'][-1] if existing_data[-1]['sent_emails'] else {'id': 0}
        new_email_id = last_email['id'] + 1

        new_email = {
            'id': new_email_id,
            'sender': {
                'name': 'me',  
                'email': 'me@gmail.com'
            },
            'receiver': {
                'name': receiver_name,
                'email': receiver_email
            },
            'subject': subject,
            'email_content': email_content,
            'email_date': email_date.strftime('%Y-%m-%d %H:%M:%S')
        }

        existing_data[-1]['sent_emails'].append(new_email)
        collection_sent.update_one({}, {"$set": {"sent_emails": existing_data[-1]['sent_emails']}})

        return redirect(url_for('sent'))

    return render_template('new_email.html')


@app.route('/delete_email/<email_id>', methods=['POST'])
def delete_email(email_id):
    try:
        email_id = int(email_id)  
        collection_received.update_one({}, {"$pull": {"emails": {"id": email_id}}})
        return jsonify({"message": "Email deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/delete_sent_email/<int:email_id>', methods=['POST'])
def delete_sent_email(email_id):
    try:
        email_id = int(email_id)
        result = collection_sent.update_one({}, {"$pull": {"sent_emails": {"id": email_id}}})
        if result.modified_count > 0:
            return jsonify({"message": "Email deleted successfully"}), 200
        else:
            return jsonify({"error": "Email not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()