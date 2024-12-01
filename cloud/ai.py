from ultralytics import YOLOv10

# Load the pretrained model
model = YOLOv10('yolov10n.pt')

# Perform prediction on an image
results = model.predict(source='example.jpg')

# Display or save results
results.show()  # To display the image with detections
results.save(save_dir='output')  # Save output to the 'output' folder
