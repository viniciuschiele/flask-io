Changelog
---------

1.6.0
++++++++++++++++++
- Added DelimitedList field
- Added request tracing
- Made some marshmallow classes importable from the flask-io
- Made parameters that use from_body mandatory
- Updated marshmallow to the version 2.1.2

1.5.0
++++++++++++++++++
- Changed error response to wrap the list of errors into an attribute 'errors'
- Added extra arguments to the error class
- Refactored/Simplified the core
- Removed trace stuff (a new one will be released)

1.4.1
++++++++++++++++++
- Bug fixed in the Enum field

1.4.0
++++++++++++++++++
- Renamed module fields_ext to fields
- Added Complexity validator
- Added Password field
- Updated Marshmallow to 2.1.0
 
1.3.3
++++++++++++++++++
- Added forbidden method to the FlaskIO class

1.3.2
++++++++++++++++++
- Added member_type parameter to the Enum field to specify the type of the members

1.3.1
++++++++++++++++++
- Made Enum field compatible with marshmallow 2.0.0

1.3.0
++++++++++++++++++
- Removed fields code and message from the root level of the error response
- Renamed field reason to code in the error response

1.2.0
++++++++++++++++++
- Only non http exceptions are logged
- The content-type for response with no payload is text/html

1.1.1
++++++++++++++++++
- Added log for unhandled exceptions

1.1.0
++++++++++++++++++
- Added Enum field which accept python Enum object
- New error message when the content-type is not supported
