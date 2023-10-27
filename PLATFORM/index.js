const express = require('express');
const app = express();
const port = 3000;

// Define a route handler for the root path
app.get('/', (req, res) => {
  res.send('Hello');
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
