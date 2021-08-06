# Flask-framework-Project

## Goal

 Hosting a Machine Learning model on Flask Web application, this application is designed to work when there is Internet Connectivity and it will act as API service to serve incoming HTTP requests from Web & Flutter applicaitons, and the output is Jsonified and sent as HTTP response.

## Architecture with Connectivity

When the input data is fed to the flutter application, when the user clicks on submit button, application checks if there is connectivity, Incase there is connectivity, an API Service calls the Model that is Hosted on Flask Web Server, this flask application process the input HTTP request, predicts the output, and then it is Jsonified and sent to the flutter application which is then shown on the Results screen.

![Finished App](https://github.com/VikranthAle/Flutter-Portfolio/blob/main/ContactCard-Flutter-App/MyCard.png)


> For further details/explanation please refer this document -> [HARP Flask Framework Workflow](https://github.com/AVcodeMaverick7/Flask-framework-Project/blob/main/HARP-Flask-Framework-Workflow.pdf)

