import mysql.connector
import json

db_config = {
  'user': '',
  'password': '',
  'host': '',
  'database': 'casad_collegebaseball',
  'raise_on_warnings': True
}

# Connect to the database
try:
  connection = mysql.connector.connect(**db_config)

  # Create a cursor object to interact with the database
  cursor = connection.cursor()

  # Execute a sample query
  query = "SELECT * FROM old_school"
  cursor.execute(query)

  # Fetch the column names
  column_names = [desc[0] for desc in cursor.description]
  
  # Fetch the results
  results = cursor.fetchall()
  schools = []
  for row in results:
    school = {}
    for column in column_names:
      if column != "geo":
        school[column] = row[column_names.index(column)]

    schools.append(school)
  
  # print(f"{schools}")

  with open(f"./schools_from_mysql.json", 'w') as file:
    json.dump(schools, file)

except mysql.connector.Error as err:
  print(f"Error: {err}")

finally:
  # Close the cursor and connection
  if 'connection' in locals():
      cursor.close()
      connection.close()
