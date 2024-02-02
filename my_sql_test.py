import mysql.connector

db_config = {
  'user': 'casad_9',
  'password': 'w4sJyAywexSXAaFm',
  'host': 'db110a.pair.com',
  'database': 'casad_collegebaseball',
  'raise_on_warnings': True
}

# Connect to the database
try:
  connection = mysql.connector.connect(**db_config)

  # Create a cursor object to interact with the database
  cursor = connection.cursor()

  # Execute a sample query
  query = "SELECT * FROM school"
  cursor.execute(query)

  # Fetch the column names
  column_names = [desc[0] for desc in cursor.description]
  
  # Fetch the results
  results = cursor.fetchall()
  for row in results:
    id = row[column_names.index("id")]
    name = row[column_names.index("name")]
    url = row[column_names.index("url")]
    print(f"{id} {name} {url}")

except mysql.connector.Error as err:
  print(f"Error: {err}")

finally:
  # Close the cursor and connection
  if 'connection' in locals():
      cursor.close()
      connection.close()
