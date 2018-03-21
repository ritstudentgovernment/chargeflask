
Charge Tracker Documentation {#mainpage}
=========
This is the documentation for the [ChargeTracker](https://github.com/ritstudentgovernment/chargeflask) backend, the front-end documentation is located in the [chargevue](https://github.com/ritstudentgovernment/chargevue) repository.

[TOC]

# Getting Started {#gettingstarted}

This guide contains step-by-step instructions on how to install the server, how to get data to the backend and how to get data from it.

## Server Installation {#serverinstall}
Prerequisites: Flask and PostgreSQL
1. Pull project from [this repo](https://github.com/ritstudentgovernment/chargeflask).
2. Install and create [virtual environment](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/).
3. Create a database for the project.
4. Specify the ``SQLALCHEMY_DATABASE_URI`` in the ``config.py`` file with the database path.
5. Activate virtual environment.
6. Execute `pip install -r requirements.txt`
7. Complete the `secrets.py` file (Contact System Administrator for relevant data). 
8. Run ``python run.py``

## Testing Utilities {#testutil}
In some cases, you'd like to test if your backend code is properly working. But, because you don't have access to a frontend yet, it might seem quite hard to test your code while developing it. For this, it's recommended to install in your machine a tool called [Socket.io tester](https://electronjs.org/apps/socket-io-tester), which let's so send and retrieve data from the backend without the need of a developed client.


# Data Manipulation {#datamani}
ChargeTracker uses a technology called [SocketIO](https://socket.io/), which basically provides real-time communication between two different machines through WebSockets. SocketIO allows the easy implementation of WebSockets cross-platform and cross-language. For example, the [chargevue](https://github.com/ritstudentgovernment/chargevue) client for this application, uses the native Javascript SocketIO library, meanwhile this backend utilizes the Flask library [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/). Bellow, there are a few detailed examples on how to request or submit data to and from the ChargeTracker backend.

## Submitting Data {#submitData}
Submitting data to ChargeTracker is very simple. Basically, inside each the controllers file of each module there are certain functions that _listen_ for data in a specific event name. For example, inside the controllers of the Committees module, we can see the `get_commitees` method:

~~~~~~~~~~~~~python
##
##  Gets list of all committees.
##
##  	@param      broadcast  Flag to broadcast list of committees to all users.
##
## @emit       Emits a list of committees.
##
@socketio.on('get_committees')
def get_committees(broadcast = False):
    committees = Committees.query.filter_by(enabled = True).all()
    comm_ser = [{"id": c.id, "title": c.title} for c in committees]
    emit("get_committees", comm_ser, broadcast= broadcast)
~~~~~~~~~~~~~

We can see that every method inside the controllers start with the line `@socketio.on('<event_name>')`, this basically means that once the server listens to a request in that specific event, the function under it will be executed. In this case, when a person sends a request with the event `get_committees` to the server, the function get_committees will be executed.

To send this request to the server, the request can be written in the following way:

~~~~~~~~~~~~~{.js}
// Javascript Socket-IO request.
var socket = io.connect('http://localhost:5000');
socket.emit('get_committees');
~~~~~~~~~~~~~

We can also notice that the `get_committees` method gets the parameter broadcast, which basically broadcasts the list of committees to all the users listening, to send data to the server, you can send a JSON object or a String.

For example, if I want my request of committees to be broadcasted to everyone that is listening to `get_committees`, I can do:

```javascript
// Javascript Socket-IO request with params.
var socket = io.connect('http://localhost:5000');
socket.emit('get_committees', true);
```

## Retrieving Data {#retrieveData}

**IMPORTANT**: Also take into account that to receive this data, you have to be listening to the events with the same event_name. So, if I'd like to receive all the committees, you have to listen to the `get_committees` event name:

```javascript
// Javascript Socket-IO listener.
var socket = io.connect('http://localhost:5000');
socket.on('get_committees', function(data){
  	console.log(data);
});
```

These channels are always open, so you only have to listen to data once and you'll keep receiving new data as it becomes available, without having to create new requests!

# Module Structure {#modulestruct}

To keep the source code organized, each functionality of [ChargeTracker](https://github.com/ritstudentgovernment/chargeflask) is divided in different modules. For example, the Users module contains everything relevant to user authentication, meanwhile the Committees module has everything relevant to manipulating committees.

Every module in ChargeTracker contains the following files:

- `__init__.py` (required): This file is usually empty, its necessary to create a Python module.
- `models.py` (required): This file contains the model declaration of the module itself. This usually contains the SQLAlchemy model declaration.
- `controllers.py` (required): This file contains all the relevant controllers to manipulate data on the server, please refer to the examples on the [Data Manipulation](#datamani) section.
- `test_<module_name>.py` (required): This file contains all the test cases for this specific module, please refer to the examples on the Testing Modules section.
- `<module_name>_response.py`: Instead of hard-coding response strings inside the controllers class, all the response strings specific to this module are located inside this class. In the future, this will allow the easy implementation of [ChargeTracker](https://github.com/ritstudentgovernment/chargeflask) in a different language.

# Unit Tests and Code Coverage {#unittests}

Every module in this project is unit tested to check if the code implemented is fully functional. For unit testing, ChargeTracker utilizes the Python testing utility, [pytest](https://docs.pytest.org). To execute your unit tests locally, you can simply run the command: `py.test --cov=./app`, if you want to generate a html coverage report, the same command can be executed with the flag `--cov-report=html`. For code coverage, this project uses [TravisCI](https://travis-ci.org/) and [Codecov](https://codecov.io/gh), the TravisCI .yml file is located under `.travis.yml`, which basically contains the configuration that Travis needs to execute your code. Also, take into account that TravisCI needs a copy of your `secrets.py` to execute your code, this is done by encrypting your secrets file with TravisCI.

 