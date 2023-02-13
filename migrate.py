import sqlite3
conn = sqlite3.connect('data.sqlite')
c = conn.cursor()
c.execute('ALTER TABLE Users ADD COLUMN is_ban INTEGER DEFAULT 0;')
conn.commit()
conn.close()