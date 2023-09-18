from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
output = {}
table = 'student'


@app.route("/", methods=['GET'], endpoint='index')
def index():
    return render_template('index.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')


@app.route("/jobRegister", methods=['GET','POST'])
def jobRegister():
    comp_name = request.form['comp_name']
    job_title = request.form['job_title']
    job_desc = request.form['job_desc']
    job_req = request.form['job_req']
    sal_range = request.form['sal_range']
    contact_person_name = request.form['contact_person_name']
    contact_person_email = request.form['contact_person_email']
    contact_number = request.form['contact_number']
    comp_state = request.form['comp_state']
    companyImage = request.files['companyImage']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if companyImage.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (comp_name, job_title, job_desc, job_req, sal_range, contact_person_name, contact_person_email, contact_number, comp_state))
        db_conn.commit()
        # Uplaod image file in S3 #
        comp_image_file_name_in_s3 = "company-" + str(comp_name) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=comp_image_file_name_in_s3, Body=companyImage)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                comp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()
    return render_template('jobRegister.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)