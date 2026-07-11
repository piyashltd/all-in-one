const express = require('express');
const path = require('path');
const app = express();

const port = process.env.PORT || 3000;

// পুরো রুট ডিরেক্টরিকে স্ট্যাটিক হিসেবে সার্ভ করা হচ্ছে
app.use(express.static(__dirname));

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
