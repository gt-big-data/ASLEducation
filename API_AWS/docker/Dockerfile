FROM python:3.8-slim

WORKDIR /app

COPY ec2_api.py /app/ec2_api.py
COPY resnet101_seg.h5 /app/resnet101_seg.h5

COPY handtrackingSSD /app/handtrackingSSD
COPY Image_Segmentation /app/Image_Segmentation
COPY Upscaling /app/Upscaling
COPY requirements.txt /app/requirements.txt

# Debugging: Print the contents of requirements.txt

RUN ls -l /app
RUN cat /app/requirements.txt

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Define environment variable
ENV FLASK_APP=ec2_api.py

# Run flask app
CMD ["flask", "run", "--host=0.0.0.0"]
