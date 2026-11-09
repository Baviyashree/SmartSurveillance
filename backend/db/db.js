const mysql = require('mysql2');

const pool = mysql.createPool({
  host: '<host>',
  user: '<user>',
  password: '<password>',
  database: '<database>'
});

module.exports = pool.promise();
