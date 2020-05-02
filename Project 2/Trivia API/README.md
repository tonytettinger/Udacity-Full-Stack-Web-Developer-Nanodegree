# Full Stack API Final Project

## Full Stack Trivia

This full stack trivia game application is built with **React JS** on the front-end, **Flask Python** in the back-end and **SQLAlchemy** handling the ORM SQL access. The application was built on the starter code of the 2nd project of the Udacity Full Stack Developer Nanodegree. It is a fully working application which integrates the front-end, back-end and database layers and handles requests and errors.

This application is capable of the following tasks:

1) Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer. 
2) Delete questions.
3) Add questions and require that they include question and answer text.
4) Search for questions based on a text query string.
5) Allow to play the quiz game, randomizing either all questions or within a specific category. 

## Getting Started

Base url: At present this app can run locally on localhost:3000. 

To start the application start the backend from the ./backend folder running 

```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```
This will start the back-end on port 5000.
To start the front-end of the application install the npm packages with npm install (requires Node JS installed) from the ./frontend folder.
The SQL starter database can be imported with the following command:
```
psql trivia < trivia.psql
```
After this the application can be accessed from localhost:3000 and the trivia game can be played.

## Endpoints


### GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs.
 
 ```
{
'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"
}
```

### GET '/questions?page=<int: page_number> '
- Fetches a dictionary of questions up to 10 questions per page, and the pages can be offset by the page_number query variable.
- Request Arguments: page_number, submitted as query string
- Returns: A JSON object with the three keys:
  -Questions: Containing a dictionary of questions.
  -totalQuestions: Number of total questions in the database.
  -categories: a list of categories
``` 
{
'questions': convert_questions_to_dict(questions_current_page),
'totalQuestions': query_count,
'categories': categories_dict
}
```

### GET '/questions?page=<int: page_number>'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs.

{
        'status' : 200,
        'success': True,
        'question' : question
}

### DELETE '/questionsDelete/<int:post_id>'
- Deletes a record from the questions table, based on the post_id variable.
- Request Arguments: post_id variable submitted as part of the GET request URL.
- Returns: A JSON object with a 200 status message, success: True and the deleted question object.
```
{
  'status' : 200,
  'success': True,
  'question' : question
}
```

### POST '/questionsPost'
- Posts a record from the add questions page, which contains the following variables: question, answer, difficuly and category.
- Request Arguments: The arguments will be sent as an AJAX JSON request.
- Returns: A JSON object with a the following data:
```
{
          'question': question string,
          'answer': answer string,
          'category': int number of the category,
          'difficulty': int number of difficulty
}
```

### GET '/categories/<int:category_id>/questions'
- Gets the question records from the questions database table, where the category id equals the submitted category_id.
- Request Arguments: The argument of category ID is submitted via the URL of the get request
- Returns: A JSON object with a the following data:
```
{
          'questions': questions object,
          'totalQuestions' : number of questions in given category,
          'current_category': the clicked category to update the state for the current category
}
```

### GET '/quizzes'
- Gets the question records from the questions database table, where the category id equals the submitted category_id.
- Request Arguments: A JSON object containing quiz category which contains the id of the currently played category and an array of the previous question that is used to filter out questions that the user has already seen in the current round.
- Returns: A JSON object containing a single question object.
```
{
          'question': current questions object,
}
```

## Error Handling

Errors are returned as JSON objects in the following format:
```
{
      'success': False,
      'error' : 422,
      "message" : "Unprocessable"
}
```
