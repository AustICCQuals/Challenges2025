const bodyParser = require('body-parser')
const crypto = require('crypto')
const express = require('express')
const fs = require('fs')
const sqlite3 = require('sqlite3')

const app = express()
app.use(bodyParser.json())

const db = new sqlite3.Database(':memory:');

db.serialize(() => {
  db.run(`CREATE TABLE users (username TEXT, password TEXT, twofac INTEGER);`)
  db.run(`INSERT INTO users VALUES (
    'admin', '${hashPassword(crypto.randomBytes(16).toString('hex'))}', ${crypto.randomInt(2**32)}
  );`)
})

function hashPassword(password) {
  return crypto.createHash('sha256').update(password).digest('base64url')
}

function sqlEscape(s) {
  return `'` + s.toString().replace(/'/g, `''`) + `'`
}

function sqlPrepare(query, params) {
  params.map((e) => {
    query = query.replace(/\?/, sqlEscape(e))
  })
  return query
}

app.post('/login', (req, res) => {
  res.type('json')
  let {username, password, twofac} = req.body
  if (typeof username !== 'string' || username.length > 16) {
     res.send({success: false, message: "Username not valid."})
     return;
  }
  hashed = hashPassword(password)
  preparedStmt = sqlPrepare(
    `SELECT * FROM users WHERE username = ? AND password = ?`,
    [username, hashed]
  )
  db.get(preparedStmt, {}, (err, row) => {
    if (err) {
      res.send({success: false, message: "SQL error."})
    } else if (row && row.twofac == twofac) {
      res.send({success: true, message: fs.readFileSync('/flag.txt').toString()})
    } else if (row) {
      res.send({success: false, message: "Incorrect two factor."})
    } else {
      res.send({success: false, message: "Incorrect details."})
    }
  })
})

app.get('/', (req, res) => {
  res.setHeader('Content-Type','text/html')
  res.sendFile('index.html', {root: __dirname})
})

app.listen(1337, () => console.log('Now accepting requests on port 1337...'))
