const express = require('express');
const app = express();
const port = 3000;
const sharp = require('sharp');

app.use(express.json());

// Define an endpoint for image manipulation
app.post('/api/manipulate-image', async (req, res) => {
  try {
    // Get the base64-encoded image data from the request body
    const imageDataBase64 = req.body.imageData;

    // Decode the base64 image data to a buffer
    const imageBuffer = Buffer.from(imageDataBase64, 'base64');

    // Perform image manipulation (e.g., resizing)
    const manipulatedImageBuffer = await sharp(imageBuffer)
      .resize({ width: 300, height: 300 }) // Resize the image to 300x300 pixels
      .toBuffer();

    // Send the manipulated image back to the user as base64-encoded data
    const manipulatedImageData = manipulatedImageBuffer.toString('base64');
    res.json({ imageData: manipulatedImageData });
  } catch (error) {
    console.error('Error during image manipulation:', error);
    res.status(500).json({ error: 'Image manipulation failed' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});