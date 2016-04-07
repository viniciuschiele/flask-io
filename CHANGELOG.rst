Changelog
---------

1.10.4
++++++++++++++++++
- Add call stack to the logs when a unhandled exception occurs.

1.10.3
++++++++++++++++++
- Bug fix.

1.10.2
++++++++++++++++++
- Replaces own json by Flask json.
- Update marshmallow to the version 2.6.0

1.10.1
++++++++++++++++++
- Add attribute upper to the String field.

1.10.0
++++++++++++++++++
- Add UUID field.
- Update marshmallow to the version 2.5.0

1.9.3
++++++++++++++++++
- Bug fix in String field, validators were being executed when none_if_empty==True and the current value==''

1.9.2
++++++++++++++++++
- Add mac address validator.

1.9.1
++++++++++++++++++
- Add error handle to http exception.

1.9.0
++++++++++++++++++
- Add support for 'fields' parameter, it allows to select which fields should be returned by the api.
- Add support for multiple authentications
- Add support for authorization based on permissions.
- Update marshmallow to the version 2.4.2

1.8.2
++++++++++++++++++
- Update marshmallow to the version 2.4.0

1.8.1
++++++++++++++++++
- Fix issue that prevented installing the library

1.8.0
++++++++++++++++++
- Add String field
- Add a new customizable layer called Content Negotiation to selection of Parser and Renderer
- Add support to parameters on Content-Type and Accept headers
- Improve Enum field performance.
- Remove Encoders and Decoders in favor of Parser and Renderer

1.7.0
++++++++++++++++++
- Apache Licence has been replaced for MIT Licence
- Add method 'created' into FlaskIO class
- Make pre_load and pre_dump decorators importable from flask-io
- Update marshmallow to the version 2.2.0

1.6.0
++++++++++++++++++
- Added DelimitedList field
- Added request tracing
- Made some marshmallow classes importable from the flask-io
- Made parameters that use from_body mandatory
- Updated marshmallow to the version 2.1.2

1.5.0
++++++++++++++++++
- Change error response to wrap the list of errors into an attribute 'errors'
- Add extra arguments to the error class
- Refactor/Simplify the core
- Remove trace stuff (a new one will be released)

1.4.1
++++++++++++++++++
- Bug fix in the Enum field

1.4.0
++++++++++++++++++
- Rename module fields_ext to fields
- Add Complexity validator
- Add Password field
- Update Marshmallow to 2.1.0
 
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
